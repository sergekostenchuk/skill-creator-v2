# Expected Platform Smoke Output: Codex

The output must treat Codex as a native runtime target and must not mutate it silently.

Required behavior:

- generate a dry-run install plan with `scripts/install_skill.py --target codex --output <plan.json>`;
- require explicit user approval before adding `--apply`;
- if apply is approved, record the backup path from the installer plan;
- validate the installed target with `quick_validate.py` and `lint_skill.py`;
- compare the installed `SKILL.md` hash with the staged source hash;
- save all plan, validation, hash, and rollback evidence in the release workspace.

The result is accepted only when install evidence exists and the runtime copy matches the selected release candidate, or when the target is explicitly marked skipped with a reason.
