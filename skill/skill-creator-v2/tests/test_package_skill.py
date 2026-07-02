from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.package_skill import package_skill


FIXTURES = ROOT / "tests" / "fixtures" / "skills"


def test_package_includes_evals_and_excludes_cache_files(tmp_path):
    skill_copy = tmp_path / "minimal_valid_skill"
    shutil.copytree(FIXTURES / "minimal_valid_skill", skill_copy)
    evals_dir = skill_copy / "evals"
    evals_dir.mkdir()
    (evals_dir / "evals.json").write_text('{"skill_name":"minimal-valid-skill","evals":[]}\n', encoding="utf-8")
    cache_dir = skill_copy / "scripts" / "__pycache__"
    cache_dir.mkdir(parents=True)
    (cache_dir / "ignored.pyc").write_bytes(b"cache")

    package_path = package_skill(skill_copy, tmp_path / "dist")
    assert package_path is not None

    with zipfile.ZipFile(package_path) as archive:
        names = set(archive.namelist())

    assert "minimal_valid_skill/evals/evals.json" in names
    assert not any("__pycache__" in name or name.endswith(".pyc") for name in names)
