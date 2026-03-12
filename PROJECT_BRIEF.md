# Polymarket Research Engine

## Project Objective

Build a serious research engine for discovering **platform-specific, execution-aware edge** on Polymarket.

This project is **not** about launching a bot quickly, collecting pretty charts, or finding interesting historical patterns that disappear under realistic execution. The purpose is to build the correct research architecture so that:

- raw patterns are separated from executable edge,
- maker and taker logic are kept distinct,
- weak ideas are falsified early,
- realistic constraints are applied before conclusions are made,
- and only robust ideas are promoted into implementation.

The engine should help answer a narrow, practical question:

> Where does apparent Polymarket edge survive realistic execution, fees, spread, fill uncertainty, adverse selection, and market-specific mechanics?

---

## Primary Research Directions

### 1. Maker-first microstructure engine

Investigate whether a **maker-first** framework can produce better research prospects than naïve taker-style prediction market trading.

This direction focuses on:
- spread dynamics,
- top-of-book and local depth behavior,
- refill and resiliency,
- fill probability,
- quote survival,
- adverse selection,
- quote cancellation logic,
- regime detection,
- and the difference between *being filled* and *being filled for the wrong reasons*.

This is the highest-priority direction because it forces execution realism early and is closest to the actual mechanics of a CLOB-style market.

### 2. Crypto fair-value model

Investigate whether crypto-linked Polymarket contracts deviate in a useful way from a rough but honest fair-probability estimate derived from:
- underlying crypto price,
- contract threshold / barrier,
- time to expiry,
- realized volatility,
- and simple regime descriptors.

The goal is not model elegance. The goal is to determine whether an external anchor produces **tradable residuals** once spread, fees, and liquidity are taken seriously.

### 3. Displayed-price anchor / stale-last-trade correction

Investigate whether Polymarket-specific display behavior and stale last trades create temporary distortions that affect slower participants or create predictable re-anchoring dynamics.

This direction is explicitly platform-specific. It should not be collapsed into generic momentum or mean reversion unless the platform-specific component fails to survive falsification.

---

## Research Philosophy

This project operates under the following principles:

- **Truth over excitement**
- **Falsification over storytelling**
- **Execution realism over paper alpha**
- **Learning speed over elegance**
- **Platform-specific insight over generic finance clichés**
- **Smallest meaningful next step over overengineering**
- **Simple baselines before complicated models**
- **Modular architecture before optimization**

The standard for evidence is intentionally high. A signal is not interesting merely because:
- it looks visually compelling,
- it predicts some future price path,
- it works on midpoint,
- or it appears profitable in thin books.

A signal matters only if it remains credible after:
- executable pricing,
- fill uncertainty,
- spread,
- fees,
- partial fills,
- and adverse selection.

---

## Core Constraints

The project must respect the following constraints from the start:

### Execution constraints
- Historical prints are not executable prices.
- Midpoint is not an execution assumption.
- Maker fills are uncertain and queue-sensitive.
- Taker fills depend on actual displayed depth and book walking.
- Partial fills are normal, not edge cases.

### Research constraints
- Maker and taker logic must remain separate.
- Token-level, market-level, event-level, and cross-market logic must not be mixed carelessly.
- Wide-spread and thin markets are dangerous by default.
- Backtests are suspect until execution is modeled honestly.
- Data limitations must be stated explicitly, not hidden.

### Engineering constraints
- Build reusable modules, not one-off scripts.
- Preserve raw data before normalization.
- Version parsers and schemas.
- Make the project easy to update as platform behavior changes.
- Prefer robust infrastructure over elegant but brittle code.

### Modeling constraints
- Do not introduce complicated ML unless simpler baselines clearly fail for the right reasons.
- Do not promote a fancy model when a cheap falsification test can kill the idea first.
- Do not confuse external “fair value” with executable edge.
- Do not treat weak proxies as hard truth without labeling them as such.

---

## What This Project Rejects

The project explicitly moves away from the initial naïve framing based on:
- “cheap vs expensive by history,”
- percentile gimmicks,
- simplistic threshold screens,
- generic TA-style indicators on prediction-market prices,
- and print-based heuristics without executable context.

These ideas are not banned forever, but they are not good enough to serve as the core research framework.

---

## Success Criteria

The first phase of the project is successful if, after roughly two weeks, the following are true:

### Infrastructure success
- The engine can reconstruct a trustworthy executable market-state timeline.
- Market metadata, token mappings, and live orderbook state are normalized correctly.
- Crypto reference data can be aligned to relevant contract families.
- Raw and normalized data pipelines are stable enough for repeated experiments.

### Research success
- At least one direction produces evidence that survives realistic execution assumptions.
- Weak hypotheses are explicitly invalidated rather than quietly ignored.
- The project can distinguish raw signal from execution-feasible signal.
- The simulator is credible enough to kill obviously fake edges.

### Decision success
- The hypothesis set is narrowed from many possibilities to a small shortlist.
- One primary direction is identified for the next implementation sprint.
- The reasons for continuing or killing each direction are written down clearly.
- The next phase is chosen based on evidence, not preference.

---

## Non-Goals

The following are not immediate goals of this phase:

- launching a fully automated production bot,
- building a portfolio optimizer,
- training large ML models,
- searching for broad “alpha” without market-structure grounding,
- or optimizing strategy complexity before signal validity is established.

Those may become relevant later, but only after basic edge credibility is earned.

---

## Standard of Evidence

A hypothesis should only be considered promising if it survives most of the following:

- executable entry/exit assumptions,
- pessimistic or bounded maker fill modeling,
- fee and spread inclusion,
- sensitivity to size,
- walk-forward or later-period testing,
- liquidity-bucket stratification,
- time-to-resolution stratification,
- and at least one meaningful negative control.

Anything weaker should remain classified as speculative.

---

## Project Outcome We Are Actually Optimizing For

The real objective is not “find a strategy quickly.”

The real objective is:

- build the correct research architecture,
- identify the few hypotheses worth testing,
- implement only what has high information value,
- separate alpha from execution illusion,
- and iteratively turn promising research into robust implementation.

That is the standard this project should preserve in every future update.