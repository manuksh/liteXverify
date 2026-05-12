import pytest

from litex_verify.models.project import ProjectState


def test_project_name_validation() -> None:
    with pytest.raises(ValueError):
        ProjectState(project_name="1bad")

    state = ProjectState(project_name="Good_Name")
    assert state.project_name == "Good_Name"
