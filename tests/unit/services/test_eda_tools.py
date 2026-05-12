"""Unit tests for EDAToolService."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from litex_verify.core.exceptions import ToolNotFoundError
from litex_verify.models.project import ToolInfo
from litex_verify.services.eda_tools import EDAToolService, VerilatorTool


@pytest.mark.asyncio
async def test_detect_all_returns_empty_when_no_tools() -> None:
    svc = EDAToolService()
    with patch("shutil.which", return_value=None):
        result = await svc.detect_all(force=True)
    assert result == {}


@pytest.mark.asyncio
async def test_detect_all_caches_results() -> None:
    svc = EDAToolService()
    with patch("shutil.which", return_value=None):
        r1 = await svc.detect_all(force=True)
        r2 = await svc.detect_all(force=False)
    assert r1 == r2


@pytest.mark.asyncio
async def test_detect_all_force_rescans() -> None:
    svc = EDAToolService()
    call_count = 0

    original = VerilatorTool.detect

    async def counting_detect(self):  # type: ignore[override]
        nonlocal call_count
        call_count += 1
        return None

    with patch.object(VerilatorTool, "detect", counting_detect):
        await svc.detect_all(force=True)
        await svc.detect_all(force=True)
    assert call_count == 2


def test_get_tool_raises_when_not_available() -> None:
    svc = EDAToolService()
    with pytest.raises(ToolNotFoundError):
        svc.get_tool("questa")


@pytest.mark.asyncio
async def test_get_tool_returns_adapter_after_detect() -> None:
    from litex_verify.utils.subprocess import ProcessResult

    svc = EDAToolService()
    fake_result = ProcessResult(returncode=0, stdout="Verilator 5.0", stderr="", duration_ms=1)

    with patch("shutil.which", return_value="/usr/bin/verilator"):
        with patch(
            "litex_verify.services.eda_tools.run_command",
            new=AsyncMock(return_value=fake_result),
        ):
            await svc.detect_all(force=True)
    adapter = svc.get_tool("verilator")
    assert adapter.name == "verilator"


def test_verification_tier_zero_when_no_tools() -> None:
    svc = EDAToolService()
    assert svc.get_verification_tier() == 0
