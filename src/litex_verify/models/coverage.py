"""Coverage data models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CoverageHole(BaseModel):
    type: str
    location: str
    description: str
    suggestion: str


class CoverageSummary(BaseModel):
    overall: float
    by_type: dict[str, float] = Field(default_factory=dict)
    by_module: dict[str, float] = Field(default_factory=dict)
    holes: list[CoverageHole] = Field(default_factory=list)
    trend: list[float] = Field(default_factory=list)
    meets_threshold: bool = False
