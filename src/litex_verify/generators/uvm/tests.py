"""UVM test generator."""

from __future__ import annotations

from pathlib import Path

import aiofiles
from jinja2 import Environment


class UVMTestGenerator:
    def __init__(self, template_env: Environment) -> None:
        self.env = template_env

    async def generate(self, output_dir: Path, agent_name: str) -> Path:
        tests_dir = output_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        template = self.env.get_template("uvm/test_base.sv.j2")
        content = template.render(agent_name=agent_name)
        path = tests_dir / "test_sanity.sv"
        async with aiofiles.open(path, "w", encoding="utf-8") as file:
            await file.write(content)
        return path
