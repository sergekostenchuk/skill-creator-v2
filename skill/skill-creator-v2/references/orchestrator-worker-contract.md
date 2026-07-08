# Orchestrator-Worker Contract

Use this reference for skill groups and systems where one skill coordinates workers or subagents.

Also read `group-decomposition-taxonomy.md` and `worker-group-layout.md` before drafting a group. The group-level classification does not replace per-worker classification, and worker decomposition does not automatically mean every worker becomes an installed skill.

## Group Decomposition Gate

Before writing worker skills:

1. Classify the parent request.
2. Propose worker roles.
3. Re-run classification for each worker.
4. Define each worker's input, output, write zone, evidence, gate, failure modes, retry limit, stop rule, and context-review checkpoint.
5. Assign each role a `group_membership_type`: `merge_into_parent`, `internal_worker`, `reusable_satellite_skill`, or `shared_module`.
6. Choose `group_layout`: `single_skill`, `single_visible_orchestrator_with_workers`, `multi_skill_group`, or `hybrid_group`.
7. Merge workers whose boundaries are artificial.
8. Split workers that mix production and review, use conflicting tools, or need materially different evidence contracts.
9. Keep tightly coupled workers hidden under `group/workers/**/WORKER.md`; create standalone `SKILL.md` folders only for reusable satellite skills.

## Required Worker Contract

Each worker must define:

- Membership type: whether it is an internal worker, reusable satellite skill, shared module, or merged parent step.
- Inputs: exact files/data and format.
- Outputs: exact artifacts and location.
- Write zone: files/directories the worker may modify.
- Classification packet: worker-specific activity/domain/tool/risk/evidence/workflow tuple.
- Gate: numeric or boolean acceptance criteria.
- Failure modes: closed list from `failure-modes.md`.
- Retry limits: max attempts and escalation path.
- Stop rule: when the worker returns `blocked` instead of expanding scope.
- Evidence: command output, file diff, fetched content, or review artifact.
- Context-review checkpoint: what approved context must be carried into the next block.

For internal workers, the contract lives in `WORKER.md`. For reusable satellite skills, the contract is distributed across `SKILL.md`, references, scripts, and evals. `group/workers/**/SKILL.md` is invalid because it creates hidden nested installable skills and confuses runtime discovery.

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

- group_layout: `single_visible_orchestrator_with_workers`, `multi_skill_group`, or `hybrid_group` when a group exists;
- worker_registry: registry path and expected worker IDs;
- membership_map: each role's `group_membership_type` and visibility rationale;
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
