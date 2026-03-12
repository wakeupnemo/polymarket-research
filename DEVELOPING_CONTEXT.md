# Developing Context

## Current Development Focus
- Treat diagnostics and tradability outputs as the active triage boundary for market selection.
- Prioritize artifact hygiene + explicit gating interpretation before expanding simulator complexity.

## Decisions Made In This Chat
- Confirmed that tradability/active-universe implementation already exists in-repo (`build_tradability_report`, CLI wiring, runner script, focused test).
- Confirmed this layer already outputs:
  - `tradability_report_<feature_set_id>.json`
  - `tradability_report_<feature_set_id>_market_summary.csv`
  - `active_universe_<feature_set_id>.csv`
  - `latest_tradability_manifest.json`
- Confirmed maker-markout scaffold modules also already exist and consume the active-universe outputs.
- Decided not to duplicate tradability or maker-markout implementation layers in this step.

## Current Coding Task
- Align project context docs with repository reality so next work is scoped to:
  - repo/artifact hygiene choices,
  - threshold interpretation and gating decisions,
  - active-universe narrowing review,
  - conservative maker-markout refinement (not simulator expansion).

## Implementation Constraints / Assumptions
- Keep diagnostics and feature-set artifacts immutable inputs.
- Keep tradability as reporting/triage (not alpha signal generation).
- Avoid new ingestion, websocket, event-enrichment, stale-anchor, or fair-value scaffolding in this step.

## Immediate Next Steps
- Run diagnostics + tradability on current data if manifests are missing/outdated in the working tree.
- Review keep/watch/exclude counts and common exclusion reasons for threshold calibration decisions.
- Use keep-only active universe as the default scope for the next conservative maker-markout iteration.
