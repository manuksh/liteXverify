"""Simulation log parsing."""

from __future__ import annotations

from pathlib import Path


class LogParser:
    def parse(self, log_path: Path) -> dict[str, object]:
        text = log_path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        errors = [line for line in lines if "ERROR" in line.upper()]
        warnings = [line for line in lines if "WARN" in line.upper()]
        passed = sum(1 for line in lines if "TEST " in line.upper() and " PASSED" in line.upper())
        failed = sum(1 for line in lines if "TEST " in line.upper() and " FAILED" in line.upper())
        uvm_fatal = sum(1 for line in lines if "UVM_FATAL" in line)
        uvm_error = sum(1 for line in lines if "UVM_ERROR" in line)
        uvm_warning = sum(1 for line in lines if "UVM_WARNING" in line)
        return {
            "summary": {"passed": passed, "failed": failed, "errors": len(errors)},
            "tests": [],
            "errors": errors[:50],
            "warnings": warnings[:50],
            "uvm_report": {"fatal": uvm_fatal, "error": uvm_error, "warning": uvm_warning},
        }
