# Changelog

## 0.2.1

- Publishes the post-`0.2.0` behavioral grader hardening to npm.
- Updates canonical `release/benchmark.json` to RA-023 evidence: GitHub Actions green, 17 actual behavioral executor outputs, 51/51 assertions passed, package/runtime smoke, and native CLI smoke.
- Adds regression coverage for behavioral grading edge cases around negated group/orchestrator language and trigger-eval labels.
- Records remaining platform caveats honestly: installer/package smoke passed, while native auto-loading is still adapter-dependent for some runtimes.

## 0.2.0

- Adds reproducible pytest runner metadata for staged and public package checks.
- Adds platform-smoke eval fixtures for Codex, portable runtime roots, and adapter-needed targets.
- Adds canonical `benchmark.json` release evidence alongside release readiness reports.
- Fixes safe installer backup collisions when multiple runtime roots contain same-name skill folders.
- Updates local runtime roots through explicit safe installer apply mode with rollback evidence.

## 0.1.0

- Initial public release of `skill-creator-v2`.
- Includes production skill architecture, failure taxonomy, dependency policy, eval loop, behavioral eval helpers, package helper, and final review gate.
- Adds npm installer support for Codex, Claude Code, Gemini, Antigravity, VS Codium, QWEN, Z.AI GLM, Kimi, and GitHub Copilot local runtime roots.
- Includes multilingual documentation and a sanitized UI Intelligence case study.
