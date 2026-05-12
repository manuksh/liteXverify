"""config_create tool."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from litex_verify.core.exceptions import StateError
from litex_verify.core.state import WorkflowState
from litex_verify.models.soc_config import (
    CPUConfig,
    ClockConfig,
    MemoryConfig,
    PeripheralConfig,
    SoCConfig,
)
from litex_verify.tools.base import BaseTool


class PeripheralInput(BaseModel):
    type: Literal["uart", "spi", "i2c", "gpio", "timer", "ethernet", "custom"]
    name: str | None = None
    base_addr: str | None = None
    params: dict[str, object] = Field(default_factory=dict)


class ConfigCreateInput(BaseModel):
    cpu: Literal["vexriscv", "picorv32", "minerva", "none"]
    bus_standard: Literal["wishbone", "axi", "axi-lite"] = "wishbone"
    clock_freq: int = 100_000_000
    peripherals: list[PeripheralInput] = Field(default_factory=list)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)


class ConfigCreateOutput(BaseModel):
    success: bool
    config_path: str
    memory_map: dict[str, str]
    warnings: list[str]


class ConfigCreateTool(BaseTool[ConfigCreateInput, ConfigCreateOutput]):
    name = "config_create"
    description = "Create or modify LiteX SoC configuration"
    input_schema = ConfigCreateInput
    output_schema = ConfigCreateOutput
    allowed_states = frozenset({WorkflowState.S1_CONFIG, WorkflowState.S2_RTL})

    async def execute(self, input_data: ConfigCreateInput) -> ConfigCreateOutput:
        if not self.context.active_project:
            raise StateError("No active project")

        peripherals = self._normalize_peripherals(input_data.peripherals)
        config = SoCConfig(
            cpu=CPUConfig(type=input_data.cpu),
            clock=ClockConfig(sys_clk_freq=input_data.clock_freq),
            memory=input_data.memory,
            peripherals=peripherals,
            bus={"standard": input_data.bus_standard},
        )
        await self.context.fs.write_json(self.context.config_file, config.model_dump(mode="json"))

        state = await self.context.load_project_state()
        state.config = config
        await self.context.save_project_state(state)
        return ConfigCreateOutput(
            success=True,
            config_path=str(self.context.config_file),
            memory_map={p.name: p.base_addr for p in peripherals},
            warnings=[],
        )

    def _normalize_peripherals(self, raw: list[PeripheralInput]) -> list[PeripheralConfig]:
        base = 0x82000000
        step = 0x1000
        out: list[PeripheralConfig] = []
        for idx, item in enumerate(raw):
            name = item.name or f"{item.type}_{idx}"
            addr = item.base_addr or hex(base + (idx * step))
            out.append(
                PeripheralConfig(
                    type=item.type,
                    name=name,
                    base_addr=addr,
                    params=item.params,
                )
            )
        return out
