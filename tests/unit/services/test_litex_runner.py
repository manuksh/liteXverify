"""Unit tests for LiteXRunner."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from litex_verify.models.soc_config import BusConfig, CPUConfig, SoCConfig
from litex_verify.services.litex_runner import LiteXRunner
from litex_verify.utils.subprocess import ProcessResult


@pytest.fixture(autouse=True)
def reset_litex_cache() -> None:
    """Reset the class-level LiteX availability cache between tests."""
    LiteXRunner._litex_available = None
    yield
    LiteXRunner._litex_available = None


def _config() -> SoCConfig:
    return SoCConfig(cpu=CPUConfig(type="vexriscv"), bus=BusConfig())


@pytest.mark.asyncio
async def test_stub_mode_true_skips_litex(tmp_path: Path) -> None:
    runner = LiteXRunner()
    files = await runner.generate_rtl(_config(), tmp_path, stub_mode=True)
    assert files
    assert files[0].exists()
    content = files[0].read_text()
    assert "soc_top" in content


@pytest.mark.asyncio
async def test_stub_contains_cpu_type(tmp_path: Path) -> None:
    runner = LiteXRunner()
    files = await runner.generate_rtl(_config(), tmp_path, stub_mode=True)
    content = files[0].read_text()
    assert "vexriscv" in content


@pytest.mark.asyncio
async def test_auto_detect_falls_back_to_stub_when_litex_missing(tmp_path: Path) -> None:
    no_litex = ProcessResult(returncode=1, stdout="", stderr="No module named litex", duration_ms=1)
    with patch(
        "litex_verify.services.litex_runner.run_command",
        new=AsyncMock(return_value=no_litex),
    ):
        runner = LiteXRunner()
        files = await runner.generate_rtl(_config(), tmp_path, stub_mode=None)
    assert files[0].exists()


@pytest.mark.asyncio
async def test_auto_detect_uses_real_when_litex_present(tmp_path: Path) -> None:
    found = ProcessResult(returncode=0, stdout="2023.08", stderr="", duration_ms=1)
    rtl_result = ProcessResult(returncode=0, stdout="", stderr="", duration_ms=10)
    call_count = 0

    async def fake_cmd(cmd, **kwargs):  # noqa: ANN001
        nonlocal call_count
        call_count += 1
        if "import litex" in " ".join(cmd):
            return found
        return rtl_result

    with patch("litex_verify.services.litex_runner.run_command", new=fake_cmd):
        runner = LiteXRunner()
        # Even if LiteX runs but produces no files, we fall back to stub
        await runner.generate_rtl(_config(), tmp_path, stub_mode=None)
    assert call_count >= 2


@pytest.mark.asyncio
async def test_vhdl_stub_format(tmp_path: Path) -> None:
    runner = LiteXRunner()
    files = await runner.generate_rtl(_config(), tmp_path, output_format="vhdl", stub_mode=True)
    assert files[0].suffix == ".vhd"
    assert "entity" in files[0].read_text()
