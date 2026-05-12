"""coverage_analyze tool."""

from __future__ import annotations

from pydantic import BaseModel, Field

from litex_verify.core.exceptions import StateError
from litex_verify.core.state import WorkflowState
from litex_verify.models.coverage import CoverageHole
from litex_verify.services.coverage_db import CoverageDatabase
from litex_verify.tools.base import BaseTool


class CoverageAnalyzeInput(BaseModel):
    run_ids: list[str] = Field(default_factory=list)
    coverage_types: list[str] = Field(default_factory=lambda: ["code", "functional", "toggle", "fsm"])
    threshold: int = 90


class CoverageAnalyzeOutput(BaseModel):
    overall: float
    by_type: dict[str, float]
    by_module: dict[str, float]
    holes: list[CoverageHole]
    trend: list[float]
    meets_threshold: bool


class CoverageAnalyzeTool(BaseTool[CoverageAnalyzeInput, CoverageAnalyzeOutput]):
    name = "coverage_analyze"
    description = "Aggregate and analyze coverage metrics"
    input_schema = CoverageAnalyzeInput
    output_schema = CoverageAnalyzeOutput
    allowed_states = frozenset({WorkflowState.S4_SIM, WorkflowState.S5_ANALYSIS, WorkflowState.S6_REPORT})

    async def execute(self, input_data: CoverageAnalyzeInput) -> CoverageAnalyzeOutput:
        if not self.context.active_project:
            raise StateError("No active project")
        state = await self.context.load_project_state()
        runs = state.runs
        if input_data.run_ids:
            selected = set(input_data.run_ids)
            runs = [item for item in state.runs if item.run_id in selected]
        summary = CoverageDatabase().analyze(runs, threshold=input_data.threshold)
        if self.context.state_machine and self.context.state_machine.current_state == WorkflowState.S5_ANALYSIS:
            await self.context.state_machine.transition(WorkflowState.S6_REPORT, "coverage_analyze")
        return CoverageAnalyzeOutput(**summary.model_dump(mode="python"))
