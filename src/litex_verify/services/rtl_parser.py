"""Simple RTL parser for hierarchy/interface extraction."""

from __future__ import annotations

import re
from pathlib import Path


MODULE_RE = re.compile(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)")
PORT_RE = re.compile(r"\b(input|output|inout)\b[^;,\n]*\b([A-Za-z_][A-Za-z0-9_]*)")


class RTLParser:
    def parse_hierarchy(self, files: list[Path]) -> dict[str, list[str]]:
        modules: list[str] = []
        for file in files:
            text = file.read_text(encoding="utf-8", errors="replace")
            modules.extend(MODULE_RE.findall(text))
        if not modules:
            return {}
        return {modules[0]: modules[1:]}

    def extract_interfaces(self, files: list[Path]) -> dict[str, dict[str, str]]:
        out: dict[str, dict[str, str]] = {}
        for file in files:
            text = file.read_text(encoding="utf-8", errors="replace")
            for direction, name in PORT_RE.findall(text):
                out[name] = {"direction": direction}
        return out
