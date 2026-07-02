# Failure Modes And Retry Policy

Use a closed taxonomy so generated skills do not hide problems behind vague "failed" language.

## Failure Mode Taxonomy

| failure_mode | Meaning | Default Action |
| --- | --- | --- |
| `tool_unavailable` | Required local tool, MCP, API, browser, or runtime capability is missing. | Report missing dependency and fallback if one exists. |
| `permission_blocked` | User approval, filesystem permission, or account access is required. | Stop and ask for the exact approval or credential path, without exposing secrets. |
| `timeout` | A command, tool call, or subagent run exceeded a practical time limit. | Retry once with narrower scope, then escalate. |
| `partial_output` | Some artifacts exist but required outputs are missing or incomplete. | Record missing artifacts and either forward-fix or block release. |
| `hallucinated_source` | Output claims external evidence that was not actually fetched/read. | Fail the check and remove the claim. |
| `stale_data` | Source may be outdated or verification date is too old. | Mark as manual-review-required or refresh with explicit command. |
| `ambiguous_scope` | The request can reasonably mean multiple incompatible things. | Ask a narrow clarification or choose a safe default and disclose it. |
| `schema_mismatch` | JSON/report/eval artifact does not match expected schema. | Fix schema or block downstream tooling. |
| `security_blocked` | Dependency is blocklisted, unsafe, unpinned, or lacks required trust evidence. | Hard-block or require explicit manual approval. |
| `regression_detected` | A previous behavior or contract no longer works. | Reopen the implementation task and preserve evidence. |

## Retry Limits

Retries must be finite:

- `tool_unavailable`: no silent retry; verify once, then report missing/fallback.
- `permission_blocked`: no retry without new user input.
- `timeout`: maximum 2 attempts, with narrower scope on the second attempt.
- `partial_output`: maximum 1 forward-fix attempt before review.
- `schema_mismatch`: maximum 2 correction attempts before escalation.
- `security_blocked`: no retry unless policy or dependency changes.
- `regression_detected`: reopen the responsible implementation step.

## Evidence Rule

Success requires evidence:

- File paths for created or changed artifacts.
- Command output for validations.
- Tool verification report for dependencies.
- Eval outputs, grading, benchmark, or review report for quality claims.
- Explicit skipped-check records when a gate is intentionally not run.

Never convert a planned command into evidence. If a check was not run, say `not_run` and explain why.
