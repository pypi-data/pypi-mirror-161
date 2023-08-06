from dataclasses import asdict

import pytest

from dkist_processing_vbi.tasks.vbi_base import VbiTaskBase
from dkist_processing_vbi.tests.conftest import VbiConstantsDb


@pytest.fixture(scope="session")
def expected_constant_dict() -> dict:
    lower_dict = asdict(VbiConstantsDb())
    return {k.upper(): v for k, v in lower_dict.items()}


@pytest.fixture(scope="function")
def vbi_science_task_with_constants(expected_constant_dict, recipe_run_id):
    class Task(VbiTaskBase):
        def run(self):
            ...

    task = Task(
        recipe_run_id=recipe_run_id,
        workflow_name="test_vbi_constants",
        workflow_version="VX.Y",
    )
    task.constants._update(expected_constant_dict)

    yield task

    task.constants._purge()


def test_vbi_constants(vbi_science_task_with_constants, expected_constant_dict):
    """
    Given: A VbiScienceTask with a constants attribute
    When: Accessing specifici constants
    Then: The correct values are returned
    """
    task = vbi_science_task_with_constants
    for k, v in expected_constant_dict.items():
        if type(v) is tuple:
            v = list(v)  # Because dataclass

        raw_val = getattr(task.constants, k.lower())
        if type(raw_val) is tuple:
            raw_val = list(raw_val)  # Because dataclass

        assert raw_val == v
