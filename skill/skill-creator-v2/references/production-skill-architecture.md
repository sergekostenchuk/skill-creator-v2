# Production Skill Architecture

Use this reference when drafting or improving a skill.

## Target Shape

```text
skill-name/
├── SKILL.md
├── references/
├── scripts/
├── assets/
├── agents/
└── evals/
```

`SKILL.md` is the routing layer. It should explain when the skill triggers, how to choose the right workflow, and which references or scripts to read next. Put long domain rules in `references/`, deterministic helpers in `scripts/`, reusable templates in `assets/`, and specialized subagent prompts in `agents/`.

## Required Fields

Every production candidate must define:

- `name`: kebab-case and stable.
- `description`: trigger-focused, specific, and concise.
- Inputs and outputs.
- Non-goals.
- Required tools, MCPs, APIs, packages, or external accounts.
- Failure modes and retry policy.
- Evidence rule.
- Eval or review path.
- Packaging/reporting path.

## Progressive Disclosure

Keep `SKILL.md` compact enough to be useful when loaded into context. If a section becomes procedural, move it to a reference and add a routing sentence. Avoid duplicating the same rule in both locations unless the body needs a short safety summary.

## Skill Types

### Single Skill

Use one `SKILL.md` and optional references/scripts/assets. This is the default for a self-contained workflow.

### Existing Skill Improvement

Snapshot the old skill before editing. Preserve the name unless the user explicitly wants a new skill. Run old-vs-new comparisons where the runtime supports it.

### Skill Group

Use separate skills only when boundaries are real. Define shared references, shared state, ownership, and conflict rules. Do not split a skill just to look modular.

### Orchestrator-Worker

Use when delegation, parallelism, or multiple write zones are part of the actual work. Read `orchestrator-worker-contract.md` before writing the skill.

## 10/10 Rubric

A release-grade skill must score at least 9/10 in every applicable category and at least 9.5/10 weighted average:

- Single-skill quality.
- Skill-group quality.
- Orchestrator-worker quality.
- Trigger quality.
- Regression preservation.
- Usability.
- Security/tool dependency quality.
- Simplicity/friction budget.
- Evidence integrity.

No score may rely on planned commands, fake outputs, missing fixtures, or unevaluated impressions.

