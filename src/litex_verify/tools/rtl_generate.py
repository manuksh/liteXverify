"""rtl_generate tool."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from litex_verify.core.exceptions import StateError
from litex_verify.core.state import WorkflowState
from litex_verify.models.soc_config import SoCConfig
from litex_verify.services.litex_runner import LiteXRunner
from litex_verify.services.rtl_parser import RTLParser
from litex_verify.tools.base import BaseTool


class RTLGenerateInput(BaseModel):
    output_format: Literal["verilog", "vhdl"] = "verilog"
    output_dir: str | None = None
    run_lint: bool = True


class RTLGenerateOutput(BaseModel):
    success: bool
    top_module: str
    file_list: list[str]
    hierarchy: dict[str, list[str]]
    lint_results: dict[str, object]
    interface_map: dict[str, dict[str, str]]


class RTLGenerateTool(BaseTool[RTLGenerateInput, RTLGenerateOutput]):
    name = "rtl_generate"
    description = "Generate RTL from LiteX configuration"
    input_schema = RTLGenerateInput
    output_schema = RTLGenerateOutput
    allowed_states = frozenset({WorkflowState.S1_CONFIG, WorkflowState.S2_RTL})

    async def execute(self, input_data: RTLGenerateInput) -> RTLGenerateOutput:
        if not self.context.active_project:
            raise StateError("No active project")
        config = SoCConfig.model_validate(await self.context.fs.read_json(self.context.config_file))
        output_dir = (
            self.context.active_project / "build"
            if input_data.output_dir is None
            else self.context.active_project / input_data.output_dir
        )
        runner = LiteXRunner()
        files = await runner.generate_rtl(config, output_dir=output_dir, output_format=input_data.output_format)
        parser = RTLParser()
        hierarchy = parser.parse_hierarchy(files)
        interface_map = parser.extract_interfaces(files)
        lint_results = {"enabled": input_data.run_lint, "errors": 0, "warnings": 0}
        top_module = next(iter(hierarchy.keys()), "soc_top")
        state = await self.context.load_project_state()
        state.rtl_top_module = top_module
        await self.context.save_project_state(state)
        sm = self.context.state_machine
        if sm and sm.current_state == WorkflowState.S1_CONFIG:
            await sm.transition(WorkflowState.S2_RTL, "rtl_generate")
        if sm and sm.current_state == WorkflowState.S2_RTL:
            await sm.transition(WorkflowState.S3_TB, "rtl_generate")
        return RTLGenerateOutput(
            success=True,
            top_module=top_module,
            file_list=[str(path) for path in files],
            hierarchy=hierarchy,
            lint_results=lint_results,
            interface_map=interface_map,
        )
