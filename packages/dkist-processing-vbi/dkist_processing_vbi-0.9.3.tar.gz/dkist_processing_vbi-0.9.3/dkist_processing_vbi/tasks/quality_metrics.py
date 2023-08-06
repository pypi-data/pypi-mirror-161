"""VBI specific quality metrics."""
from dkist_processing_common.parsers.quality import L1QualityFitsAccess
from dkist_processing_common.tasks.mixin.fits import FitsDataMixin
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_common.tasks.quality_metrics import QualityL0Metrics

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.vbi_base import VbiTaskBase


class VbiQualityL0Metrics(QualityL0Metrics):
    """
    Task class for collecting VBI L0 quality metrics.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    def run(self) -> None:
        """Calculate L0 metrics for VBI data."""
        paths = self.read(tags=[VbiTag.input()])
        self.calculate_l0_metrics(paths=paths)


class VbiQualityL1Metrics(VbiTaskBase, QualityMixin, FitsDataMixin):
    """
    Task class for collecting VBI L1 quality metrics.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    def run(self):
        """Calculate L1 metrics for VBI data."""
        frames = self.fits_data_read_fits_access(
            tags=[
                VbiTag.output(),
                VbiTag.frame(),
            ],
            cls=L1QualityFitsAccess,
        )
        datetimes = []
        noise_values = []
        with self.apm_processing_step("Calculating VBI L1 quality metrics"):
            for frame in frames:
                datetimes.append(frame.time_obs)
                noise_values.append(self.avg_noise(frame.data))

        with self.apm_processing_step("Sending lists for storage"):
            self.quality_store_noise(datetimes=datetimes, values=noise_values)
