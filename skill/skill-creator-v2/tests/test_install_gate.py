from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.install_gate import decide


ALLOWLIST = {
    "safe-tool": {
        "version": "1.2.3",
        "integrity": "sha256-fixture",
        "verified_at": "2026-07-02",
    },
    "no-integrity": {
        "version": "1.0.0",
        "verified_at": "2026-07-02",
    },
}

BLOCKLIST = {
    "evil-package": {"reason": "known fixture risk"},
    "requests": {"blocked_versions": ["latest-stable"], "reason": "floating version fixture"},
}


def test_blocklist_hard_blocks_package():
    decision = decide("evil-package", "1.0.0", ALLOWLIST, BLOCKLIST)
    assert decision.tier == "hard_blocked"
    assert not decision.approved


def test_unknown_package_requires_manual_approval():
    decision = decide("unknown-tool", "1.0.0", ALLOWLIST, BLOCKLIST)
    assert decision.tier == "manual_approval_required"
    assert decision.requires_user_approval


def test_version_drift_requires_manual_approval():
    decision = decide("safe-tool", "1.2.4", ALLOWLIST, BLOCKLIST)
    assert decision.tier == "manual_approval_required"
    assert "Version drift" in decision.reason


def test_latest_stable_never_auto_approves():
    decision = decide("requests", "latest-stable", ALLOWLIST, BLOCKLIST)
    assert decision.tier in {"hard_blocked", "manual_approval_required"}
    assert not decision.approved


def test_missing_integrity_blocks_auto_approval():
    decision = decide("no-integrity", "1.0.0", ALLOWLIST, BLOCKLIST)
    assert decision.tier == "manual_approval_required"
    assert "integrity" in decision.reason


def test_exact_pin_with_integrity_auto_approves():
    decision = decide("safe-tool", "1.2.3", ALLOWLIST, BLOCKLIST)
    assert decision.tier == "auto"
    assert decision.approved
