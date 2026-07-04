# Risk To Gate Matrix

Use this reference after classification. Gates are derived from risk and destructive potential, not from broad class names.

## Gate Principle

The generated skill must not say "done" until the gates required by its `risk_profile` are either passed, explicitly blocked, or consciously waived by the user with the remaining risk documented.

When risks combine, apply the strictest gate set. If risk confidence is low, default upward.

## Matrix

| Risk Profile | Minimum Required Gates |
| --- | --- |
| `low_advisory` | State assumptions; do not claim production readiness; cite sources when used; keep evidence proportional. |
| `internal_reversible` | Record before/after diff or manifest; describe rollback path; avoid broad unrelated edits. |
| `external_source_freshness` | Capture source URL, access date, source status, and screenshot/hash/quote metadata where useful; label unreachable or stale sources. |
| `visual_client_facing` | Capture screenshot or rendered artifact; run viewport/visual checks where UI is built; include subjective human choice point for direction. |
| `production_infrastructure` | Capture before-state; require rollback plan; show command output; run health/connectivity check; require approval before mutation when lockout or downtime is possible. |
| `security_privacy` | Define secret boundary; scan or state secret-handling check; verify permission boundary; avoid credential exposure; include security-specific failure modes. |
| `legal_high_stakes` | Identify jurisdiction and matter type; separate facts from assumptions; cite dated legal sources; require human approval before final legal/filing/defense use. |
| `financial_business` | Cite dated market/source evidence; disclose spend/business risk; require human approval before irreversible spend or public campaign action. |
| `irreversible_destructive` | Require explicit confirmation; prove backup or state rollback impossibility; prefer dry-run/staged mode; block if confirmation is missing. |

## Production Infrastructure Gates

For live infrastructure, deployment, DNS, SSL, router, VPN, server, or release operations:

- `before_state_required`: capture config, status, current DNS/SSL/deploy hash, route table, or service state before mutation.
- `rollback_required`: write the exact rollback path before mutation.
- `approval_before_mutation`: stop for user approval before actions that can cause lockout, downtime, account risk, or data loss.
- `post_check_required`: run health, connectivity, smoke, DNS, SSL, or service checks after mutation.
- `command_evidence_required`: cite command output or API response, not only prose.

## Legal High-Stakes Gates

For legal, tax, traffic, administrative defense, compliance, or filing workflows:

- `jurisdiction_required`: identify jurisdiction before analysis.
- `matter_type_required`: identify the procedure/matter type and stage.
- `facts_assumptions_split`: separate user facts, inferred facts, and assumptions.
- `dated_citations_required`: cite legal sources with dates or version markers when available.
- `human_approval_required`: stop before final filing, legal conclusion, appeal, defense submission, or external communication.
- `no_professional_overclaim`: do not present output as licensed legal advice unless the user explicitly supplies that authority context.

## Security And Privacy Gates

For security, privacy, VPN, supply-chain, credentials, permissions, or sensitive data:

- `secret_boundary_required`: define what must never be printed, stored, or committed.
- `permission_boundary_required`: define allowed accounts, paths, hosts, APIs, and write zones.
- `supply_chain_gate`: unpinned or unverified packages require `manual_approval_required` or `hard_blocked`.
- `redaction_required`: redact secrets, tokens, private keys, private hostnames, and sensitive personal data in reports.
- `security_failure_modes_required`: include relevant failure modes and escalation paths.

## Destructive Gates

For deletion, migration, public publication, account changes, irreversible writes, or non-reversible production changes:

- `explicit_confirmation_required`: do not proceed from implied approval.
- `backup_or_snapshot_required`: prove a backup/snapshot or state why rollback is impossible.
- `dry_run_preferred`: run dry-run/staged mode when available.
- `blast_radius_required`: describe what can be affected.
- `stop_if_unclear`: if scope, target, or rollback is unclear, block.

## Visual And External-Source Gates

For visual/design/client-facing and current-source workflows:

- `screenshot_or_artifact_required`: capture what was actually inspected or built.
- `source_status_required`: mark source as reachable, unreachable, partial, paywalled, blocked, stale, or user-provided.
- `originality_or_license_gate`: do not copy proprietary layouts, images, code, text, SVGs, unique animations, or private source assets.
- `human_choice_point`: ask the user to choose among subjective directions when the choice affects final creative direction.

## Overblocking Guard

Do not apply high-risk gates to low-risk fast-path tasks unless the classification packet justifies them. Heavy gates are required by risk, not by prestige or complexity theater.

If a task is low-risk and local, produce a small evidence note instead of a full workbench, and disclose the reduced claim.
