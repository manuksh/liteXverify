"""Shared fixtures for unit tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import pytest_asyncio

from litex_verify.core.context import ServerContext
from litex_verify.core.state import WorkflowState
from litex_verify.models.project import ProjectState
from litex_verify.models.soc_config import BusConfig, CPUConfig, SoCConfig


@pytest.fixture()
def workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws


@pytest.fixture()
def ctx(workspace: Path) -> ServerContext:
    return ServerContext(workspace)


@pytest.fixture()
def soc_config() -> SoCConfig:
    return SoCConfig(
        cpu=CPUConfig(type="vexriscv"),
        bus=BusConfig(standard="wishbone"),
    )


@pytest_asyncio.fixture()
async def active_project(ctx: ServerContext, soc_config: SoCConfig) -> Path:
    """Create a minimal active project directory with state + config files."""
    project_dir = ctx.workspace / "projects" / "test_proj"
    meta = project_dir / ".litex_verify"
    cfg_dir = project_dir / "config"
    meta.mkdir(parents=True)
    cfg_dir.mkdir(parents=True)

    state = ProjectState(project_name="test_proj")
    state.workflow_state = WorkflowState.S1_CONFIG
    (meta / "state.json").write_text(
        json.dumps(state.model_dump(mode="json")), encoding="utf-8"
    )

    (cfg_dir / "soc_config.json").write_text(
        soc_config.model_json_schema() and soc_config.model_dump_json(),
        encoding="utf-8",
    )

    ctx.set_active_project(project_dir)
    return project_dir
