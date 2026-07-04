# Workbench Lifecycle

Use this lifecycle when `references/workbench-source-runtime-model.md` applies.

## Lifecycle

1. `candidate`: user goal, working name, and initial classification packet exist.
2. `active`: workbench is created and all traces/evidence go there.
3. `source-ready`: clean source files exist under `source/<skill-name>/`.
4. `review-ready`: evidence, decisions, evals, and reviewer notes are complete enough for release review.
5. `accepted`: source/package passed gates and release decision is recorded.
6. `archived`: workbench is retained or compressed according to project policy.

## Required Workbench Files

### `CONTEXT.md`

Raw working context, brief, constraints, source notes, and open questions. This file may be messy and private.

### `APPROVED-CONTEXT.md`

Append-only approved context packets. Every major block should consume the latest approved packet and return an updated one.

Minimum packet:

```yaml
approved_context_packet:
  version: 0
  original_user_goal: ""
  current_interpretation: ""
  non_goals: []
  hard_constraints: []
  accepted_decisions: []
  rejected_options: []
  open_questions: []
  human_owned_decisions: []
  evidence_paths: []
  confidence: medium
  escalation_required: false
```

Use `references/context-reviewer-gate.md` when a checkpoint must approve or reject the packet before the next worker acts.

### `DECISIONS.md`

Accepted and rejected decisions with reasons. Record why a path was chosen, not only what was chosen.

### `TRACE.md`

Chronological trace of major actions, tool calls, source visits, command runs, and handoffs. Do not paste secrets or bulky raw logs.

### `EVIDENCE.md`

Index of evidence artifacts and what claim each artifact supports.

### `ARTIFACT-MANIFEST.json`

Machine-readable inventory of important source, evidence, report, package, and runtime artifacts.

## Source Promotion

Promote from workbench to source only when:

- the classification packet is approved or explicitly accepted with caveats;
- risk-derived gates are known;
- evidence contract is known;
- source files are clean and do not include private workbench data;
- unresolved questions are either answered or listed as blockers/caveats.

## Runtime Sync

Sync source to runtime only after:

- lint passes;
- tool/dependency checks pass or missing/fallback states are documented;
- evals required by risk tier pass or are explicitly blocked;
- sanitation scan passes;
- release decision is recorded.

Do not silently propagate to non-Codex runtimes when the task only authorized staged or Codex work.

## Fast-Path Exception

If the request is low-risk, local, and explicitly lightweight:

- a physical workbench can be skipped;
- keep at least a short decision/evidence note in the final response or delivery report;
- do not claim production readiness;
- disclose skipped gates.

## Retention

Default private retention policy:

- keep workbench while the skill is active or being evaluated;
- archive after accepted release if the project needs auditability;
- exclude private workbench files from public release unless reviewed one by one.
