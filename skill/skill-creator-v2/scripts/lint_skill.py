#!/usr/bin/env python3
"""Production linter for generated skills."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from scripts.quick_validate import validate_skill
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.quick_validate import validate_skill


MAX_SKILL_MD_LINES = 500
REQUIRED_REFERENCE_LINKS = {
    "production-skill-architecture.md",
    "failure-modes.md",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def linked_reference_names(body: str) -> set[str]:
    return set(re.findall(r"references/([A-Za-z0-9_.-]+\.md)", body))


def linked_reference_text(skill_path: Path, body: str) -> str:
    refs = []
    for name in sorted(linked_reference_names(body)):
        path = skill_path / "references" / name
        if path.exists():
            refs.append(read(path))
    return "\n\n".join(refs)


def heading_present(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, re.IGNORECASE | re.MULTILINE))


def lint_links(skill_path: Path, body: str) -> list[str]:
    errors = []
    for name in linked_reference_names(body):
        if not (skill_path / "references" / name).exists():
            errors.append(f"SKILL.md references missing file: references/{name}")
    return errors


def lint_python_scripts(skill_path: Path) -> list[str]:
    errors = []
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.exists():
        return errors
    for py_file in sorted(scripts_dir.glob("*.py")):
        try:
            source = py_file.read_text(encoding="utf-8")
            compile(source, str(py_file), "exec")
        except SyntaxError as exc:
            errors.append(f"Python syntax error in {py_file.relative_to(skill_path)}: {exc.msg}")
        except OSError as exc:
            errors.append(f"Cannot read Python script {py_file.relative_to(skill_path)}: {exc}")
    return errors


def lint(skill_path: Path, orchestrator: bool = False, json_output: bool = False) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    skill_path = skill_path.resolve()

    valid, message = validate_skill(skill_path)
    if not valid:
        errors.append(message)

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return {"errors": errors or ["SKILL.md is missing"], "warnings": warnings}

    text = read(skill_md)
    line_count = len(text.splitlines())
    if line_count > MAX_SKILL_MD_LINES:
        warnings.append(f"SKILL.md has {line_count} lines; route more detail to references/")

    body = text.split("---", 2)[-1] if text.count("---") >= 2 else text
    refs_text = linked_reference_text(skill_path, body)
    combined = body + "\n\n" + refs_text

    errors.extend(lint_links(skill_path, body))
    errors.extend(lint_python_scripts(skill_path))

    missing_required_links = REQUIRED_REFERENCE_LINKS - linked_reference_names(body)
    if missing_required_links:
        warnings.append(f"SKILL.md does not link required production references: {', '.join(sorted(missing_required_links))}")

    required_gates = {
        "failure modes": r"(^|\n)#+\s+.*failure modes?|failure_mode",
        "retry policy": r"(^|\n)#+\s+.*retry|retry limits?|backoff",
        "evidence rule": r"(^|\n)#+\s+.*evidence|evidence rule",
        "tool verification": r"verify_tools\.py|tool verification|dependency states",
        "final review": r"final-review-gate\.md|final review|review\.json",
    }
    for label, pattern in required_gates.items():
        if not heading_present(combined, pattern):
            errors.append(f"Missing production gate: {label}")

    if orchestrator:
        orchestrator_checks = {
            "write zones": r"write zones?|write_zone",
            "dependency/parallelism table": r"dependency\s*/\s*parallelism table|parallelism",
            "stop rules": r"stop rules?|stop_rule",
            "completion vs acceptance": r"completion.*acceptance|accepted_by_orchestrator",
        }
        for label, pattern in orchestrator_checks.items():
            if not heading_present(combined, pattern):
                errors.append(f"Missing orchestrator-worker contract element: {label}")

    if "evidence" in body.lower() and "failure" in body.lower() and "retry" in body.lower() and not linked_reference_names(body):
        errors.append("Keyword-only production gates detected: gate terms appear but no linked references support them")

    return {"errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint a production skill")
    parser.add_argument("skill_path", type=Path)
    parser.add_argument("--orchestrator", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = lint(args.skill_path, orchestrator=args.orchestrator)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Lint report for {args.skill_path}")
        if report["errors"]:
            print("Errors:")
            for error in report["errors"]:
                print(f"  - {error}")
        if report["warnings"]:
            print("Warnings:")
            for warning in report["warnings"]:
                print(f"  - {warning}")
        if not report["errors"] and not report["warnings"]:
            print("OK: no errors or warnings")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
