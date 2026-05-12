"""Unit tests for project_init tool."""
from __future__ import annotations

from pathlib import Path

import pytest

from litex_verify.core.context import ServerContext
from litex_verify.core.exceptions import ProjectExistsError, ToolError
from litex_verify.tools.project_init import ProjectInitInput, ProjectInitTool


@pytest.mark.asyncio
async def test_project_init_creates_structure(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    tool = ProjectInitTool(ctx)
    result = await tool.execute(ProjectInitInput(project_name="my_proj"))
    assert result.success
    assert Path(result.project_path).exists()
    assert (Path(result.project_path) / "README.md").exists()


@pytest.mark.asyncio
async def test_project_init_sets_active_project(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    tool = ProjectInitTool(ctx)
    await tool.execute(ProjectInitInput(project_name="my_proj"))
    assert ctx.active_project is not None


@pytest.mark.asyncio
async def test_project_init_duplicate_raises(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    tool = ProjectInitTool(ctx)
    await tool.execute(ProjectInitInput(project_name="my_proj"))
    with pytest.raises(ProjectExistsError):
        await tool.execute(ProjectInitInput(project_name="my_proj"))


@pytest.mark.asyncio
async def test_project_init_outside_workspace_raises(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    ws.mkdir()
    outside = tmp_path / "outside"
    ctx = ServerContext(ws)
    tool = ProjectInitTool(ctx)
    with pytest.raises(ToolError):
        await tool.execute(
            ProjectInitInput(project_name="bad", target_dir=str(outside))
        )


@pytest.mark.asyncio
async def test_project_init_invalid_name_raises(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    tool = ProjectInitTool(ctx)
    with pytest.raises(Exception):
        await tool.execute(ProjectInitInput(project_name="123bad"))


@pytest.mark.asyncio
async def test_project_init_minimal_template(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    tool = ProjectInitTool(ctx)
    result = await tool.execute(
        ProjectInitInput(project_name="mini", template="minimal")
    )
    assert result.success
    assert "rtl" in result.structure
