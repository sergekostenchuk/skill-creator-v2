# Runtime Targets

The npm installer copies the bundled `skill-creator-v2` folder into local runtime skill roots.

```bash
skill-creator-v2 install --target codex
skill-creator-v2 install --target claude-code
skill-creator-v2 install --target gemini
skill-creator-v2 install --target antigravity
skill-creator-v2 install --target vs-codium
skill-creator-v2 install --target qwen
skill-creator-v2 install --target zai-glm
skill-creator-v2 install --target kimi
skill-creator-v2 install --target github-copilot
```

`--all` installs all targets.

`--dry-run` shows the planned writes without copying files.

QWEN, Kimi, and Z.AI/GLM receive a portable `AGENTS.md` projection because native `SKILL.md` auto-discovery may differ by runtime version.
