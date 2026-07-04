#!/usr/bin/env python3
"""Lightweight diagnostic coverage report for skill-creator-v2."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_MODES = {
    "vibe",
    "single-skill",
    "existing-skill-improvement",
    "skill-group",
    "orchestrator-worker",
    "eval-benchmark",
    "description-optimization",
    "package-report",
}
EXPECTED_GROUP_REQUIREMENTS = {"single_skill", "skill_group", "orchestrator_worker", "blocked_for_human_decision"}
EXPECTED_ROUTING_PATHS = {"fast", "deep", "blocked"}
EXPECTED_EVIDENCE_REFERENCES = {
    "evidence-contract-schema.json",
    "evidence-contract-templates.md",
    "risk-to-gate-matrix.md",
    "workbench-source-runtime-model.md",
    "workbench-lifecycle.md",
    "context-reviewer-gate.md",
}
EXPECTED_PLATFORM_SMOKE_FIXTURES = {
    "platform-smoke-codex",
    "platform-smoke-portable",
    "platform-smoke-adapter-needed",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(read(path))


def frontmatter_description(skill_md: str) -> str:
    match = re.match(r"^---\n(.*?)\n---", skill_md, re.DOTALL)
    if not match:
        return ""
    for line in match.group(1).splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return ""


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def collect_taxonomy_coverage(fixtures_dir: Path) -> dict[str, Any]:
    coverage: dict[str, set[str]] = {
        "activity_type": set(),
        "domain": set(),
        "tool_surface": set(),
        "risk_profile": set(),
        "evidence_profile": set(),
        "workflow_shape": set(),
        "derived_archetype": set(),
        "group_requirement": set(),
        "routing_path": set(),
    }
    files = sorted(fixtures_dir.glob("*.json"))
    errors: list[str] = []
    for path in files:
        try:
            case = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: invalid JSON: {exc}")
            continue
        expected = case.get("expected") or case.get("expected_risk_increasing") or {}
        for field in ("activity_type", "domain", "tool_surface", "evidence_profile", "workflow_shape"):
            coverage[field].update(normalize_list(expected.get(field)))
        risk = expected.get("risk_profile", {})
        if isinstance(risk, dict):
            coverage["risk_profile"].update(normalize_list(risk.get("primary")))
            coverage["risk_profile"].update(normalize_list(risk.get("secondary")))
        coverage["derived_archetype"].update(normalize_list(expected.get("derived_archetype")))
        coverage["group_requirement"].update(normalize_list(expected.get("group_requirement")))
        coverage["routing_path"].update(normalize_list(expected.get("routing_path")))

    return {
        "fixture_count": len(files),
        "errors": errors,
        "coverage": {key: sorted(value - {""}) for key, value in coverage.items()},
    }


def collect_meta_eval_coverage(meta_path: Path) -> dict[str, Any]:
    meta = load_json(meta_path)
    evals = meta.get("evals", [])
    names = [str(item.get("name", "")) for item in evals]
    mode_hits = {mode: False for mode in EXPECTED_MODES}
    joined = " ".join(names).lower()
    aliases = {
        "single-skill": ["single-skill", "single skill"],
        "existing-skill-improvement": ["existing-skill", "existing skill", "improvement"],
        "skill-group": ["skill-group", "skill group"],
        "orchestrator-worker": ["orchestrator-worker", "orchestrator worker"],
        "eval-benchmark": ["eval", "benchmark"],
        "description-optimization": ["description"],
        "package-report": ["package", "report"],
        "vibe": ["vibe"],
    }
    for mode, terms in aliases.items():
        mode_hits[mode] = any(term in joined for term in terms)
    return {
        "meta_eval_count": len(evals),
        "eval_names": names,
        "mode_hits": mode_hits,
        "missing_mode_hits": sorted([mode for mode, present in mode_hits.items() if not present]),
    }


def collect_platform_smoke_coverage(fixtures_dir: Path) -> dict[str, Any]:
    present = {path.name for path in fixtures_dir.glob("platform-smoke-*") if path.is_dir()}
    fixture_errors: list[str] = []
    for name in sorted(EXPECTED_PLATFORM_SMOKE_FIXTURES & present):
        fixture = fixtures_dir / name
        for required_file in ("prompt.md", "expected-output.md", "assertions.json"):
            if not (fixture / required_file).exists():
                fixture_errors.append(f"{name}: missing {required_file}")
        assertions_path = fixture / "assertions.json"
        if assertions_path.exists():
            try:
                assertions = load_json(assertions_path)
            except json.JSONDecodeError as exc:
                fixture_errors.append(f"{name}: invalid assertions.json: {exc}")
                continue
            if not isinstance(assertions, list) or not assertions:
                fixture_errors.append(f"{name}: assertions.json must be a non-empty list")
    return {
        "expected": sorted(EXPECTED_PLATFORM_SMOKE_FIXTURES),
        "present": sorted(present),
        "missing": sorted(EXPECTED_PLATFORM_SMOKE_FIXTURES - present),
        "errors": fixture_errors,
    }


def collect_reference_coverage(skill_path: Path) -> dict[str, Any]:
    references = {path.name for path in (skill_path / "references").glob("*") if path.is_file()}
    missing = sorted(EXPECTED_EVIDENCE_REFERENCES - references)
    return {
        "expected_reference_count": len(EXPECTED_EVIDENCE_REFERENCES),
        "present_expected_references": sorted(EXPECTED_EVIDENCE_REFERENCES & references),
        "missing_expected_references": missing,
    }


def score_report(
    taxonomy: dict[str, Any],
    meta: dict[str, Any],
    refs: dict[str, Any],
    platform: dict[str, Any],
    description: str,
) -> tuple[float, list[str]]:
    warnings: list[str] = []
    points = 0
    total = 8

    if taxonomy["fixture_count"] >= 12 and not taxonomy["errors"]:
        points += 1
    else:
        warnings.append("taxonomy fixture count or JSON validity is below target")
    if EXPECTED_ROUTING_PATHS <= set(taxonomy["coverage"]["routing_path"]):
        points += 1
    else:
        warnings.append("routing path coverage is incomplete")
    if {"single_skill", "skill_group", "orchestrator_worker"} <= set(taxonomy["coverage"]["group_requirement"]):
        points += 1
    else:
        warnings.append("single/group/orchestrator group-requirement coverage is incomplete")
    if len(taxonomy["coverage"]["risk_profile"]) >= 5:
        points += 1
    else:
        warnings.append("risk profile coverage is thin")
    if not meta["missing_mode_hits"]:
        points += 1
    else:
        warnings.append("meta-eval mode coverage has gaps: " + ", ".join(meta["missing_mode_hits"]))
    if not refs["missing_expected_references"]:
        points += 1
    else:
        warnings.append("evidence/risk/workbench references missing: " + ", ".join(refs["missing_expected_references"]))
    if not platform["missing"] and not platform["errors"]:
        points += 1
    else:
        warning_parts = []
        if platform["missing"]:
            warning_parts.append("missing platform smoke fixtures: " + ", ".join(platform["missing"]))
        if platform["errors"]:
            warning_parts.append("platform smoke fixture errors: " + "; ".join(platform["errors"]))
        warnings.append("; ".join(warning_parts))
    if len(description.split()) >= 12 and len(description) <= 1024:
        points += 1
    else:
        warnings.append("frontmatter description may be too short or too long")

    return round(points / total, 4), warnings


def diagnose(skill_path: Path) -> dict[str, Any]:
    skill_md = read(skill_path / "SKILL.md")
    description = frontmatter_description(skill_md)
    taxonomy = collect_taxonomy_coverage(skill_path / "evals" / "classification-golden")
    meta = collect_meta_eval_coverage(skill_path / "evals" / "meta-evals.json")
    platform = collect_platform_smoke_coverage(skill_path / "evals" / "fixtures")
    refs = collect_reference_coverage(skill_path)
    coverage_score, warnings = score_report(taxonomy, meta, refs, platform, description)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_mode": "deterministic_self_diagnostic",
        "behavioral_proof": False,
        "skill_path": str(skill_path),
        "description": {
            "length_chars": len(description),
            "word_count": len(description.split()),
        },
        "taxonomy_coverage": taxonomy,
        "meta_eval_coverage": meta,
        "platform_smoke_coverage": platform,
        "reference_coverage": refs,
        "quality_impact": {
            "coverage_score": coverage_score,
            "severity": "pass" if coverage_score >= 0.85 and not taxonomy["errors"] else "needs_review",
            "interpretation": "Advisory coverage signal only; independent behavioral evals remain required for 10/10 claims.",
        },
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run lightweight skill self-diagnostics")
    parser.add_argument("--skill-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = diagnose(args.skill_path.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["quality_impact"], indent=2, sort_keys=True))
    return 0 if report["quality_impact"]["severity"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
