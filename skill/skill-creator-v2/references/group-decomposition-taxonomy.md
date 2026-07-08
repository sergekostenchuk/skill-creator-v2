# Group Decomposition Taxonomy

Use this reference when the classification packet suggests `skill_group` or `orchestrator_worker`.

The parent classification does not replace worker classification. A group is accepted only when worker boundaries are real and each worker has its own contract.

Also read `worker-group-layout.md` before creating folders. Group decomposition decides boundaries; worker group layout decides which boundaries should be visible installable skills and which should remain internal workers or shared modules.

## When A Group Is Justified

Create a group only when at least one is true:

- workers need materially different tools or evidence;
- workers represent different specialist roles;
- one stage should not judge its own output;
- stages have different risk profiles or stop rules;
- parallel research lanes must be reconciled;
- handoff context must be reviewed before the next worker acts;
- one orchestrator must coordinate write zones, dependencies, and acceptance.

Do not create a group only because the workflow has many steps.

## Decomposition Flow

1. Classify the parent user goal.
2. Draft candidate worker roles.
3. For each worker, create a worker-specific classification packet.
4. Extract the worker's human workflow if the worker is complex or high-risk.
5. Define worker input, output, write zone, evidence, gates, failure modes, retry limit, and stop rule.
6. Assign `group_membership_type`: `merge_into_parent`, `internal_worker`, `reusable_satellite_skill`, or `shared_module`.
7. Choose `group_layout`: `single_skill`, `single_visible_orchestrator_with_workers`, `multi_skill_group`, or `hybrid_group`.
8. Run merge/split/visibility review: merge weak workers; split overloaded workers; hide tightly coupled workers; keep reusable capabilities installable.
9. Define handoff contracts and context-review checkpoints.
10. Define orchestrator acceptance and independent review.
11. Define group-level evals plus worker-level evals.

## Visibility Review

After decomposition, apply this review before generating files:

- If the role is just a step with the same tools, evidence, risk, and reviewer as the parent, set `group_membership_type: merge_into_parent`.
- If the role has a real specialist boundary but no standalone user trigger, set `group_membership_type: internal_worker` and write `WORKER.md`.
- If the role can be called directly by a future user, has independent evals, and produces value outside this group, set `group_membership_type: reusable_satellite_skill` and write a normal `SKILL.md`.
- If the item is a registry, policy, schema, template, source list, or helper script, set `group_membership_type: shared_module`.

This review is a required anti-clutter gate. The goal is not to minimize folders at any cost; the goal is to minimize installed skills while preserving true reuse.

## Worker Contract

Every internal worker must define these fields in `WORKER.md`. Every reusable satellite skill must define equivalent fields through its own `SKILL.md`, references, and evals.

- `worker_id`
- `purpose`
- `specialist_role`
- `classification_packet`
- `inputs`
- `outputs`
- `write_zone`
- `read_zone`
- `required_evidence`
- `risk_gates`
- `failure_modes`
- `retry_limit`
- `stop_rules`
- `handoff_packet`
- `context_review_checkpoint`
- `group_membership_type`

## Example

```json
{
  "group_name": "design-intelligence-group",
  "parent_classification": {
    "activity_type": ["research", "analyze", "design", "validate", "orchestrate"],
    "domain": ["design_ux"],
    "tool_surface": ["browser", "external_website", "filesystem"],
    "risk_profile": {
      "primary": "external_source_freshness",
      "secondary": ["visual_client_facing"]
    },
    "evidence_profile": ["screenshot", "dom_metadata", "source_citation", "decision_packet"],
    "workflow_shape": ["parallel_research", "orchestrator_worker", "independent_reviewer"],
    "derived_archetype": "ui_reference_research"
  },
  "workers": [
    {
      "worker_id": "award-reference-scout",
      "specialist_role": "design_researcher",
      "classification_packet": {
        "activity_type": ["research", "analyze"],
        "domain": ["design_ux"],
        "tool_surface": ["browser", "external_website"],
        "risk_profile": {
          "primary": "external_source_freshness",
          "secondary": ["visual_client_facing"]
        },
        "evidence_profile": ["screenshot", "dom_metadata", "network_log", "source_citation"],
        "workflow_shape": ["iterative", "parallel_research"],
        "derived_archetype": "ui_reference_research"
      },
      "write_zone": "workbench/award-references/",
      "required_evidence": ["reference cards", "screenshots", "DOM/tech notes"],
      "stop_rules": ["source blocked", "insufficient visual evidence", "copying risk"]
    },
    {
      "worker_id": "originality-guard",
      "specialist_role": "design_reviewer",
      "classification_packet": {
        "activity_type": ["validate", "analyze"],
        "domain": ["design_ux"],
        "tool_surface": ["filesystem", "browser"],
        "risk_profile": {
          "primary": "visual_client_facing",
          "secondary": ["external_source_freshness"]
        },
        "evidence_profile": ["visual_review", "source_citation", "decision_packet"],
        "workflow_shape": ["independent_reviewer"],
        "derived_archetype": "ui_reference_research"
      },
      "write_zone": "workbench/reviews/originality/",
      "required_evidence": ["accepted/rejected similarity notes", "source URLs"],
      "stop_rules": ["copy risk unresolved", "missing source evidence"]
    }
  ]
}
```

## Merge/Split Review

Merge workers when:

- they share the same tools, evidence, risk, and reviewer;
- handoff adds no quality;
- group structure only adds latency.

Hide workers as `internal_worker` when:

- the role is meaningful only inside one parent orchestrator;
- it lacks a standalone user trigger;
- installing it separately would clutter runtime skill roots;
- its evals only make sense through the parent group.

Promote a role to `reusable_satellite_skill` when:

- it has a standalone user trigger and useful independent output;
- it can be tested without the parent orchestrator;
- it is likely to be reused by other groups or single skills;
- its dependencies, risk gates, and evidence contract are meaningful outside the parent workflow.

Store shared modules when:

- the artifact is a source registry, policy, schema, template, or helper script;
- it supports multiple workers but should not be directly invoked as a skill;
- it is better validated as data/config/reference than as a natural-language agent capability.

Split workers when:

- one worker has conflicting roles, such as producing and approving the same artifact;
- evidence contracts differ materially;
- tool permissions or write zones differ;
- one worker can block the whole group and needs isolated retry rules.

## Orchestrator Responsibilities

The orchestrator owns:

- route selection;
- dependency and parallelism table;
- approved context packet;
- worker assignment;
- handoff validation;
- group-level evidence bundle;
- final synthesis;
- acceptance decision after independent verification.

The orchestrator must not silently accept worker output without evidence.
