#!/usr/bin/env python3
"""Safe skill installer with dry-run default."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TARGET_ROOTS = {
    "codex": "~/.codex/skills",
    "claude-code": "~/.claude/skills",
    "gemini": "~/.gemini/skills",
    "antigravity": "~/.antigravity/skills",
    "perplexity": "~/.perplexity-pro-mcp/skills",
    "github-copilot": "~/.copilot/skills",
    "qwen": "~/.qwen/skills",
    "zai": "~/.zai/skills",
    "glm": "~/.glm/skills",
    "kimi": "~/.kimi/skills",
}
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", "node_modules"}
EXCLUDE_GLOBS = {"*.pyc"}
EXCLUDE_FILES = {".DS_Store"}


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def should_ignore(_dir: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in EXCLUDE_DIRS or name in EXCLUDE_FILES:
            ignored.add(name)
            continue
        if any(fnmatch.fnmatch(name, pattern) for pattern in EXCLUDE_GLOBS):
            ignored.add(name)
    return ignored


def count_files(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file() and item.name not in EXCLUDE_FILES)


def resolve_target_path(skill_path: Path, target: str | None, target_path: Path | None) -> Path:
    if target_path:
        return target_path.expanduser().resolve()
    if not target:
        raise ValueError("Either --target or --target-path is required")
    if target not in DEFAULT_TARGET_ROOTS:
        raise ValueError(f"Unknown target {target!r}; use --target-path for custom runtimes")
    return (Path(DEFAULT_TARGET_ROOTS[target]).expanduser() / skill_path.name).resolve()


def build_plan(skill_path: Path, destination: Path, target: str | None, apply: bool, backup_root: Path | None) -> dict[str, Any]:
    existing = destination.exists()
    backup_path = None
    if existing:
        root = (backup_root or destination.parent / ".skill-install-backups").expanduser().resolve()
        destination_key = hashlib.sha256(str(destination).encode("utf-8")).hexdigest()[:10]
        backup_path = root / f"{destination.name}-{destination_key}-{now_stamp()}"
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if apply else "dry_run",
        "target": target or "custom",
        "source_path": str(skill_path),
        "destination_path": str(destination),
        "source_exists": skill_path.exists(),
        "destination_exists": existing,
        "source_skill_md_sha256": sha256(skill_path / "SKILL.md"),
        "destination_skill_md_sha256": sha256(destination / "SKILL.md"),
        "source_file_count": count_files(skill_path) if skill_path.exists() else 0,
        "backup_path": str(backup_path) if backup_path else None,
        "actions": [
            "validate source folder",
            "create destination parent if needed",
            "backup existing destination" if existing else "no existing destination to backup",
            "copy source to destination with cache exclusions",
        ],
        "no_runtime_roots_modified": not apply,
        "rollback": {
            "available": bool(backup_path),
            "instruction": "Restore backup_path to destination_path after removing the applied destination."
            if backup_path
            else "Remove destination_path if this was a new install.",
        },
    }


def apply_install(skill_path: Path, destination: Path, backup_path: str | None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if not backup_path:
            raise ValueError("backup_path is required when destination exists")
        backup = Path(backup_path)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(destination, backup, ignore=should_ignore)
        shutil.rmtree(destination)
    shutil.copytree(skill_path, destination, ignore=should_ignore)


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely install a skill folder")
    parser.add_argument("--skill-path", type=Path, required=True)
    parser.add_argument("--target", choices=sorted(DEFAULT_TARGET_ROOTS))
    parser.add_argument("--target-path", type=Path)
    parser.add_argument("--backup-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--apply", action="store_true", help="Perform writes. Omit for dry-run.")
    parser.add_argument("--dry-run", action="store_true", help="Explicit dry-run; this is the default.")
    args = parser.parse_args()

    skill_path = args.skill_path.expanduser().resolve()
    if not (skill_path / "SKILL.md").exists():
        raise SystemExit(f"SKILL.md not found in {skill_path}")

    destination = resolve_target_path(skill_path, args.target, args.target_path)
    plan = build_plan(skill_path, destination, args.target, args.apply, args.backup_root)
    if args.apply:
        apply_install(skill_path, destination, plan["backup_path"])
        plan["applied"] = True
        plan["destination_skill_md_sha256_after"] = sha256(destination / "SKILL.md")
    else:
        plan["applied"] = False

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
