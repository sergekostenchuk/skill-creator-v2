#!/usr/bin/env python3
"""Validate taxonomy classification golden fixtures.

This is a deterministic regression runner. It validates fixture shape,
taxonomy enum compatibility, negative constraints, and monotonic risk
invariants. It does not execute an LLM and must not be presented as a
behavioral skill-generation eval.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


GROUP_REQUIREMENTS = {"single_skill", "skill_group", "orchestrator_worker", "blocked_for_human_decision"}
ROUTING_PATHS = {"fast", "deep", "blocked"}
CASE_TYPES = {"golden", "negative", "monotonic_risk"}
RISK_ORDER = {
    "low_advisory": 0,
    "internal_reversible": 1,
    "external_source_freshness": 2,
    "visual_client_facing": 2,
    "financial_business": 3,
    "production_infrastructure": 4,
    "security_privacy": 4,
    "legal_high_stakes": 4,
    "irreversible_destructive": 5,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def has_forbidden(expected: dict[str, Any], field: str, forbidden: list[str]) -> list[str]:
    if not forbidden:
        return []
    if field == "derived_archetype":
        present = [expected.get("derived_archetype")]
    elif field == "group_requirement":
        present = [expected.get("group_requirement")]
    elif field == "routing_path":
        present = [expected.get("routing_path")]
    elif field == "risk_profile":
        risk = expected.get("risk_profile", {})
        present = [risk.get("primary"), *normalize_list(risk.get("secondary"))]
    else:
        present = normalize_list(expected.get(field))
    return sorted({item for item in present if item in forbidden})


def validate_expected(case_id: str, expected: dict[str, Any], taxonomy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = [
        "activity_type",
        "domain",
        "tool_surface",
        "risk_profile",
        "evidence_profile",
        "workflow_shape",
        "derived_archetype",
        "group_requirement",
        "routing_path",
    ]
    for field in required:
        if field not in expected:
            errors.append(f"{case_id}: expected missing {field}")

    axes = taxonomy["required_axes"]
    list_fields = {
        "activity_type": axes["activity_type"],
        "domain": axes["domain"],
        "tool_surface": axes["tool_surface"],
        "evidence_profile": axes["evidence_profile"],
        "workflow_shape": axes["workflow_shape"],
    }
    for field, allowed in list_fields.items():
        values = normalize_list(expected.get(field))
        if not values:
            errors.append(f"{case_id}: expected.{field} is empty")
        for value in values:
            if value not in allowed:
                errors.append(f"{case_id}: expected.{field} has unknown value {value!r}")

    risk = expected.get("risk_profile", {})
    if not isinstance(risk, dict):
        errors.append(f"{case_id}: expected.risk_profile must be object")
    else:
        allowed_risks = axes["risk_profile"]
        primary = risk.get("primary")
        if primary not in allowed_risks:
            errors.append(f"{case_id}: expected.risk_profile.primary has unknown value {primary!r}")
        for secondary in normalize_list(risk.get("secondary")):
            if secondary not in allowed_risks:
                errors.append(f"{case_id}: expected.risk_profile.secondary has unknown value {secondary!r}")

    derived = expected.get("derived_archetype")
    if derived != "custom_tuple" and derived not in taxonomy["derived_archetypes"]:
        errors.append(f"{case_id}: unknown derived_archetype {derived!r}")

    group_requirement = expected.get("group_requirement")
    if group_requirement not in GROUP_REQUIREMENTS:
        errors.append(f"{case_id}: unknown group_requirement {group_requirement!r}")

    routing_path = expected.get("routing_path")
    if routing_path not in ROUTING_PATHS:
        errors.append(f"{case_id}: unknown routing_path {routing_path!r}")

    if expected.get("derived_archetype") == "browser_live_inspection":
        for required in ("screenshot", "dom_metadata", "network_log", "trace_log"):
            if required not in expected.get("evidence_profile", []):
                errors.append(f"{case_id}: browser_live_inspection missing evidence {required}")

    if expected.get("derived_archetype") == "figma_canvas_operation":
        for required in ("generated_artifact", "before_after_comparison", "trace_log"):
            if required not in expected.get("evidence_profile", []):
                errors.append(f"{case_id}: figma_canvas_operation missing evidence {required}")

    return errors


def validate_standard_case(path: Path, case: dict[str, Any], taxonomy: dict[str, Any]) -> list[str]:
    case_id = str(case.get("case_id", path.stem))
    errors: list[str] = []
    for field in ("case_id", "case_type", "prompt", "expected", "notes"):
        if field not in case:
            errors.append(f"{case_id}: missing {field}")
    expected = case.get("expected")
    if not isinstance(expected, dict):
        return errors + [f"{case_id}: expected must be object"]

    errors.extend(validate_expected(case_id, expected, taxonomy))

    must_not = case.get("must_not", {})
    if must_not and not isinstance(must_not, dict):
        errors.append(f"{case_id}: must_not must be object")
    for field, forbidden_value in must_not.items():
        forbidden = normalize_list(forbidden_value)
        found = has_forbidden(expected, field, forbidden)
        if found:
            errors.append(f"{case_id}: expected.{field} includes forbidden values {found}")
    return errors


def validate_monotonic_case(path: Path, case: dict[str, Any], taxonomy: dict[str, Any]) -> list[str]:
    case_id = str(case.get("case_id", path.stem))
    errors: list[str] = []
    for field in ("case_id", "case_type", "base_prompt", "risk_increasing_prompt", "expected_base", "expected_risk_increasing"):
        if field not in case:
            errors.append(f"{case_id}: missing {field}")

    base = case.get("expected_base", {})
    increased = case.get("expected_risk_increasing", {})
    if not isinstance(base, dict) or not isinstance(increased, dict):
        return errors + [f"{case_id}: expected_base and expected_risk_increasing must be objects"]

    base_primary = base.get("risk_profile", {}).get("primary")
    increased_primary = increased.get("risk_profile", {}).get("primary")
    if base_primary not in taxonomy["required_axes"]["risk_profile"]:
        errors.append(f"{case_id}: unknown base risk {base_primary!r}")
    if increased_primary not in taxonomy["required_axes"]["risk_profile"]:
        errors.append(f"{case_id}: unknown increased risk {increased_primary!r}")
    if RISK_ORDER.get(increased_primary, -1) < RISK_ORDER.get(base_primary, -1):
        errors.append(f"{case_id}: risk-increasing prompt lowered risk from {base_primary} to {increased_primary}")

    if increased.get("routing_path") == "fast" and RISK_ORDER.get(increased_primary, 0) >= 3:
        errors.append(f"{case_id}: high-risk increased prompt stayed fast path")

    if not increased.get("required_evidence"):
        errors.append(f"{case_id}: risk-increasing prompt missing required_evidence")

    for route in (base.get("routing_path"), increased.get("routing_path")):
        if route not in ROUTING_PATHS:
            errors.append(f"{case_id}: unknown routing_path {route!r}")
    return errors


def validate_case(path: Path, taxonomy: dict[str, Any]) -> dict[str, Any]:
    case = load_json(path)
    case_id = str(case.get("case_id", path.stem))
    case_type = case.get("case_type")
    errors: list[str] = []
    if case_type not in CASE_TYPES:
        errors.append(f"{case_id}: unknown case_type {case_type!r}")
    elif case_type == "monotonic_risk":
        errors.extend(validate_monotonic_case(path, case, taxonomy))
    else:
        errors.extend(validate_standard_case(path, case, taxonomy))
    return {
        "case_id": case_id,
        "file": str(path),
        "case_type": case_type,
        "passed": not errors,
        "errors": errors,
    }


def run(fixtures_dir: Path, taxonomy_path: Path) -> dict[str, Any]:
    taxonomy = load_json(taxonomy_path)
    files = sorted(fixtures_dir.glob("*.json"))
    results = [validate_case(path, taxonomy) for path in files]
    passed = sum(1 for result in results if result["passed"])
    failed = len(results) - passed
    return {
        "runtime_mode": "deterministic_fixture_validation",
        "behavioral_model_execution": False,
        "fixtures_dir": str(fixtures_dir),
        "taxonomy_path": str(taxonomy_path),
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed,
        },
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate taxonomy classification golden fixtures")
    parser.add_argument("--fixtures", type=Path, default=Path("evals/classification-golden"))
    parser.add_argument("--taxonomy", type=Path, default=Path("references/taxonomy-reference.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = run(args.fixtures.resolve(), args.taxonomy.resolve())
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
