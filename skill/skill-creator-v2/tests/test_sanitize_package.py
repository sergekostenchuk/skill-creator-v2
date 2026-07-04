from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_scan(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/sanitize_package.py", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_sanitize_package_passes_clean_directory(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "SKILL.md").write_text("---\nname: demo\ndescription: Demo.\n---\n", encoding="utf-8")
    output = tmp_path / "sanitation.json"

    proc = run_scan("--path", str(candidate), "--output", str(output))

    assert proc.returncode == 0, proc.stderr
    report = json.loads(output.read_text())
    assert report["status"] == "passed"


def test_sanitize_package_blocks_cache_and_local_paths(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    cache = candidate / "scripts" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "bad.pyc").write_bytes(b"cache")
    local_path = "/Users/" + "kostenchuksergey/private"
    (candidate / "README.md").write_text(f"artifact lives under {local_path}\n", encoding="utf-8")

    proc = run_scan("--path", str(candidate))

    assert proc.returncode == 1
    report = json.loads(proc.stdout)
    assert report["status"] == "failed"
    assert report["forbidden_entries"]
    assert report["content_hits"]
