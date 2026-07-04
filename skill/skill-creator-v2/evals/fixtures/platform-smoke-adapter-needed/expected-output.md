# Expected Platform Smoke Output: Adapter-Needed Targets

The output must avoid turning filesystem guesses into support claims.

Required behavior:

- inspect available CLI/config evidence for OpenCode/opencode and VS Codium;
- if native skill discovery is unconfirmed, mark the target `adapter_needed` or `unsupported_for_release`;
- define the adapter artifact shape, such as `AGENTS.md` projection or documented manual import;
- require a smoke test that proves the runtime actually reads the adapter;
- exclude unproven adapter targets from public support claims;
- preserve evidence in a runtime adapter decision report.

The result is accepted only when unverified targets are blocked or explicitly caveated, not silently grouped with validated skill roots.
