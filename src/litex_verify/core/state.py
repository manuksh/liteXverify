"""Workflow state machine implementation."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from litex_verify.core.exceptions import InvalidTransitionError
from litex_verify.utils.filesystem import SandboxedFileSystem


class WorkflowState(str, Enum):
    S0_INIT = "S0"
    S1_CONFIG = "S1"
    S2_RTL = "S2"
    S3_TB = "S3"
    S4_SIM = "S4"
    S5_ANALYSIS = "S5"
    S6_REPORT = "S6"
    ERROR = "ERROR"
    DONE = "DONE"


TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.S0_INIT: {WorkflowState.S1_CONFIG, WorkflowState.ERROR},
    WorkflowState.S1_CONFIG: {WorkflowState.S2_RTL, WorkflowState.S1_CONFIG},
    WorkflowState.S2_RTL: {WorkflowState.S3_TB, WorkflowState.S1_CONFIG},
    WorkflowState.S3_TB: {WorkflowState.S4_SIM},
    WorkflowState.S4_SIM: {WorkflowState.S5_ANALYSIS, WorkflowState.S4_SIM},
    WorkflowState.S5_ANALYSIS: {WorkflowState.S6_REPORT},
    WorkflowState.S6_REPORT: {WorkflowState.DONE, WorkflowState.S4_SIM},
    WorkflowState.ERROR: {WorkflowState.S0_INIT, WorkflowState.S1_CONFIG},
    WorkflowState.DONE: set(),
}


class StateTransition(BaseModel):
    from_state: WorkflowState
    to_state: WorkflowState
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trigger: str


class StateMachine:
    """Async-safe workflow state machine with persistence."""

    def __init__(self, project_path: Path, fs: SandboxedFileSystem) -> None:
        self._project_path = project_path
        self._state_file = project_path / ".litex_verify" / "workflow_state.json"
        self._fs = fs
        self._current_state = WorkflowState.S0_INIT
        self._history: list[StateTransition] = []
        self._lock = asyncio.Lock()

    @property
    def current_state(self) -> WorkflowState:
        return self._current_state

    @property
    def history(self) -> list[StateTransition]:
        return list(self._history)

    async def load(self) -> None:
        if not await self._fs.exists(self._state_file):
            return
        payload = await self._fs.read_json(self._state_file)
        self._current_state = WorkflowState(payload.get("current_state", "S0"))
        raw_hist = payload.get("history", [])
        self._history = [StateTransition.model_validate(item) for item in raw_hist]

    async def transition(self, target: WorkflowState, trigger: str, force: bool = False) -> bool:
        async with self._lock:
            if not force and target not in TRANSITIONS[self._current_state]:
                raise InvalidTransitionError(
                    f"Cannot transition from {self._current_state.value} to {target.value}"
                )
            transition = StateTransition(
                from_state=self._current_state,
                to_state=target,
                trigger=trigger,
            )
            self._history.append(transition)
            self._current_state = target
            await self._persist()
            return True

    async def reset(self, trigger: str = "workflow_state.reset") -> None:
        async with self._lock:
            self._history.append(
                StateTransition(
                    from_state=self._current_state,
                    to_state=WorkflowState.S0_INIT,
                    trigger=trigger,
                )
            )
            self._current_state = WorkflowState.S0_INIT
            await self._persist()

    async def _persist(self) -> None:
        payload = {
            "current_state": self._current_state.value,
            "history": [item.model_dump(mode="json") for item in self._history[-200:]],
        }
        await self._fs.write_json(self._state_file, payload)
