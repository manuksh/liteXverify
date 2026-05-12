"""Unit tests for workflow_state tool."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from litex_verify.core.context import ServerContext
from litex_verify.core.exceptions import StateError, ToolError
from litex_verify.core.state import WorkflowState
from litex_verify.models.project import ProjectState
from litex_verify.tools.workflow_state import WorkflowStateInput, WorkflowStateTool


def _setup_project(ctx: ServerContext, state: WorkflowState = WorkflowState.S0_INIT) -> None:
    proj = ctx.workspace / "proj"
    meta = proj / ".litex_verify"
    meta.mkdir(parents=True)
    ps = ProjectState(project_name="proj", workflow_state=state)
    (meta / "state.json").write_text(
        json.dumps(ps.model_dump(mode="json")), encoding="utf-8"
    )
    ctx.set_active_project(proj)


@pytest.mark.asyncio
async def test_get_current_state(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _setup_project(ctx)
    tool = WorkflowStateTool(ctx)
    result = await tool.execute(WorkflowStateInput(action="get"))
    assert result.current_state == WorkflowState.S0_INIT.value


@pytest.mark.asyncio
async def test_transition_with_force(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _setup_project(ctx)
    tool = WorkflowStateTool(ctx)
    # WorkflowState enum values are "S0","S1",... not "S0_INIT","S1_CONFIG"
    result = await tool.execute(
        WorkflowStateInput(action="transition", target_state="S1", force=True)
    )
    assert result.current_state == "S1"


@pytest.mark.asyncio
async def test_invalid_state_raises_tool_error(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _setup_project(ctx)
    tool = WorkflowStateTool(ctx)
    with pytest.raises(ToolError) as exc_info:
        await tool.execute(
            WorkflowStateInput(action="transition", target_state="NONEXISTENT", force=True)
        )
    assert exc_info.value.code == 1001


@pytest.mark.asyncio
async def test_reset_returns_to_init(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _setup_project(ctx, WorkflowState.S3_TB)
    tool = WorkflowStateTool(ctx)
    result = await tool.execute(WorkflowStateInput(action="reset"))
    assert result.current_state == WorkflowState.S0_INIT.value


@pytest.mark.asyncio
async def test_no_state_machine_raises(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)  # no active project → no state machine
    tool = WorkflowStateTool(ctx)
    with pytest.raises(StateError):
        await tool.execute(WorkflowStateInput(action="get"))
