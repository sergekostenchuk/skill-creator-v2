from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.verify_tools import verify


def test_verified_from_available_manifest():
    report = verify(
        [{"name": "browser.open", "category": "mcp", "required": True}],
        {"browser.open"},
    )
    assert report["results"][0]["status"] == "verified"
    assert not report["blocking"]


def test_missing_with_fallback_is_not_blocking():
    report = verify(
        [{"name": "firecrawl", "category": "mcp", "required": True, "fallback": "use browser search with lower confidence"}],
        set(),
    )
    assert report["results"][0]["status"] == "fallback"
    assert not report["blocking"]


def test_missing_without_fallback_blocks():
    report = verify(
        [{"name": "private-mcp", "category": "mcp", "required": True}],
        set(),
    )
    assert report["results"][0]["status"] == "missing"
    assert report["blocking"]


def test_cli_check_uses_path():
    report = verify(
        [{"name": "python3", "category": "cli", "command": "python3", "required": True}],
        set(),
    )
    assert report["results"][0]["status"] == "verified"


def test_python_package_check_finds_stdlib_module():
    report = verify(
        [{"name": "json", "category": "python_package", "module": "json", "required": True}],
        set(),
    )
    assert report["results"][0]["status"] == "verified"


def test_env_presence_check_does_not_capture_secret_value(monkeypatch):
    monkeypatch.setenv("SKILL_CREATOR_SECRET_FIXTURE", "super-secret-value")
    report = verify(
        [{"name": "SKILL_CREATOR_SECRET_FIXTURE", "category": "env", "required": True}],
        set(),
    )
    evidence = report["results"][0]["evidence"]
    assert report["results"][0]["status"] == "verified"
    assert "super-secret-value" not in evidence
    assert "value was not read" in evidence
