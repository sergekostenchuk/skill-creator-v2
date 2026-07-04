from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_self_diagnose_reports_advisory_coverage(tmp_path: Path) -> None:
    output = tmp_path / "self-diagnose.json"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/self_diagnose.py",
            "--skill-path",
            str(ROOT),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    report = json.loads(output.read_text())
    assert report["runtime_mode"] == "deterministic_self_diagnostic"
    assert report["behavioral_proof"] is False
    assert report["quality_impact"]["coverage_score"] >= 0.85
    assert report["taxonomy_coverage"]["fixture_count"] >= 12
    assert "inline" not in report["quality_impact"]["interpretation"].lower()
    assert "independent behavioral evals remain required" in report["quality_impact"]["interpretation"]
