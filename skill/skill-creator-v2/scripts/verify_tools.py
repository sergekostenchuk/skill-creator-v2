#!/usr/bin/env python3
"""Verify declared tool dependencies without leaking secret values."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_deps(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        return data.get("dependencies", [])
    if isinstance(data, list):
        return data
    raise ValueError("deps must be a list or object with dependencies[]")


def normalize_available(data: Any) -> set[str]:
    if isinstance(data, dict):
        values = data.get("tools", []) + data.get("mcp", []) + data.get("commands", []) + data.get("packages", [])
    elif isinstance(data, list):
        values = data
    else:
        values = []
    return {str(v) for v in values}


def verify_one(dep: dict[str, Any], available: set[str]) -> dict[str, Any]:
    name = str(dep.get("name", "")).strip()
    category = str(dep.get("category", "unknown")).strip()
    fallback = dep.get("fallback")
    required = bool(dep.get("required", True))
    status = "missing"
    evidence = ""

    if name in available:
        status = "verified"
        evidence = "found in supplied available manifest"
    elif category in {"cli", "command"}:
        command = str(dep.get("command", name))
        found = shutil.which(command)
        if found:
            status = "verified"
            evidence = f"command found on PATH: {command}"
        else:
            evidence = f"command not found on PATH: {command}"
    elif category in {"python", "python_package", "package"}:
        module = str(dep.get("module", name)).replace("-", "_")
        if importlib.util.find_spec(module):
            status = "verified"
            evidence = f"python module import spec found: {module}"
        else:
            evidence = f"python module import spec missing: {module}"
    elif category in {"env", "environment"}:
        variable = str(dep.get("env", name))
        if variable in os.environ:
            status = "verified"
            evidence = f"environment variable is present: {variable}; value was not read"
        else:
            evidence = f"environment variable missing: {variable}"
    else:
        evidence = "not found in supplied available manifest"

    if status != "verified" and fallback:
        status = "fallback"
        evidence = f"{evidence}; fallback declared"
    elif status != "verified" and not required:
        status = "assumed"
        evidence = f"{evidence}; dependency marked optional"

    blocking = status == "missing" and required and not fallback
    return {
        "name": name,
        "category": category,
        "used_for": dep.get("used_for", ""),
        "required": required,
        "status": status,
        "verified": status == "verified",
        "fallback": fallback,
        "blocking": blocking,
        "evidence": evidence,
    }


def verify(deps: list[dict[str, Any]], available: set[str]) -> dict[str, Any]:
    results = [verify_one(dep, available) for dep in deps]
    unresolved = [r for r in results if r["blocking"]]
    return {
        "results": results,
        "all_verified": all(r["status"] == "verified" for r in results),
        "unresolved_missing": unresolved,
        "blocking": bool(unresolved),
        "summary": {
            "verified": sum(1 for r in results if r["status"] == "verified"),
            "fallback": sum(1 for r in results if r["status"] == "fallback"),
            "assumed": sum(1 for r in results if r["status"] == "assumed"),
            "missing": sum(1 for r in results if r["status"] == "missing"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify skill tool dependencies")
    parser.add_argument("--deps", required=True)
    parser.add_argument("--available", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    deps = normalize_deps(load_json(Path(args.deps)))
    available = normalize_available(load_json(Path(args.available)))
    report = verify(deps, available)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for result in report["results"]:
            print(f"[{result['status'].upper()}] {result['name']} ({result['category']}): {result['evidence']}")
    return 1 if report["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main())

