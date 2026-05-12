"""UVM RAL generator."""

from __future__ import annotations

from pathlib import Path

import aiofiles


class UVMRALGenerator:
    async def generate(self, output_dir: Path, top_module: str) -> Path:
        path = output_dir / "ral_model.sv"
        content = (
            f"class {top_module}_ral_model extends uvm_reg_block;\n"
            f"  `uvm_object_utils({top_module}_ral_model)\n"
            "endclass\n"
        )
        async with aiofiles.open(path, "w", encoding="utf-8") as file:
            await file.write(content)
        return path
