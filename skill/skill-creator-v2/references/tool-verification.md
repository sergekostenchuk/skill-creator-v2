# Tool Verification And Dependency Policy

Use this reference before a skill assumes any external tool, MCP, API, package, browser capability, CLI, or environment variable.

## Dependency States

Every dependency must be classified as one of:

- `verified`: available and usable in this environment.
- `assumed`: not directly verifiable here, but the limitation is disclosed.
- `missing`: required and not available.
- `fallback`: missing primary dependency has an explicit weaker path.
- `manual_approval_required`: dependency might be installable but needs user approval.
- `hard_blocked`: dependency is unsafe, blocklisted, or violates policy.

## Verification Flow

1. Ask the skill author to declare dependencies in `deps.json`.
2. Capture available tools in `available.json` or inspect local commands/packages.
3. Run:

```bash
python3 scripts/verify_tools.py --deps deps.json --available available.json --json
```

4. If packages must be installed or trusted, run:

```bash
python3 scripts/install_gate.py \
  --name <package> \
  --version <version> \
  --allowlist-json references/allowlist.json \
  --blocklist-json references/blocklist.json \
  --json
```

## Install Gate Rules

Blocklist wins over allowlist. Auto-approval is allowed only when all are true:

- Package name exactly matches allowlist.
- Requested version exactly matches the pinned allowlist entry.
- The version is not `latest`, `latest-stable`, wildcard, range-only, or missing.
- The allowlist entry contains integrity/hash evidence.
- `verified_at` exists.

Manual approval is required for:

- Unknown packages.
- Version drift from a pinned allowlist entry.
- Missing integrity.
- Stale `verified_at`.
- Recently published or low-adoption packages.
- Any live-network trust check that cannot be completed.

Hard-block:

- Blocklisted packages.
- Known compromised packages or typosquats.
- Dependency requests that require secret disclosure.

## Secret Handling

It is acceptable to check whether an environment variable exists. Never print, copy, or store its value in reports, evals, plans, or wiki pages.

