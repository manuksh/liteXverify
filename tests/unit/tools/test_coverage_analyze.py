"""Unit tests for coverage_analyze tool."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from litex_verify.core.context import ServerContext
from litex_verify.core.exceptions import StateError
from litex_verify.core.state import WorkflowState
from litex_verify.models.project import ProjectState
from litex_verify.models.simulation import SimulationRun
from litex_verify.tools.coverage_analyze import CoverageAnalyzeInput, CoverageAnalyzeTool


def _setup(
    ctx: ServerContext,
    runs: list[SimulationRun] | None = None,
    state: WorkflowState = WorkflowState.S5_ANALYSIS,
) -> Path:
    proj = ctx.workspace / "proj"
    meta = proj / ".litex_verify"
    meta.mkdir(parents=True)
    ps = ProjectState(project_name="proj", workflow_state=state, runs=runs or [])
    (meta / "state.json").write_text(
        json.dumps(ps.model_dump(mode="json")), encoding="utf-8"
    )
    ctx.set_active_project(proj)
    return proj


def _make_run(tmp_path: Path, coverage: float, status: str = "passed") -> SimulationRun:
    cov_file = tmp_path / f"cov_{coverage}.json"
    cov_file.write_text(json.dumps({"coverage": coverage}), encoding="utf-8")
    log_file = tmp_path / f"run_{coverage}.log"
    log_file.write_text("", encoding="utf-8")
    return SimulationRun(
        run_id=f"r{int(coverage)}",
        status=status,
        tests=[],
        duration=1,
        log_path=str(log_file),
        coverage_db=str(cov_file),
    )


@pytest.mark.asyncio
async def test_no_project_raises(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    with pytest.raises(StateError):
        await CoverageAnalyzeTool(ctx).execute(CoverageAnalyzeInput())


@pytest.mark.asyncio
async def test_empty_runs_returns_zero_coverage(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    _setup(ctx)
    result = await CoverageAnalyzeTool(ctx).execute(CoverageAnalyzeInput())
    assert result.overall == 0.0
    assert not result.meets_threshold


@pytest.mark.asyncio
async def test_high_coverage_meets_threshold(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    runs = [_make_run(tmp_path, 95.0)]
    _setup(ctx, runs=runs)
    result = await CoverageAnalyzeTool(ctx).execute(CoverageAnalyzeInput(threshold=90))
    assert result.overall == 95.0
    assert result.meets_threshold


@pytest.mark.asyncio
async def test_trend_reflects_multiple_runs(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    runs = [_make_run(tmp_path, float(v)) for v in [50, 70, 90]]
    _setup(ctx, runs=runs)
    result = await CoverageAnalyzeTool(ctx).execute(CoverageAnalyzeInput())
    assert len(result.trend) == 3


@pytest.mark.asyncio
async def test_filter_by_run_id(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    runs = [_make_run(tmp_path, 30.0), _make_run(tmp_path, 95.0)]
    _setup(ctx, runs=runs)
    result = await CoverageAnalyzeTool(ctx).execute(
        CoverageAnalyzeInput(run_ids=[runs[1].run_id], threshold=90)
    )
    assert result.meets_threshold
