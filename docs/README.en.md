# Skill Creator V2

Skill Creator V2 is a meta-skill for building other AI skills and skill groups with production discipline.

It is useful when you want a skill to be documented, testable, dependency-aware, and honest about evidence instead of being just a prompt that looks finished.

Use it by installing the npm package, copying the skill into your runtime, and asking your agent to create or improve a skill. The skill classifies the request, loads only the needed references, verifies tools and dependencies, runs lint/evals where applicable, and produces a readiness report.

Expected result: a structured package with `SKILL.md`, references, scripts, evals, tests, and an evidence-backed review.

Example: the UI Intelligence group used this process to move from shallow reference collection to live-site evidence, screenshot review, public code/font/effect metadata, originality checks, and feedback loops that improved the skills themselves.
