#!/usr/bin/env python3
"""Prepare behavioral eval packets for independent model/agent execution.

This script does not execute a model. It creates run folders and executor
prompts that can be handed to an independent runtime such as Codex
`multi_agent_v1`, a CLI adapter, or a manual runner. Actual outputs must be
recorded later with `record_behavioral_result.py`.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_CONFIGS = {"with_skill", "without_skill", "old_skill"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(read_text(path))


def slug_eval_dir(index: int, name: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in name.lower()).strip("-")
    return f"eval-{index:03d}-{safe or 'eval'}"


def render_executor_prompt(
    *,
    config: str,
    eval_id: str,
    eval_name: str,
    prompt: str,
    assertions: list[dict[str, Any]],
    skill_path: Path,
    old_skill_path: Path | None,
    run_dir: Path,
) -> str:
    assertion_lines = "\n".join(f"- {item.get('id', 'A?')}: {item.get('text', '')}" for item in assertions)
    output_contract = f"""Save or return the final answer as plain Markdown.

The coordinator will record your final answer into:
{run_dir / 'outputs' / 'result.md'}

Do not modify source files outside your run directory. Do not claim checks you did not run.
"""

    if config == "with_skill":
        skill_clause = f"""You are the WITH-SKILL executor.

Use the candidate skill at:
{skill_path}

Before answering, read the skill's SKILL.md and any references it routes you to for this task. Apply the skill as a real user-facing workflow, not as a static text inspection.
"""
    elif config == "old_skill":
        if old_skill_path is None:
            skill_clause = """You are the OLD-SKILL baseline executor.

No old skill path is available for this fixture. Return `blocked: old_skill_missing` and explain what is missing.
"""
        else:
            skill_clause = f"""You are the OLD-SKILL baseline executor.

Use the old/baseline skill at:
{old_skill_path}

Apply it as a real user-facing workflow, not as a static text inspection.
"""
    else:
        skill_clause = """You are the WITHOUT-SKILL baseline executor.

Do not use `skill-creator-v2` or any candidate skill path. Solve the task using general assistant judgment only. This is the baseline run.
"""

    return f"""# Behavioral Eval Executor Prompt

eval_id: {eval_id}
eval_name: {eval_name}
configuration: {config}

{skill_clause}

## User Task Prompt

{prompt.strip()}

## Expectations The Grader Will Check

{assertion_lines}

## Output Contract

{output_contract}
"""


def selected_evals(meta: dict[str, Any], eval_ids: set[str] | None) -> list[tuple[int, dict[str, Any]]]:
    result: list[tuple[int, dict[str, Any]]] = []
    for index, item in enumerate(meta.get("evals", []), start=1):
        if eval_ids and item.get("id") not in eval_ids:
            continue
        result.append((index, item))
    return result


def prepare(
    *,
    skill_path: Path,
    meta_evals_path: Path,
    workspace: Path,
    configs: list[str],
    eval_ids: set[str] | None,
    adapter: str,
    run_number: int,
) -> dict[str, Any]:
    meta = load_json(meta_evals_path)
    workspace.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(timezone.utc).isoformat()
    prepared_runs: list[dict[str, Any]] = []

    for config in configs:
        if config not in VALID_CONFIGS:
            raise ValueError(f"Invalid config {config!r}; expected one of {sorted(VALID_CONFIGS)}")

    for index, item in selected_evals(meta, eval_ids):
        eval_dir = workspace / slug_eval_dir(index, item["name"])
        prompt_file = skill_path / item["prompt_file"]
        assertions_file = skill_path / item["assertions_file"]
        fixture_dir = skill_path / item.get("fixture_dir", "")
        old_skill_path = fixture_dir / "old_skill" if (fixture_dir / "old_skill").exists() else None
        prompt = read_text(prompt_file)
        assertions = load_json(assertions_file)

        eval_metadata = {
            "eval_id": index,
            "eval_key": item["id"],
            "eval_name": item["name"],
            "prompt": prompt,
            "assertions": assertions,
            "runtime_mode": "behavioral_packet",
            "adapter": adapter,
            "created_at": created_at,
            "candidate_skill_path": str(skill_path),
            "old_skill_path": str(old_skill_path) if old_skill_path else None,
        }
        write_json(eval_dir / "eval_metadata.json", eval_metadata)

        for config in configs:
            if config == "old_skill" and old_skill_path is None:
                continue
            run_dir = eval_dir / config / f"run-{run_number}"
            (run_dir / "outputs").mkdir(parents=True, exist_ok=True)
            executor_prompt = render_executor_prompt(
                config=config,
                eval_id=item["id"],
                eval_name=item["name"],
                prompt=prompt,
                assertions=assertions,
                skill_path=skill_path,
                old_skill_path=old_skill_path,
                run_dir=run_dir,
            )
            prompt_path = run_dir / "executor-prompt.md"
            prompt_path.write_text(executor_prompt, encoding="utf-8")
            run_record = {
                "eval_id": item["id"],
                "eval_name": item["name"],
                "configuration": config,
                "run_number": run_number,
                "run_dir": str(run_dir),
                "executor_prompt": str(prompt_path),
                "result_path": str(run_dir / "outputs" / "result.md"),
                "status": "awaiting_executor_output",
                "adapter": adapter,
                "created_at": created_at,
            }
            write_json(run_dir / "run-record.json", run_record)
            prepared_runs.append(run_record)

    manifest = {
        "skill_name": meta.get("skill_name"),
        "runtime_mode": "behavioral_packet",
        "adapter": adapter,
        "created_at": created_at,
        "skill_path": str(skill_path),
        "meta_evals_path": str(meta_evals_path),
        "workspace": str(workspace),
        "configs": configs,
        "eval_ids": sorted(eval_ids) if eval_ids else "all",
        "runs": prepared_runs,
        "actual_outputs_required": True,
        "inline_fallback_counts_as_behavioral": False,
    }
    write_json(workspace / "behavioral-run-manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare behavioral eval run packets")
    parser.add_argument("--skill-path", type=Path, required=True)
    parser.add_argument("--meta-evals", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--config", action="append", choices=sorted(VALID_CONFIGS), dest="configs")
    parser.add_argument("--eval-id", action="append", dest="eval_ids")
    parser.add_argument("--adapter", default="manual-multi-agent")
    parser.add_argument("--run-number", type=int, default=1)
    args = parser.parse_args()

    configs = args.configs or ["with_skill", "without_skill"]
    manifest = prepare(
        skill_path=args.skill_path.resolve(),
        meta_evals_path=args.meta_evals.resolve(),
        workspace=args.workspace.resolve(),
        configs=configs,
        eval_ids=set(args.eval_ids) if args.eval_ids else None,
        adapter=args.adapter,
        run_number=args.run_number,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
