"""cocotb test generator."""

from __future__ import annotations

from pathlib import Path

import aiofiles
from jinja2 import Environment


class CocotbTestGenerator:
    def __init__(self, template_env: Environment) -> None:
        self.env = template_env

    async def generate(self, output_dir: Path, module_name: str) -> Path:
        template = self.env.get_template("cocotb/test_module.py.j2")
        content = template.render(module_name=module_name)
        path = output_dir / f"test_{module_name}.py"
        async with aiofiles.open(path, "w", encoding="utf-8") as file:
            await file.write(content)
        return path
