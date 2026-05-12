"""Coverage analysis helper."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

from litex_verify.models.coverage import CoverageHole, CoverageSummary
from litex_verify.models.simulation import SimulationRun


class CoverageDatabase:
    def analyze(self, runs: list[SimulationRun], threshold: int = 90) -> CoverageSummary:
        if not runs:
            return CoverageSummary(overall=0.0, meets_threshold=False)
        trend: list[float] = []
        for run in runs:
            value = self._read_coverage(run)
            trend.append(value)
        overall = round(mean(trend), 2)
        by_type = {"code": overall, "functional": max(0.0, overall - 5.0), "toggle": max(0.0, overall - 8.0)}
        holes: list[CoverageHole] = []
        if overall < threshold:
            holes.append(
                CoverageHole(
                    type="functional",
                    location="soc_top.default_bin",
                    description="Below threshold in baseline regression.",
                    suggestion="Add directed register and interrupt tests.",
                )
            )
        return CoverageSummary(
            overall=overall,
            by_type=by_type,
            by_module={"soc_top": overall},
            holes=holes,
            trend=trend,
            meets_threshold=overall >= threshold,
        )

    def _read_coverage(self, run: SimulationRun) -> float:
        if not run.coverage_db:
            return 0.0
        path = Path(run.coverage_db)
        if not path.exists():
            return 0.0
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return 0.0
        raw_value = payload.get("coverage", 0.0)
        try:
            return round(float(raw_value), 2)
        except (TypeError, ValueError):
            return 0.0
