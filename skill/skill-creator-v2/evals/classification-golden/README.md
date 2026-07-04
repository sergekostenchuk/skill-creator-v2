# Classification Golden Fixtures

These fixtures are regression anchors for the multi-axis taxonomy. They do not execute a model by themselves.

Fixture types:

- `golden`: expected axis tuple for a representative local skill class.
- `negative`: guards against known collapse errors.
- `monotonic_risk`: adding risk-increasing details must not lower risk or keep a fast route.

The deterministic runner in `scripts/run_taxonomy_classification_evals.py` validates fixture shape and invariants.
