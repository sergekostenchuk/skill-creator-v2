from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lint_skill import lint
from scripts.package_skill import package_skill
from scripts.quick_validate import validate_skill


FIXTURES = ROOT / "tests" / "fixtures" / "skills"


WORKER_MD = """# Reference Source Router

worker_id: reference-source-router
purpose: Route source lists for the parent workflow.
specialist_role: source_router
classification_packet: local research routing packet
inputs: project brief and source policy
outputs: source plan
write_zone: workbench/source-routing/
read_zone: references/ and group/shared/
required_evidence: source-plan.md
risk_gates: external-source gate
failure_modes: partial_output
retry_limit: 1
stop_rules: blocked source policy
handoff_packet: approved source plan
context_review_checkpoint: source plan reviewed by orchestrator
group_membership_type: internal_worker
"""


def copy_minimal_skill(tmp_path: Path) -> Path:
    skill_copy = tmp_path / "minimal_valid_skill"
    shutil.copytree(FIXTURES / "minimal_valid_skill", skill_copy)
    return skill_copy


def add_valid_worker_layout(skill_path: Path) -> None:
    worker_dir = skill_path / "group" / "workers" / "reference-source-router"
    worker_dir.mkdir(parents=True)
    (worker_dir / "WORKER.md").write_text(WORKER_MD, encoding="utf-8")
    shared_dir = skill_path / "group" / "shared"
    shared_dir.mkdir(parents=True)
    (shared_dir / "source-registry.md").write_text("# Source Registry\n", encoding="utf-8")
    (skill_path / "group" / "workers" / "registry.json").write_text(
        """{
  "group_layout": "single_visible_orchestrator_with_workers",
  "visible_skill": "minimal-valid-skill",
  "workers": [
    {
      "worker_id": "reference-source-router",
      "path": "reference-source-router/WORKER.md",
      "group_membership_type": "internal_worker"
    },
    {
      "worker_id": "technology-effect-inspector",
      "path": "../../technology-effect-inspector/SKILL.md",
      "group_membership_type": "reusable_satellite_skill"
    }
  ],
  "shared_modules": [
    {
      "module_id": "source-registry",
      "path": "../shared/source-registry.md",
      "group_membership_type": "shared_module"
    }
  ]
}
""",
        encoding="utf-8",
    )


def test_valid_internal_worker_layout_passes_validate_and_lint(tmp_path: Path) -> None:
    skill_copy = copy_minimal_skill(tmp_path)
    add_valid_worker_layout(skill_copy)

    valid, message = validate_skill(skill_copy)
    assert valid, message
    assert lint(skill_copy)["errors"] == []


def test_nested_skill_md_under_internal_workers_fails_validation(tmp_path: Path) -> None:
    skill_copy = copy_minimal_skill(tmp_path)
    add_valid_worker_layout(skill_copy)
    nested_skill = skill_copy / "group" / "workers" / "reference-source-router" / "SKILL.md"
    nested_skill.write_text("---\nname: leaked-worker\n---\n", encoding="utf-8")

    valid, message = validate_skill(skill_copy)
    assert not valid
    assert "nested SKILL.md" in message


def test_unregistered_worker_md_fails_validation(tmp_path: Path) -> None:
    skill_copy = copy_minimal_skill(tmp_path)
    add_valid_worker_layout(skill_copy)
    extra_worker = skill_copy / "group" / "workers" / "unregistered-worker"
    extra_worker.mkdir()
    (extra_worker / "WORKER.md").write_text(WORKER_MD.replace("reference-source-router", "unregistered-worker"), encoding="utf-8")

    valid, message = validate_skill(skill_copy)
    assert not valid
    assert "not registered" in message


def test_incomplete_worker_contract_fails_validation(tmp_path: Path) -> None:
    skill_copy = copy_minimal_skill(tmp_path)
    add_valid_worker_layout(skill_copy)
    worker_md = skill_copy / "group" / "workers" / "reference-source-router" / "WORKER.md"
    worker_md.write_text(WORKER_MD.replace("required_evidence: source-plan.md\n", ""), encoding="utf-8")

    valid, message = validate_skill(skill_copy)
    assert not valid
    assert "required_evidence" in message


def test_package_refuses_invalid_internal_worker_layout(tmp_path: Path) -> None:
    skill_copy = copy_minimal_skill(tmp_path)
    add_valid_worker_layout(skill_copy)
    (skill_copy / "group" / "workers" / "reference-source-router" / "SKILL.md").write_text(
        "---\nname: leaked-worker\n---\n",
        encoding="utf-8",
    )

    assert package_skill(skill_copy, tmp_path / "dist") is None
