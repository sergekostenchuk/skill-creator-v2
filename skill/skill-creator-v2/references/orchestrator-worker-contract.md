# Orchestrator-Worker Contract

Use this reference for skill groups and systems where one skill coordinates workers or subagents.

## Required Worker Contract

Each worker must define:

- Inputs: exact files/data and format.
- Outputs: exact artifacts and location.
- Write zone: files/directories the worker may modify.
- Gate: numeric or boolean acceptance criteria.
- Failure modes: closed list from `failure-modes.md`.
- Retry limits: max attempts and escalation path.
- Stop rule: when the worker returns `blocked` instead of expanding scope.
- Evidence: command output, file diff, fetched content, or review artifact.

## Dependency / Parallelism Table

Before delegation, create:

| Stream | Goal | Write zone | Depends on | Decision | Reason |
| --- | --- | --- | --- | --- | --- |

Allowed sequential reasons:

- dependency chain
- write conflict
- shared verification bottleneck
- shared external resource
- uncertain scope

If none of these apply and the user/runtime allows delegation, streams may run in parallel. Otherwise run sequentially and report why.

## Completion Is Not Acceptance

Keep four entities separate:

1. Completion event: worker says it is done.
2. Artifact: concrete output exists.
3. Orchestrator review: accept/reject decision.
4. Verification: independent proof the artifact is correct.
5. Final acceptance: the coordinator accepts the reviewed and verified artifact.

`accepted_by_orchestrator: true` is invalid without verification evidence.

File existence alone is not acceptance. A worker output file may exist and still be rejected when checks, review evidence, artifact contents, or verification are missing.

## Skill Group Observability Contract

Production skill groups must expose enough state for a coordinator or reviewer to tell what actually happened. Required fields:

- artifact_manifest: expected artifact path, owner, status, and verification state;
- worker_status: pending / in_progress / done / blocked / failed;
- commands_run: real commands or tool calls executed, not planned commands;
- evidence_paths: files, screenshots, fetched content, diffs, reports, or citations backing important claims;
- acceptance_status: not_reviewed / rejected / accepted_with_caveats / accepted;
- caveats: missing baselines, partial outputs, skipped checks, and follow-up gates;
- final_synthesis: what was accepted, what was rejected, and why.

Missing artifact manifests, missing status evidence, or worker-completed-without-evidence must be rejected as `partial_output` or `regression_detected`, not accepted silently.

## Behavioral Pressure Tests

For orchestrator-worker systems, include tests that prove:

- independent write zones are not serialized without reason;
- worker output without evidence is rejected;
- missing observability artifacts are rejected;
- retry limits stop loops;
- a worker blocked by scope returns `blocked` instead of editing outside its zone.
