#!/usr/bin/env python3
"""Scan a public skill package candidate for local/private artifacts."""

from __future__ import annotations

import argparse
import json
import re
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


FORBIDDEN_DIRS = {"__pycache__", ".pytest_cache", "node_modules", ".git", ".github"}
FORBIDDEN_FILES = {".DS_Store", ".env", ".npmrc"}
FORBIDDEN_SUFFIXES = {".pyc"}
TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".js",
    ".ts",
    ".html",
    ".css",
    ".csv",
}
FORBIDDEN_PATTERNS = [
    re.compile(r"/Users/" + r"kostenchuksergey"),
    re.compile(r"npm_hh[A-Za-z0-9]+"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"token=[A-Za-z0-9_-]{16,}"),
]


def is_forbidden_path(path: Path) -> bool:
    return bool(set(path.parts) & FORBIDDEN_DIRS) or path.name in FORBIDDEN_FILES or path.suffix in FORBIDDEN_SUFFIXES


def scan_text(name: str, text: str) -> list[dict[str, str]]:
    hits = []
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            hits.append({"file": name, "pattern": pattern.pattern})
    return hits


def scan_directory(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    forbidden_entries = []
    content_hits: list[dict[str, str]] = []
    for item in sorted(path.rglob("*")):
        rel = item.relative_to(path)
        if is_forbidden_path(rel):
            forbidden_entries.append(str(rel))
            continue
        if item.is_file() and item.suffix.lower() in TEXT_SUFFIXES:
            content_hits.extend(scan_text(str(rel), item.read_text(encoding="utf-8", errors="ignore")))
    return forbidden_entries, content_hits


def scan_zip(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    forbidden_entries = []
    content_hits: list[dict[str, str]] = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            rel = Path(name)
            if is_forbidden_path(rel):
                forbidden_entries.append(name)
                continue
            if rel.suffix.lower() in TEXT_SUFFIXES:
                content_hits.extend(scan_text(name, archive.read(name).decode("utf-8", errors="ignore")))
    return forbidden_entries, content_hits


def scan_tar(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    forbidden_entries = []
    content_hits: list[dict[str, str]] = []
    with tarfile.open(path) as archive:
        for member in archive.getmembers():
            rel = Path(member.name)
            if is_forbidden_path(rel):
                forbidden_entries.append(member.name)
                continue
            if member.isfile() and rel.suffix.lower() in TEXT_SUFFIXES:
                extracted = archive.extractfile(member)
                if extracted:
                    content_hits.extend(scan_text(member.name, extracted.read().decode("utf-8", errors="ignore")))
    return forbidden_entries, content_hits


def scan(path: Path) -> dict:
    if path.is_dir():
        forbidden_entries, content_hits = scan_directory(path)
        artifact_type = "directory"
    elif zipfile.is_zipfile(path):
        forbidden_entries, content_hits = scan_zip(path)
        artifact_type = "zip"
    elif tarfile.is_tarfile(path):
        forbidden_entries, content_hits = scan_tar(path)
        artifact_type = "tar"
    else:
        raise ValueError(f"Unsupported package path: {path}")
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_type": artifact_type,
        "path": str(path),
        "status": "passed" if not forbidden_entries and not content_hits else "failed",
        "forbidden_entries": forbidden_entries,
        "content_hits": content_hits,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sanitize public package candidate")
    parser.add_argument("--path", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = scan(args.path.resolve())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
