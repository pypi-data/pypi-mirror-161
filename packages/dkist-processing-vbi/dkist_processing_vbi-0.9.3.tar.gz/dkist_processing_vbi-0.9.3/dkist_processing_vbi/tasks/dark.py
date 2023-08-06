"""VBI dark calibration task."""
import logging

from astropy.io import fits
from dkist_processing_common.tasks.mixin.fits import FitsDataMixin
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.statistics import average_numpy_arrays

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess
from dkist_processing_vbi.tasks.vbi_base import VbiTaskBase


class DarkCalibration(VbiTaskBase, FitsDataMixin, QualityMixin):
    """
    Task class for calculation of the averaged dark frame for a VBI calibration run.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    record_provenance = True

    def run(self) -> None:
        """
        For each spatial step.

            - Gather input dark frames
            - Calculate average dark
            - Write average dark
            - Record quality metrics

        Returns
        -------
        None

        """
        target_exp_times = list(
            set(self.constants.gain_exposure_times + self.constants.observe_exposure_times)
        )
        logging.info(f"{target_exp_times = }")
        with self.apm_task_step(
            f"Calculating dark frames for {self.constants.num_spatial_steps} steps and {len(target_exp_times)} exp times",
        ):
            total_dark_frames_used = 0
            for exp_time in target_exp_times:
                for step in range(1, self.constants.num_spatial_steps + 1):
                    logging.info(f"collecting dark frames for step {step}")
                    dark_tags = [
                        VbiTag.input(),
                        VbiTag.frame(),
                        VbiTag.task("DARK"),
                        VbiTag.spatial_step(step),
                        VbiTag.exposure_time(exp_time),
                    ]
                    current_exp_dark_count = self.count(tags=dark_tags)
                    if current_exp_dark_count == 0:
                        raise ValueError(f"Could not find any darks for {exp_time = }")
                    total_dark_frames_used += current_exp_dark_count
                    input_dark_fits_access = self.fits_data_read_fits_access(
                        tags=dark_tags,
                        cls=VbiL0FitsAccess,
                    )
                    input_dark_arrays = (obj.data for obj in input_dark_fits_access)

                    with self.apm_processing_step(
                        f"Processing dark for {step = } and {exp_time = }"
                    ):
                        logging.info(f"averaging arrays for step {step}")
                        averaged_dark_array = average_numpy_arrays(input_dark_arrays)
                        logging.info(
                            f"average dark signal in step {step} = {averaged_dark_array.mean():.3e}"
                        )

                    with self.apm_writing_step(
                        f"Writing intermediate dark for {step = } and {exp_time = }",
                    ):
                        logging.info(f"writing dark calibration for step {step}")
                        hdul = fits.HDUList([fits.PrimaryHDU(data=averaged_dark_array)])
                        self.fits_data_write(
                            hdu_list=hdul,
                            tags=[
                                VbiTag.intermediate(),
                                VbiTag.frame(),
                                VbiTag.task("DARK"),
                                VbiTag.spatial_step(step),
                                VbiTag.exposure_time(exp_time),
                            ],
                        )

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_dark_frames: int = self.count(
                tags=[VbiTag.input(), VbiTag.frame(), VbiTag.task("DARK")]
            )
            unused_count = no_of_raw_dark_frames - total_dark_frames_used
            self.quality_store_task_type_counts(
                task_type="dark", total_frames=no_of_raw_dark_frames, frames_not_used=unused_count
            )
