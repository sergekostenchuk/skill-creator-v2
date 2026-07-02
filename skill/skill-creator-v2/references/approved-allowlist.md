# Approved Allowlist Policy

This file explains the bundled `allowlist.json`. It is not a blanket trust grant.

Auto-approval requires:

- exact package name;
- exact version match;
- integrity/hash evidence;
- `verified_at`;
- no matching blocklist entry;
- version is not `latest`, `latest-stable`, wildcard, or range-only.

Anything else requires manual approval or is hard-blocked.

The allowlist is intentionally small and conservative. A popular package can still be compromised at a specific version, so name recognition alone is not enough.

