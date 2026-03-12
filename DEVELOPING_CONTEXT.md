# Developing Context

## Current Development Focus
- The missing diagnostics delta has been resolved in repo reality: the diagnostics layer already exists, is wired into the CLI, and runs successfully on the Debian server.
- Current focus has shifted from diagnostics implementation to:
  - interpreting diagnostics outputs,
  - keeping repo hygiene clean,
  - deciding what generated artifacts should be committed,
  - and identifying the next smallest research delta.

## Decisions Made In This Chat
- Do not add more ingestion, more feature-builder scaffolding, or a new smoke experiment.
- Inspect local repo reality first before proposing changes.
- GitHub `main` already contained:
  - `src/pmre/reporting/build_feature_diagnostics.py`
  - diagnostics CLI wiring in `src/pmre/cli.py`
  - `scripts/run_build_feature_diagnostics.sh`
  - `tests/test_build_feature_diagnostics.py`
- The Debian server matched those targeted diagnostics files locally; no extra diagnostics code patch was needed.
- The diagnostics job was run successfully against the current stable feature-set manifest.
- The diagnostics layer produced all expected outputs:
  - diagnostics JSON
  - market-summary CSV
  - latest diagnostics manifest
- Validation passed:
  - `tests/test_build_feature_diagnostics.py`
  - focused feature + diagnostics test slice
  - broader feature/smoke test slice

## Current Coding Task
- No new diagnostics implementation is required immediately.
- Current coding/repo task is:
  - remove `__pycache__` / `.pyc` junk,
  - inspect local generated artifacts intentionally,
  - rebase local `main` before pushing,
  - and decide whether diagnostics outputs or only feature/freeze artifacts should be committed.
- Current research task is:
  - inspect diagnostics results,
  - decide whether stale/repeated-hash behavior should drive gating or triage,
  - and choose the next minimal delta accordingly.

## Current Runtime Reality
- Latest stable feature-set manifest points to freeze `20260311T214230Z__20260312T175753Z`.
- Latest feature-set row count is `60`.
- Latest diagnostics run succeeded and reported:
  - `stale_row_count = 26`
  - `stale_row_fraction = 0.43333333333333335`
  - `missing_spread_count = 0`
  - `non_positive_spread_count = 0`
  - `wide_spread_count = 0`
  - `zero_or_empty_top_size_count = 0`
  - `null_imbalance_count = 0`
  - `null_microprice_count = 0`
  - `repeated_hash_row_count = 26`

## Implementation Constraints / Assumptions
- Smallest meaningful next step only.
- Do not duplicate work already present in GitHub.
- GitHub is the source of truth for code.
- ChatGPT Project files are persistent context; do not assume they exist in the Debian checkout.
- Keep diagnostics as a dedicated reporting layer on top of the stable feature pipeline unless there is a strong reason to fold anything into core feature generation.
- Current local branch state observed in this chat: `main...origin/main [ahead 1, behind 2]`; rebase before push.
