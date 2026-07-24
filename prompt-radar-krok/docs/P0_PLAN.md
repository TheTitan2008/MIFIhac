# P0 plan: offline batch vertical slice

Scope is limited to the Gate-1 hackathon slice approved in `STRATEGY.md`,
`RED_TEAM.md`, and `DECISION_LOG.md`.

## Deliverable

One deterministic CPU-only command takes the supplied topics workbook through:

1. schema/provenance validation and a split-before-augmentation generator;
2. redaction/quarantine and long-input sketching;
3. multi-axis classification with confidence/abstention;
4. known matching plus one constrained residual discovery path;
5. extractive evidence summary and one sealed-challenge passport;
6. reconciled run-level E0 economics;
7. separate synthetic/manual evaluation, leakage/stability/security checks;
8. DuckDB/Parquet artifacts, a static smoke-test report, and one Streamlit
   dashboard.

## Acceptance checks

- `A32` and all derivatives are absent from dev/catalog/tuning.
- No cross-split exact/near-duplicate leakage.
- Ten aligned stability perturbations and a known-only negative control run.
- Child cost equals run cost; one run equals one business task and at most one
  gross-value contribution; failed/partial/cancelled runs stay in denominators.
- Seeded PII/secrets do not reach persisted artifacts and data-borne
  instructions do not alter configuration.
- 100k-token start/middle/end/injection profiles do not crash and either retain
  intent or abstain with `coverage_warning`.
- A clean offline rerun produces the same deterministic fingerprint.

## Explicitly out of scope

P2/P3 work: product-surface comparison, causal claims, GPU paths, external or
local LLMs, real-time ingestion, MLOps, advanced organizational slices, and
visual polish beyond the single demo dashboard.
