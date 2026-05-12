"""Unit tests for RTLParser."""
from __future__ import annotations

from pathlib import Path

import pytest

from litex_verify.services.rtl_parser import RTLParser


@pytest.fixture()
def rtl_file(tmp_path: Path) -> Path:
    return tmp_path / "soc_top.v"


def test_parse_empty_returns_empty(tmp_path: Path) -> None:
    f = tmp_path / "empty.v"
    f.write_text("", encoding="utf-8")
    result = RTLParser().parse_hierarchy([f])
    assert result == {}


def test_parse_single_module(rtl_file: Path) -> None:
    rtl_file.write_text("module soc_top(input wire clk);\nendmodule\n", encoding="utf-8")
    result = RTLParser().parse_hierarchy([rtl_file])
    assert "soc_top" in result


def test_parse_multiple_modules(tmp_path: Path) -> None:
    f1 = tmp_path / "top.v"
    f2 = tmp_path / "sub.v"
    f1.write_text("module top_mod();\nendmodule\n", encoding="utf-8")
    f2.write_text("module sub_mod();\nendmodule\n", encoding="utf-8")
    result = RTLParser().parse_hierarchy([f1, f2])
    assert "top_mod" in result
    assert "sub_mod" in result.get("top_mod", [])


def test_extract_interfaces_input_output(rtl_file: Path) -> None:
    rtl_file.write_text(
        "module soc_top(input wire clk, output wire ready);\nendmodule\n",
        encoding="utf-8",
    )
    result = RTLParser().extract_interfaces([rtl_file])
    assert "clk" in result
    assert result["clk"]["direction"] == "input"
    assert "ready" in result
    assert result["ready"]["direction"] == "output"


def test_extract_no_ports(rtl_file: Path) -> None:
    rtl_file.write_text("module empty_mod();\nendmodule\n", encoding="utf-8")
    result = RTLParser().extract_interfaces([rtl_file])
    assert result == {}
