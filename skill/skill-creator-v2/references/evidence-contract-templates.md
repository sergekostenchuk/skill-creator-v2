# Evidence Contract Templates

Use this reference after classification and risk gates. Evidence must describe the proof required for a claim, not merely name an artifact type.

## Required Evidence Fields

Every required evidence item should include:

- `evidence_id`: stable ID, for example `E-001`.
- `type`: evidence type from `activity-taxonomy.md`.
- `claim_supported`: the claim this evidence proves.
- `why_needed`: why this evidence is required for the task.
- `collection_method`: how to collect it.
- `artifact_path`: where it will be saved.
- `validator`: who or what checks it.
- `required_for_done`: whether work cannot be accepted without it.
- `sanitation_rule`: what must be redacted or excluded before sharing.
- `status`: `planned`, `collected`, `validated`, `blocked`, or `waived_with_risk`.

## Template

```json
{
  "evidence_id": "E-001",
  "type": "config_diff",
  "claim_supported": "The router configuration changed only in the approved route section.",
  "why_needed": "Prevents accepting an unsafe network change from prose alone.",
  "collection_method": "Capture before config, apply intended change, capture after config, generate diff.",
  "artifact_path": "workbench/evidence/router-config-diff.txt",
  "validator": "reviewer confirms diff touches only approved sections",
  "required_for_done": true,
  "sanitation_rule": "Redact public IPs, private hostnames, secrets, tokens, and account identifiers.",
  "status": "planned"
}
```

## Common Evidence Types

### `command_output`

Use for terminal, SSH, CLI, package, deploy, DNS, SSL, health, and test commands.

- `collection_method`: run the exact command, capture relevant stdout/stderr and exit code.
- `validator`: check command, exit code, and expected state.
- `sanitation_rule`: redact secrets, tokens, IPs, private hostnames, usernames, and paths when needed.

### `config_diff`

Use for router, Xray, server, app config, DNS records, CI/CD, and policy files.

- `collection_method`: save before-state and after-state, then diff.
- `validator`: confirm the diff touches only intended zones.
- `sanitation_rule`: redact secrets, keys, credentials, internal hostnames, account IDs.

### `screenshot`

Use for visual/UI/client-facing output and live-site reference inspection.

- `collection_method`: capture viewport screenshot with URL, viewport size, timestamp, and interaction state.
- `validator`: compare against user goal, reference brief, and visual quality checklist.
- `sanitation_rule`: avoid public release of private/client screens unless approved.

### `dom_metadata`

Use for live website inspection, visual reference research, and technology/effect analysis.

- `collection_method`: record page title, URL, selected DOM structure, font hints, script/style hints, interaction notes.
- `validator`: confirm metadata supports the design or technology claim.
- `sanitation_rule`: do not copy proprietary source code; summarize effects and technologies.

### `network_log`

Use when loading behavior, third-party scripts, fonts, media, or performance affects the claim.

- `collection_method`: capture request summary, status codes, asset types, timing, and blocked requests.
- `validator`: confirm load behavior supports or contradicts the claim.
- `sanitation_rule`: redact tokens, signed URLs, user IDs, private endpoints.

### `source_citation`

Use for current facts, external-source research, SERP, market, product, documentation, or public site claims.

- `collection_method`: save URL, title, access date, source status, and short non-copyrighted summary.
- `validator`: check relevance, freshness, and whether the source directly supports the claim.
- `sanitation_rule`: respect copyright limits and do not paste long source text.

### `legal_citation`

Use for legal, tax, traffic, administrative, compliance, or jurisdiction-specific work.

- `collection_method`: record jurisdiction, source authority, date/version, article/section, and relevance.
- `validator`: confirm source is authoritative and facts/assumptions are separated.
- `sanitation_rule`: redact personal case details before public release.

### `rollback_proof`

Use for production, destructive, deployment, DNS, SSL, server, VPN, router, or migration work.

- `collection_method`: record snapshot, backup, revert command, previous config, or rollback plan before mutation.
- `validator`: confirm rollback path is feasible or explicitly impossible.
- `sanitation_rule`: redact credentials and internal topology.

### `package_hash`

Use for packaged skills, npm/GitHub releases, dependency artifacts, and distribution.

- `collection_method`: run hash command on package/tarball and record package contents scan.
- `validator`: confirm hash and contents match expected release scope.
- `sanitation_rule`: package must exclude private workbench, caches, bytecode, and secrets.

### `visual_review`

Use for UI build, Figma, generated media, animation, and client-facing design.

- `collection_method`: capture screenshot/video/frame, viewport, and review notes.
- `validator`: review against brief, usability, text fit, accessibility, originality, and implementation feasibility.
- `sanitation_rule`: avoid public release of client/private visuals unless approved.

### `decision_packet`

Use when the skill must stop, choose a route, ask the user, or preserve context between workers.

- `collection_method`: record options, criteria, accepted/rejected choices, confidence, open questions, and human-owned decisions.
- `validator`: reviewer checks decision follows criteria and preserves the user goal.
- `sanitation_rule`: redact personal or client context before publishing.

## Waived Evidence

If evidence is waived, record:

- who waived it;
- why it was waived;
- which claim is weakened;
- what risk remains;
- whether release is blocked or downgraded.

Waived evidence cannot support a 10/10 claim unless the waiver is irrelevant to the claimed behavior.
