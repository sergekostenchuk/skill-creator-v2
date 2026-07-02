# Eval And Iteration Workflow

This reference preserves the original skill-creator loop.

## Create Evals

Save realistic prompts to `evals/evals.json`:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User task prompt",
      "expected_output": "What success should look like",
      "files": [],
      "expectations": [
        "The output includes evidence for every external claim"
      ]
    }
  ]
}
```

## Run Comparisons

Use a workspace sibling to the skill directory:

```text
<skill-name>-workspace/
└── iteration-1/
    └── eval-001/
        ├── eval_metadata.json
        ├── with_skill/run-1/
        └── without_skill/run-1/
```

For existing-skill improvement, snapshot the old skill and use `old_skill` as the baseline.

When subagents are explicitly authorized, launch with-skill and baseline runs in the same turn. When not authorized, use inline fallback and mark the lower isolation in reports.

## Behavioral Eval Harness

Use the behavioral harness when a release claim depends on whether an independent agent actually applies the skill.

The harness has three layers:

- `prepare_behavioral_evals.py` creates run packets and `executor-prompt.md` files.
- An independent runtime executes the packets. For Codex desktop this can be `multi_agent_v1`; for other environments it can be a CLI or manual runner.
- `record_behavioral_result.py` records actual executor output, then `grade_behavioral_evals.py` grades the recorded output.

Supported configurations:

- `with_skill`: executor receives the candidate skill path.
- `without_skill`: executor receives no candidate skill path and acts as baseline.
- `old_skill`: executor receives an old/baseline skill snapshot when the fixture has one.

Required files:

```text
<workspace>/
└── eval-001-name/
    ├── eval_metadata.json
    ├── with_skill/run-1/
    │   ├── executor-prompt.md
    │   ├── run-record.json
    │   ├── outputs/result.md
    │   ├── outputs/metrics.json
    │   ├── timing.json
    │   └── grading.json
    ├── without_skill/run-1/
    └── diff.md
```

Hard rules:

- A prepared packet is not evidence by itself.
- A missing `outputs/result.md` is a failed behavioral run.
- `inline_fallback` is lower-isolation evidence and must not be counted as independent behavioral proof.
- A 10/10 behavioral claim requires actual `with_skill` and baseline/old-skill outputs, grading, and diff evidence.
- If timing/token metadata is not available from the runtime, record `timing_unavailable` instead of inventing it.

## Grade

Every `grading.json` must use:

```json
{
  "expectations": [
    {
      "text": "Expectation text",
      "passed": true,
      "evidence": "Concrete evidence"
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 0,
    "total": 1,
    "pass_rate": 1.0
  }
}
```

For programmatically checkable expectations, prefer scripts over eyeballing.

## Aggregate And Review

Run:

```bash
python3 scripts/aggregate_benchmark.py <workspace>/iteration-1 --skill-name <skill-name>
python3 eval-viewer/generate_review.py <workspace>/iteration-1 --skill-name <skill-name> --benchmark <workspace>/iteration-1/benchmark.json --static <workspace>/iteration-1/review.html
```

Use the generated review page for human inspection. Do not replace it with custom ad hoc HTML.

## Improve

Improve from evidence:

- failed expectations;
- user feedback;
- benchmark deltas;
- analyzer observations;
- final-review revision instructions.

Avoid overfitting to one prompt. Generalize the root cause and re-run evals when the change affects behavior.
