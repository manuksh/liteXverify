"""Script resources."""

from __future__ import annotations

from pathlib import Path


def read_script_resource(workspace: Path, uri: str) -> str:
    mapping = {
        "scripts://questa/compile.do": workspace / "data" / "scripts" / "questa" / "compile.do.j2",
        "scripts://questa/run.do": workspace / "data" / "scripts" / "questa" / "run.do.j2",
        "scripts://vcs/compile.sh": workspace / "data" / "scripts" / "vcs" / "compile.sh.j2",
        "scripts://vcs/run.sh": workspace / "data" / "scripts" / "vcs" / "run.sh.j2",
        "scripts://vcs/coverage.sh": workspace / "data" / "scripts" / "vcs" / "coverage.sh.j2",
        "scripts://verilator/Makefile": workspace / "data" / "scripts" / "verilator" / "Makefile.j2",
        "scripts://vivado/synth.tcl": workspace / "data" / "scripts" / "vivado" / "synth.tcl.j2",
    }
    path = mapping.get(uri)
    if path is None or not path.exists():
        raise FileNotFoundError(f"Unknown script resource: {uri}")
    return path.read_text(encoding="utf-8")
