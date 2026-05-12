"""Template resources."""

from __future__ import annotations

from pathlib import Path


def read_template_resource(workspace: Path, uri: str) -> str:
    mapping = {
        "templates://uvm/agent": workspace / "data" / "templates" / "uvm" / "agent.sv.j2",
        "templates://uvm/env": workspace / "data" / "templates" / "uvm" / "env.sv.j2",
        "templates://uvm/test": workspace / "data" / "templates" / "uvm" / "test_base.sv.j2",
        "templates://uvm/sequence": workspace / "data" / "templates" / "uvm" / "sequence_base.sv.j2",
        "templates://cocotb/test": workspace / "data" / "templates" / "cocotb" / "test_module.py.j2",
        "templates://cocotb/bfm": workspace / "data" / "templates" / "cocotb" / "bfm.py.j2",
    }
    path = mapping.get(uri)
    if path is None or not path.exists():
        raise FileNotFoundError(f"Unknown template resource: {uri}")
    return path.read_text(encoding="utf-8")
