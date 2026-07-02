#!/usr/bin/env python3
"""Conservative dependency install gate."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any


UNPINNED = {"", "*", "latest", "latest-stable", "stable", "dev", "main", "master"}


@dataclass
class Decision:
    name: str
    requested_version: str | None
    tier: str
    reason: str
    requires_user_approval: bool
    approved: bool
    evidence: list[str]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def is_unpinned(version: str | None) -> bool:
    if version is None:
        return True
    normalized = version.strip().lower()
    if normalized in UNPINNED:
        return True
    return bool(re.search(r"[\*<>=~^, ]", normalized))


def verified_at_is_stale(verified_at: str | None, max_age_days: int) -> bool:
    if not verified_at:
        return True
    try:
        verified = date.fromisoformat(verified_at)
    except ValueError:
        return True
    return (date.today() - verified).days > max_age_days


def blocklist_match(name: str, version: str | None, blocklist: dict[str, Any]) -> str | None:
    entry = blocklist.get(name)
    if not entry:
        return None
    blocked_versions = entry.get("blocked_versions")
    if blocked_versions:
        if version in blocked_versions:
            return f"BLOCKLISTED version: {entry.get('reason', 'blocked dependency')}"
        return None
    return f"BLOCKLISTED package: {entry.get('reason', 'blocked dependency')}"


def decide(
    name: str,
    requested_version: str | None,
    allowlist: dict[str, Any],
    blocklist: dict[str, Any],
    meta: dict[str, Any] | None = None,
    max_verified_age_days: int = 180,
) -> Decision:
    meta = meta or {}
    evidence: list[str] = []

    blocked_reason = blocklist_match(name, requested_version, blocklist)
    if blocked_reason:
        return Decision(
            name=name,
            requested_version=requested_version,
            tier="hard_blocked",
            reason=blocked_reason,
            requires_user_approval=True,
            approved=False,
            evidence=["blocklist matched"],
        )

    if is_unpinned(requested_version):
        return Decision(
            name=name,
            requested_version=requested_version,
            tier="manual_approval_required",
            reason="Version is missing, floating, ranged, or otherwise not exactly pinned.",
            requires_user_approval=True,
            approved=False,
            evidence=["unversioned/floating dependency requests cannot auto-approve"],
        )

    entry = allowlist.get(name)
    if not entry:
        flags = []
        if meta.get("publish_age_days") is not None and meta.get("publish_age_days", 999999) < 90:
            flags.append("published_less_than_90_days_ago")
        if meta.get("weekly_downloads") is not None and meta.get("weekly_downloads", 999999) < 1000:
            flags.append("low_download_signal")
        if meta.get("official_registry") is False:
            flags.append("not_from_official_registry")
        suffix = f" Risk flags: {', '.join(flags)}." if flags else ""
        return Decision(
            name=name,
            requested_version=requested_version,
            tier="manual_approval_required",
            reason=f"Package is not on the allowlist.{suffix}",
            requires_user_approval=True,
            approved=False,
            evidence=["unknown dependency defaults to manual approval"],
        )

    pinned_version = str(entry.get("version", "")).strip()
    if requested_version != pinned_version:
        return Decision(
            name=name,
            requested_version=requested_version,
            tier="manual_approval_required",
            reason=f"Version drift: requested {requested_version}, allowlist pins {pinned_version}.",
            requires_user_approval=True,
            approved=False,
            evidence=["allowlist name match is insufficient without exact version match"],
        )

    integrity = str(entry.get("integrity", "")).strip()
    if not integrity:
        return Decision(
            name=name,
            requested_version=requested_version,
            tier="manual_approval_required",
            reason="Allowlist entry lacks integrity/hash evidence.",
            requires_user_approval=True,
            approved=False,
            evidence=["missing integrity"],
        )

    verified_at = entry.get("verified_at")
    if verified_at_is_stale(verified_at, max_verified_age_days):
        return Decision(
            name=name,
            requested_version=requested_version,
            tier="manual_approval_required",
            reason=f"Allowlist verification date is missing, invalid, or older than {max_verified_age_days} days.",
            requires_user_approval=True,
            approved=False,
            evidence=["stale or missing verified_at"],
        )

    evidence.extend([
        "exact allowlist name match",
        "exact pinned version match",
        "integrity evidence present",
        "verified_at within policy window",
    ])
    return Decision(
        name=name,
        requested_version=requested_version,
        tier="auto",
        reason=f"Matches exact pinned allowlist entry {name}@{requested_version}.",
        requires_user_approval=False,
        approved=True,
        evidence=evidence,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Conservative dependency install gate")
    parser.add_argument("--name", required=True)
    parser.add_argument("--version", default=None)
    parser.add_argument("--allowlist-json", default="references/allowlist.json")
    parser.add_argument("--blocklist-json", default="references/blocklist.json")
    parser.add_argument("--meta-json", default=None)
    parser.add_argument("--max-verified-age-days", type=int, default=180)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    allowlist = load_json(Path(args.allowlist_json))
    blocklist = load_json(Path(args.blocklist_json))
    meta = load_json(Path(args.meta_json)) if args.meta_json else {}

    decision = decide(
        args.name,
        args.version,
        allowlist,
        blocklist,
        meta,
        max_verified_age_days=args.max_verified_age_days,
    )

    if args.json:
        print(json.dumps(asdict(decision), indent=2, sort_keys=True))
    else:
        print(f"[{decision.tier.upper()}] {decision.name}@{decision.requested_version}: {decision.reason}")
        for item in decision.evidence:
            print(f"  evidence: {item}")
    return 0 if decision.approved else 1


if __name__ == "__main__":
    sys.exit(main())

