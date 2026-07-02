---
name: minimal-valid-skill
description: Create a small verified artifact from a user workflow. Use when the user asks to capture a workflow as a reusable skill with evidence, tool checks, failure modes, retry limits, and final review.
---

# Minimal Valid Skill

Use this skill for a compact workflow.

Read `references/production-skill-architecture.md` and `references/failure-modes.md`.

## Workflow

Verify tools before relying on them with `scripts/verify_tools.py`. Run final review through `references/final-review-gate.md`.

## Failure Modes

Use the taxonomy in the linked reference.

## Retry Policy

Retry limits are finite and failures escalate.

## Evidence Rule

Every success claim must cite a file, command output, or review artifact.
