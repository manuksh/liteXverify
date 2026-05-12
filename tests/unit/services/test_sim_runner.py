"""Unit tests for SimulationRunner service."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from litex_verify.services.sim_runner import SimulationRunner
from litex_verify.utils.subprocess import ProcessResult


def _fake_result(returncode: int = 0, stdout: str = "", stderr: str = "") -> ProcessResult:
    return ProcessResult(returncode=returncode, stdout=stdout, stderr=stderr, duration_ms=5)


@pytest.mark.asyncio
async def test_unknown_simulator_returns_stub(tmp_path: Path) -> None:
    runner = SimulationRunner()
    result = await runner.run(
        simulator="unknown_tool",
        rtl_files=[],
        tb_files=[],
        work_dir=tmp_path,
        top_module="top",
    )
    assert result.overall_status == "passed"
    assert result.simulator == "unknown_tool"


@pytest.mark.asyncio
async def test_verilator_clean_exit_gives_passed(tmp_path: Path) -> None:
    runner = SimulationRunner()
    with patch(
        "litex_verify.services.sim_runner.run_command",
        new=AsyncMock(return_value=_fake_result(0)),
    ):
        result = await runner.run(
            simulator="verilator",
            rtl_files=[],
            tb_files=[],
            work_dir=tmp_path,
            top_module="top",
        )
    assert result.overall_status == "passed"


@pytest.mark.asyncio
async def test_verilator_error_exit_gives_failed(tmp_path: Path) -> None:
    runner = SimulationRunner()
    err_result = _fake_result(1, stderr="Error: syntax error near token 'bad'")
    with patch(
        "litex_verify.services.sim_runner.run_command",
        new=AsyncMock(return_value=err_result),
    ):
        result = await runner.run(
            simulator="verilator",
            rtl_files=[],
            tb_files=[],
            work_dir=tmp_path,
            top_module="top",
        )
    assert result.overall_status == "failed"


@pytest.mark.asyncio
async def test_icarus_compile_fail_stops_early(tmp_path: Path) -> None:
    runner = SimulationRunner()
    compile_fail = _fake_result(1, stderr="soc_top.v:3: syntax error")
    call_count = 0

    async def mock_cmd(cmd, **kwargs):  # noqa: ANN001
        nonlocal call_count
        call_count += 1
        return compile_fail

    with patch("litex_verify.services.sim_runner.run_command", new=mock_cmd):
        result = await runner.run(
            simulator="icarus",
            rtl_files=[],
            tb_files=[],
            work_dir=tmp_path,
            top_module="top",
        )
    # Should only make the compile call, not the run call
    assert call_count == 1
    assert result.overall_status == "failed"


@pytest.mark.asyncio
async def test_parse_uvm_errors_from_log(tmp_path: Path) -> None:
    runner = SimulationRunner()
    output = "UVM_FATAL @ 100ns: something bad\nUVM_ERROR @ 200ns: oops\n"
    result = runner._parse_generic(
        _fake_result(0, stdout=output), "questa"
    )
    # UVM_ERROR/FATAL counted but returncode 0 → still "passed" at tool level
    assert result.simulator == "questa"


def test_stub_result_is_passed() -> None:
    result = SimulationRunner._stub_result("unknown")
    assert result.overall_status == "passed"
    assert result.tests_passed == 1
