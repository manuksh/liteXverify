"""Project state models."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from litex_verify.core.state import WorkflowState
from litex_verify.models.simulation import SimulationRun
from litex_verify.models.soc_config import SoCConfig


class ToolInfo(BaseModel):
    name: str
    version: str
    path: Path
    tier: int = Field(ge=1, le=3)
    capabilities: list[str] = Field(default_factory=list)


class ProjectState(BaseModel):
    version: str = "1.0"
    project_name: str = Field(..., min_length=1, max_length=64)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    workflow_state: WorkflowState = WorkflowState.S0_INIT
    verification_tier: int = Field(default=1, ge=1, le=3)
    tools: dict[str, ToolInfo] = Field(default_factory=dict)
    config: SoCConfig | None = None
    rtl_top_module: str | None = None
    runs: list[SimulationRun] = Field(default_factory=list)

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, value: str) -> str:
        if not re.fullmatch(r"^[A-Za-z][A-Za-z0-9_]*$", value):
            raise ValueError(
                "Project name must start with a letter and contain only alphanumeric or underscore"
            )
        return value
