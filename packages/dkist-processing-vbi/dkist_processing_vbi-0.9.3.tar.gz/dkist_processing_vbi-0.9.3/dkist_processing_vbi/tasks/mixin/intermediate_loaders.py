"""Helper to manage intermediate data."""
from typing import Generator

import numpy as np
from dkist_processing_common.tasks.base import tag_type_hint

from dkist_processing_vbi.models.tags import VbiTag


class IntermediateLoaderMixin:
    """Mixin for methods that allow easy loading of an intermediate frame's numpy arrays."""

    def load_intermediate_arrays(self, tags: tag_type_hint) -> Generator[np.ndarray, None, None]:
        """
        Load intermediate fits arrays.

        Parameters
        ----------
        tags
            Tags to denote what frames to load

        Returns
        -------
        Generator:
            Generator of loaded intermediate arrays

        """
        if VbiTag.intermediate() not in tags:
            tags += [VbiTag.intermediate()]
        for path, hdu in self.fits_data_read_hdu(tags=tags):
            yield hdu.data

    def intermediate_dark_array(self, spatial_step: int, exposure_time: float) -> np.ndarray:
        """
        Load intermediate dark array for a single spatial step and exposure time.

        Parameters
        ----------
        spatial_step : int
            The single step within the spatial scan for this dark array
        exposure_time : float
            The exposure time of the dark array

        Returns
        -------
        np.ndarray:
            Intermediate dark array

        """
        tags = [
            VbiTag.task("DARK"),
            VbiTag.spatial_step(spatial_step),
            VbiTag.exposure_time(exposure_time),
        ]
        return next(self.load_intermediate_arrays(tags=tags))

    def intermediate_gain_array(self, spatial_step: int) -> np.ndarray:
        """
        Load intermediate gain array for a single spatial step and exposure time.

        Parameters
        ----------
        spatial_step : int
            The single step within the spatial scan for this gain array

        Returns
        -------
        np.ndarray:
            Intermediate gain array

        """
        tags = [VbiTag.task("GAIN"), VbiTag.spatial_step(spatial_step)]
        return next(self.load_intermediate_arrays(tags=tags))
