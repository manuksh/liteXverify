"""Unit tests for tool_discover tool."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from litex_verify.core.context import ServerContext
from litex_verify.tools.tool_discover import ToolDiscoverInput, ToolDiscoverTool


@pytest.mark.asyncio
async def test_tool_discover_returns_output(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    tool = ToolDiscoverTool(ctx)
    with patch.object(ctx.eda_tools, "detect_all", new=AsyncMock(return_value={})):
        result = await tool.execute(ToolDiscoverInput())
    assert result.verification_tier >= 1
    assert isinstance(result.tools, dict)
    assert isinstance(result.missing_recommended, list)


@pytest.mark.asyncio
async def test_tool_discover_lists_missing(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    tool = ToolDiscoverTool(ctx)
    with patch.object(ctx.eda_tools, "detect_all", new=AsyncMock(return_value={})):
        result = await tool.execute(ToolDiscoverInput())
    assert "verilator" in result.missing_recommended


@pytest.mark.asyncio
async def test_tool_discover_force_rescan(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    tool = ToolDiscoverTool(ctx)
    mock_detect = AsyncMock(return_value={})
    with patch.object(ctx.eda_tools, "detect_all", new=mock_detect):
        await tool.execute(ToolDiscoverInput(force_rescan=True))
    mock_detect.assert_called_once_with(force=True)
