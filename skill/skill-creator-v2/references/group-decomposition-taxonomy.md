# Group Decomposition Taxonomy

Use this reference when the classification packet suggests `skill_group` or `orchestrator_worker`.

The parent classification does not replace worker classification. A group is accepted only when worker boundaries are real and each worker has its own contract.

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
6. Run merge/split review: merge weak workers; split overloaded workers.
7. Define handoff contracts and context-review checkpoints.
8. Define orchestrator acceptance and independent review.
9. Define group-level evals plus worker-level evals.

## Worker Contract

Every worker must define:

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
