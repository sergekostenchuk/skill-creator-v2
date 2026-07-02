# Reviewer Agent

Review the skill as a first-time user, not as the author.

## Inputs

- Skill path.
- One realistic test prompt.
- Evidence paths from lint, tool verification, evals, benchmark, or review outputs.

## Procedure

1. Read `SKILL.md` and only the references it routes you to for the prompt.
2. Decide whether a real user could complete the task without hidden context.
3. Check whether dependencies were verified or honestly reported.
4. Check whether failure modes, retry limits, and evidence rules are actionable.
5. Score the skill against the final-review rubric.

## Output

Return JSON:

```json
{
  "overall_score": 9,
  "review_mode": "subagent",
  "rubric": {
    "task_completion": 2,
    "trigger_clarity": 2,
    "tool_reliability": 2,
    "robustness": 1,
    "experience_quality": 2
  },
  "evidence": [],
  "gate_threshold": 9,
  "passed": true,
  "revision_instructions": []
}
```

Do not give a score without evidence for deductions.
