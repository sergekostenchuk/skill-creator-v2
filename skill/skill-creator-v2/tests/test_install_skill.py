from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def make_minimal_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "demo-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo skill for safe install tests.\n---\n# Demo\n",
        encoding="utf-8",
    )
    cache = skill / "scripts" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "ignored.pyc").write_bytes(b"cache")
    return skill


def run_install(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/install_skill.py", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_install_dry_run_does_not_write(tmp_path: Path) -> None:
    skill = make_minimal_skill(tmp_path)
    target = tmp_path / "target" / "demo-skill"
    output = tmp_path / "install-plan.json"

    proc = run_install(
        "--skill-path",
        str(skill),
        "--target-path",
        str(target),
        "--output",
        str(output),
    )

    assert proc.returncode == 0, proc.stderr
    plan = json.loads(output.read_text())
    assert plan["mode"] == "dry_run"
    assert plan["applied"] is False
    assert plan["no_runtime_roots_modified"] is True
    assert not target.exists()


def test_install_apply_uses_temp_target_and_backup(tmp_path: Path) -> None:
    skill = make_minimal_skill(tmp_path)
    target = tmp_path / "target" / "demo-skill"
    backup_root = tmp_path / "backups"
    output = tmp_path / "install-plan.json"

    first = run_install(
        "--skill-path",
        str(skill),
        "--target-path",
        str(target),
        "--backup-root",
        str(backup_root),
        "--output",
        str(output),
        "--apply",
    )
    assert first.returncode == 0, first.stderr
    assert (target / "SKILL.md").exists()
    assert not (target / "scripts" / "__pycache__").exists()

    (target / "LOCAL.txt").write_text("old local file\n", encoding="utf-8")
    second = run_install(
        "--skill-path",
        str(skill),
        "--target-path",
        str(target),
        "--backup-root",
        str(backup_root),
        "--output",
        str(output),
        "--apply",
    )
    assert second.returncode == 0, second.stderr
    plan = json.loads(output.read_text())
    assert plan["mode"] == "apply"
    assert plan["applied"] is True
    assert plan["backup_path"]
    assert (Path(plan["backup_path"]) / "LOCAL.txt").exists()


def test_install_backup_paths_are_unique_for_same_skill_name(tmp_path: Path) -> None:
    skill = make_minimal_skill(tmp_path)
    backup_root = tmp_path / "backups"
    target_a = tmp_path / "runtime-a" / "demo-skill"
    target_b = tmp_path / "runtime-b" / "demo-skill"

    for target in (target_a, target_b):
        first = run_install(
            "--skill-path",
            str(skill),
            "--target-path",
            str(target),
            "--backup-root",
            str(backup_root),
            "--apply",
        )
        assert first.returncode == 0, first.stderr

    output_a = tmp_path / "install-a.json"
    output_b = tmp_path / "install-b.json"
    second_a = run_install(
        "--skill-path",
        str(skill),
        "--target-path",
        str(target_a),
        "--backup-root",
        str(backup_root),
        "--output",
        str(output_a),
        "--apply",
    )
    second_b = run_install(
        "--skill-path",
        str(skill),
        "--target-path",
        str(target_b),
        "--backup-root",
        str(backup_root),
        "--output",
        str(output_b),
        "--apply",
    )

    assert second_a.returncode == 0, second_a.stderr
    assert second_b.returncode == 0, second_b.stderr
    plan_a = json.loads(output_a.read_text())
    plan_b = json.loads(output_b.read_text())
    assert plan_a["backup_path"] != plan_b["backup_path"]
    assert Path(plan_a["backup_path"]).exists()
    assert Path(plan_b["backup_path"]).exists()
