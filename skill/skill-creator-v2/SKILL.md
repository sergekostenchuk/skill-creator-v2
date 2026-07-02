---
name: skill-creator-v2
description: Create, improve, evaluate, harden, and package production-grade Codex/Claude skills and skill groups. Use when the user wants to turn a workflow into a reusable skill, upgrade an existing skill, create multiple coordinated skills, design orchestrator-worker systems, run skill evals or benchmarks, verify tool/MCP dependencies, harden dependency install policy, optimize a skill description for triggering, or produce an evidence-backed delivery report. Also use for lightweight "vibe" skill drafting when the user explicitly wants less process.
---

# Skill Creator V2

This skill creates skills like small production systems: scoped, testable, honest about dependencies, and easy to improve. It preserves the original skill-creator eval loop while adding production gates for tool reality, failure modes, retry limits, evidence, dependency safety, and final review.

## Classify The Request

Pick the smallest mode that satisfies the user:

- `vibe`: the user explicitly wants a lightweight draft or says to skip formal evals.
- `single-skill`: one self-contained capability.
- `existing-skill-improvement`: upgrade or repair an existing skill.
- `skill-group`: multiple related skills with shared references or state.
- `orchestrator-worker`: one coordinating skill delegates to worker skills or subagents.
- `eval-benchmark`: run or improve evals, benchmarks, grading, viewer output, or feedback loops.
- `description-optimization`: improve frontmatter description trigger precision/recall.
- `package-report`: validate, package, and report a completed skill.

If the request is ambiguous, start as `single-skill` unless dependencies, shared state, or parallel work make `skill-group` or `orchestrator-worker` more truthful.

## Reference Routing

Read only the references needed for the selected mode:

| Mode | Read |
| --- | --- |
| all production work | `references/production-skill-architecture.md`, `references/failure-modes.md` |
| external tools, MCPs, APIs, packages | `references/tool-verification.md` |
| external-source research, live sites, current facts, screenshots, citations, or recommendations | `references/external-source-evidence.md` |
| skill groups or delegated workers | `references/orchestrator-worker-contract.md` |
| evals, benchmark, feedback loop | `references/eval-and-iteration.md`, `references/schemas.md` |
| trigger description optimization | `references/description-optimization.md` |
| final packaging/release | `references/final-review-gate.md` |

Use bundled scripts for deterministic checks before relying on judgment:

- `scripts/lint_skill.py <skill-path>`
- `scripts/verify_tools.py --deps <deps.json> --available <available.json>`
- `scripts/install_gate.py --name <pkg> --version <version> --allowlist-json references/allowlist.json --blocklist-json references/blocklist.json`
- `scripts/aggregate_benchmark.py <workspace>/iteration-N --skill-name <name>`
- `eval-viewer/generate_review.py <workspace>/iteration-N --skill-name <name> --static <review.html>`
- `scripts/package_skill.py <skill-path> <dist-dir>`
- `scripts/prepare_behavioral_evals.py --skill-path <skill-path> --meta-evals <meta-evals.json> --workspace <workspace>`
- `scripts/record_behavioral_result.py --run-dir <run-dir> < result.md`
- `scripts/grade_behavioral_evals.py --workspace <workspace>`

## Production-Ready Gate

Do not call a generated skill production-ready unless all applicable facts are backed by evidence:

- Inputs, outputs, trigger conditions, and non-goals are explicit.
- Tool/MCP/API/package dependencies are declared and verified, or missing/fallback/manual-approval states are reported.
- Failure modes use a closed taxonomy from `references/failure-modes.md`.
- Retry limits and escalation paths are stated.
- Success claims cite artifacts, command output, generated files, fetched content, or review evidence.
- Evals include realistic prompts and evidence-backed grading where useful.
- Final review score is at least 9/10 or release is blocked with revision instructions.

Unknown dependency safety means `manual_approval_required` or `hard_blocked`, not auto-install. Never auto-approve `latest`, `latest-stable`, unpinned versions, version drift, blocklisted packages, or packages without integrity evidence.

## Workflow

1. Capture intent from the conversation before asking questions. Confirm only gaps that affect scope, dependencies, or success criteria.
2. Choose the request mode and route to the relevant references.
3. Verify tool reality before writing instructions that depend on external tools.
4. Draft or improve the skill using progressive disclosure: concise `SKILL.md`, details in `references/`, deterministic helpers in `scripts/`, templates in `assets/`.
5. Add evals when the output is verifiable or the user wants confidence. Keep vibe mode light when explicitly requested, but disclose skipped checks.
6. Run lint, tool verification, install gate checks, eval aggregation, and viewer generation as applicable.
7. Iterate from evidence: user feedback, grading output, failed assertions, review findings, and benchmark deltas.
8. Before packaging, run the final review gate and produce a delivery report.

## Vibe Mode

If the user explicitly asks to "just draft it", "vibe", or skip formal evaluation:

- Keep the workflow short.
- Still avoid unsafe tool assumptions.
- Do not claim production readiness.
- Report which gates were skipped and what risk remains.

## Eval Discipline

For serious skill creation or improvement, use the eval loop in `references/eval-and-iteration.md`:

- Create realistic prompts in `evals/evals.json`.
- Run with-skill and baseline/old-skill comparisons where the runtime supports isolation.
- Grade assertions with evidence, not impressions.
- Aggregate results into `benchmark.json`.
- Generate the review UI so a human can inspect outputs.
- Improve the skill from feedback and evidence, not from abstract polishing.

When subagent execution is unavailable or not explicitly authorized, use the documented inline fallback and label results as lower-isolation evidence.

For 10/10 behavioral claims, inline fallback is not enough. Prepare behavioral eval packets, run actual independent `with_skill` and baseline/old-skill executors, record their real outputs, and grade those outputs before claiming behavioral correctness.

For external-source skills, do not accept catalog cards, source names, hero-only screenshots, or file existence as final evidence. Use `references/external-source-evidence.md` unless the task is tiny, purely local, or explicitly vibe-mode; in those cases, skip heavy external-source gates and disclose the reduced claim.

## Skill Group And Orchestrator-Worker Rules

For groups and worker systems, read `references/orchestrator-worker-contract.md` before drafting. The output must include:

- Skill or worker boundaries.
- Write zones.
- Dependency/parallelism table.
- Stop rules.
- Completion versus acceptance distinction.
- Independent verification before accepting worker output.

## Final Response Format

When delivering a skill or skill group, report:

- final path and package path
- files created or changed
- tools verified, assumed, missing, fallback, manual-approval-required, and hard-blocked
- checks run and whether they passed
- eval/review score and evidence path
- skipped gates and unresolved risks
- rollback or safe replacement path
