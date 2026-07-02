# Final User-Journey Review Gate

Run this after linting and evals, before packaging.

## Purpose

Per-assertion grading can pass while the whole user journey is confusing. This gate simulates a first-time user relying on the skill end to end.

Files-only completion is not enough. A created file, package, or manifest is rejected unless the review cites executed checks, artifact contents, and evidence that the output satisfies the task.

## Modes

- `subagent`: preferred when the runtime explicitly authorizes independent subagent work.
- `inline_fallback`: same agent performs a separated review pass and labels the weaker isolation honestly.
- `skipped`: allowed only with explicit reason; skipped does not equal passed.

## Rubric

Score each 0-2, total /10:

- Task completion.
- Trigger clarity.
- Tool reliability.
- Robustness.
- Experience quality.

Gate passes only when `overall_score >= 9` and each deduction cites evidence.

## Required Output

Save `review.json`:

```json
{
  "overall_score": 9,
  "review_mode": "inline_fallback",
  "rubric": {
    "task_completion": 2,
    "trigger_clarity": 2,
    "tool_reliability": 2,
    "robustness": 1,
    "experience_quality": 2
  },
  "evidence": [
    "Robustness docked because the missing-tool fixture relies on fallback disclosure rather than a real unavailable MCP run."
  ],
  "gate_threshold": 9,
  "passed": true,
  "revision_instructions": []
}
```

If the score is below 9, do not package as final. Feed revision instructions back into the improvement loop. Stop after 2 final-review revision cycles and report remaining gaps.
