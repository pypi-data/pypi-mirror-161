from unittest.mock import PropertyMock

import pytest

from dkist_processing_vbi.tasks.vbi_base import VbiTaskBase


@pytest.fixture
def expected_constants_dict():
    # Just make up a super simple db with a single constant that vbi uses
    return {"NUM_SPATIAL_STEPS": 4}


@pytest.fixture(scope="function")
def vbi_science_task(recipe_run_id, expected_constants_dict):
    class DummyTask(VbiTaskBase):
        def run(self):
            pass

    task = DummyTask(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_dummy_task",
        workflow_version="VX.Y",
    )

    task.constants._update(expected_constants_dict)
    yield task
    task.scratch.purge()
    task.constants._purge()


def test_constants_init(vbi_science_task, expected_constants_dict):
    """
    Given: A VbiTaskBase with a populated backend ConstantsDb
    When: Initializing the task
    Then: The .constants attribute is loaded correctly
    """
    constants_obj = vbi_science_task.constants
    for k, v in expected_constants_dict.items():
        assert getattr(constants_obj, k.lower()) == v
