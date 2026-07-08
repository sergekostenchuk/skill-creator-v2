# Classifier Output Contract

Use this contract after `references/activity-taxonomy.md` when the request is serious enough to need explicit routing, gates, or group decisions.

The classifier output is a decision packet. It is not a final skill and it is not a decorative summary. Downstream skill architecture, evidence requirements, eval strategy, and group decomposition must be traceable to this packet.

## Required Packet

```json
{
  "packet_version": "2026-07-03.ra017",
  "request_summary": "Create a skill group for UI reference research and design direction synthesis.",
  "classification": {
    "catalog_family": "design",
    "specialist_role": "designer",
    "activity_type": ["research", "analyze", "design"],
    "domain": ["design_ux"],
    "tool_surface": ["browser", "external_website", "filesystem"],
    "risk_profile": {
      "primary": "external_source_freshness",
      "secondary": ["visual_client_facing"]
    },
    "evidence_profile": ["screenshot", "dom_metadata", "source_citation", "decision_packet"],
    "workflow_shape": ["parallel_research", "sequential_pipeline", "independent_reviewer"],
    "derived_archetype": "ui_reference_research"
  },
  "classification_confidence": {
    "activity_type": 0.86,
    "domain": 0.9,
    "tool_surface": 0.84,
    "risk_profile": 0.78,
    "evidence_profile": 0.82,
    "workflow_shape": 0.8
  },
  "required_evidence": [
    {
      "type": "screenshot",
      "why_needed": "Proves the visual reference was inspected, not inferred from a catalog card.",
      "minimum_artifact": "workbench/evidence/reference-001-home.png"
    }
  ],
  "readiness_gates": [
    {
      "gate_id": "risk-evidence-match",
      "required": true,
      "reason": "External live references require source URL and dated evidence."
    }
  ],
  "failure_modes": ["tool_unavailable", "external_source_unreachable", "insufficient_evidence"],
  "eval_strategy": ["golden_classification_fixture", "negative_overprocessing_fixture"],
  "group_requirement": "skill_group",
  "group_layout": "hybrid_group",
  "membership_map": {
    "award-reference-scout": "internal_worker",
    "technology-effect-inspector": "reusable_satellite_skill",
    "source-registry": "shared_module"
  },
  "human_review_required": true,
  "routing_decision": {
    "path": "deep",
    "reason": "Multiple activities, live external evidence, and independent review are required."
  },
  "open_questions": [],
  "blocked_reason": null
}
```

## Required Fields

- `packet_version`: version of this contract.
- `request_summary`: short restatement of the user goal.
- `classification.activity_type`: values from `activity-taxonomy.md`.
- `classification.domain`: values from `activity-taxonomy.md`.
- `classification.tool_surface`: values from `activity-taxonomy.md`.
- `classification.risk_profile.primary`: one risk value from `activity-taxonomy.md`.
- `classification.risk_profile.secondary`: optional list of additional risk values.
- `classification.evidence_profile`: evidence values from `activity-taxonomy.md`.
- `classification.workflow_shape`: workflow values from `activity-taxonomy.md`.
- `classification.derived_archetype`: a known derived archetype or `custom_tuple`.
- `classification_confidence`: 0.0 to 1.0 per core axis.
- `required_evidence`: concrete proof expected from the generated skill or worker.
- `readiness_gates`: checks that must pass before claiming done.
- `failure_modes`: closed taxonomy values, or proposed additions that must be reviewed.
- `eval_strategy`: what evals are needed for this request type.
- `group_requirement`: `single_skill`, `skill_group`, `orchestrator_worker`, or `blocked_for_human_decision`.
- `group_layout`: optional layout decision; use `single_skill`, `single_visible_orchestrator_with_workers`, `multi_skill_group`, or `hybrid_group`.
- `membership_map`: optional role-to-visibility map; values are `merge_into_parent`, `internal_worker`, `reusable_satellite_skill`, or `shared_module`.
- `human_review_required`: boolean.
- `routing_decision.path`: `fast`, `deep`, or `blocked`.
- `routing_decision.reason`: why that path is selected.
- `open_questions`: questions that affect scope, dependency safety, or success criteria.
- `blocked_reason`: null unless the next step must stop.

## Confidence Rules

Use `0.70` as the default discussion threshold until a project-specific threshold is provided.

- If any core axis confidence is below threshold, do not choose a risky path silently.
- If risk confidence is low, default upward and require review.
- If evidence confidence is low, create a decision packet or ask for missing context before writing production instructions.
- If group requirement confidence is low, start with a single-skill draft only when risk is low and handoffs are not needed.

## Low-Confidence Fallback

When the packet is incomplete or contradictory:

```json
{
  "group_requirement": "blocked_for_human_decision",
  "routing_decision": {
    "path": "blocked",
    "reason": "Cannot distinguish production router operation from advisory network planning."
  },
  "human_review_required": true,
  "open_questions": [
    "Will the skill execute live router commands or only draft a runbook?"
  ],
  "blocked_reason": "Risk and tool-surface uncertainty affects safety gates."
}
```

Do not continue into implementation when `blocked_reason` is non-null unless the user explicitly accepts the risk or narrows the scope.

## Fast Path Minimum

For lightweight requests, the packet may be short but must still include:

- request summary
- core axis tuple
- primary risk
- minimum evidence
- `group_requirement`
- routing path and reason

## Deep Path Minimum

For production, legal, security, destructive, meta-skill, group, or uncertain requests, include the full packet and carry it into the workbench as the first approved context artifact.
