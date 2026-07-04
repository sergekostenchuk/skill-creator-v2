# Expected Platform Smoke Output: Portable Runtimes

The output must classify each target by support tier before claiming support.

Required behavior:

- use `scripts/install_skill.py --target <runtime>` for known targets when available;
- use `--target-path <path>` only for explicit custom roots;
- record dry-run and apply plans separately;
- validate every applied destination with file-count, `SKILL.md` hash, quick validation, and lint;
- mark portable roots as `portable_root_installed` when runtime native discovery is not proven;
- list skipped or stale targets with reasons;
- avoid claiming native OpenCode or VS Codium support unless adapter smoke evidence exists.

The result is accepted only when every target has a support tier, evidence path, and rollback instruction.
