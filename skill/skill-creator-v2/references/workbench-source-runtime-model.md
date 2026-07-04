# Workbench / Source / Runtime Model

Use this model for serious, high-risk, public, or group skill work. It separates where the agent thinks, where the clean skill source lives, and what gets installed into an agent runtime.

## Three Locations

```text
workbench/  -> reasoning, traces, evidence, reviews, runs, rejected options
source/     -> clean skill source: SKILL.md, references, scripts, assets, agents, evals
runtime/    -> installed copy for Codex, Claude, Gemini, or another runtime
```

The runtime folder is not a project notebook. It must not collect raw logs, screenshots, private notes, failed attempts, full browser traces, or long decision history.

## Responsibilities

| Location | Contains | Must Not Contain |
| --- | --- | --- |
| `workbench/` | context packets, decisions, trace logs, source notes, evidence, screenshots, eval outputs, review notes, rejected options, raw task-plan excerpts | secrets, unredacted tokens, private data in public exports |
| `source/` | clean `SKILL.md`, references, scripts, assets, agents, evals, docs meant to ship | private workbench traces, raw screenshots, local-only task logs, unreviewed claims |
| `runtime/` or installed root | packaged skill files only | workbench history, release deliberation, private artifacts, caches, bytecode |

## When To Create A Workbench

Create a workbench after:

1. the user's goal is captured;
2. the first classification packet exists;
3. a stable working name exists;
4. the task is not a tiny throwaway/vibe request.

Workbench is mandatory for:

- production infrastructure or deployment skills;
- security/privacy skills;
- legal/high-stakes skills;
- public-release candidates;
- skill groups or orchestrator-worker systems;
- external-source/browser/Figma workflows where evidence must be inspected;
- meta-skills that create or modify other skills.

Fast-path skills may skip physical workbench creation only when the final report discloses the reduced evidence claim.

## Recommended Shape

```text
skill-name-workbench/
├── CONTEXT.md
├── APPROVED-CONTEXT.md
├── DECISIONS.md
├── TRACE.md
├── EVIDENCE.md
├── ARTIFACT-MANIFEST.json
├── reviews/
├── runs/
├── artifacts/
├── evals-results/
└── source/
    └── skill-name/
        ├── SKILL.md
        ├── references/
        ├── scripts/
        ├── assets/
        ├── agents/
        └── evals/
```

This shape can be simplified for standard single-skill work, but the boundary must remain clear.

## Public Sanitation Gate

Before packaging or publishing:

- scan workbench and source for secrets, tokens, `.env` values, private URLs, personal data, client data, private screenshots, and local-only paths;
- publish sanitized source/package, not the private workbench;
- include derived evidence summaries when useful;
- record what was excluded and why;
- keep exact local paths only in private reports or when explicitly safe.

## Acceptance Rules

- `file exists` does not mean the artifact is accepted.
- `worker done` does not mean the result is accepted.
- `package built` does not mean the workbench is safe to publish.
- `runtime installed` does not mean the runtime auto-loads the skill unless smoke-tested.

Acceptance requires a clean source artifact, valid evidence, review, and final release decision.
