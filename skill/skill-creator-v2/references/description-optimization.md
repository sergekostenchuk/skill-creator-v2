# Description Optimization

The `description` field is the primary trigger signal for a skill. Optimize it after the skill body is stable.

## Eval Set

Create 16-20 realistic trigger queries:

- 8-10 should-trigger prompts.
- 8-10 should-not-trigger prompts.
- Include near misses, ambiguous phrasing, typos, paths, concrete work context, and adjacent domains.
- Avoid obvious negatives that do not test trigger precision.

## Metrics

Report:

- should-trigger recall
- should-not-trigger precision
- near-miss false positive rate
- train results
- held-out results

Do not select a description from train score alone.

## Loop

Use `scripts/run_loop.py` when `claude` CLI is available:

```bash
python3 -m scripts.run_loop \
  --eval-set <trigger-evals.json> \
  --skill-path <skill-path> \
  --model <model-id> \
  --max-iterations 5 \
  --verbose
```

If the CLI or runtime is unavailable, create the eval set and report that optimization was not run.
