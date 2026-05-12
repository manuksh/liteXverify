"""config_validate tool."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from litex_verify.core.exceptions import StateError
from litex_verify.core.state import WorkflowState
from litex_verify.models.soc_config import SoCConfig
from litex_verify.tools.base import BaseTool


class ConfigValidateInput(BaseModel):
    config_path: str | None = None
    check_level: Literal["basic", "standard", "strict"] = "standard"


class ConfigValidateOutput(BaseModel):
    valid: bool
    errors: list[str]
    warnings: list[str]
    info: list[str]
    memory_map_report: str


class ConfigValidateTool(BaseTool[ConfigValidateInput, ConfigValidateOutput]):
    name = "config_validate"
    description = "Validate SoC configuration rules"
    input_schema = ConfigValidateInput
    output_schema = ConfigValidateOutput
    allowed_states = frozenset({WorkflowState.S1_CONFIG, WorkflowState.S2_RTL, WorkflowState.S3_TB})

    async def execute(self, input_data: ConfigValidateInput) -> ConfigValidateOutput:
        if not self.context.active_project:
            raise StateError("No active project")
        path = self.context.config_file if input_data.config_path is None else self.context.active_project / input_data.config_path
        cfg = SoCConfig.model_validate(await self.context.fs.read_json(path))
        errors: list[str] = []
        warnings: list[str] = []
        info: list[str] = []

        addresses = [int(p.base_addr, 16) for p in cfg.peripherals]
        if len(addresses) != len(set(addresses)):
            errors.append("ADDR-001: overlapping peripheral base addresses")
        for addr in addresses:
            if addr % 0x1000 != 0:
                errors.append("ADDR-002: peripheral base address must be 4KB aligned")
        if cfg.clock.sys_clk_freq <= 0:
            errors.append("CLK-001: clock must be positive")
        if cfg.clock.sys_clk_freq > 300_000_000:
            warnings.append("CLK-001: unusually high clock frequency")
        if cfg.bus.standard not in {"wishbone", "axi", "axi-lite"}:
            errors.append("BUS-001: unsupported bus")
        if cfg.memory.size < 8 * 1024:
            warnings.append("RSC-001: very low memory size for practical tests")
        info.append(f"Detected {len(cfg.peripherals)} peripherals.")

        if not errors and self.context.state_machine and self.context.state_machine.current_state == WorkflowState.S1_CONFIG:
            await self.context.state_machine.transition(WorkflowState.S2_RTL, "config_validate")

        report_lines = [f"{item.name}: {item.base_addr}" for item in cfg.peripherals] or ["No peripherals"]
        return ConfigValidateOutput(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            info=info,
            memory_map_report="\n".join(report_lines),
        )
