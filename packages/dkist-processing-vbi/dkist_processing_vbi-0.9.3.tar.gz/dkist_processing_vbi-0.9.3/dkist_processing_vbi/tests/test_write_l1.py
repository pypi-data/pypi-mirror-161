import logging
from dataclasses import asdict
from random import randint

import numpy as np
import pytest
from astropy.io import fits
from dkist_fits_specifications import __version__ as spec_version
from dkist_header_validator import spec122_validator
from dkist_header_validator import spec214_validator
from dkist_processing_common.models.tags import Tag

from dkist_processing_vbi.models.constants import VbiConstants
from dkist_processing_vbi.tasks.write_l1 import VbiWriteL1Frame
from dkist_processing_vbi.tests.conftest import FakeGQLClient
from dkist_processing_vbi.tests.conftest import VbiConstantsDb
from dkist_processing_vbi.tests.conftest import VbiS122Headers


@pytest.fixture(scope="session")
def calibrated_header():
    ds = VbiS122Headers(array_shape=(1, 2, 2), num_steps=1)
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]

    header = header_list[0]
    header["CUNIT1"] = "m"
    header["CUNIT2"] = "arcsec"
    header["CUNIT3"] = "s"
    header["VBINSTP"] = 9
    header["VBISTP"] = 5
    header["VBINFRAM"] = 3
    header["VBICFRAM"] = 2
    header["DSPSNUM"] = 2
    return header


@pytest.fixture(scope="session")
def write_l1_task(calibrated_header):
    recipe_run_id = randint(0, 99999)
    constants_db = VbiConstantsDb(
        AVERAGE_CADENCE=10,
        MINIMUM_CADENCE=10,
        MAXIMUM_CADENCE=10,
        VARIANCE_CADENCE=0,
        NUM_DSPS_REPEATS=2,
        SPECTRAL_LINE="VBI-Red H-alpha",
    )
    # Repeat ini_vbi_constants fixture here because of a scope conflict
    constants = VbiConstants(recipe_run_id=recipe_run_id, task_name="test")
    constants._update(asdict(constants_db))
    with VbiWriteL1Frame(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        hdu = fits.PrimaryHDU(data=np.ones(shape=(10, 11)), header=calibrated_header)
        hdul = fits.HDUList([hdu])
        task.fits_data_write(
            hdu_list=hdul,
            tags=[Tag.calibrated(), Tag.frame(), Tag.stokes("I")],
        )
        yield task
        task.constants._purge()
        task.scratch.purge()


def test_write_l1_frame(write_l1_task, mocker):
    """
    :Given: a write L1 task
    :When: running the task
    :Then: no errors are raised
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    task = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output(), Tag.stokes("I")]))
    assert len(files) == 1
    for file in files:
        logging.info(f"Checking file {file}")
        assert file.exists
        hdl = fits.open(file)
        assert len(hdl) == 2
        header = hdl[1].header
        assert spec214_validator.validate(input_headers=header, extra=False)
        assert header["DNAXIS1"] == 11
        assert header["DNAXIS2"] == 10
        assert header["DNAXIS3"] == 6  # num_dsps * num_exp_per_dsp
        assert header["DINDEX3"] == 5
        assert header["DUNIT1"] == "m"
        assert header["DUNIT2"] == "arcsec"
        assert header["DUNIT3"] == "s"
        assert header["WAVEMIN"] == 656.258
        assert header["WAVEMAX"] == 656.306
        assert header["WAVEBAND"] == "VBI-Red H-alpha"
        assert header["MAXIS1"] == 3
        assert header["MAXIS2"] == 3
        assert header["MINDEX1"] == 2
        assert header["MINDEX2"] == 2
        assert header["INFO_URL"] == task.docs_base_url
        assert header["HEADVERS"] == spec_version
        assert (
            header["HEAD_URL"] == f"{task.docs_base_url}/projects/data-products/en/v{spec_version}"
        )
        calvers = task._get_version_from_module_name()
        assert header["CALVERS"] == calvers
        assert (
            header["CAL_URL"]
            == f"{task.docs_base_url}/projects/{task.constants.instrument.lower()}/en/v{calvers}/{task.workflow_name}.html"
        )
