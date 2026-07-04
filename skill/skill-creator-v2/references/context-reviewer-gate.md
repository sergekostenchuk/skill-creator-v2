# Context Reviewer Gate

Use this reference for deep-path workflows, skill groups, orchestrator-worker systems, high-risk work, and long iterative skill creation.

The Context Reviewer does not redo the worker's task. It checks whether the next block receives the right approved context and whether the previous block can be accepted.

## When Required

Context review is required when:

- risk includes production, legal, security, financial, destructive, or public-release impact;
- the workflow is a skill group or orchestrator-worker system;
- the next worker depends on a prior decision packet;
- a worker output will be used as evidence by another worker;
- a human-owned decision may have been made by the agent;
- classification confidence is low or changed during work;
- context changed materially from the original user goal.

Context review is optional for low-risk fast-path micro skills. Do not force it when it adds process without reducing risk.

## Reviewer Checklist

The reviewer must check:

- `goal_retention`: original user goal is still intact.
- `constraint_retention`: non-goals, hard constraints, and forbidden areas were not dropped.
- `assumption_labeling`: assumptions are labeled and not treated as facts.
- `evidence_sufficiency`: claims have evidence contracts or are marked as caveats/blockers.
- `handoff_readiness`: next worker gets enough context, not raw noise.
- `decision_integrity`: accepted/rejected options have reasons.
- `human_boundary`: human-owned decisions were not silently made by the agent.
- `risk_gate_alignment`: risk-derived gates still match current scope.
- `sanitation`: private workbench data is not promoted into source/runtime/public docs.

## Approved Context Packet

Each major block should consume and return an approved context packet:

```yaml
approved_context_packet:
  version: 1
  original_user_goal: ""
  current_interpretation: ""
  classification_packet_path: ""
  non_goals: []
  hard_constraints: []
  accepted_decisions: []
  rejected_options: []
  open_questions: []
  human_owned_decisions: []
  evidence_paths: []
  risk_gates: []
  next_worker_inputs: []
  confidence: medium
  escalation_required: false
  escalation_reason: null
```

For deep-path work, append context packets to `APPROVED-CONTEXT.md`. For automation, a matching JSON file may be used, but the Markdown packet is enough for manual review.

## Reviewer Output

```json
{
  "context_review_id": "CR-001",
  "review_mode": "inline_fallback",
  "passed": false,
  "findings": [
    {
      "field": "human_boundary",
      "severity": "blocker",
      "message": "The worker selected a final design direction that the user was supposed to choose."
    }
  ],
  "approved_context_packet_version": 1,
  "next_action": "return_to_worker"
}
```

Allowed `next_action` values:

- `continue`
- `return_to_worker`
- `ask_user`
- `revise_classification`
- `block_release`

## Escalation

Ask the user or block when:

- the worker made a human-owned decision;
- the next action is destructive, public, legal, financial, production-affecting, or credential-sensitive;
- evidence is missing for a required-for-done claim;
- context drift changes the user goal;
- the group boundary is wrong and requires merge/split review.

## Completion Is Not Acceptance

A worker can be complete and still fail context review.

Acceptance requires:

- worker output exists;
- required evidence exists or is explicitly blocked/waived;
- context reviewer passes where required;
- orchestrator accepts the reviewed output;
- final review or human decision passes when required by risk.
