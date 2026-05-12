"""tb_generate tool."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from litex_verify.core.exceptions import StateError
from litex_verify.core.state import WorkflowState
from litex_verify.services.testbench_gen import TestbenchGenerator
from litex_verify.tools.base import BaseTool


class TBGenerateInput(BaseModel):
    framework: Literal["uvm", "cocotb", "auto"] = "auto"
    components: list[str] = Field(default_factory=list)
    include_ral: bool = True
    test_templates: list[str] = Field(default_factory=lambda: ["sanity"])


class TBGenerateOutput(BaseModel):
    success: bool
    framework: str
    files: list[str]
    compile_order: list[str]
    run_command: str


class TBGenerateTool(BaseTool[TBGenerateInput, TBGenerateOutput]):
    name = "tb_generate"
    description = "Generate UVM or cocotb testbench"
    input_schema = TBGenerateInput
    output_schema = TBGenerateOutput
    allowed_states = frozenset({WorkflowState.S2_RTL, WorkflowState.S3_TB})

    async def execute(self, input_data: TBGenerateInput) -> TBGenerateOutput:
        if not self.context.active_project:
            raise StateError("No active project")
        state = await self.context.load_project_state()
        top_module = state.rtl_top_module or "soc_top"
        resolved_framework = input_data.framework
        if resolved_framework == "auto":
            resolved_framework = "uvm" if state.verification_tier >= 2 else "cocotb"
        gen = TestbenchGenerator()
        tb_dir = self.context.active_project / "tb"
        if resolved_framework == "uvm":
            files = await gen.generate_uvm(tb_dir, top_module)
            run_cmd = "vsim -c -do run.do"
        else:
            files = await gen.generate_cocotb(tb_dir, top_module)
            run_cmd = "make -C tb"
        if self.context.state_machine:
            await self.context.state_machine.transition(WorkflowState.S4_SIM, "tb_generate")
        str_files = [str(path) for path in files]
        return TBGenerateOutput(
            success=True,
            framework=resolved_framework,
            files=str_files,
            compile_order=str_files,
            run_command=run_cmd,
        )
