"""VBI tags."""
from enum import Enum

from dkist_processing_common.models.tags import Tag


class VbiStemName(str, Enum):
    """VBI specific tag stems."""

    current_spatial_step = "STEP"


class VbiTag(Tag):
    """VBI specific tag formatting."""

    @classmethod
    def spatial_step(cls, step_num: int) -> str:
        """
        Tags by spatial step.

        Parameters
        ----------
        step_num: int
            The step number in the FOV
        """
        return cls.format_tag(VbiStemName.current_spatial_step, step_num)
