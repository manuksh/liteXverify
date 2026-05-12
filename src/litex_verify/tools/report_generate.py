"""report_generate tool."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from litex_verify.core.exceptions import StateError
from litex_verify.core.state import WorkflowState
from litex_verify.services.coverage_db import CoverageDatabase
from litex_verify.tools.base import BaseTool


class ReportGenerateInput(BaseModel):
    format: Literal["html", "markdown", "json"] = "html"
    include_sections: list[str] = Field(default_factory=list)
    output_path: str | None = None


class ReportGenerateOutput(BaseModel):
    report_path: str
    format: str
    generated_at: str
    meets_threshold: bool
    iterate_required: bool


class ReportGenerateTool(BaseTool[ReportGenerateInput, ReportGenerateOutput]):
    name = "report_generate"
    description = "Generate verification summary report"
    input_schema = ReportGenerateInput
    output_schema = ReportGenerateOutput
    allowed_states = frozenset({WorkflowState.S5_ANALYSIS, WorkflowState.S6_REPORT})

    async def execute(self, input_data: ReportGenerateInput) -> ReportGenerateOutput:
        if not self.context.active_project:
            raise StateError("No active project")
        state = await self.context.load_project_state()
        coverage = CoverageDatabase().analyze(state.runs, threshold=90)
        report = {
            "project": state.project_name,
            "workflow_state": state.workflow_state.value,
            "runs": [item.model_dump(mode="json") for item in state.runs],
            "coverage_summary": coverage.model_dump(mode="json"),
        }
        ext = {"html": "html", "markdown": "md", "json": "json"}[input_data.format]
        target = (
            self.context.active_project / "reports" / f"verification_report.{ext}"
            if input_data.output_path is None
            else self.context.active_project / input_data.output_path
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        if input_data.format == "json":
            target.write_text(json.dumps(report, indent=2), encoding="utf-8")
        elif input_data.format == "markdown":
            target.write_text(
                f"# Verification Report\n\n- Project: {state.project_name}\n- Overall coverage: {coverage.overall}%\n",
                encoding="utf-8",
            )
        else:
            target.write_text(
                "<html><body>"
                f"<h1>Verification Report</h1><p>Project: {state.project_name}</p>"
                f"<p>Overall coverage: {coverage.overall}%</p>"
                "</body></html>",
                encoding="utf-8",
            )
        latest_run_passed = bool(state.runs) and state.runs[-1].status == "passed"
        meets_threshold = coverage.meets_threshold and latest_run_passed
        if self.context.state_machine:
            if self.context.state_machine.current_state == WorkflowState.S5_ANALYSIS:
                await self.context.state_machine.transition(WorkflowState.S6_REPORT, "report_generate")
            if meets_threshold and self.context.state_machine.current_state == WorkflowState.S6_REPORT:
                await self.context.state_machine.transition(WorkflowState.DONE, "report_generate")
            elif not meets_threshold and self.context.state_machine.current_state == WorkflowState.S6_REPORT:
                await self.context.state_machine.transition(WorkflowState.S4_SIM, "report_generate")
        return ReportGenerateOutput(
            report_path=str(target),
            format=input_data.format,
            generated_at=datetime.now(timezone.utc).isoformat(),
            meets_threshold=meets_threshold,
            iterate_required=not meets_threshold,
        )
