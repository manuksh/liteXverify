"""Unit tests for report_generate tool."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from litex_verify.core.context import ServerContext
from litex_verify.core.state import WorkflowState
from litex_verify.models.project import ProjectState
from litex_verify.models.simulation import SimulationRun, TestResult
from litex_verify.tools.report_generate import ReportGenerateInput, ReportGenerateTool


def _make_run(tmp_path: Path, coverage: float, status: str = "passed") -> SimulationRun:
    cov = tmp_path / f"c{int(coverage)}.json"
    cov.write_text(json.dumps({"coverage": coverage}), encoding="utf-8")
    log = tmp_path / f"l{int(coverage)}.log"
    log.write_text("", encoding="utf-8")
    t = TestResult(name="t", status=status, duration_ms=100, seed=1, log_snippet="")
    return SimulationRun(
        run_id=f"r{int(coverage)}",
        status=status,
        tests=[t],
        duration=0,
        log_path=str(log),
        coverage_db=str(cov),
    )


def _setup(
    ctx: ServerContext,
    runs: list[SimulationRun],
    state: WorkflowState = WorkflowState.S5_ANALYSIS,
) -> None:
    proj = ctx.workspace / "proj"
    meta = proj / ".litex_verify"
    rpts = proj / "reports"
    meta.mkdir(parents=True)
    rpts.mkdir(parents=True)
    ps = ProjectState(project_name="proj", workflow_state=state, runs=runs)
    (meta / "state.json").write_text(
        json.dumps(ps.model_dump(mode="json")), encoding="utf-8"
    )
    ctx.set_active_project(proj)


@pytest.mark.asyncio
async def test_report_html_created(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _setup(ctx, runs=[_make_run(tmp_path, 95.0)])
    result = await ReportGenerateTool(ctx).execute(ReportGenerateInput(format="html"))
    assert Path(result.report_path).exists()
    assert result.format == "html"


@pytest.mark.asyncio
async def test_report_json_format(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _setup(ctx, runs=[_make_run(tmp_path, 95.0)])
    result = await ReportGenerateTool(ctx).execute(ReportGenerateInput(format="json"))
    content = json.loads(Path(result.report_path).read_text())
    assert "project" in content


@pytest.mark.asyncio
async def test_high_coverage_meets_threshold(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _setup(ctx, runs=[_make_run(tmp_path, 95.0, "passed")])
    result = await ReportGenerateTool(ctx).execute(ReportGenerateInput())
    assert result.meets_threshold
    assert not result.iterate_required


@pytest.mark.asyncio
async def test_low_coverage_triggers_iterate(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _setup(ctx, runs=[_make_run(tmp_path, 50.0, "passed")])
    result = await ReportGenerateTool(ctx).execute(ReportGenerateInput())
    assert not result.meets_threshold
    assert result.iterate_required


@pytest.mark.asyncio
async def test_failed_run_does_not_meet_threshold(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _setup(ctx, runs=[_make_run(tmp_path, 95.0, "failed")])
    result = await ReportGenerateTool(ctx).execute(ReportGenerateInput())
    assert not result.meets_threshold
