"""VBI-specific assemble movie task subclass."""
import numpy as np
from astropy.visualization import ZScaleInterval
from dkist_processing_common.tasks import AssembleMovie
from matplotlib import cm
from PIL import ImageDraw

from dkist_processing_vbi.parsers.vbi_l1_fits_access import VbiL1FitsAccess


class AssembleVbiMovie(AssembleMovie):
    """
    Class for assembling pre-made movie frames (as FITS/numpy) into an mp4 movie file.

    Subclassed from the AssembleMovie task in dkist_processing_common to add VBI specific text overlays.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    @property
    def fits_parsing_class(self):
        """VBI specific subclass of L1FitsAccess to use for reading images."""
        return VbiL1FitsAccess

    def apply_colormap(self, array: np.ndarray) -> np.ndarray:
        """
        Convert floats to RGB colors using the ZScale normalization scheme.

        Parameters
        ----------
        array : np.ndarray
            data to convert
        """
        color_mapper = cm.get_cmap(self.MPL_COLOR_MAP)
        scaled_array = ZScaleInterval()(array)
        return color_mapper(scaled_array, bytes=True)[
            :, :, :-1
        ]  # Drop the last (alpha) color dimension

    def write_overlay(self, draw: ImageDraw, fits_obj: VbiL1FitsAccess) -> None:
        """
        Mark each image with it's instrument, observed wavelength, and observation time.

        Parameters
        ----------
        draw
            A simple 2D drawing function for PIL images

        fits_obj
            A single movie "image", i.e., a single array tagged with VBITag.movie_frame
        """
        self.write_line(
            draw, f"INSTRUMENT: {self.constants.instrument}", 3, "right", font=self.font_18
        )
        self.write_line(draw, f"WAVELENGTH: {fits_obj.wavelength}", 2, "right", font=self.font_15)
        self.write_line(draw, f"DATE OBS: {fits_obj.time_obs}", 1, "right", font=self.font_15)
