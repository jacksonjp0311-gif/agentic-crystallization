# Agentic Crystallization v1.3
## Learned Relevance Gating, Acquisition Costs, and Negative Transfer

**Status:** Synthetic, deterministic research; no observed critical phase transition, autonomous agent self-improvement, or real-world Pegasus transfer. This paper continues the archived [v1.2 whitepaper](archive/WHITE_PAPER_1.2.md) and preserves the prior experiments.

### Abstract

Version 1.2 established that a fixed search prior could accelerate related-task discovery while harming unrelated-task discovery. Version 1.3 tests whether a simple policy trained on prior worlds can choose when to reuse. We plant two disjoint six-procedure latent families and supply an imperfect binary relatedness cue (80% accurate). A gate is fit using only 1,800 training worlds, then frozen and evaluated on 1,800 new worlds. First-procedure acquisition cost is explicitly charged to all policies. The gate improves over no prior at both 25% and 75% related-task prevalence. Yet at 75% relatedness, always-reuse is better on average than the learned gate. This is evidence of contextual transfer under synthetic assumptions, not a criticality result.

### 1. Research invariants

H0: improvements are attributable to caching, prior exposure, budget, smooth adaptation or fixed procedure value. H1: some procedures have measurable nonadditive value (earlier planted synthetic evidence). H2: controlled dependency structure creates a reproducible nonlinear transition (unestablished). H3: prior validated clusters reduce the cost of subsequent independently verified improvement (only partial synthetic evidence; full end-to-end H3 unestablished).

A receipt of execution is not correctness. A planted oracle is not a learned real-world evaluator. Graph connectivity is not itself adaptive benefit. The model weights, scoring rules, costs and experiment definitions must be kept distinct.

### 2. Mathematics carried forward

For procedure set S and independently evaluated task distribution D, let J(S;D) be expected utility. For disjoint interaction group T, the finite difference is:

\[\Gamma_T(S)=\sum_{A\subseteq T}(-1)^{|T|-|A|}J(S\cup A;D).\]

A pure three-way AND task has \(\Gamma_{ABC}(\varnothing)=1\) and all empty-baseline pairwise coefficients zero. This is a finite-difference identity, not a novel law. A graph-cost hypothesis remains:

\[F(S)=\alpha B(S)+\kappa V(S)-\beta U(S),\]

where B and V are measured coordination and verification costs, and U is measured future utility. No thermodynamic interpretation or universal exponent is assumed.

### 3. New contextual reuse estimand

Let C be a training-visible noisy relevance cue, A in {reuse, independent} the policy decision, and Y the independently evaluated future utility. The gate estimates:

\[\widehat\Delta(c)=\widehat{\mathbb E}[Y(\mathrm{reuse})-Y(\mathrm{independent})\mid C=c].\]

Then \(\pi(c)=\mathrm{reuse}\) if \(\widehat\Delta(c)>0\), otherwise independent. Training and evaluation use disjoint seeds. The rule is not a confidence-calibrated gate and does not update posterior beliefs after failed second-task queries.

The complete measured utility in this synthetic setup is:

\[Y=40\cdot\mathbf1\{\mathrm{second\ target\ found}\}-0.1(Q_1+\min(Q_2,40)),\]

where Q1 is the actual rank of the first validated triple in a shuffled catalog, and Q2 is the rank of the next hidden triple under the selected ordering. Failure after 40 second-task attempts is censored and charged 40 queries; we do not impute uncensored time to discovery. The common first-discovery cost can cancel in paired utility differences, but still matters to end-to-end economics.

### 4. Experimental design

Catalog sizes 12, 15 and 18. Relatedness prevalences 0.25 and 0.75. Two disjoint latent groups of six. An already discovered first triple comes from group A; the second hidden target is a different triple from A if related, or from B if unrelated. Every policy receives the same procedure universe, query budget, candidate shuffle and observation cue. No policy receives the target or true relatedness label except the **oracle_context** upper bound, which is explicitly marked as nondeployable.

Six arms: no prior; cache-only; always reuse; learned gate; random sham prior; oracle-context upper bound. The learned gate uses training seeds 1000–1299 and is frozen before holdout seeds 2000–2299. The holdout contains 300 seeds per catalog size and prevalence, 1,800 independent worlds. An additional 600-world development execution with seeds 1300–1399 is retained separately. All six arms are evaluated on each world, so comparisons are paired.

### 5. Held-out results

| Related prevalence | Gate minus no-prior utility | 95% world-bootstrap interval | Gate minus always-reuse utility | 95% world-bootstrap interval |
|---|---:|---|---:|---|
| 25% | +2.123 | [+1.295, +3.000] | +1.546 | [+0.745, +2.417] |
| 75% | +9.494 | [+8.157, +10.796] | -0.906 | [-1.707, -0.121] |

These are descriptive percentile bootstrap intervals over worlds, not preregistered confirmatory confidence statements. The same learned gate is used across both prevalence conditions, so the benchmark reveals sensitivity to distribution composition. Its decisions are conditioned on a noisy cue, not a learned embedding or semantic task classifier.

### 6. Interpretation and counterexamples

The learned gate chooses independent search for a negative relevance cue and reuse for a positive cue. It improves over no prior in both mixtures. In the low-relatedness condition it also beats indiscriminate reuse. In the high-relatedness condition indiscriminate reuse is better on average: a false-negative cue can cost more than the gate saves by abstaining. This is a concrete counterexample to a universally optimal reuse gate.

A structurally connected procedure graph may remain functionally useless. No graph-size scaling collapse, susceptibility peak, hysteresis, or stable nonlinear threshold was tested here. The synthetic oracle and planted disjoint groups make transfer easier to interpret but limit generality. The first triple is discovered by a prescribed shuffle, not autonomously invented by an agent. The learner fits only a two-cell decision rule and never revises its candidate ranking based on negative oracle feedback. None of this establishes full learning-to-learn.

### 7. Next falsifiable research step

Charge for the whole first-discovery search in all arms (already implemented), then replace the binary cue with graded, partially observable relatedness; introduce posterior updating after failed queries; train a calibrated gate with explicit abstention; compare it against Bayes-optimal and strong adaptive non-graph baselines; and report all outcomes including censoring. Use a frozen development set and newly generated holdout. Investigate structural threshold claims separately through preregistered finite-size sweeps and edge/hyperedge interventions.

### 8. Reproducibility and navigation

Run `PYTHONPATH=src python -m unittest discover -s tests -v` and `PYTHONPATH=src python -m agentic_crystallization.stage_e --out experiments/reproduced_stage_e --start-seed 2000 --count 300` from the package root. On PowerShell set `$env:PYTHONPATH='src'` first. Stage A, B and D code, results and previous papers remain in the package.

[Source](../src/agentic_crystallization/stage_e.py) · [Tests](../tests/test_stage_e.py) · [Manifest](../experiments/stage_e_holdout/manifest.json) · [Raw data](../experiments/stage_e_holdout/runs.csv) · [Analysis](../experiments/stage_e_holdout/analysis.json) · [v1.2 whitepaper](archive/WHITE_PAPER_1.2.md).
