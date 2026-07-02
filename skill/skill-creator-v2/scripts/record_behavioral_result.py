#!/usr/bin/env python3
"""Record an actual behavioral eval executor result into a run directory."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def record_result(
    *,
    run_dir: Path,
    result_text: str,
    runtime_mode: str,
    adapter: str,
    agent_id: str | None,
    status: str,
    duration_ms: int | None,
    total_tokens: int | None,
    source: str,
) -> dict[str, Any]:
    result_text = result_text.strip()
    if not result_text:
        raise ValueError("Refusing to record an empty behavioral result")

    outputs_dir = run_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    result_path = outputs_dir / "result.md"
    result_path.write_text(result_text + "\n", encoding="utf-8")

    now = datetime.now(timezone.utc).isoformat()
    run_record_path = run_dir / "run-record.json"
    run_record = load_json(run_record_path)
    run_record.update(
        {
            "status": status,
            "runtime_mode": runtime_mode,
            "adapter": adapter,
            "agent_id": agent_id,
            "result_path": str(result_path),
            "result_recorded_at": now,
            "source": source,
            "actual_output_recorded": True,
            "inline_fallback": runtime_mode == "inline_fallback",
        }
    )
    write_json(run_record_path, run_record)

    metrics = {
        "tool_calls": {},
        "total_tool_calls": 0,
        "total_steps": 1,
        "files_created": [str(result_path)],
        "errors_encountered": 0 if status == "complete" else 1,
        "output_chars": len(result_text),
        "transcript_chars": len(read_optional(run_dir / "transcript.md")),
        "runtime_mode": runtime_mode,
    }
    write_json(outputs_dir / "metrics.json", metrics)

    timing = {
        "runtime_mode": runtime_mode,
        "adapter": adapter,
        "total_tokens": total_tokens,
        "duration_ms": duration_ms,
        "total_duration_seconds": round(duration_ms / 1000, 4) if duration_ms is not None else 0.0,
        "recorded_at": now,
        "timing_unavailable": duration_ms is None,
    }
    write_json(run_dir / "timing.json", timing)
    return run_record


def main() -> int:
    parser = argparse.ArgumentParser(description="Record behavioral eval executor output")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--result-file", type=Path)
    parser.add_argument("--runtime-mode", default="multi_agent_v1")
    parser.add_argument("--adapter", default="manual-multi-agent")
    parser.add_argument("--agent-id")
    parser.add_argument("--status", default="complete")
    parser.add_argument("--duration-ms", type=int)
    parser.add_argument("--total-tokens", type=int)
    parser.add_argument("--source", default="executor_final_message")
    args = parser.parse_args()

    if args.result_file:
        result_text = args.result_file.read_text(encoding="utf-8")
    else:
        result_text = sys.stdin.read()

    record = record_result(
        run_dir=args.run_dir.resolve(),
        result_text=result_text,
        runtime_mode=args.runtime_mode,
        adapter=args.adapter,
        agent_id=args.agent_id,
        status=args.status,
        duration_ms=args.duration_ms,
        total_tokens=args.total_tokens,
        source=args.source,
    )
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
