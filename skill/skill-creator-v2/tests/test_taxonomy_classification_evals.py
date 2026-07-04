from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_taxonomy_classification_golden_fixtures_pass(tmp_path: Path) -> None:
    output = tmp_path / "taxonomy-report.json"
    proc = run_cmd(
        "scripts/run_taxonomy_classification_evals.py",
        "--fixtures",
        "evals/classification-golden",
        "--taxonomy",
        "references/taxonomy-reference.json",
        "--output",
        str(output),
    )

    assert proc.returncode == 0, proc.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["runtime_mode"] == "deterministic_fixture_validation"
    assert report["behavioral_model_execution"] is False
    fixture_count = len(list((ROOT / "evals" / "classification-golden").glob("*.json")))
    assert report["summary"] == {"total": fixture_count, "passed": fixture_count, "failed": 0}


def test_taxonomy_runner_rejects_negative_constraint_violation(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    bad_case = {
        "case_id": "BAD-001",
        "case_type": "negative",
        "prompt": "Bad browser collapse fixture.",
        "expected": {
            "activity_type": ["research"],
            "domain": ["browser_web"],
            "tool_surface": ["browser"],
            "risk_profile": {"primary": "external_source_freshness", "secondary": []},
            "evidence_profile": ["source_citation"],
            "workflow_shape": ["single_pass"],
            "derived_archetype": "browser_live_inspection",
            "group_requirement": "single_skill",
            "routing_path": "fast",
        },
        "must_not": {
            "domain": ["browser_web"],
            "derived_archetype": ["browser_live_inspection"],
        },
        "notes": "This should fail because expected includes forbidden values.",
    }
    (fixtures / "bad.json").write_text(json.dumps(bad_case), encoding="utf-8")

    proc = run_cmd(
        "scripts/run_taxonomy_classification_evals.py",
        "--fixtures",
        str(fixtures),
        "--taxonomy",
        "references/taxonomy-reference.json",
    )

    assert proc.returncode == 1
    report = json.loads(proc.stdout)
    assert report["summary"] == {"total": 1, "passed": 0, "failed": 1}
    assert any("forbidden values" in error for error in report["results"][0]["errors"])


def test_taxonomy_runner_rejects_monotonic_risk_downgrade(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    bad_case = {
        "case_id": "BAD-002",
        "case_type": "monotonic_risk",
        "base_prompt": "Draft a local checklist.",
        "risk_increasing_prompt": "Run the checklist on a live production server.",
        "expected_base": {
            "risk_profile": {"primary": "production_infrastructure", "secondary": []},
            "routing_path": "deep",
        },
        "expected_risk_increasing": {
            "risk_profile": {"primary": "low_advisory", "secondary": []},
            "routing_path": "fast",
            "required_evidence": ["command_output"],
        },
    }
    (fixtures / "bad.json").write_text(json.dumps(bad_case), encoding="utf-8")

    proc = run_cmd(
        "scripts/run_taxonomy_classification_evals.py",
        "--fixtures",
        str(fixtures),
        "--taxonomy",
        "references/taxonomy-reference.json",
    )

    assert proc.returncode == 1
    report = json.loads(proc.stdout)
    assert report["summary"]["failed"] == 1
    assert "lowered risk" in report["results"][0]["errors"][0]
