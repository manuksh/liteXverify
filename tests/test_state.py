from pathlib import Path

import pytest

from litex_verify.core.state import StateMachine, WorkflowState
from litex_verify.utils.filesystem import SandboxedFileSystem


@pytest.mark.asyncio
async def test_state_machine_transition(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    sm = StateMachine(project, SandboxedFileSystem(tmp_path))
    await sm.transition(WorkflowState.S1_CONFIG, "test", force=True)
    assert sm.current_state == WorkflowState.S1_CONFIG
