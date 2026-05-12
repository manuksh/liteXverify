import json

from litex_verify.models.simulation import SimulationRun
from litex_verify.services.coverage_db import CoverageDatabase


def test_coverage_reads_coverage_file(tmp_path) -> None:
    cov_path = tmp_path / "run.cov.json"
    cov_path.write_text(json.dumps({"coverage": 88.5}), encoding="utf-8")
    run = SimulationRun(run_id="r1", status="passed", coverage_db=str(cov_path))
    summary = CoverageDatabase().analyze([run], threshold=80)
    assert summary.overall == 88.5
    assert summary.meets_threshold
