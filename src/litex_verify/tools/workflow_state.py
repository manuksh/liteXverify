"""workflow_state tool."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from litex_verify.core.exceptions import StateError, ToolError
from litex_verify.core.state import TRANSITIONS, WorkflowState
from litex_verify.tools.base import BaseTool


class WorkflowStateInput(BaseModel):
    action: Literal["get", "transition", "reset"]
    target_state: str | None = None
    force: bool = False


class WorkflowStateOutput(BaseModel):
    current_state: str
    previous_state: str | None
    available_transitions: list[str]
    state_history: list[dict]


class WorkflowStateTool(BaseTool[WorkflowStateInput, WorkflowStateOutput]):
    name = "workflow_state"
    description = "Query or transition workflow state"
    input_schema = WorkflowStateInput
    output_schema = WorkflowStateOutput
    allowed_states = frozenset(WorkflowState)

    async def execute(self, input_data: WorkflowStateInput) -> WorkflowStateOutput:
        if not self.context.state_machine:
            raise StateError("No active state machine")
        sm = self.context.state_machine
        previous = sm.current_state
        if input_data.action == "transition":
            if not input_data.target_state:
                raise StateError("target_state is required for transition action")
            try:
                target = WorkflowState(input_data.target_state)
            except ValueError as exc:
                valid = ", ".join(item.value for item in WorkflowState)
                raise ToolError(
                    code=1001,
                    category="project",
                    message=f"Invalid state value: {input_data.target_state!r}",
                    details=f"Valid values: {valid}",
                ) from exc
            await sm.transition(target, "workflow_state.transition", force=input_data.force)
        elif input_data.action == "reset":
            await sm.reset()
        current = sm.current_state
        return WorkflowStateOutput(
            current_state=current.value,
            previous_state=previous.value if input_data.action != "get" else None,
            available_transitions=sorted(item.value for item in TRANSITIONS[current]),
            state_history=[item.model_dump(mode="json") for item in sm.history[-20:]],
        )
