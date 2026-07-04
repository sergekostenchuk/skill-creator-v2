# Maintenance Policy

Use this reference when publishing, reviewing, or updating `skill-creator-v2`.

## Review Interval

- `review_interval_days`: 45
- Review sooner when Codex/Claude/Gemini/OpenCode skill formats change, dependency policy changes, or behavioral eval harnesses change.

## Schema Expectations

Expected local schemas and contracts:

- `references/classifier-output-schema.json`
- `references/evidence-contract-schema.json`
- `evals/evals.json`
- `evals/meta-evals.json`
- `evals/classification-golden/*.json`
- `release/metadata.json`

## Support Tiers

Do not collapse all installed folders into "supported":

- `validated_static_current`: static folder checks pass and installed copy matches the staged source.
- `validated_static_stale`: static checks pass but installed copy is older than staging.
- `format_adapter_needed`: runtime exists but needs adapter or native prompt format.
- `blocked`: root or invocation is missing.

## Required Release Evidence

Before public publication:

- `scripts/run_all_checks.py` output;
- canonical `release-benchmark.json`;
- sanitation report for folder and package/archive;
- platform smoke matrix;
- safe install dry-run plan;
- final release review.

## Deprecation And Drift

Mark the package `needs_review` when:

- the last verified date is older than `review_interval_days`;
- platform matrix has stale or blocked P0 targets;
- dependency allowlist entries no longer have exact version/integrity evidence;
- independent behavioral eval support regresses to inline-only evidence.
