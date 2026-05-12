"""report_parse tool."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from litex_verify.core.exceptions import StateError, ToolError
from litex_verify.core.state import WorkflowState
from litex_verify.services.log_parser import LogParser
from litex_verify.tools.base import BaseTool


class ReportParseInput(BaseModel):
    run_id: str | None = None
    log_path: str | None = None


class ReportParseOutput(BaseModel):
    summary: dict[str, int]
    tests: list[dict]
    errors: list[str]
    warnings: list[str]
    uvm_report: dict[str, int]


class ReportParseTool(BaseTool[ReportParseInput, ReportParseOutput]):
    name = "report_parse"
    description = "Extract structured results from simulation logs"
    input_schema = ReportParseInput
    output_schema = ReportParseOutput
    allowed_states = frozenset({WorkflowState.S4_SIM, WorkflowState.S5_ANALYSIS})

    async def execute(self, input_data: ReportParseInput) -> ReportParseOutput:
        if not self.context.active_project:
            raise StateError("No active project")
        state = await self.context.load_project_state()
        if input_data.log_path:
            log_path = Path(input_data.log_path)
        else:
            run = None
            if input_data.run_id:
                run = next((item for item in state.runs if item.run_id == input_data.run_id), None)
            if run is None and state.runs:
                run = state.runs[-1]
            if run is None:
                raise ToolError(code=6001, category="analysis", message="No simulation runs found to parse")
            log_path = Path(run.log_path)
        parsed = LogParser().parse(log_path)
        if self.context.state_machine and self.context.state_machine.current_state == WorkflowState.S4_SIM:
            await self.context.state_machine.transition(WorkflowState.S5_ANALYSIS, "report_parse")
        return ReportParseOutput(**parsed)
