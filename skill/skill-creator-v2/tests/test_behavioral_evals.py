from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_skill_fixture(tmp_path: Path) -> tuple[Path, Path]:
    skill = tmp_path / "skill"
    fixture = skill / "evals" / "fixtures" / "single_skill_workflow"
    write(skill / "SKILL.md", "---\nname: skill-creator-v2\n---\n# Skill\n")
    write(
        skill / "evals" / "meta-evals.json",
        json.dumps(
            {
                "skill_name": "skill-creator-v2",
                "evals": [
                    {
                        "id": "ME-001",
                        "name": "single-skill-workflow",
                        "fixture_dir": "evals/fixtures/single_skill_workflow",
                        "prompt_file": "evals/fixtures/single_skill_workflow/prompt.md",
                        "assertions_file": "evals/fixtures/single_skill_workflow/assertions.json",
                    }
                ],
            }
        ),
    )
    write(fixture / "prompt.md", "Create a tiny meeting-notes summarizer skill.")
    write(
        fixture / "assertions.json",
        json.dumps(
            [
                {"id": "ME-001-A1", "text": "The output is a single skill.", "failure_mode": "over_scoped"},
                {"id": "ME-001-A2", "text": "Inputs and outputs are defined.", "failure_mode": "missing_contract"},
                {"id": "ME-001-A3", "text": "Eval prompts are included.", "failure_mode": "missing_evals"},
            ]
        ),
    )
    return skill, skill / "evals" / "meta-evals.json"


def run_cmd(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def test_prepare_creates_packets_without_fake_results(tmp_path: Path) -> None:
    skill, meta = make_skill_fixture(tmp_path)
    workspace = tmp_path / "workspace"

    proc = run_cmd(
        "scripts/prepare_behavioral_evals.py",
        "--skill-path",
        str(skill),
        "--meta-evals",
        str(meta),
        "--workspace",
        str(workspace),
        "--eval-id",
        "ME-001",
    )

    assert proc.returncode == 0, proc.stderr
    run_dir = workspace / "eval-001-single-skill-workflow" / "with_skill" / "run-1"
    assert (run_dir / "executor-prompt.md").exists()
    assert (run_dir / "run-record.json").exists()
    assert not (run_dir / "outputs" / "result.md").exists()
    manifest = json.loads((workspace / "behavioral-run-manifest.json").read_text())
    assert manifest["actual_outputs_required"] is True
    assert manifest["inline_fallback_counts_as_behavioral"] is False


def test_grade_fails_closed_when_result_is_missing(tmp_path: Path) -> None:
    skill, meta = make_skill_fixture(tmp_path)
    workspace = tmp_path / "workspace"
    assert run_cmd(
        "scripts/prepare_behavioral_evals.py",
        "--skill-path",
        str(skill),
        "--meta-evals",
        str(meta),
        "--workspace",
        str(workspace),
        "--eval-id",
        "ME-001",
        "--config",
        "with_skill",
    ).returncode == 0

    proc = run_cmd("scripts/grade_behavioral_evals.py", "--workspace", str(workspace))

    assert proc.returncode == 2
    grading = json.loads(
        (workspace / "eval-001-single-skill-workflow" / "with_skill" / "run-1" / "grading.json").read_text()
    )
    assert grading["summary"]["pass_rate"] == 0.0
    assert grading["expectations"][0]["failure_mode"] == "missing_actual_output"
    assert grading["expectations"][0]["failure_attribution"] == "environment"
    assert grading["failure_attribution_summary"]["environment"] == 1


def test_record_and_grade_actual_output(tmp_path: Path) -> None:
    skill, meta = make_skill_fixture(tmp_path)
    workspace = tmp_path / "workspace"
    assert run_cmd(
        "scripts/prepare_behavioral_evals.py",
        "--skill-path",
        str(skill),
        "--meta-evals",
        str(meta),
        "--workspace",
        str(workspace),
        "--eval-id",
        "ME-001",
        "--config",
        "with_skill",
    ).returncode == 0
    run_dir = workspace / "eval-001-single-skill-workflow" / "with_skill" / "run-1"
    result = """# meeting-notes-summarizer

Type: single-skill

Inputs: messy meeting notes.
Outputs: summary, decisions, and action items.

Evals:
- Eval prompt: summarize a standup note and check action items.
- Expectation: output includes action items and owners.
"""

    record = run_cmd(
        "scripts/record_behavioral_result.py",
        "--run-dir",
        str(run_dir),
        "--runtime-mode",
        "multi_agent_v1",
        "--adapter",
        "manual-multi-agent",
        input_text=result,
    )
    assert record.returncode == 0, record.stderr

    proc = run_cmd("scripts/grade_behavioral_evals.py", "--workspace", str(workspace))
    assert proc.returncode == 0, proc.stderr
    grading = json.loads((run_dir / "grading.json").read_text())
    assert grading["summary"]["passed"] == 3
    assert {item["failure_attribution"] for item in grading["expectations"]} == {"not_applicable"}
    report = json.loads((workspace / "behavioral-eval-report.json").read_text())
    assert report["runtime_mode"] == "behavioral_recorded_outputs"
    assert report["inline_fallback_counts_as_behavioral"] is False


def test_grade_attributes_skill_failure(tmp_path: Path) -> None:
    skill, meta = make_skill_fixture(tmp_path)
    workspace = tmp_path / "workspace"
    assert run_cmd(
        "scripts/prepare_behavioral_evals.py",
        "--skill-path",
        str(skill),
        "--meta-evals",
        str(meta),
        "--workspace",
        str(workspace),
        "--eval-id",
        "ME-001",
        "--config",
        "with_skill",
    ).returncode == 0
    run_dir = workspace / "eval-001-single-skill-workflow" / "with_skill" / "run-1"
    result = """# meeting-notes-summarizer

Type: single-skill

Inputs: messy notes.
Outputs: summary.
"""
    assert run_cmd(
        "scripts/record_behavioral_result.py",
        "--run-dir",
        str(run_dir),
        "--runtime-mode",
        "multi_agent_v1",
        input_text=result,
    ).returncode == 0

    assert run_cmd("scripts/grade_behavioral_evals.py", "--workspace", str(workspace)).returncode == 2
    grading = json.loads((run_dir / "grading.json").read_text())
    failed = [item for item in grading["expectations"] if not item["passed"]]
    assert failed
    assert failed[0]["failure_attribution"] == "skill"
    assert grading["failure_attribution_summary"]["skill"] >= 1


def test_grade_attributes_agent_failure(tmp_path: Path) -> None:
    skill, meta = make_skill_fixture(tmp_path)
    workspace = tmp_path / "workspace"
    assert run_cmd(
        "scripts/prepare_behavioral_evals.py",
        "--skill-path",
        str(skill),
        "--meta-evals",
        str(meta),
        "--workspace",
        str(workspace),
        "--eval-id",
        "ME-001",
        "--config",
        "with_skill",
    ).returncode == 0
    run_dir = workspace / "eval-001-single-skill-workflow" / "with_skill" / "run-1"
    assert run_cmd(
        "scripts/record_behavioral_result.py",
        "--run-dir",
        str(run_dir),
        "--runtime-mode",
        "multi_agent_v1",
        input_text="I ignored the provided skill and answered from generic memory.",
    ).returncode == 0

    assert run_cmd("scripts/grade_behavioral_evals.py", "--workspace", str(workspace)).returncode == 2
    grading = json.loads((run_dir / "grading.json").read_text())
    assert grading["failure_attribution_summary"]["agent"] >= 1


def test_grade_attributes_ambiguous_failure(tmp_path: Path) -> None:
    skill, meta = make_skill_fixture(tmp_path)
    workspace = tmp_path / "workspace"
    assert run_cmd(
        "scripts/prepare_behavioral_evals.py",
        "--skill-path",
        str(skill),
        "--meta-evals",
        str(meta),
        "--workspace",
        str(workspace),
        "--eval-id",
        "ME-001",
        "--config",
        "with_skill",
    ).returncode == 0
    run_dir = workspace / "eval-001-single-skill-workflow" / "with_skill" / "run-1"
    assert run_cmd(
        "scripts/record_behavioral_result.py",
        "--run-dir",
        str(run_dir),
        "--runtime-mode",
        "multi_agent_v1",
        input_text="Not enough context to determine the correct skill output.",
    ).returncode == 0

    assert run_cmd("scripts/grade_behavioral_evals.py", "--workspace", str(workspace)).returncode == 2
    grading = json.loads((run_dir / "grading.json").read_text())
    assert grading["failure_attribution_summary"]["ambiguous"] >= 1
