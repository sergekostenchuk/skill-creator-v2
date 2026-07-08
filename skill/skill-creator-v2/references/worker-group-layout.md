# Worker Group Layout

Use this reference when a user asks for a skill group, an orchestrator-worker system, or any capability that may otherwise create many installed skills.

The goal is to prevent runtime `skills/` roots from filling with roles that only make sense inside one orchestrated workflow, while still preserving reusable capabilities as standalone skills when they have independent value.

## Core Decision

Before writing folders, classify each proposed role by `group_membership_type`:

- `merge_into_parent`: the role is only a step in the parent skill and does not deserve a worker boundary.
- `internal_worker`: the role is a real specialist boundary, but it is tightly coupled to one parent orchestrator and should not appear as an installable skill.
- `reusable_satellite_skill`: the role participates in the group, but also has a standalone user trigger, evidence contract, evals, and value outside this one group.
- `shared_module`: the item is shared policy, data, schema, template, source registry, or script, not an agent-facing skill.

Then choose `group_layout`:

- `single_skill`: one visible skill, no worker registry.
- `single_visible_orchestrator_with_workers`: one installable root `SKILL.md` plus hidden internal workers.
- `multi_skill_group`: multiple independently installable skills coordinated by docs or an orchestrator.
- `hybrid_group`: one visible orchestrator plus internal workers, reusable satellite skills, and shared modules.

## Reuse Test

A role may become a `reusable_satellite_skill` only when all are true:

- It has a natural standalone user request.
- It has its own trigger description that is not just "called by the parent".
- It can produce useful output without the parent orchestrator.
- It has its own inputs, outputs, evidence, failure modes, stop rules, and evals.
- Its dependencies and risk gates can be understood outside the parent group.
- Installing it separately would reduce future duplication instead of adding clutter.

If any of these are false, prefer `internal_worker`, `shared_module`, or `merge_into_parent`.

## Internal Worker Layout

For one visible skill with hidden workers:

```text
skill-name/
  SKILL.md
  group/
    workers/
      registry.json
      worker-id/
        WORKER.md
    shared/
      artifact-contract.md
      source-registry.md
  references/
  scripts/
  evals/
```

Rules:

- Internal workers use `WORKER.md`, not `SKILL.md`.
- `group/workers/**/SKILL.md` is forbidden.
- `group/workers/registry.json` is required when internal workers exist.
- Every worker in the registry must have a matching `WORKER.md`.
- Every `WORKER.md` must include the required worker contract fields from `orchestrator-worker-contract.md`.
- Shared files are referenced as shared modules, not counted as skills.

## Registry Shape

Use this shape for `group/workers/registry.json`:

```json
{
  "group_layout": "hybrid_group",
  "visible_skill": "design-intelligence-orchestrator",
  "workers": [
    {
      "worker_id": "reference-source-router",
      "path": "reference-source-router/WORKER.md",
      "group_membership_type": "internal_worker"
    },
    {
      "worker_id": "technology-effect-inspector",
      "path": "../../technology-effect-inspector/SKILL.md",
      "group_membership_type": "reusable_satellite_skill"
    }
  ],
  "shared_modules": [
    {
      "module_id": "source-registry",
      "path": "../shared/source-registry.md",
      "group_membership_type": "shared_module"
    }
  ]
}
```

Use relative paths from `group/workers/registry.json`. Internal worker paths should normally stay under `group/workers/`.

## Worker Contract Fields

Each internal `WORKER.md` must contain these field labels:

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

## Boundary Examples

UI intelligence:

- `reference-source-router`: `internal_worker` when it only routes sources for the parent design intelligence run.
- `pattern-inventory-builder`: `internal_worker` when its output is only consumed by the group synthesis.
- `technology-effect-inspector`: `reusable_satellite_skill` when it can inspect any live site for public technology, font, motion, and effect metadata.
- `source-registry.md`: `shared_module`, not a skill.

VPN/Xray operations:

- `routing-rule-planner`: `internal_worker` when it only prepares config fragments for the parent VPN architect.
- `server-log-crawler-analyst`: `reusable_satellite_skill` when it can analyze logs across unrelated infra tasks.
- `provider-port-matrix.json`: `shared_module`.

## Anti-Patterns

Reject these shapes:

- Every phase of a single workflow becomes an installed skill.
- A worker has no standalone trigger but is emitted as `SKILL.md`.
- Shared policy files become skills just to make the group look larger.
- A reusable satellite is hidden as an internal worker even though future projects would need it directly.
- A parent orchestrator accepts worker completion without registry, evidence, and context-review checkpoints.

## Acceptance Questions

Before finalizing a group, answer:

- Which folders will appear in runtime `skills/` roots?
- Which roles are hidden internal workers and why?
- Which roles are reusable satellite skills and what standalone prompt proves that?
- Which files are shared modules rather than skills?
- Which roles were merged back into the parent because their boundary was artificial?
- What eval proves the group does not overproduce standalone skills?
