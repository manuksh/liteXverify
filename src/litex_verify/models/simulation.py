"""Simulation and test result models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class FailureDetail(BaseModel):
    time: str
    message: str


class TestResult(BaseModel):
    name: str
    status: Literal["passed", "failed", "error", "timeout"]
    duration_ms: int
    seed: int
    log_snippet: str = ""
    failures: list[FailureDetail] = Field(default_factory=list)


class SimulationRun(BaseModel):
    run_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: Literal["running", "passed", "failed", "error"]
    tests: list[TestResult] = Field(default_factory=list)
    duration: int = 0
    log_path: str = ""
    coverage_db: str = ""
    wave_file: str | None = None
