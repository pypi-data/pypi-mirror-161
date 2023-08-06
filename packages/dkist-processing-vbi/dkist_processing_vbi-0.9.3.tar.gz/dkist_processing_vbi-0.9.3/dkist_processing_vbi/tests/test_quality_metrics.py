import json

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS
from dkist_data_simulator.spec214 import Spec214Dataset
from dkist_processing_common.models.tags import Tag

from dkist_processing_vbi.tasks.quality_metrics import VbiQualityL1Metrics


class BaseSpec214Dataset(Spec214Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
        )

    @property
    def fits_wcs(self):
        w = WCS(naxis=2)
        w.wcs.crpix = self.array_shape[1] / 2, self.array_shape[0] / 2
        w.wcs.crval = 0, 0
        w.wcs.cdelt = 1, 1
        w.wcs.cunit = "arcsec", "arcsec"
        w.wcs.ctype = "HPLN-TAN", "HPLT-TAN"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


@pytest.fixture
def vbi_l1_quality_task(tmp_path, recipe_run_id):
    with VbiQualityL1Metrics(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        for i in range(10):
            header_dict = [
                d.header(required_only=False, expected_only=False) for d in BaseSpec214Dataset()
            ][0]
            data = np.ones(shape=BaseSpec214Dataset().array_shape)
            hdu = fits.PrimaryHDU(data=data, header=fits.Header(header_dict))
            hdul = fits.HDUList([hdu])
            task.fits_data_write(hdu_list=hdul, tags=[Tag.output(), Tag.frame()])
        yield task
    task.scratch.purge()
    task.constants._purge()


def test_noise(vbi_l1_quality_task):
    """
    Given: a task with the QualityL1Metrics class
    When: checking that the noise metric was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the expected schema
    """
    task = vbi_l1_quality_task
    task()
    files = list(task.read(tags=Tag.quality("NOISE")))
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert all(isinstance(item, str) for item in data["x_values"])
            assert all(isinstance(item, float) for item in data["y_values"])
