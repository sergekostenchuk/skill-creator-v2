#!/usr/bin/env python3
"""Grade behavioral eval outputs created by independent executors."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(read(path))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def has_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def has_all(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return all(term.lower() in lower for term in terms)


def check_assertion(eval_key: str, assertion: dict[str, Any], output: str, files_created: list[str]) -> tuple[bool, str]:
    aid = assertion.get("id", "")
    lower = output.lower()

    if eval_key == "ME-001":
        if aid.endswith("A1"):
            single_scope = has_any(
                lower,
                [
                    "single-skill",
                    "single skill",
                    "single codex skill",
                    "single lightweight codex skill",
                    "one self-contained skill",
                    "this is a single",
                ],
            )
            group_positive = has_any(lower, ["skill group"]) and not has_any(
                lower,
                [
                    "not a skill group",
                    "does not define a skill group",
                    "do not create a skill group",
                    "do not include skill-group",
                    "no skill group",
                ],
            )
            orchestrator_positive = has_any(lower, ["orchestrator-worker", "orchestrator worker"]) and not has_any(
                lower,
                [
                    "not an orchestrator-worker",
                    "does not define a skill group, subagents, or an orchestrator-worker",
                    "does not require an orchestrator-worker",
                    "do not create an orchestrator-worker",
                    "no orchestrator-worker",
                ],
            )
            passed = single_scope and not group_positive and not orchestrator_positive
            return passed, "actual output uses single-skill scope and avoids group/orchestrator complexity"
        if aid.endswith("A2"):
            passed = has_any(lower, ["inputs", "input"]) and has_any(lower, ["outputs", "output"])
            return passed, "actual output includes input and output contract"
        if aid.endswith("A3"):
            passed = has_any(lower, ["eval prompt", "evals", "test prompt", "evaluation"]) and has_any(
                lower, ["assert", "expectation", "checks", "tests"]
            )
            return passed, "actual output includes eval/test prompts or expectations"

    if eval_key == "ME-002":
        if aid.endswith("A1"):
            return "changelog-helper" in lower, "actual output preserves changelog-helper name"
        if aid.endswith("A2"):
            return has_any(lower, ["old_skill", "old skill", "baseline"]), "actual output references old skill or baseline comparison"
        if aid.endswith("A3"):
            return has_any(lower, ["eval", "grading", "test"]), "actual output defines eval/grading approach"

    if eval_key == "ME-003":
        if aid.endswith("A1"):
            return has_all(lower, ["skill"]) and has_any(lower, ["skill a", "skill b", "ingest", "query"]), "actual output defines multiple skill boundaries"
        if aid.endswith("A2"):
            return has_any(lower, ["shared state", "shared reference", "write zone", "write zones"]), "actual output defines shared state or write zones"
        if aid.endswith("A3"):
            return has_any(lower, ["eval", "test", "fixture"]), "actual output includes eval coverage"

    if eval_key == "ME-004":
        if aid.endswith("A1"):
            return has_all(lower, ["inputs", "outputs"]) and has_any(lower, ["failure", "retry", "stop", "evidence"]), "actual output includes worker contract fields"
        if aid.endswith("A2"):
            return has_any(lower, ["completion", "artifact"]) and has_any(lower, ["review", "verification", "acceptance"]), "actual output separates completion from verification"
        if aid.endswith("A3"):
            return has_any(lower, ["dependency", "parallel", "sequential"]), "actual output discusses dependency/parallelism"

    if eval_key == "ME-005":
        if aid.endswith("A1"):
            return has_any(lower, ["verify", "declared dependency", "dependency"]), "actual output addresses dependency verification"
        if aid.endswith("A2"):
            return has_any(lower, ["fallback", "reduced confidence", "manual approval"]), "actual output discloses fallback or manual approval"
        if aid.endswith("A3"):
            return has_any(lower, ["artifact", "evidence", "screenshot", "fetched", "rendered"]), "actual output ties claims to artifacts/evidence"

    if eval_key == "ME-006":
        if aid.endswith("A1"):
            return has_any(lower, ["latest-stable", "not auto", "hard block", "manual approval"]), "actual output rejects weak latest-stable auto approval"
        if aid.endswith("A2"):
            return has_any(lower, ["browserbase", "blocklist", "hard_blocked", "hard-blocked"]), "actual output hard-blocks blocklisted package"
        if aid.endswith("A3"):
            return has_any(lower, ["version drift", "manual_approval_required", "manual approval"]), "actual output requires manual approval on version drift"

    if eval_key == "ME-007":
        if aid.endswith("A1"):
            has_positive = has_any(lower, ["should_trigger", "should-trigger", "positive trigger"])
            has_negative = has_any(lower, ["should_not_trigger", "should-not-trigger", "should not trigger", "negative prompt", "near-miss"])
            return has_positive and has_negative, "actual output includes positive and negative trigger evals"
        if aid.endswith("A2"):
            return has_all(lower, ["precision", "recall"]), "actual output reports trigger precision and recall"
        if aid.endswith("A3"):
            return has_any(lower, ["held-out", "test split", "train"]), "actual output separates train and held-out/test results"

    if eval_key == "ME-008":
        if aid.endswith("A1"):
            return not has_any(lower, ["full benchmark", "full production eval"]) or has_any(lower, ["skip", "defer"]), "actual output avoids forcing full production eval loop"
        if aid.endswith("A2"):
            return has_any(lower, ["not production-ready", "draft", "not production ready"]), "actual output avoids production-ready claim"
        if aid.endswith("A3"):
            return has_any(lower, ["skipped", "deferred", "not run"]), "actual output discloses skipped checks"

    if eval_key in {"ME-009", "ME-010", "ME-011"}:
        if aid.endswith("A1"):
            return has_any(lower, ["partial_output", "partial output", "not accepted", "evidence ladder"]), "actual output rejects shallow external evidence"
        if aid.endswith("A2"):
            return has_any(lower, ["partial_output", "partial output", "missing", "downgrade"]), "actual output downgrades weak evidence"
        if aid.endswith("A3"):
            return has_any(lower, ["artifact", "citation", "metadata", "scroll", "interaction", "manual_review_required"]), "actual output requires stronger external-source evidence"

    if eval_key in {"ME-012", "ME-013", "ME-014"}:
        if aid.endswith("A1"):
            return has_any(lower, ["completion", "acceptance", "artifact", "observability"]), "actual output addresses completion vs acceptance"
        if aid.endswith("A2"):
            return has_any(lower, ["verification", "review", "commands_run", "artifact manifest"]), "actual output requires verification/review artifacts"
        if aid.endswith("A3"):
            return has_any(lower, ["rejected", "invalid", "not accepted", "missing"]), "actual output rejects unverified completion"

    if eval_key == "ME-015":
        if aid.endswith("A1"):
            return has_any(lower, ["skip external-source", "skip heavy", "simple", "local"]), "actual output preserves simple task skip"
        if aid.endswith("A2"):
            return has_any(lower, ["vibe", "lightweight", "draft"]), "actual output keeps lightweight route"
        if aid.endswith("A3"):
            return has_any(lower, ["skipped", "disclose", "not production-ready", "draft"]), "actual output discloses skipped gates"

    return False, f"No behavioral assertion grader implemented for {eval_key}/{aid}; files_created={len(files_created)}"


def failure_attribution(
    *,
    passed: bool,
    assertion: dict[str, Any],
    evidence: str,
    output: str,
    result_exists: bool,
    metrics: dict[str, Any],
    runtime_mode: str,
) -> tuple[str, str]:
    """Attribute a behavioral failure to the most likely repair layer.

    This is intentionally conservative. When the signal is weak, the grader
    returns `ambiguous` instead of pretending it can know whether the skill or
    executor was at fault.
    """
    if passed:
        return "not_applicable", "assertion passed"
    if not result_exists:
        return "environment", "actual executor output is missing"

    lower = output.lower()
    if any(term in lower for term in ["ignored the provided skill", "did not use the skill", "without reading the skill"]):
        return "agent", "output indicates the executor ignored the provided skill context"
    if any(term in lower for term in ["tool unavailable", "permission denied", "timeout", "could not run", "module not found"]):
        return "environment", "output indicates tool/runtime/environment failure"
    if any(term in lower for term in ["not enough context", "unclear", "ambiguous", "cannot determine"]):
        return "ambiguous", "output indicates ambiguous scope or insufficient context"
    if "No behavioral assertion grader implemented" in evidence:
        return "fixture", "grader does not implement this fixture assertion"
    if metrics.get("errors_encountered", 0) and runtime_mode == "unknown":
        return "environment", "runtime mode is unknown and metrics record errors"

    skill_failure_modes = {
        "over_scoped",
        "missing_contract",
        "missing_evals",
        "missing_baseline",
        "missing_dependency_verification",
        "unsafe_dependency",
        "missing_trigger_eval",
        "missing_observability",
        "missing_eval_coverage",
        "overprocessed_simple_request",
        "partial_output",
        "validation_failed",
    }
    if assertion.get("failure_mode") in skill_failure_modes:
        return "skill", f"failed expected skill behavior: {assertion.get('failure_mode')}"
    return "ambiguous", "failure lacks enough signal for reliable attribution"


def attribution_summary(expectations: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        "skill": 0,
        "agent": 0,
        "environment": 0,
        "fixture": 0,
        "ambiguous": 0,
        "not_applicable": 0,
    }
    for item in expectations:
        key = item.get("failure_attribution", "ambiguous")
        summary[key] = summary.get(key, 0) + 1
    return summary


def load_metrics(run_dir: Path) -> dict[str, Any]:
    metrics_path = run_dir / "outputs" / "metrics.json"
    if metrics_path.exists():
        return load_json(metrics_path)
    return {
        "tool_calls": {},
        "total_tool_calls": 0,
        "total_steps": 0,
        "files_created": [],
        "errors_encountered": 1,
        "output_chars": 0,
        "transcript_chars": 0,
    }


def load_timing(run_dir: Path) -> dict[str, Any]:
    timing_path = run_dir / "timing.json"
    if timing_path.exists():
        return load_json(timing_path)
    return {"runtime_mode": "unknown", "timing_unavailable": True, "total_duration_seconds": 0.0}


def grade_run(eval_dir: Path, config: str, run_dir: Path, allow_partial: bool) -> tuple[dict[str, Any], bool]:
    metadata = load_json(eval_dir / "eval_metadata.json")
    eval_key = metadata.get("eval_key")
    assertions = metadata.get("assertions", [])
    result_path = run_dir / "outputs" / "result.md"
    metrics = load_metrics(run_dir)
    timing = load_timing(run_dir)
    run_record = load_json(run_dir / "run-record.json") if (run_dir / "run-record.json").exists() else {}

    if not result_path.exists():
        grading = {
            "expectations": [
                {
                    "text": "Actual behavioral executor output exists.",
                    "passed": False,
                    "evidence": f"Missing {result_path}",
                    "assertion_id": "BEHAVIORAL-OUTPUT",
                    "failure_mode": "missing_actual_output",
                    "failure_attribution": "environment",
                    "failure_attribution_rationale": "actual executor output is missing",
                }
            ],
            "summary": {"passed": 0, "failed": 1, "total": 1, "pass_rate": 0.0},
            "failure_attribution_summary": {
                "skill": 0,
                "agent": 0,
                "environment": 1,
                "fixture": 0,
                "ambiguous": 0,
                "not_applicable": 0,
            },
            "execution_metrics": metrics,
            "timing": timing,
            "claims": [
                {
                    "claim": "No behavioral grading was possible because actual executor output is missing.",
                    "type": "runtime_mode",
                    "verified": True,
                    "evidence": str(result_path),
                }
            ],
            "user_notes_summary": {
                "uncertainties": [],
                "needs_review": ["behavioral output missing"],
                "workarounds": [],
            },
        }
        write_json(run_dir / "grading.json", grading)
        return grading, allow_partial

    output = read(result_path)
    files_created = metrics.get("files_created", [])
    expectations = []
    passed_count = 0
    runtime_mode = run_record.get("runtime_mode") or timing.get("runtime_mode") or "unknown"
    for assertion in assertions:
        passed, evidence = check_assertion(eval_key, assertion, output, files_created)
        passed_count += 1 if passed else 0
        attribution, attribution_rationale = failure_attribution(
            passed=passed,
            assertion=assertion,
            evidence=evidence,
            output=output,
            result_exists=True,
            metrics=metrics,
            runtime_mode=runtime_mode,
        )
        expectations.append(
            {
                "text": assertion.get("text", ""),
                "passed": passed,
                "evidence": evidence,
                "assertion_id": assertion.get("id"),
                "failure_mode": assertion.get("failure_mode"),
                "failure_attribution": attribution,
                "failure_attribution_rationale": attribution_rationale,
            }
        )

    total = len(expectations)
    grading = {
        "expectations": expectations,
        "summary": {
            "passed": passed_count,
            "failed": total - passed_count,
            "total": total,
            "pass_rate": round(passed_count / total, 4) if total else 0.0,
        },
        "failure_attribution_summary": attribution_summary(expectations),
        "execution_metrics": metrics,
        "timing": timing,
        "claims": [
            {
                "claim": "Behavioral eval used actual recorded executor output.",
                "type": "runtime_mode",
                "verified": True,
                "evidence": str(result_path),
            },
            {
                "claim": "inline_fallback is not counted as independent behavioral proof.",
                "type": "runtime_mode",
                "verified": runtime_mode != "inline_fallback",
                "evidence": str(run_dir / "run-record.json"),
            },
        ],
        "user_notes_summary": {
            "uncertainties": [] if runtime_mode != "inline_fallback" else ["runtime_mode is inline_fallback"],
            "needs_review": [],
            "workarounds": [],
        },
        "runtime_mode": runtime_mode,
        "configuration": config,
        "result_path": str(result_path),
    }
    write_json(run_dir / "grading.json", grading)
    return grading, allow_partial or grading["summary"]["failed"] == 0


def write_diff(eval_dir: Path, gradings: dict[str, dict[str, Any]]) -> None:
    lines = ["# Behavioral Eval Diff", ""]
    for config, grading in sorted(gradings.items()):
        summary = grading.get("summary", {})
        lines.append(f"- {config}: {summary.get('passed', 0)}/{summary.get('total', 0)} passed, pass_rate={summary.get('pass_rate', 0)}")
    if "with_skill" in gradings and "without_skill" in gradings:
        delta = gradings["with_skill"]["summary"]["pass_rate"] - gradings["without_skill"]["summary"]["pass_rate"]
        lines.append(f"- delta with_skill_vs_without_skill: {delta:+.4f}")
    if "with_skill" in gradings and "old_skill" in gradings:
        delta = gradings["with_skill"]["summary"]["pass_rate"] - gradings["old_skill"]["summary"]["pass_rate"]
        lines.append(f"- delta with_skill_vs_old_skill: {delta:+.4f}")
    (eval_dir / "diff.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def grade_workspace(workspace: Path, allow_partial: bool) -> tuple[dict[str, Any], bool]:
    eval_reports = []
    overall_ok = True
    for eval_dir in sorted(workspace.glob("eval-*")):
        if not (eval_dir / "eval_metadata.json").exists():
            continue
        gradings: dict[str, dict[str, Any]] = {}
        for config_dir in sorted(eval_dir.iterdir()):
            if not config_dir.is_dir() or not list(config_dir.glob("run-*")):
                continue
            for run_dir in sorted(config_dir.glob("run-*")):
                grading, ok = grade_run(eval_dir, config_dir.name, run_dir, allow_partial)
                overall_ok = overall_ok and ok
                gradings[config_dir.name] = grading
                eval_reports.append(
                    {
                        "eval_dir": str(eval_dir),
                        "configuration": config_dir.name,
                        "run_dir": str(run_dir),
                        "summary": grading["summary"],
                        "runtime_mode": grading.get("runtime_mode", grading.get("timing", {}).get("runtime_mode")),
                    }
                )
        write_diff(eval_dir, gradings)

    total = sum(item["summary"]["total"] for item in eval_reports)
    passed = sum(item["summary"]["passed"] for item in eval_reports)
    missing = [item for item in eval_reports if item["summary"]["total"] == 1 and item["summary"]["failed"] == 1 and item["summary"].get("pass_rate") == 0.0]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_mode": "behavioral_recorded_outputs",
        "workspace": str(workspace),
        "eval_run_count": len(eval_reports),
        "assertions_passed": passed,
        "assertions_total": total,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "inline_fallback_counts_as_behavioral": False,
        "results": eval_reports,
        "missing_or_failed_runs": missing,
    }
    write_json(workspace / "behavioral-eval-report.json", report)
    (workspace / "behavioral-eval-report.md").write_text(
        "# Behavioral Eval Report\n\n"
        f"runtime_mode: {report['runtime_mode']}\n"
        f"eval_run_count: {report['eval_run_count']}\n"
        f"assertions: {passed}/{total}\n"
        f"pass_rate: {report['pass_rate']}\n\n"
        "This report grades actual recorded executor outputs. Inline fallback is not counted as independent behavioral proof.\n",
        encoding="utf-8",
    )
    return report, overall_ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade behavioral eval outputs")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    report, ok = grade_workspace(args.workspace.resolve(), args.allow_partial)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
