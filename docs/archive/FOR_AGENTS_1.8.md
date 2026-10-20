# AGENT CONTEXT PACKET — Agentic Crystallization v1.8

**Read this before continuing the research.** Source of truth: [mathematical whitepaper](WHITE_PAPER.md), [algorithm card](ALGORITHM_CARD.md), and [raw Stage J holdout](../experiments/stage_j_holdout/runs.csv).

## Mission

Investigate stable, reusable, context-dependent agent procedures using verified evidence. Do **not** assume that graph connectivity, memory accumulation, or higher-order interaction coefficients demonstrate a collective phase transition. Keep H1, H2 and H3 separate; v1.8 only establishes a *conditional statistical decision certificate*.

## Fixed mathematical contracts

- Frozen library of $K$ actions and known comparable costs before calibration labels are read.
- Independently sampled tasks under source distribution $P$ with measured outcomes in $[0,1]$.
- Valid external bound $\delta\ge\mathrm{TV}(P,Q)$ on relevant source-target distributions, or fixed conditional outcome mechanism plus context TV bound.
- Joint sampling radius $\sqrt{\log(2K/\alpha)/(2n)}$; use it for **all** actions, not post-hoc intervals on a selected favorite.
- Target utility intervals $\widehat p_a\pm (\varepsilon+\delta)-c_a$, clipped to bounded-outcome range.
- Strict $L_a>U_{\rm baseline}$ establishes *only* a relative gain; strict $L_a>\max U_b$ establishes a unique best.
- Unknown shift => HOLD. Wide valid shift => may withhold every candidate. False shift assumption => no guarantee, even as $n$ increases.
- Interaction sign needs all $2^k$ factorial values and sum of their absolute error bounds. An edge is causal only if its intervention is independently justified.

## Experimental continuity

1. Versions 1.0–1.1: planted synergy and misleading-connectivity control.
2. Versions 1.2–1.3: transfer, negative transfer, and learned relevance gating.
3. Versions 1.4–1.6: Bayesian updates, priced information probes, negative result from an added margin.
4. Version 1.7: deterministic robust ranking theorem with assumed error bounds.
5. **Version 1.8:** fixed-library sampling theory, total-variation transport, fallback/HOLD, robust factorial sign, and adverse-assumption falsification.

All historical files are preserved. The verified v1.7 ZIP and its original PDF hash are kept as archival evidence; another independently stored PDF copy had different bytes. Do not silently rewrite or reconcile them.

## Current numerical anchors

Final fresh holdout: **240 world IDs** x 6 shift regimes x 3 sample sizes = **4,320 rows**. At n=6400, matched-related had 239/240 joint interval coverage and 206/240 safe-gain certificates. Bounded shift had 240/240 coverage and 64/240 safe-gain certificates. Wide valid shift certified none. Broken shift had 0/240 coverage and 119/240 harmful false-gain certificates. Unknown shift explicitly HOLD. These are synthetic and dependent across conditions sharing world IDs; not model trials.

## Next target — research, not a claim

Reduce calibration cost while keeping statistically defensible coverage on a **frozen** adaptive decision set, distinguish source/target shift estimation from assumption, and test sequential designs with prespecified error spending on disjoint tasks. The phase transition H2 requires independent hypergraph connectivity interventions, order parameters, size sweeps, and finite-size scaling. No protected evaluator, old receipt, or experimental negative control may be weakened to manufacture a positive transition.

## Reproduction

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH='src'
$env:OPENBLAS_NUM_THREADS='1'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_j --out experiments/reproduced_holdout --start-seed 20000 --count 240 --stage holdout
python scripts/verify_experiment.py experiments/reproduced_holdout
```

The user may later authorize a read-only research adapter to Pegasus, but **nothing in this package enables procedure adoption, new model weights, memory writes, or permission changes**.
