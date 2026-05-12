"""Base class for all MCP tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

import structlog
from pydantic import BaseModel, ValidationError

from litex_verify.core.context import ServerContext
from litex_verify.core.exceptions import StateError, ToolError
from litex_verify.core.state import WorkflowState

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class BaseTool(ABC, Generic[InputT, OutputT]):
    name: str
    description: str
    input_schema: type[InputT]
    output_schema: type[OutputT]
    allowed_states: frozenset[WorkflowState] = frozenset(WorkflowState)

    def __init__(self, context: ServerContext) -> None:
        self.context = context
        self.logger = structlog.get_logger().bind(tool=self.name)

    async def __call__(self, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            input_data = self.input_schema.model_validate(arguments)
            await self._check_state_preconditions()
            output = await self.execute(input_data)
            return output.model_dump(mode="json")
        except ValidationError as exc:
            raise ToolError(
                code=1001,
                category="project",
                message="Invalid input parameters",
                details=str(exc),
            ) from exc
        except (StateError, ToolError):
            raise
        except Exception as exc:
            self.logger.exception("tool_error", error=str(exc))
            raise ToolError(code=9999, message="Internal error", details=str(exc)) from exc

    async def _check_state_preconditions(self) -> None:
        if not self.context.active_project:
            if self.name != "project_init":
                raise StateError("No active project")
            return
        state_machine = self.context.state_machine
        if state_machine is None:
            raise StateError("State machine is unavailable")
        current = state_machine.current_state
        if current not in self.allowed_states:
            raise StateError(f"Tool {self.name} cannot execute in state {current.value}")

    @abstractmethod
    async def execute(self, input_data: InputT) -> OutputT:
        ...
