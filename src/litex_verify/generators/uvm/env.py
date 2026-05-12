"""UVM environment generator."""

from __future__ import annotations

from pathlib import Path

import aiofiles
from jinja2 import Environment


class UVMEnvGenerator:
    def __init__(self, template_env: Environment) -> None:
        self.env = template_env

    async def generate(self, output_dir: Path, agent_name: str) -> Path:
        template = self.env.get_template("uvm/env.sv.j2")
        content = template.render(agent_name=agent_name)
        path = output_dir / "env.sv"
        async with aiofiles.open(path, "w", encoding="utf-8") as file:
            await file.write(content)
        return path
