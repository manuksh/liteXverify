"""Unit tests for sim_run tool."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from litex_verify.core.context import ServerContext
from litex_verify.core.exceptions import StateError, ToolError
from litex_verify.core.state import WorkflowState
from litex_verify.models.project import ProjectState
from litex_verify.tools.sim_run import SimRunInput, SimRunTool


def _make_project(ctx: ServerContext, state: WorkflowState = WorkflowState.S3_TB) -> Path:
    proj = ctx.workspace / "proj"
    meta = proj / ".litex_verify"
    meta.mkdir(parents=True)
    ps = ProjectState(project_name="proj", workflow_state=state)
    (meta / "state.json").write_text(
        json.dumps(ps.model_dump(mode="json")), encoding="utf-8"
    )
    ctx.set_active_project(proj)
    await_sm = ctx.state_machine
    return proj


@pytest.mark.asyncio
async def test_sim_run_stub_passed(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _make_project(ctx)
    tool = SimRunTool(ctx)
    with patch.object(ctx.eda_tools, "detect_all", new=AsyncMock(return_value={})):
        result = await tool.execute(SimRunInput(tests=["sanity"]))
    assert result.status == "passed"
    assert len(result.tests) == 1
    assert result.tests[0].name == "sanity"


@pytest.mark.asyncio
async def test_sim_run_stub_fail_named_test(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _make_project(ctx)
    tool = SimRunTool(ctx)
    with patch.object(ctx.eda_tools, "detect_all", new=AsyncMock(return_value={})):
        result = await tool.execute(SimRunInput(tests=["fail_test"]))
    assert result.status == "failed"


@pytest.mark.asyncio
async def test_sim_run_no_project_raises(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    tool = SimRunTool(ctx)
    with pytest.raises(StateError):
        await tool.execute(SimRunInput())


@pytest.mark.asyncio
async def test_sim_run_unavailable_simulator_raises(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _make_project(ctx)
    tool = SimRunTool(ctx)
    with patch.object(ctx.eda_tools, "detect_all", new=AsyncMock(return_value={})):
        with pytest.raises(ToolError) as exc_info:
            await tool.execute(SimRunInput(simulator="questa"))
    assert exc_info.value.code == 9001


@pytest.mark.asyncio
async def test_sim_run_creates_log_file(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _make_project(ctx)
    tool = SimRunTool(ctx)
    with patch.object(ctx.eda_tools, "detect_all", new=AsyncMock(return_value={})):
        result = await tool.execute(SimRunInput())
    assert Path(result.log_path).exists()


@pytest.mark.asyncio
async def test_sim_run_wave_file_when_enabled(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _make_project(ctx)
    tool = SimRunTool(ctx)
    with patch.object(ctx.eda_tools, "detect_all", new=AsyncMock(return_value={})):
        result = await tool.execute(SimRunInput(waves=True))
    assert result.wave_file is not None
    assert Path(result.wave_file).exists()


@pytest.mark.asyncio
async def test_sim_run_no_wave_file_by_default(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _make_project(ctx)
    tool = SimRunTool(ctx)
    with patch.object(ctx.eda_tools, "detect_all", new=AsyncMock(return_value={})):
        result = await tool.execute(SimRunInput(waves=False))
    assert result.wave_file is None


@pytest.mark.asyncio
async def test_sim_run_appends_to_project_state(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _make_project(ctx)
    tool = SimRunTool(ctx)
    with patch.object(ctx.eda_tools, "detect_all", new=AsyncMock(return_value={})):
        result = await tool.execute(SimRunInput())
    state = await ctx.load_project_state()
    assert any(r.run_id == result.run_id for r in state.runs)
