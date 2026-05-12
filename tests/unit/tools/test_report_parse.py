"""Unit tests for report_parse tool."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from litex_verify.core.context import ServerContext
from litex_verify.core.exceptions import StateError, ToolError
from litex_verify.core.state import WorkflowState
from litex_verify.models.project import ProjectState
from litex_verify.models.simulation import SimulationRun
from litex_verify.tools.report_parse import ReportParseInput, ReportParseTool


def _setup(ctx: ServerContext, runs: list[SimulationRun] | None = None) -> Path:
    proj = ctx.workspace / "proj"
    meta = proj / ".litex_verify"
    logs = proj / "sim" / "logs"
    meta.mkdir(parents=True)
    logs.mkdir(parents=True)
    ps = ProjectState(
        project_name="proj",
        workflow_state=WorkflowState.S4_SIM,
        runs=runs or [],
    )
    (meta / "state.json").write_text(
        json.dumps(ps.model_dump(mode="json")), encoding="utf-8"
    )
    ctx.set_active_project(proj)
    return proj


@pytest.mark.asyncio
async def test_parse_no_runs_raises(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _setup(ctx)
    tool = ReportParseTool(ctx)
    with pytest.raises(ToolError) as exc_info:
        await tool.execute(ReportParseInput())
    assert exc_info.value.code == 6001


@pytest.mark.asyncio
async def test_parse_explicit_log_path(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    proj = _setup(ctx)
    log = proj / "sim" / "logs" / "test.log"
    log.write_text("TEST sanity PASSED\n", encoding="utf-8")
    tool = ReportParseTool(ctx)
    result = await tool.execute(ReportParseInput(log_path=str(log)))
    assert result.summary["passed"] == 1


@pytest.mark.asyncio
async def test_parse_last_run(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    log_path = tmp_path / "sim.log"
    log_path.write_text("TEST alpha PASSED\nTEST beta FAILED\n", encoding="utf-8")
    run = SimulationRun(
        run_id="abc",
        status="failed",
        tests=[],
        duration=0,
        log_path=str(log_path),
        coverage_db=str(tmp_path / "cov.json"),
    )
    _setup(ctx, runs=[run])
    tool = ReportParseTool(ctx)
    result = await tool.execute(ReportParseInput())
    assert result.summary["passed"] == 1
    assert result.summary["failed"] == 1


@pytest.mark.asyncio
async def test_parse_uvm_errors_detected(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    log_path = tmp_path / "uvm.log"
    log_path.write_text("UVM_FATAL @ 100ns: assertion failed\n", encoding="utf-8")
    run = SimulationRun(
        run_id="x1",
        status="failed",
        tests=[],
        duration=0,
        log_path=str(log_path),
        coverage_db=str(tmp_path / "cov.json"),
    )
    _setup(ctx, runs=[run])
    tool = ReportParseTool(ctx)
    result = await tool.execute(ReportParseInput())
    assert result.uvm_report["fatal"] == 1
