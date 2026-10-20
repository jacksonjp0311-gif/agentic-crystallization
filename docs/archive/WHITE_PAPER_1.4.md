# Agentic Crystallization v1.4
## Bayesian Evidence Updates and the Value of New Information

**Status:** Reproducible synthetic research. No observed phase transition, universal coherence law, or autonomous Pegasus self-improvement. Earlier code, results, and papers are retained.

## Abstract

Agentic Crystallization studies whether interacting validated procedures can support efficient future adaptation. Versions 1.0–1.3 established useful higher-order interactions in planted synthetic tasks, the insufficiency of graph density, positive and negative transfer, and the limitations of a fixed relevance gate. Version 1.4 introduces a trained conditional target-likelihood model, a Bayesian relatedness posterior, and an optional second noisy cue after eight failed searches. In 1,800 held-out worlds, the online probing policy improves over the static Bayesian policy in the 75%-related mixture but not in the 25%-related mixture. More fundamentally, negative exact-match results alone cannot reorder candidates under a fixed joint prior: they only eliminate tested targets and renormalize the survivors. Thus a useful adaptive computational system must account for the *marginal value and cost of new information*, not merely maximize information acquisition.

## 1. Hypothesis ledger

- **H0:** Ordinary caching, smooth optimization, independent procedure value, or matched Bayesian inference explains the gain.
- **H1:** Some procedure sets have nonadditive utility. Supported by exact finite-difference identities and planted synthetic cases.
- **H2:** Causal dependency structure induces a reproducible nonlinear adaptive phase transition beyond smooth nulls. **Not established.**
- **H3:** Validated clusters improve the discovery of later independently verified improvements in a persistent system. **Not established generally.**

## 2. Mathematical continuity

For a procedure set S and independent task distribution D, let J(S;D) denote expected evaluated utility. For disjoint T, the Möbius finite difference is

\[
\Gamma_T(S)=\sum_{A\subseteq T}(-1)^{|T|-|A|}J(S\cup A;D).
\]

The three-way AND task has a three-way coefficient of one at the empty baseline and pairwise coefficients of zero at that baseline. A proposed engineering potential is

\[
F(S)=\alpha B(S)+\kappa V(S)-\beta U(S),
\]

where B is measured coordination boundary, V is verification/maintenance cost, and U is independently measured future utility. It is **not** thermodynamic free energy. Connectivity, synergy, and learning-to-learn remain distinct quantities.

## 3. New conditional Bayesian model

Let R denote whether the next task belongs to a related latent family, T its hidden target triple, F the first validated triple, and C1 a noisy relatedness cue. From *training-only* labeled synthetic worlds, estimate conditional candidate likelihoods grouped by overlap k = |T intersection F|:

\[
L_r(t\mid F)\approx P(T=t\mid R=r,F),\quad r\in\{0,1\}.
\]

The initial relatedness posterior is

\[
q_0=P(R=1\mid C_1)=\frac{P(C_1\mid R=1)P(R=1)}{\sum_r P(C_1\mid R=r)P(R=r)}.
\]

Candidate probability is the mixture

\[
P(T=t\mid C_1,F)=q_0 L_1(t\mid F)+(1-q_0)L_0(t\mid F).
\]

If an exact-match oracle rejects t, the posterior updates according to

\[
q^+=\frac{q(1-L_1(t\mid F))}{q(1-L_1(t\mid F))+(1-q)(1-L_0(t\mid F))},
\]

where likelihoods are normalized over remaining candidates at the decision point.

**A useful mathematical identity:** With a fixed joint distribution over targets and no observation except exact-match rejection, conditioning on failures removes candidates and renormalizes the others; it does not change their relative posterior ordering. Bayesian elimination alone therefore cannot improve the optimal ranking over one initially sorted using the same prior. A new informative observation *can* change the ranking. This identity is explicitly tested by the no-probe control.

A second cue C2, independently accurate with probability 0.8, becomes available after eight unsuccessful tests and costs one query. The tested rule probes at a fixed point. It is not an optimized value-of-information controller.

## 4. Experimental protocol

- Sizes n in {12,15,18}; two disjoint planted latent groups of six procedures.
- Related-task prevalence 25% or 75%; 40-query second-task budget including any probe.
- Frozen conditional-likelihood training seeds 3000–3399; inherited v1.3 gate trained separately.
- Fresh evaluation seeds 5000–5299: 900 worlds per mixture, 1,800 total.
- Same hidden target, first procedure, candidate universe, initial cue and base ordering for all arms.
- Arms: no prior, always reuse, v1.3 gate, static Bayes, Bayes without probing, Bayes with probing, and an oracle-context heuristic that knows true relatedness. The latter is **not** a globally optimal upper bound.
- Utility = 40 x second-target success minus 0.1 x (first-discovery queries + second-task queries + probe queries).
- Failed searches are right-censored at 40 second-task queries; all spent queries are charged.

The trained conditional likelihood uses labels available in synthetic training, not in real-world unsupervised agent execution. No agent-generated procedure is created or promoted.

## 5. New held-out findings

| Related prevalence | No prior success | Always reuse success | Static Bayes success | Online Bayes success | Online minus static Bayes utility |
|---|---:|---:|---:|---:|---:|
| 25% | 11.1% | 13.1% | 25.4% | 25.3% | -0.069 [-0.718, +0.621] |
| 75% | 8.8% | 33.6% | 33.6% | 35.8% | +0.896 [+0.244, +1.584] |

Intervals are descriptive 95% paired world-bootstrap percentile intervals (2,500 resamples, fixed seed 741), not preregistered confirmatory inference. The online policy exceeds the inherited v1.3 learned gate by +2.785 and +2.589 utility in the low- and high-relatedness mixtures respectively. **However, probing does not beat static Bayes in the low-relatedness mixture.**

The static and no-probe Bayesian arms match exactly, as required by the elimination identity. The second cue can be valuable but can also consume more resources than it saves. No universal probing or coherence threshold follows.

## 6. What this tells us about balancing computation

A plausible next objective is a bounded information-acquisition policy:

\[
a^*(h)=\arg\max_{a\in\{\text{probe},\text{continue},\text{hold}\}}\mathbb E[U\mid h,a]-C(a),
\]

subject to fixed authorization, evidence and execution budgets. This is a **proposed decision rule**, not a proven optimal algorithm. It must estimate the expected *incremental* value of information rather than assume additional reasoning or retrieval always helps.

The result is consistent with conditional reuse: retained knowledge helps when relevant, but can produce negative transfer or wasted probing when the environment changes.

## 7. Limitations and next falsification

All worlds are planted synthetic tasks with an exact-match oracle. Latent family labels are used in training. The generator is shared between training and holdout; only seeds differ. The likelihood model uses a coarse overlap stratum, not a general Bayesian learner. Cue accuracy and timing are fixed. The first triple is discovered through a prescribed shuffle. There is no real Pegasus model execution, no learned hypergraph, no causal finite-size phase-transition sweep, and no full H3 experiment.

**v1.5 target:** Learn a cost-aware *whether-to-probe* decision on training data, include a strong static baseline, degrade cue quality and vary task similarity continuously, and evaluate untouched worlds under equal budgets. Separately test H2 using preregistered causal hyperedge interventions and finite-size scaling. Never infer criticality from a fitted sigmoid alone.

## 8. Reproduction and archive

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m agentic_crystallization.stage_f --out experiments/reproduced_stage_f --start-seed 5000 --count 300
```

On PowerShell, first set `$env:PYTHONPATH='src'`, then run the Python commands. No language-model API is required.

[Source](../src/agentic_crystallization/stage_f.py) · [Tests](../tests/test_stage_f.py) · [Raw results](../experiments/stage_f_holdout/runs.csv) · [Frozen manifest](../experiments/stage_f_holdout/manifest.json) · [v1.3 whitepaper](archive/WHITE_PAPER_1.3.md).

**Scientific integrity:** v1.0–v1.3 results and their limitations are retained; neither synthetic interaction nor conditional transfer establishes a physical phase transition or self-improving agent.
