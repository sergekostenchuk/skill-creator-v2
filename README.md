# Skill Creator V2

[![test](https://github.com/sergekostenchuk/skill-creator-v2/actions/workflows/test.yml/badge.svg)](https://github.com/sergekostenchuk/skill-creator-v2/actions/workflows/test.yml)

Skill Creator V2 is a production-grade meta-skill for creating, improving, evaluating, hardening, and packaging AI skills and skill groups.

It turns skill creation from an improvised writing task into a structured engineering workflow with explicit gates for scope, dependencies, failure modes, evals, evidence, packaging, and release readiness.

## What It Does

- Creates single skills, skill groups, and orchestrator-worker systems.
- Improves existing skills while preserving behavior and regression evidence.
- Verifies tool, MCP, API, and package dependencies before relying on them.
- Blocks unsafe dependency assumptions such as unpinned `latest` installs.
- Runs lint, eval, benchmark, behavioral-eval, packaging, and final review helpers.
- Requires evidence before claiming that a skill is production-ready.

## Who It Is For

- Codex and Claude Code users who maintain reusable local skills.
- AI workflow builders who need skill groups instead of one large prompt.
- Teams building agent systems with tools, MCPs, scripts, browser work, or external sources.
- Reviewers who need evidence-backed readiness reports instead of "looks good" claims.

## Install

```bash
npm install -g skill-creator-v2
```

Install into one runtime:

```bash
skill-creator-v2 install --target codex
skill-creator-v2 install --target claude-code
skill-creator-v2 install --target gemini
```

Install into every supported local runtime root:

```bash
skill-creator-v2 install --all
```

Preview writes without changing files:

```bash
skill-creator-v2 install --all --dry-run
```

Supported targets:

- `codex`
- `claude-code`
- `gemini`
- `antigravity`
- `vs-codium`
- `qwen`
- `zai-glm`
- `kimi`
- `github-copilot`

Some runtimes do not have a confirmed native `SKILL.md` auto-loader. For QWEN, Kimi, and Z.AI/GLM, the installer creates a local `skills/skill-creator-v2` folder plus an `AGENTS.md` projection that points the runtime/user to the skill.

## Basic Usage

After installation, ask your agent:

```text
Use skill-creator-v2.

Create a production-grade skill for <workflow>.
It should declare inputs/outputs, dependencies, failure modes, tests, evals, and a final readiness report.
```

For an existing skill:

```text
Use skill-creator-v2.

Improve the existing skill at <path>. Preserve behavior, add production gates, run regression checks, and package the result separately.
```

For a skill group:

```text
Use skill-creator-v2.

Create a skill group for UI intelligence: research references, extract patterns, synthesize design directions, and guard originality.
```

## What To Expect

The output should be more than a single Markdown prompt. A serious result usually includes:

- `SKILL.md`
- `references/`
- `scripts/`
- `assets/`
- `agents/`
- `evals/`
- deterministic validation commands
- a packaging artifact
- a readiness report with evidence and caveats

## Why It Is Different

| Area | Skill Creator V2 | Typical hand-written skill |
| --- | --- | --- |
| Quality gate | Explicit production-ready gate and final review | Often subjective |
| Dependencies | Declared, verified, allowlisted/blocklisted | Often implicit |
| Failures | Closed taxonomy and retry policy | Often vague |
| Evidence | Commands, artifacts, evals, reports | Often not captured |
| Structure | Progressive disclosure | Often one flat prompt |
| Skill groups | Orchestrator-worker contracts | Often unclear boundaries |

## Case Study: UI Intelligence Group

The UI Intelligence group started as a set of design-research skills. Real runs showed that catalog pages and hero screenshots were not enough. The workflow was upgraded to require:

- live destination URLs from award directories
- 3-5 scroll-state screenshots where possible
- public DOM/CSS/font/script metadata
- effect cards that capture principles without copying code, layouts, images, text, SVGs, or unique animations
- originality review before any design handoff
- a feedback loop from failed runs back into the skills themselves

See [case-studies/ui-intelligence.md](case-studies/ui-intelligence.md).

## Documentation

- [English](docs/README.en.md)
- [Russian](docs/README.ru.md)
- [French](docs/README.fr.md)
- [Spanish](docs/README.es.md)
- [German](docs/README.de.md)
- [Chinese](docs/README.zh.md)
- [Korean](docs/README.ko.md)
- [Japanese](docs/README.ja.md)
- [Runtime targets](docs/runtime-targets.md)
- [10/10 rubric](docs/10-10-rubric.md)
- [Eval runtime notes](docs/eval-runtime.md)

## Evidence Status

The package includes deterministic checks and eval fixtures. Prior local validation passed unit tests, lint, meta-evals, behavioral smoke evals, package inspection, and multi-runtime filesystem propagation checks.

Important caveat: a true 10/10 behavioral claim requires broader independent with-skill vs baseline runs across multiple fixtures. This project records that gap instead of hiding it.
