from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lint_skill import lint


FIXTURES = ROOT / "tests" / "fixtures" / "skills"


def test_valid_skill_passes_lint():
    report = lint(FIXTURES / "minimal_valid_skill")
    assert report["errors"] == []


def test_missing_reference_fails_lint():
    report = lint(FIXTURES / "missing_reference_skill")
    assert any("references missing file" in error for error in report["errors"])


def test_keyword_only_gate_fails_lint():
    report = lint(FIXTURES / "keyword_only_skill")
    assert any("Keyword-only production gates" in error for error in report["errors"])


def test_orchestrator_missing_contract_fails_orchestrator_lint():
    report = lint(FIXTURES / "minimal_valid_skill", orchestrator=True)
    assert any("orchestrator-worker" in error for error in report["errors"])


def make_tree_read_only(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        child.chmod(0o555 if child.is_dir() else 0o444)
    path.chmod(0o555)


def make_tree_writable(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        child.chmod(0o755 if child.is_dir() else 0o644)
    path.chmod(0o755)


def test_lint_python_scripts_is_write_free_for_read_only_skill_copy(tmp_path):
    skill_copy = tmp_path / "minimal_valid_skill"
    shutil.copytree(FIXTURES / "minimal_valid_skill", skill_copy)
    scripts_dir = skill_copy / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "valid_script.py").write_text("def run():\n    return 1\n", encoding="utf-8")

    make_tree_read_only(skill_copy)
    try:
        report = lint(skill_copy)
        assert report["errors"] == []
        assert not (scripts_dir / "__pycache__").exists()
    finally:
        make_tree_writable(skill_copy)


def test_lint_python_scripts_still_reports_syntax_errors(tmp_path):
    skill_copy = tmp_path / "minimal_valid_skill"
    shutil.copytree(FIXTURES / "minimal_valid_skill", skill_copy)
    scripts_dir = skill_copy / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "broken.py").write_text("def broken(:\n    pass\n", encoding="utf-8")

    report = lint(skill_copy)
    assert any("Python syntax error in scripts/broken.py" in error for error in report["errors"])
