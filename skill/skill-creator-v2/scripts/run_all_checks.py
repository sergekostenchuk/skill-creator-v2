#!/usr/bin/env python3
"""Run the canonical release-readiness checks for skill-creator-v2."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FORBIDDEN_ARCHIVE_PARTS = {"__pycache__", ".pytest_cache", "node_modules", ".github"}
FORBIDDEN_ARCHIVE_SUFFIXES = {".pyc"}
FORBIDDEN_ARCHIVE_NAMES = {".DS_Store", ".env", ".npmrc"}
FORBIDDEN_CONTENT_PATTERNS = [
    re.compile(r"/Users/" + r"kostenchuksergey"),
    re.compile(r"npm_hh[A-Za-z0-9]+"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"token=[A-Za-z0-9_-]{16,}"),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_command(args: list[str]) -> str:
    return " ".join(args)


def run_command(args: list[str], cwd: Path) -> dict[str, Any]:
    started = time.time()
    proc = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    duration = round(time.time() - started, 4)
    return {
        "command": as_command(args),
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "duration_seconds": duration,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "status": "passed" if proc.returncode == 0 else "failed",
    }


def load_json_if_exists(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def should_scan_archive_member(name: str) -> bool:
    lower = name.lower()
    if lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".gz", ".tgz", ".skill", ".pdf", ".docx")):
        return False
    return True


def archive_sanitation(package_path: Path) -> dict[str, Any]:
    forbidden_entries: list[str] = []
    content_hits: list[dict[str, str]] = []
    if not package_path.exists():
        return {
            "status": "failed",
            "package_path": str(package_path),
            "error": "package missing",
            "forbidden_entries": forbidden_entries,
            "content_hits": content_hits,
        }

    with zipfile.ZipFile(package_path) as archive:
        for name in archive.namelist():
            path = Path(name)
            parts = set(path.parts)
            if parts & FORBIDDEN_ARCHIVE_PARTS or path.suffix in FORBIDDEN_ARCHIVE_SUFFIXES or path.name in FORBIDDEN_ARCHIVE_NAMES:
                forbidden_entries.append(name)
                continue
            if not should_scan_archive_member(name):
                continue
            try:
                text = archive.read(name).decode("utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in FORBIDDEN_CONTENT_PATTERNS:
                if pattern.search(text):
                    content_hits.append({"file": name, "pattern": pattern.pattern})

    status = "passed" if not forbidden_entries and not content_hits else "failed"
    return {
        "status": status,
        "package_path": str(package_path),
        "forbidden_entries": forbidden_entries,
        "content_hits": content_hits,
    }


def add_step(report: dict[str, Any], name: str, step: dict[str, Any]) -> None:
    step["name"] = name
    report["steps"].append(step)


def run_checks(skill_path: Path, workspace: Path, pytest_args: list[str]) -> dict[str, Any]:
    skill_path = skill_path.resolve()
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    py = sys.executable
    report: dict[str, Any] = {
        "generated_at": now_iso(),
        "runtime_mode": "local_release_check_runner",
        "skill_path": str(skill_path),
        "workspace": str(workspace),
        "steps": [],
    }

    add_step(report, "quick_validate", run_command([py, "scripts/quick_validate.py", str(skill_path)], skill_path))
    add_step(report, "production_lint", run_command([py, "scripts/lint_skill.py", str(skill_path), "--json"], skill_path))
    add_step(report, "pytest", run_command([py, "-m", "pytest", *pytest_args], skill_path))

    taxonomy_output = workspace / "taxonomy-classification-report.json"
    add_step(
        report,
        "taxonomy_classification",
        run_command(
            [
                py,
                "scripts/run_taxonomy_classification_evals.py",
                "--fixtures",
                str(skill_path / "evals" / "classification-golden"),
                "--taxonomy",
                str(skill_path / "references" / "taxonomy-reference.json"),
                "--output",
                str(taxonomy_output),
            ],
            skill_path,
        ),
    )

    meta_workspace = workspace / "meta-evals"
    add_step(
        report,
        "meta_evals_inline_fallback",
        run_command(
            [
                py,
                "scripts/run_meta_evals.py",
                "--skill-path",
                str(skill_path),
                "--meta-evals",
                str(skill_path / "evals" / "meta-evals.json"),
                "--workspace",
                str(meta_workspace),
            ],
            skill_path,
        ),
    )

    self_diagnose = skill_path / "scripts" / "self_diagnose.py"
    if self_diagnose.exists():
        add_step(
            report,
            "self_diagnose",
            run_command(
                [
                    py,
                    "scripts/self_diagnose.py",
                    "--skill-path",
                    str(skill_path),
                    "--output",
                    str(workspace / "self-diagnose.json"),
                ],
                skill_path,
            ),
        )
    else:
        add_step(
            report,
            "self_diagnose",
            {
                "command": "scripts/self_diagnose.py",
                "cwd": str(skill_path),
                "returncode": 0,
                "duration_seconds": 0.0,
                "stdout": "",
                "stderr": "self_diagnose.py not present; optional until RA-020 T-082",
                "status": "skipped",
            },
        )

    package_dir = workspace / "dist"
    add_step(report, "package_skill", run_command([py, "scripts/package_skill.py", str(skill_path), str(package_dir)], skill_path))
    package_path = package_dir / f"{skill_path.name}.skill"
    add_step(report, "package_sanitation", archive_sanitation(package_path))

    passed = sum(1 for step in report["steps"] if step["status"] == "passed")
    failed = sum(1 for step in report["steps"] if step["status"] == "failed")
    skipped = sum(1 for step in report["steps"] if step["status"] == "skipped")
    report["summary"] = {
        "total": len(report["steps"]),
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": round(passed / (passed + failed), 4) if passed + failed else 0.0,
        "release_ready_checks_passed": failed == 0,
    }
    report["artifacts"] = {
        "taxonomy_report": str(taxonomy_output),
        "meta_eval_report": str(meta_workspace / "meta-eval-report.json"),
        "self_diagnose_report": str(workspace / "self-diagnose.json"),
        "package_path": str(package_path),
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all skill-creator-v2 release checks")
    parser.add_argument("--skill-path", type=Path, default=Path.cwd())
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pytest-arg", action="append", default=[], help="Extra pytest argument; may be provided multiple times")
    args = parser.parse_args()

    pytest_args = args.pytest_arg or ["tests"]
    report = run_checks(args.skill_path, args.workspace, pytest_args)
    output = args.output or args.workspace / "run-all-checks.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0 if report["summary"]["release_ready_checks_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
