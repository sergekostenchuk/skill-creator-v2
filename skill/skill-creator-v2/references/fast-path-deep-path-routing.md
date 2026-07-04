# Fast Path / Deep Path Routing

Use this reference after the classification packet. The goal is to avoid overprocessing small skills while still enforcing strict gates for serious work.

## Routing Decision

Set `routing_decision.path` to one of:

- `fast`: compact skill creation with proportional evidence.
- `deep`: workbench-based skill creation with workflow extraction, evidence contracts, gates, evals, and review.
- `blocked`: missing or conflicting context prevents safe implementation.

## Fast Path

Use fast path when all are true:

- primary risk is `low_advisory`, `internal_reversible`, or limited `visual_client_facing`;
- one dominant activity exists;
- one role can make the key decisions;
- tool surfaces are few and familiar;
- no destructive, legal, production, security, public-release, or uncertain dependency gate is present;
- classification confidence is at or above threshold on all core axes;
- user did not ask for a production-grade package or skill group.

Fast path output:

- concise `SKILL.md`;
- minimal references only when they reduce complexity;
- focused eval or example prompt when behavior is verifiable;
- small evidence note;
- explicit caveat that production gates were not run when skipped.

Fast path must not pretend to be production-ready unless the production gates actually pass.

## Deep Path

Use deep path when any are true:

- risk includes `production_infrastructure`, `security_privacy`, `legal_high_stakes`, `financial_business`, or `irreversible_destructive`;
- the skill creates, improves, packages, or publishes other skills;
- there are multiple specialist roles;
- activity types require materially different evidence contracts;
- live external-source/browser/Figma evidence is central to quality;
- the user asks for a skill group or orchestrator-worker system;
- the user asks for 10/10, production, publication, or release candidate quality;
- classification confidence is below threshold on a core axis;
- tool/dependency safety is unknown.

Deep path output:

- workbench/source/runtime boundary;
- approved classification packet;
- human workflow extraction where needed;
- risk-derived gates;
- evidence contract;
- eval strategy with positive, negative, edge, and regression fixtures where useful;
- independent review or context reviewer when risk or group handoff requires it.

## Blocked Path

Use blocked path when:

- the task could affect production, legal, security, financial, destructive, or private state and the target/scope is unclear;
- the user has not approved an irreversible or risky mutation;
- required credentials/tools are missing and no safe fallback exists;
- classification conflicts cannot be resolved from local context;
- a requested public release could expose private workbench data.

Blocked output:

- decision packet;
- missing context;
- safest next question or required approval;
- explicit statement of what will not be done.

## Anti-Overprocessing Rules

- Do not create a skill group only because the workflow has many steps.
- Do not create a physical workbench for a tiny local helper unless the user wants auditability.
- Do not force browser/live-source gates into a local text-formatting skill.
- Do not run heavyweight evals for explicit vibe drafts; disclose skipped checks instead.
- Do not block a reversible low-risk draft because a production version would need stronger gates.

## Escalation Rules

Escalate to the user when:

- route confidence is below threshold;
- risk and evidence disagree;
- one skill vs group is uncertain and the choice affects quality or cost;
- the next action is destructive, public, legal, financial, production-affecting, or credential-sensitive;
- the user must choose a subjective direction.

## Routing Checklist

Before writing a skill, answer:

1. What is the smallest truthful route?
2. Which risk makes the route stricter?
3. Which evidence is mandatory for done?
4. Is a workbench required?
5. Is a group required?
6. What must be asked before continuing?
