"""UVM agent generator."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, NamedTuple

import aiofiles
from jinja2 import Environment
from pydantic import BaseModel


class InterfaceSignal(NamedTuple):
    name: str
    direction: Literal["input", "output", "inout"]
    width: int
    description: str = ""


class InterfaceSpec(BaseModel):
    name: str
    protocol: Literal["wishbone", "axi", "axi-lite", "apb", "custom"]
    signals: list[InterfaceSignal]
    clock: str = "clk"
    reset: str = "rst"
    reset_active_low: bool = True


class UVMAgentGenerator:
    def __init__(self, template_env: Environment) -> None:
        self.env = template_env

    async def generate(self, interface: InterfaceSpec, output_dir: Path) -> list[Path]:
        agent_dir = output_dir / f"{interface.name}_agent"
        agent_dir.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []
        components = [
            ("interface.sv", "uvm/interface.sv.j2"),
            ("seq_item.sv", "uvm/seq_item.sv.j2"),
            ("driver.sv", "uvm/driver.sv.j2"),
            ("monitor.sv", "uvm/monitor.sv.j2"),
            ("sequencer.sv", "uvm/sequencer.sv.j2"),
            ("agent.sv", "uvm/agent.sv.j2"),
            ("agent_config.sv", "uvm/agent_config.sv.j2"),
            ("agent_pkg.sv", "uvm/agent_pkg.sv.j2"),
        ]
        context = {"interface": interface, "agent_name": f"{interface.name}_agent", "signals": interface.signals}
        for filename, template_name in components:
            template = self.env.get_template(template_name)
            content = template.render(**context)
            file_path = agent_dir / filename
            async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
                await file.write(content)
            generated.append(file_path)
        return generated
