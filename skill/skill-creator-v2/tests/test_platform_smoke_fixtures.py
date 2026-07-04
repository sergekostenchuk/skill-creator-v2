from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "evals" / "fixtures"
REQUIRED_FIXTURES = {
    "platform-smoke-codex",
    "platform-smoke-portable",
    "platform-smoke-adapter-needed",
}
REQUIRED_ASSERTION_KEYS = {
    "id",
    "text",
    "evidence_required",
    "failure_mode",
    "evaluation_method",
    "required",
}


def test_platform_smoke_fixtures_exist() -> None:
    present = {path.name for path in FIXTURE_ROOT.glob("platform-smoke-*") if path.is_dir()}
    assert REQUIRED_FIXTURES <= present


def test_platform_smoke_fixture_schema() -> None:
    for fixture_name in sorted(REQUIRED_FIXTURES):
        fixture = FIXTURE_ROOT / fixture_name
        assert (fixture / "prompt.md").read_text(encoding="utf-8").strip()
        assert (fixture / "expected-output.md").read_text(encoding="utf-8").strip()
        assertions = json.loads((fixture / "assertions.json").read_text(encoding="utf-8"))
        assert isinstance(assertions, list)
        assert len(assertions) >= 3
        for assertion in assertions:
            assert REQUIRED_ASSERTION_KEYS <= set(assertion)
            assert assertion["required"] is True
            assert assertion["id"].startswith("PS-")
            assert assertion["evidence_required"].strip()


def test_platform_smoke_fixtures_cover_support_tiers() -> None:
    combined = "\n".join(
        (FIXTURE_ROOT / name / "expected-output.md").read_text(encoding="utf-8")
        for name in sorted(REQUIRED_FIXTURES)
    )
    for term in (
        "native",
        "portable",
        "adapter_needed",
        "unsupported_for_release",
        "rollback",
        "hash",
    ):
        assert term in combined
