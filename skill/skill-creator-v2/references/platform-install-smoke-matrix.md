# Platform Install And Smoke Matrix

Use this reference when preparing cross-runtime installation or publication claims.

## Support Tiers

| Tier | Meaning |
| --- | --- |
| `validated_static_current` | Folder exists, quick validation and lint pass, and installed `SKILL.md` matches the current staged source. |
| `validated_static_stale` | Folder exists and static checks pass, but the installed copy does not match the current staged source. |
| `installed_but_static_failed` | Folder exists, but quick validation or lint fails. |
| `installed_only` | Folder exists but smoke checks were not run. Do not call this runtime support. |
| `format_adapter_needed` | Runtime exists, but the skill-folder contract or invocation path is not confirmed. |
| `blocked` | Expected root or invocation is missing. |
| `not_supported` | Runtime has no compatible skill mechanism. |

## RA-020 Matrix Summary

Evidence artifact for the current project is stored in the RA-020 workbench as `platform-smoke-matrix.json`. Public/runtime packages must not hard-code local absolute paths.

Current result:

- `validated_static_stale`: 15 runtime copies
- `format_adapter_needed`: VS Codium discovery, OpenCode/opencode
- `blocked`: expected VS Codium skill-folder path

Important interpretation:

- Static validation is not runtime behavior proof.
- Stale copies must not be presented as current RA-020 installs.
- OpenCode/opencode is installed as a CLI, but no native skill-folder root was discovered in local config/data roots.
- VS Codium exists locally, but no skill-root contract was discovered.
- Safe install mode must run before any runtime root is updated.

## Minimum Smoke Evidence Per Target

For each target, record:

- platform name;
- install/root path;
- expected package format;
- exact smoke command or blocker;
- `quick_validate` result when a skill folder exists;
- `lint_skill` result when a skill folder exists;
- whether installed `SKILL.md` matches current staging;
- support tier;
- caveat.

Never claim a platform is validated only because a folder exists.
