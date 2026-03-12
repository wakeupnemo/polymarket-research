# Hypothesis Catalog

## Purpose of This Document

This file is the living catalog of research hypotheses for the Polymarket Research Engine.

Its purpose is to keep the project focused on:
- falsifiable ideas,
- exact data requirements,
- execution-aware testing,
- and explicit status tracking.

A hypothesis belongs here only if it can be tested in a concrete way.

---

## Status Labels

Use the following status labels consistently:

- **untested** — defined clearly, not yet tested
- **in_progress** — data or experiment currently being built or run
- **weak_evidence** — some support, but fragile or likely confounded
- **promising** — survives initial realism well enough to justify expansion
- **invalidated** — failed the relevant test or proved too fragile to matter

Do not use vague labels such as “interesting” or “maybe good.”

---

## Reading Rule

Every hypothesis should be interpreted through three layers:

1. **Raw signal**  
   Is there a pattern in the data at all?

2. **Execution-feasible signal**  
   Could that pattern actually be entered or captured?

3. **Post-cost signal**  
   Does it survive spread, fees, fill uncertainty, and adverse selection?

A hypothesis is not genuinely alive unless it survives all three layers.

---

# Direction 1 — Maker-First Microstructure

## M1 — Narrow-spread stable books allow positive maker EV
**Status:** untested

### Intuition
When spreads are non-trivial but books are stable and not highly toxic, passive quoting may earn positive expected value through spread capture and favorable execution economics.

### Required Data
- normalized best bid / ask state,
- top-of-book and top-level depth,
- trade events,
- quote-relevant book updates,
- time-to-resolution,
- fee / rebate applicability where relevant.

### Required Features
- spread,
- top-of-book depth,
- update intensity,
- aggression burst score,
- markout windows,
- quote lifetime,
- fill proxy.

### Test Design
Simulate posting passive quotes at or near the best touch under conservative queue assumptions, then evaluate fill-adjusted net EV across regime buckets.

### Positive Evidence
- positive net EV under conservative fill assumptions,
- stability across multiple days or liquidity buckets,
- positive results not fully dependent on rebates.

### Negative Evidence
- fills cluster in toxic moments,
- positive spread capture disappears after markout,
- signal survives only under optimistic queue assumptions.

### Likely Confounders
- unmodeled catalyst windows,
- stale book state,
- hidden regime mixing.

### Common False-Positive Trap
Treating every touch interaction as a realistic fill.

### Implementation Cost
Medium

### Research Priority
Highest

### Expected Half-Life if Real
Medium

---

## M2 — Post-burst exhaustion creates safer maker entry
**Status:** untested

### Intuition
After short aggressive-flow bursts, books may temporarily become less toxic before fully repricing, creating a safer maker entry window.

### Required Data
- trade events,
- burst timestamps,
- post-burst book recovery,
- markout windows.

### Required Features
- aggression burst score,
- refill speed,
- spread compression / widening,
- update intensity,
- short-horizon flow imbalance.

### Test Design
Run event studies around aggressive bursts and compare maker EV immediately after the burst versus after a short cooldown period.

### Positive Evidence
- maker EV improves measurably after a defined post-burst delay,
- fill toxicity declines in exhaustion regimes.

### Negative Evidence
- burst aftermath remains strongly toxic,
- no stable difference between immediate and delayed quoting.

### Likely Confounders
- genuine information shocks,
- close-to-resolution repricing,
- liquidity vacuum effects.

### Common False-Positive Trap
Mistaking information-driven repricing for temporary flow exhaustion.

### Implementation Cost
Low

### Research Priority
High

### Expected Half-Life if Real
Medium

---

## M3 — Quote toxicity is predictable from local microstructure
**Status:** untested

### Intuition
Not all maker fills are equal. Some fills arrive in benign conditions; others are exactly the fills a maker should avoid.

### Required Data
- pre-fill book state,
- trade flow,
- post-fill markouts,
- fill simulation output.

### Required Features
- short-horizon trade imbalance,
- update intensity,
- last trade direction,
- local depth imbalance,
- refill asymmetry,
- recent spread state.

### Test Design
Classify simulated fills by pre-fill state and test whether adverse 5-second and 30-second markouts are predictable.

### Positive Evidence
- strong separation between safe-fill and toxic-fill environments,
- clear reduction in adverse markout when a toxicity filter is applied.

### Negative Evidence
- toxicity appears mostly random,
- local microstructure features do not materially improve fill quality.

### Likely Confounders
- omitted catalyst risk,
- hidden data alignment errors,
- lookahead leakage.

### Common False-Positive Trap
Using post-fill information as if it were available at quote placement time.

### Implementation Cost
Medium

### Research Priority
Highest

### Expected Half-Life if Real
Medium to high

---

## M4 — Refill speed predicts maker safety
**Status:** untested

### Intuition
Fast refill after local depletion suggests resilient liquidity; slow refill suggests fragile liquidity and higher maker risk.

### Required Data
- book updates,
- depletion events,
- post-depletion refill paths,
- markouts.

### Required Features
- refill half-life,
- spread recovery time,
- local depth loss,
- update intensity.

### Test Design
Identify touch or near-touch depletion events, measure refill speed, and compare later maker EV across refill-speed buckets.

### Positive Evidence
- maker EV is concentrated in fast-refill regimes,
- refill speed improves toxicity discrimination.

### Negative Evidence
- no reliable relationship between refill speed and later maker outcomes.

### Likely Confounders
- market category,
- time-to-resolution,
- burst regimes.

### Common False-Positive Trap
Treating refill as causal when it is merely correlated with other healthy market conditions.

### Implementation Cost
Low

### Research Priority
High

### Expected Half-Life if Real
Medium

---

## M5 — Imbalance matters only when displayed depth is real and stable
**Status:** untested

### Intuition
Book imbalance in a fake or unstable book is noise. Imbalance may matter only when depth is both meaningful and persistent.

### Required Data
- L2 ladders,
- cancel / update events,
- trade flow,
- local state stability windows.

### Required Features
- top-3 depth imbalance,
- cancel intensity,
- depth persistence,
- spread,
- touch churn.

### Test Design
Test predictive value of imbalance only in stable-depth and stable-spread regimes, then compare against all-market imbalance tests.

### Positive Evidence
- imbalance becomes useful only after stability filters,
- maker or taker outcomes improve materially in stable books only.

### Negative Evidence
- imbalance is weak everywhere,
- or only “works” in thin books.

### Likely Confounders
- near-resolution one-sided markets,
- low-activity periods,
- hidden market closures.

### Common False-Positive Trap
Treating one snapshot of imbalance as meaningful without any persistence filter.

### Implementation Cost
Low

### Research Priority
Medium-high

### Expected Half-Life if Real
Short to medium

---

## M6 — Queue crowding kills top-of-book maker EV
**Status:** untested

### Intuition
Even if the best price looks attractive, a crowded queue can make the fill profile too poor to justify quoting.

### Required Data
- displayed size at quoted level,
- subsequent trade flow through the level,
- local cancellation dynamics,
- quote lifetime.

### Required Features
- estimated queue ahead,
- touch churn,
- expected fill fraction,
- fill latency proxy.

### Test Design
Compare top-of-book posting versus alternative quote placements across queue-ahead buckets using upper and lower fill bounds.

### Positive Evidence
- EV deteriorates materially as queue-ahead grows,
- alternative placement logic becomes preferable in crowded conditions.

### Negative Evidence
- queue-ahead estimate adds little explanatory value,
- top-of-book economics remain unchanged across crowding regimes.

### Likely Confounders
- unknown cancellation ordering,
- unobserved internalization or matching details,
- stale state.

### Common False-Positive Trap
Assuming you are near the front of the queue without evidence.

### Implementation Cost
Medium-high

### Research Priority
High

### Expected Half-Life if Real
Medium

---

## M7 — Fee / rebate overlay flips marginal maker setups positive
**Status:** untested

### Intuition
Some maker setups may be close to flat before fees and meaningfully positive after maker economics are included.

### Required Data
- fee-enabled market identification,
- fee rates or fee assumptions,
- maker simulation output,
- market type metadata.

### Required Features
- raw spread capture,
- net markout,
- fee-adjusted EV,
- rebate scenario overlays.

### Test Design
Measure maker EV before and after fee / rebate adjustment for fee-enabled markets only.

### Positive Evidence
- fee overlay improves marginal maker strategies without being the sole source of edge,
- effect appears in more than one liquid regime.

### Negative Evidence
- fee overlay is too small relative to toxicity,
- signal remains poor even after favorable fee treatment.

### Likely Confounders
- uncertain historical rebate capture,
- over-assuming maker eligibility,
- evolving fee schedule.

### Common False-Positive Trap
Using optimistic rebate assumptions to rescue a bad underlying signal.

### Implementation Cost
Medium

### Research Priority
Medium-high

### Expected Half-Life if Real
Policy-dependent

---

## M8 — Near-resolution liquidity clustering is maker-positive only in quiet-close regimes
**Status:** untested

### Intuition
As resolution nears, activity can rise, but so can informed flow. Maker value may exist only in quiet-close pockets, not in general close-to-resolution trading.

### Required Data
- time-to-resolution,
- live book state,
- trade bursts,
- close-period markouts.

### Required Features
- time-to-resolution bucket,
- update intensity,
- spread,
- realized short-horizon volatility,
- burst score.

### Test Design
Stratify maker EV by time-to-resolution and interaction with activity / burst conditions.

### Positive Evidence
- a narrow quiet-close regime remains maker-positive,
- close-to-resolution is not uniformly toxic.

### Negative Evidence
- close-to-resolution is consistently bad for makers,
- any apparent positive effect vanishes under realistic fill assumptions.

### Likely Confounders
- scheduled catalysts,
- endgame liquidity distortion,
- event-specific information arrival.

### Common False-Positive Trap
Averaging all close periods together and missing the distinction between calm closes and information-driven closes.

### Implementation Cost
Low

### Research Priority
Medium

### Expected Half-Life if Real
Medium

---

# Direction 2 — Crypto Fair-Value

## C1 — A crude fair-value baseline already explains useful variation
**Status:** untested

### Intuition
A rough external probability model may already capture enough structure to make Polymarket deviations informative.

### Required Data
- underlying crypto price,
- contract threshold / barrier,
- time to expiry,
- realized volatility,
- Polymarket executable state.

### Required Features
- moneyness or threshold distance,
- time to expiry,
- realized volatility,
- baseline fair probability,
- midpoint / executable gap to fair value.

### Test Design
Construct a deliberately simple baseline and measure whether residuals between model fair value and Polymarket implied levels contain useful information.

### Positive Evidence
- residuals show structured behavior,
- liquid-market residuals outperform thin-market residuals,
- baseline model materially outperforms random or naïve nulls.

### Negative Evidence
- residuals are dominated by model error,
- no predictive or corrective structure remains after execution filters.

### Likely Confounders
- contract wording differences,
- jump risk,
- bad volatility proxies,
- settlement-rule misparsing.

### Common False-Positive Trap
Assuming model residuals are meaningful before proving the model is at least directionally sane.

### Implementation Cost
Low

### Research Priority
Highest

### Expected Half-Life if Real
Short to medium

---

## C2 — Barrier-touch logic beats terminal-only logic for threshold-style contracts
**Status:** untested

### Intuition
Contracts that care about reaching a level before expiry are path-sensitive. A terminal-only framing may miss the relevant probability structure.

### Required Data
- threshold-style crypto contract definitions,
- underlying price path,
- expiry,
- realized volatility,
- Polymarket implied values.

### Required Features
- barrier distance,
- time to expiry,
- volatility estimate,
- terminal-only fair estimate,
- barrier-touch fair estimate.

### Test Design
Compare simple terminal-style versus simple first-passage / barrier-touch approximations on explanatory power and residual behavior.

### Positive Evidence
- barrier-touch approximation reduces residual error meaningfully,
- residuals become more coherent by contract family.

### Negative Evidence
- no practical improvement over terminal approximation,
- added complexity does not improve research output.

### Likely Confounders
- approximate formula choice,
- jump-driven paths,
- contract-family heterogeneity.

### Common False-Positive Trap
Overfitting barrier formulas until they look better in-sample.

### Implementation Cost
Medium

### Research Priority
High

### Expected Half-Life if Real
Medium

---

## C3 — Fair-value deviations close only in liquid markets
**Status:** untested

### Intuition
Mispricing that appears in dead books is not necessarily tradable. If the fair-value idea is real, it should be strongest where execution is actually possible.

### Required Data
- fair-value residuals,
- spread,
- depth,
- update intensity,
- trade flow,
- executable prices.

### Required Features
- residual size,
- spread,
- top depth,
- liquidity bucket,
- time-to-expiry,
- update intensity.

### Test Design
Measure residual correction or predictive value by liquidity bucket and exclude thin-market wins from the main evaluation.

### Positive Evidence
- liquid-market residuals show more robust signal quality,
- thin-book wins are not driving the result.

### Negative Evidence
- signal appears only in untradeable books,
- signal vanishes once liquidity filters are imposed.

### Likely Confounders
- market selection bias,
- expiry-family differences,
- stale displayed prices.

### Common False-Positive Trap
Treating visually large residuals in sparse markets as evidence of tradable opportunity.

### Implementation Cost
Low

### Research Priority
Highest

### Expected Half-Life if Real
Medium

---

## C4 — Residual direction depends on volatility and momentum regime
**Status:** untested

### Intuition
Polymarket deviations from rough fair value may behave differently in calm versus fast markets, and in trending versus mean-reverting short-horizon conditions.

### Required Data
- fair-value residuals,
- underlying reference prices,
- realized volatility,
- short-horizon momentum measures,
- executable state.

### Required Features
- residual size,
- volatility regime,
- short-horizon momentum sign,
- spread,
- depth,
- time-to-expiry.

### Test Design
Run conditional residual studies by volatility and momentum regime, then test whether regime filters materially improve execution-feasible outcomes.

### Positive Evidence
- residual behavior differs in a stable and interpretable way by regime,
- execution-aware filters outperform raw residual trading.

### Negative Evidence
- regime slicing produces unstable or inconsistent results,
- any effect is too fragile across time splits.

### Likely Confounders
- too many buckets,
- regime instability,
- hidden catalyst windows.

### Common False-Positive Trap
Slicing the data until one regime happens to look good.

### Implementation Cost
Medium

### Research Priority
Medium-high

### Expected Half-Life if Real
Short

---

## C5 — Jump-sensitive periods destroy simple-model usefulness
**Status:** untested

### Intuition
Simple fair-value models are most likely to fail when jump risk or major catalysts dominate price evolution.

### Required Data
- reference price jumps,
- realized short-horizon volatility,
- contract expiry,
- Polymarket state,
- residual behavior across calm and jump periods.

### Required Features
- jump proxy,
- realized volatility regime,
- residual size,
- spread,
- update intensity.

### Test Design
Compare fair-value signal quality in calm regimes versus jump-sensitive or highly active regimes.

### Positive Evidence
- simple-model usefulness is clearly stronger outside jump regimes,
- the project gains a useful “do not trust fair value here” filter.

### Negative Evidence
- no meaningful difference by jump regime,
- or fair-value logic is too weak everywhere.

### Likely Confounders
- bad time alignment,
- underdetected jumps,
- low-quality volatility estimates.

### Common False-Positive Trap
Using future volatility or post-event data to diagnose pre-event tradability.

### Implementation Cost
Low

### Research Priority
High

### Expected Half-Life if Real
Long as a guardrail

---

## C6 — Fair-value residual plus execution filters beats raw residual
**Status:** untested

### Intuition
If crypto fair-value research is useful, it will likely need spread, depth, and state filters to become tradable.

### Required Data
- residual series,
- spread,
- depth,
- update intensity,
- taker and maker simulation assumptions.

### Required Features
- residual size,
- spread,
- depth,
- stale-trade indicator,
- volatility regime,
- liquidity-vacuum score.

### Test Design
Compare unfiltered residual signals against residual signals filtered by execution conditions.

### Positive Evidence
- filtered signal survives while raw residual signal fails,
- filtered signal remains stable across liquid markets.

### Negative Evidence
- execution filters do not meaningfully improve signal quality,
- signal disappears once realistic execution is applied.

### Likely Confounders
- post-selection bias,
- small-sample liquid regimes,
- interaction with stale-display mechanics.

### Common False-Positive Trap
Letting midpoint-based residual improvement masquerade as tradable edge.

### Implementation Cost
Low

### Research Priority
Highest

### Expected Half-Life if Real
Medium

---

# Direction 3 — Displayed-Price / Stale-Anchor

## D1 — Wide-spread stale-display episodes are common enough to matter
**Status:** untested

### Intuition
Before worrying about tradability, the setup must occur often enough in markets that are not completely dead.

### Required Data
- midpoint,
- spread,
- last trade price,
- time since last trade,
- market activity levels.

### Required Features
- displayed-price proxy,
- display gap to midpoint,
- stale last-trade age,
- spread > threshold indicator,
- update intensity.

### Test Design
Measure frequency and duration of stale-display episodes across categories, liquidity buckets, and time-to-resolution buckets.

### Positive Evidence
- stale-display setups occur regularly in at least some tradable markets,
- not all activity is confined to dead books.

### Negative Evidence
- episodes are rare or economically trivial,
- or they occur almost entirely in unusable books.

### Likely Confounders
- incorrect displayed-price proxy,
- missing last-trade updates,
- misclassified inactive markets.

### Common False-Positive Trap
Counting every stale-looking market without checking tradability.

### Implementation Cost
Very low

### Research Priority
Highest precondition

### Expected Half-Life if Real
Medium

---

## D2 — Markets re-anchor toward midpoint after spread compression
**Status:** untested

### Intuition
If the displayed reference moves from stale last trade back toward midpoint-consistent state when spreads normalize, there may be a platform-specific anchor correction process.

### Required Data
- spread path,
- midpoint path,
- displayed-price proxy,
- trade timestamps,
- update intensity.

### Required Features
- display gap,
- spread compression event,
- stale-trade age,
- short-horizon drift / reversion measures.

### Test Design
Run event studies around spread transitions from wide to normal and observe whether subsequent prices or trades move toward midpoint-consistent levels.

### Positive Evidence
- consistent directional re-anchoring after spread compression,
- effect survives conditioning on tradable regimes.

### Negative Evidence
- no stable correction,
- observed movement is inconsistent or too small.

### Likely Confounders
- concurrent real repricing,
- low-liquidity mean reversion,
- time-to-resolution effects.

### Common False-Positive Trap
Mistaking ordinary sparse-book normalization for platform-specific anchor correction.

### Implementation Cost
Low

### Research Priority
High

### Expected Half-Life if Real
Short to medium

---

## D3 — Stale displayed prices attract slower aggressive flow in the display direction
**Status:** untested

### Intuition
Some participants may react to what is displayed rather than what is executable, creating predictable follow-through in the stale display direction.

### Required Data
- displayed-price proxy,
- subsequent trade direction,
- trade size,
- local book state,
- staleness windows.

### Required Features
- display gap sign,
- stale-trade age,
- spread width,
- next aggressive trade sign,
- low-attention proxy.

### Test Design
Condition on stale-display episodes and test whether subsequent aggressive flow is biased in the displayed direction.

### Positive Evidence
- next-trade direction is systematically biased in the display direction after controls,
- effect is stronger in low-attention regimes.

### Negative Evidence
- no directional tendency,
- any effect disappears after conditioning on spread and depth.

### Likely Confounders
- information-driven follow-through,
- general trend continuation,
- low sample size.

### Common False-Positive Trap
Including the same trade that created the stale state in the response window.

### Implementation Cost
Medium

### Research Priority
Medium-high

### Expected Half-Life if Real
Short

---

## D4 — Anchor effects are strongest in low-attention quiet markets
**Status:** untested

### Intuition
If the display effect is behavioral, it should be strongest where participants are less active and market structure is less tightly arbitraged.

### Required Data
- trade counts,
- update intensity,
- spread state,
- displayed-price proxy,
- local book depth.

### Required Features
- low-attention proxy,
- display gap,
- stale age,
- liquidity-vacuum score,
- market activity bucket.

### Test Design
Stratify stale-anchor tests by market activity and compare quiet versus active conditions.

### Positive Evidence
- effect is concentrated in quiet but still tradable markets,
- active markets show much weaker display-driven behavior.

### Negative Evidence
- no meaningful attention interaction,
- or effect appears only in dead books.

### Likely Confounders
- dead-book noise,
- quiet markets being intrinsically untradeable,
- regime misclassification.

### Common False-Positive Trap
Equating “quiet” with “tradable low-attention” when it actually means “inactive and unusable.”

### Implementation Cost
Low

### Research Priority
High

### Expected Half-Life if Real
Short to medium

---

## D5 — Apparent anchor correction disappears after liquidity-vacuum controls
**Status:** untested

### Intuition
A large share of the stale-anchor story may actually be explained by generic sparse-book mechanics rather than a platform-specific display effect.

### Required Data
- display gap,
- spread,
- depth,
- refill behavior,
- update intensity,
- local trade flow.

### Required Features
- liquidity-vacuum score,
- display gap,
- stale age,
- spread width,
- refill speed.

### Test Design
Compare stale-anchor episodes with matched control episodes that have similar liquidity-vacuum conditions but different display-gap states.

### Positive Evidence
- a residual anchor effect remains after vacuum controls.

### Negative Evidence
- apparent effect largely vanishes after controlling for sparse-book conditions.

### Likely Confounders
- imperfect matching,
- omitted catalyst windows,
- noisy stale proxies.

### Common False-Positive Trap
Attributing all sparse-book normalization to UI or display psychology.

### Implementation Cost
Medium

### Research Priority
Highest falsification target

### Expected Half-Life if Real
Long as a diagnostic

---

## D6 — Anchor effects are too small unless the gap exceeds execution cost
**Status:** untested

### Intuition
Even if the effect exists, it may not matter economically after realistic entry and exit assumptions.

### Required Data
- display gap,
- spread,
- depth,
- maker and taker simulation paths,
- fee assumptions.

### Required Features
- display gap to midpoint,
- spread,
- depth,
- gap / spread ratio,
- likely executable side.

### Test Design
Run stale-anchor setups through both maker and taker simulations and test whether the gap survives realistic cost assumptions.

### Positive Evidence
- a subset of large-gap setups survives execution,
- effect remains after conservative cost treatment.

### Negative Evidence
- effect is smaller than one realistic spread-cross or too hard to capture passively.

### Likely Confounders
- queue optimism,
- stale book snapshots,
- noisy exit assumptions.

### Common False-Positive Trap
Counting “re-anchor to midpoint” as realized PnL without a credible execution path.

### Implementation Cost
Low once simulator exists

### Research Priority
Highest

### Expected Half-Life if Real
Short

---

## Cross-Hypothesis Rules

### 1. Thin-book wins do not count as strong evidence
Any result concentrated in dead or nearly dead books should be treated as suspicious until proven executable.

### 2. Midpoint-only results are not enough
A hypothesis cannot be upgraded beyond speculative if its apparent edge exists only on midpoint assumptions.

### 3. Maker and taker paths must be reported separately
Do not compress the hypothesis outcome into a single blended score.

### 4. A hypothesis can survive as a filter even if it fails as a standalone signal
For example:
- fair value may survive only as a guardrail,
- stale-anchor may survive only as a regime condition,
- maker microstructure may survive only in a narrow subset.

### 5. Negative results are valuable
A hypothesis that is invalidated cleanly improves the project.

---

## Current Priority Order

At the current stage, the research priority order is:

1. **Maker-first microstructure**
2. **Crypto fair-value**
3. **Displayed-price / stale-anchor**

This ordering should be updated only when evidence clearly justifies a change.