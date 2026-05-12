"""Unit tests for LogParser."""
from __future__ import annotations

from pathlib import Path

import pytest

from litex_verify.services.log_parser import LogParser


@pytest.fixture()
def log_path(tmp_path: Path) -> Path:
    return tmp_path / "sim.log"


def test_empty_log(log_path: Path) -> None:
    log_path.write_text("", encoding="utf-8")
    result = LogParser().parse(log_path)
    assert result["summary"]["passed"] == 0
    assert result["summary"]["failed"] == 0
    assert result["uvm_report"]["fatal"] == 0


def test_pass_detection(log_path: Path) -> None:
    log_path.write_text("TEST sanity PASSED\nTEST boot PASSED\n", encoding="utf-8")
    result = LogParser().parse(log_path)
    assert result["summary"]["passed"] == 2


def test_fail_detection(log_path: Path) -> None:
    log_path.write_text("TEST mem_check FAILED\n", encoding="utf-8")
    result = LogParser().parse(log_path)
    assert result["summary"]["failed"] == 1


def test_uvm_fatal_detected(log_path: Path) -> None:
    log_path.write_text("UVM_FATAL @ 50ns: something went wrong\n", encoding="utf-8")
    result = LogParser().parse(log_path)
    assert result["uvm_report"]["fatal"] == 1


def test_uvm_error_detected(log_path: Path) -> None:
    log_path.write_text("UVM_ERROR @ 100ns: mismatch\n", encoding="utf-8")
    result = LogParser().parse(log_path)
    assert result["uvm_report"]["error"] == 1


def test_uvm_warning_detected(log_path: Path) -> None:
    log_path.write_text("UVM_WARNING @ 20ns: unexpected data\n", encoding="utf-8")
    result = LogParser().parse(log_path)
    assert result["uvm_report"]["warning"] == 1


def test_error_lines_collected(log_path: Path) -> None:
    log_path.write_text("Compilation ERROR: syntax\nOther line\n", encoding="utf-8")
    result = LogParser().parse(log_path)
    assert result["summary"]["errors"] >= 1


def test_warning_lines_collected(log_path: Path) -> None:
    log_path.write_text("Warning: unused variable\n", encoding="utf-8")
    result = LogParser().parse(log_path)
    assert len(result["warnings"]) == 1


def test_mixed_log(log_path: Path) -> None:
    content = (
        "TEST test_a PASSED\n"
        "UVM_WARNING @ 10ns: minor\n"
        "TEST test_b FAILED\n"
        "UVM_FATAL @ 200ns: abort\n"
    )
    log_path.write_text(content, encoding="utf-8")
    result = LogParser().parse(log_path)
    assert result["summary"]["passed"] == 1
    assert result["summary"]["failed"] == 1
    assert result["uvm_report"]["fatal"] == 1
    assert result["uvm_report"]["warning"] == 1
