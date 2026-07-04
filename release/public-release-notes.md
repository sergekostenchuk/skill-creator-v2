# Public Release Notes

## 0.2.1

Version `0.2.1` synchronizes npm with the post-publication GitHub hardening after `0.2.0`.

Included:

- behavioral grader hardening from commit `1d2674d`
- expanded behavioral grader regression tests
- updated canonical `release/benchmark.json` with RA-023 evidence
- GitHub Actions green evidence
- 17 actual behavioral executor outputs with 51/51 assertions passed
- temp-home and npm-tarball installer smoke evidence
- native CLI availability smoke: 7/10 passed locally

Remaining caveats:

- native skill auto-loading is not proven for every client
- Antigravity, QWEN, and Z.AI GLM CLIs were unavailable in the local native smoke environment
- future high-risk generated skills still need their own behavioral eval evidence

## 0.2.0

Version `0.2.0` publishes the RA-021 gap-closed `skill-creator-v2` package as a reusable local AI skill package.

Included:

- bundled `skill-creator-v2`
- reproducible pytest runner metadata
- canonical `benchmark.json` release evidence
- platform-smoke eval fixtures for runtime support claims
- safer installer backups for same-name skill folders across runtime roots
- npm CLI installer
- runtime targets for Codex, Claude Code, Gemini, Antigravity, VS Codium, QWEN, Z.AI GLM, Kimi, and GitHub Copilot
- multilingual documentation
- sanitized UI Intelligence case study
- eval and readiness notes

Excluded:

- local vault files
- `.env`
- npm tokens
- private project contexts
- raw run screenshots
- raw third-party source code
