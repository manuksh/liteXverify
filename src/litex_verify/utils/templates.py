"""Template environment helper."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def create_template_environment(workspace: Path) -> Environment:
    data_templates = workspace / "data" / "templates"
    return Environment(
        loader=FileSystemLoader(str(data_templates)),
        autoescape=select_autoescape(default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
