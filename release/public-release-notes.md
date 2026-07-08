# Public Release Notes

## 0.3.0

Version `0.3.0` adds hybrid skill-group visibility so skill groups do not automatically become many installed skills.

Included:

- `group_layout` decisions: `single_skill`, `single_visible_orchestrator_with_workers`, `multi_skill_group`, and `hybrid_group`
- `group_membership_type` decisions: `merge_into_parent`, `internal_worker`, `reusable_satellite_skill`, and `shared_module`
- internal worker layout using `group/workers/*/WORKER.md`
- validation for `group/workers/registry.json`
- rejection of nested `group/workers/**/SKILL.md`
- reusable satellite skill guidance for capabilities that can live both inside and outside a group
- hybrid group eval coverage through `ME-016` and a VPN internal-worker golden fixture

Evidence:

- staged pytest: `44 passed`
- taxonomy fixtures: `15/15`
- meta-evals inline fallback: `27/27`
- `run_all_checks.py`: `8/8`
- self-diagnostic coverage score: `0.9`

Remaining caveats:

- `ME-016` is a deterministic contract check, not an independent behavioral model execution
- npm publication is not claimed until registry/auth succeeds and `npm view` confirms the new version
- high-risk generated skill groups still need their own behavioral eval evidence

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
