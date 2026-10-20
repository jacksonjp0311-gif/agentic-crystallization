---
title: "Agentic Crystallization v1.8"
subtitle: "Simultaneous Calibration, Distributional Stability, and Conditional Procedure Certification"
author: "Agentic Crystallization — Open Research Program"
date: "13 October 2026"
abstract: |
  This paper closes an important gap between deterministic decision-stability
  theorems and finite-sample adaptive-agent evidence. It derives simultaneous
  error intervals for a frozen library of procedures, transports those intervals
  across a *justified* total-variation shift bound, and certifies either a
  unique optimal procedure or a strict improvement over a named baseline.
  An explicit factorial version bounds the sign of higher-order interactions.
  A new 4,320-row synthetic holdout explores calibrated, wide, violated, and
  unavailable distribution-shift assumptions. The findings support conditional
  decision-stability claims, not a physical phase transition, autonomous
  adaptation, or a demonstrated Pegasus improvement.
---

# Research objective and why it matters

Agentic Crystallization is a falsifiable investigation of whether independently validated agent procedures develop collectively useful interactions, persist as reliable structures, and reduce the cost of subsequent adaptation. The physical crystallization analogy is **structural**, not a claim that software is governed by new forces or obeys a thermodynamic nucleation law. The research asks an engineering question: *what information, evidence, and uncertainty conditions would let us call an adaptive procedure structure stable?*

Versions 1.0–1.7 isolated different parts of the question. Planted higher-order procedure combinations produced synthetic gains that independent scoring missed (H1); dense but noncausal connectivity did not deliver the same benefit; retained knowledge helped related tasks and hurt unrelated ones; Bayesian relevance and value-of-information policies were conditionally useful; and v1.7 proved robust action-ranking statements **assuming** correct simultaneous deterministic value-error bounds.

**Version 1.8 turns those previously assumed error bounds into a statistical calibration contract**, while preserving an explicit HOLD when the distribution shift cannot be bounded. It does not infer a new physical phase transition. Neither the new analysis nor its simulator interacts with live Pegasus agents, learned model weights, private memory, or Genome promotions.

## The hypothesis ladder

| Claim | Meaning | Evidence status at v1.8 |
|---|---|---|
| H0 | Additive benefits, caching, smooth optimization, amortization, and cost explain outcomes | Remains a live alternative |
| H1 | Some procedure combinations have non-additive expected value | Planted synthetic examples and controlled estimands only |
| H2 | Functional connectivity causes a reproducible nonlinear adaptive transition beyond smooth alternatives | **Not demonstrated** |
| H3 | Existing validated clusters lower the cost of later independently verified improvements | Restricted synthetic conditional transfer; **general claim not demonstrated** |
| C1 | Finite-sample procedure choices can be conditionally certified under known sampling and shift assumptions | Theorem + new synthetic checks |
| C2 | A certificate remains reliable when the shift assumption is false or unavailable | **Refuted**; the software explicitly holds when unavailable |

# Mathematical structure retained from previous versions

Let a bounded set of agent procedures be $P$, with active combination $S\subseteq P$, evaluation distribution $\mathcal D$, and independently scored expected task utility

$$
J(S;\mathcal D)=\mathbb E_{x\sim \mathcal D}[U(x,S)].
$$

For a set of interacting procedures $T$, disjoint from baseline $S$, its finite-difference/Möbius interaction is

$$
\Gamma_T(S)=\sum_{B\subseteq T}(-1)^{|T|-|B|}J(S\cup B;\mathcal D).
$$

A pure three-way AND dependency has $\Gamma_{\{a,b,c\}}(\varnothing)=1$ with every empty-baseline pairwise coefficient zero. This is **standard algebra**; it reveals why pairwise screening can miss collective utility, not an independently discovered law. Interaction coefficients are contextual: changing $\mathcal D$, the baseline set, cost, or action semantics can change their values and signs.

A graph-oriented *engineering cost potential* remains a candidate model:

$$
F(S)=\alpha B(S)+\kappa V(S)-\beta U(S),
$$

where $B$ is measured coordination/boundary cost, $V$ is verification/maintenance cost, and $U$ is measured future utility in compatible units. This is **not thermodynamic free energy**. A graph's connected-component size and an agent's adaptation efficiency must be reported separately; neither is a reliable proxy for the other. Version 1.8 does **not** fit this potential, run a percolation experiment, or demonstrate nucleation.

# The new uncertainty contract

Consider a **fixed, finite, authorized** library $\mathcal A$ of $K$ actions representing named procedure combinations. A known action cost $c_a\in[0,1]$ is expressed in the same utility units as a bounded task outcome $Y_a\in[0,1]$. On $n$ calibration tasks $x_1,\dots,x_n$ sampled i.i.d. from a source distribution $P$, each action is observed, with calibrated mean

$$
\widehat p_a=\frac1n\sum_{i=1}^{n}Y_a(x_i),\qquad \widehat Q_a=\widehat p_a-c_a.
$$

Paired observations across actions may be correlated; **independence across actions is not required**. Independence of tasks within the calibration sample is required. It is also required that the library, evaluator, task outcomes, and costs be fixed before using this sample to certify the selected actions.

For a target distribution $Q$, assume one of the following:

1. The relevant joint task/outcome distributions are bounded by $\operatorname{TV}(P,Q)\le\delta$, or
2. The marginal task-context distributions obey that bound **and** every procedure's conditional outcome mechanism $P(Y_a\mid x)$ is invariant between environments.

The number $\delta$ must come from an independently justified constraint or external evidence. An LLM's verbal confidence, a similarity score, and an arbitrary guessed shift allowance do **not** establish it. If $\delta$ is unavailable, the software must report **HOLD / uncertifiable**, not silently substitute zero.

## Theorem 1 — Simultaneous finite-sample concentration

Fix the library $\mathcal A$ before calibration, choose a nominal error level $0<\alpha<1$, and define

$$
\boxed{\varepsilon_{n,K,\alpha}=\sqrt{\frac{\log(2K/\alpha)}{2n}}.}
$$

Then, using Hoeffding's inequality and a union bound,

$$
\Pr\!\left(\forall a\in\mathcal A:\left|\widehat p_a-\mathbb E_P Y_a\right|\le\varepsilon_{n,K,\alpha}\right)\ge 1-\alpha.
$$

**Proof.** Since $Y_a\in[0,1]$, Hoeffding gives $\Pr(|\widehat p_a-\mathbb E_PY_a|>\varepsilon)\le 2e^{-2n\varepsilon^2}$. Summing the probabilities across $K$ fixed actions bounds the probability of *any* failure by $2K e^{-2n\varepsilon^2}$. Substitution of the stated radius yields $\alpha$. Correlation between different actions does not affect the union bound. $\square$

The guarantee is **per predeclared comparison experiment**, not a guarantee of zero mistakes across thousands of independent comparisons. For a planned sequence of comparisons, conservative error spending such as $\alpha_t=\alpha_{\mathrm{total}}/[t(t+1)]$ controls their aggregate error by the union bound **only while each constituent confidence statement remains valid**. Repeatedly inventing new candidates using the same calibration set invalidates the fixed-library premise.

## Theorem 2 — Distributional transport and robust intervals

Under the above total-variation assumption, a fixed bounded outcome satisfies

$$
\left|\mathbb E_QY_a-\mathbb E_PY_a\right|\le\delta.
$$

This follows from the variational characterization of total variation, or the layer-cake representation of $f\in[0,1]$. Combining the bound with Theorem 1 gives simultaneous target-domain net-utility intervals

$$
\boxed{L_a=\max\{0,\widehat p_a-\varepsilon-\delta\}-c_a,}
$$
$$
\boxed{U_a=\min\{1,\widehat p_a+\varepsilon+\delta\}-c_a.}
$$

With probability at least $1-\alpha$, **all** true target-domain net utilities $Q_Q(a)=\mathbb E_QY_a-c_a$ lie in $[L_a,U_a]$, conditional on a correct, predeclared shift bound.

The equal-cost bounded Bernoulli model is intentionally restrictive. It is not a certificate for arbitrary token cost, changing model quality, unsupported interventions, nonstationary reward functions, or unevaluated adaptive procedure libraries.

## Theorem 3 — Stable ranking and certified gain

If one estimated winner $a^*$ satisfies

$$
\boxed{L_{a^*}>\max_{b\in\mathcal A\setminus\{a^*\}}U_b,}
$$

then $a^*$ is the **unique target-domain expected-net-utility maximizer** on the joint coverage event. This is the v1.7 robust-margin argument applied to statistically justified intervals.

A weaker, often more useful statement is **safe improvement over a named baseline $a_0$**. If for a candidate $a$,

$$
\boxed{L_a>U_{a_0},}
$$

then $Q_Q(a)>Q_Q(a_0)$ on the same coverage event. This **does not prove $a$ is globally optimal**. A controller may select the candidate with the highest lower bound among those certifiably beating $a_0$, or retain $a_0$ when none qualifies. The former is certified relative improvement; the latter is simply fallback, **not an optimality certificate**.

This establishes a compact selection rule, here called **CrystalGuard-1.8**:

1. Load a predeclared, permission-eligible procedure library and independently measured costs.
2. Acquire an independent calibration sample and determine whether the target/source shift bound is justified.
3. Calculate simultaneous intervals using the *same* $\alpha$, $n$, and $\delta$ across all actions.
4. If one procedure dominates every other interval, return **certified best**.
5. Otherwise, if a procedure's lower bound dominates the baseline's upper bound, return **certified improvement over baseline**.
6. Otherwise, keep the named baseline without claiming optimality; if the bound is unavailable, report **HOLD**.

This is a research decision core, not a live Pegasus adapter or permission authority. An admitted procedure is not automatically an approved instruction.

## Theorem 4 — Robust higher-order interaction sign

Suppose the fixed factorial family contains **all** $2^k$ procedure subsets of a predeclared group $T$ of size $k$. Each subset has a simultaneously valid net-utility error bound $e_B$. Then

$$
\left|\widehat\Gamma_T-\Gamma_T\right|
\le \sum_{B\subseteq T}e_B.
$$

For uniform calibrated errors $e_B\le\varepsilon_{n,2^k,\alpha}+\delta$,

$$
\boxed{\left|\widehat\Gamma_T-\Gamma_T\right|\le 2^k(\varepsilon_{n,2^k,\alpha}+\delta).}
$$

The proof is the triangle inequality applied to the alternating finite difference. Thus a **positive sign** is certified only if $\widehat\Gamma_T$ exceeds the full error radius; a negative sign requires $\widehat\Gamma_T$ below its negative. Neither sign certifies causal dependencies without controlled interventions, nor does it bound omitted higher-order terms when a truncated model is used. The error grows exponentially in interaction order, creating a real verification cost for purportedly collective knowledge.

## Proposition — No universal certificate under unbounded drift

If no relationship constrains the target distribution $Q$ relative to observed calibration distribution $P$, then even **infinitely many source observations** cannot certify the best target procedure for all possible targets. For example, two actions can be indistinguishable on the only context occurring under $P$, yet have opposite outcomes on an unobserved context where $Q$ concentrates. Either action can become optimal under a target consistent with the same source data. A universally valid, nontrivial source-only ranking certificate is therefore impossible without further assumptions or observations of the target. This is an identifiability limitation, not a failure of numerical optimization.

# Stage J — Reproducible calibration and shift-stress experiment

The experiment is deterministic given the committed code and manifest, but its outcomes arise from seeded stochastic task generation. We froze the Stage J source/parameter record before creating the final held-out worlds. A prior exploratory run is retained separately and **not represented as untouched holdout**.

## Simulation environment and interventions

A frozen catalog contains nine procedures: an empty baseline, all seven nonempty subsets of $\{a,b,c\}$, and a separate procedure $d$. Every procedure is evaluated on the *same* $n$ independent calibration task contexts, with binary success and fixed additive costs. There are four planted families: additive, pairwise-complementary, three-way-complementary, and dense-but-noncausal-metadata. The oracle retains exact target-domain expected utilities and three-way interaction values solely for grading. Neither the candidate selector nor its confidence algorithm sees those target truths.

Within each world, context $z\in\{0,1\}$ determines procedure success probabilities. The source has $P(z=1)=p$, and the target has $Q(z=1)=q$. Conditional outcome probabilities given $z$ are kept unchanged. Consequently the exact task-distribution total variation is $|p-q|$; these are particularly favorable conditions for Theorem 2, not a general way to infer drift on real agents.

| Scenario | $p$ | $q$ | Declared $\delta$ | Contract interpretation |
|---|---:|---:|---:|---|
| `iid_related` | .10 | .10 | 0 | Matched, procedure-cluster-favorable context |
| `iid_unrelated` | .85 | .85 | 0 | Matched, different preferred procedure |
| `bounded_shift` | .10 | .18 | .08 | Correctly bounded moderate shift |
| `wide_valid_shift` | .10 | .45 | .35 | Correctly bounded but too uncertain to certify |
| `violated_shift` | .10 | .92 | .05 | **Deliberately false** shift assertion; actual TV .82 |
| `unknown_shift` | .10 | .18 | unavailable | Controller must return HOLD |

Calibration sizes are $n=200,1000,6400$ independent task contexts **per world**, each observed for all nine actions. The final held-out set has 240 world seeds (`20000..20239`), each evaluated in all six regimes and three sample sizes: **4,320 distinct world/condition rows**. The preceding development cohort used 200 different seeds (`4000..4199`). Earlier exploratory results that informed this investigation remain identified as exploratory. The fixed random generator and no-model requirement are recorded in each run manifest.

The run evaluates (i) empirical joint coverage, (ii) rate of certificates for unique best and for baseline improvement, (iii) incorrectly certified choices, (iv) harm relative to baseline, (v) mean oracle regret, (vi) higher-order sign certificates, and (vii) calibration demand measured as the count of independent binary observations. Descriptive world-bootstrap intervals are presented in the JSON summaries; these are not separate distribution-free guarantees.

## Main holdout findings

The following table reports the **largest calibration size** $n=6400$, with **240 worlds per scenario**. The full data include every sample size and original record.

| Shift scenario | Observed joint interval coverage | Certified unique best | Certified baseline gain | Wrong best certificates | Harmful gain certificates |
|---|---:|---:|---:|---:|---:|
| Matched related | 239/240 | 60/240 | 206/240 | 0 | 0 |
| Matched unrelated | 240/240 | 240/240 | 240/240 | 0 | 0 |
| Correctly bounded shift | 240/240 | 60/240 | 64/240 | 0 | 0 |
| Wide but valid shift | 240/240 | 0 | 0 | 0 | 0 |
| Deliberately violated bound | **0/240** | 60/240 | 119/240 | **60** | **119** |
| Unknown shift | **HOLD** | 0 | 0 | Not asserted | Not asserted |

![Fraction of decisions certified as improving on baseline](../assets/stage_j_certified_gain.png){width=94%}

![Broken assumptions make precise but false certificates](../assets/stage_j_assumption_failure.png){width=94%}

**Positive:** With correctly bounded source-to-target shift, the simulated decision certificate made no false certified decisions in this cohort. This is compatible with the derived guarantee but does not establish that the real-world assumptions can be verified. As more observations arrived in matched environments, a larger fraction of actions passed the proof's separation requirement.

**Negative:** An honest but wide shift allowance caused **zero** gain certificates even after 6,400 calibration tasks per action. Formal caution can be computationally expensive and offer little usable improvement. The conservative algorithm also sacrificed nominal mean utility relative to point-estimate greedy selection in several valid regimes; its objective was conditional safety, not maximization of mean measured gain.

**Falsification stress test:** When the declared shift allowance was knowingly wrong, the reported intervals missed the target values in **all 240 worlds** at $n=6400$. There were **60 falsely certified unique-best decisions** and **119 procedures falsely certified as gains that were actually worse than the baseline**. Increasing $n$ narrowed sampling error but could not correct an incorrect domain-shift assumption. The software records the failure instead of calling it self-organization.

## Certifying three-way complementarity

The simulator plants exactly 60 three-way-dependency worlds in each scenario/size cohort; additive and misleading-connectivity worlds contain no genuine three-way term. At $n=6400$ under the matched related regime, all **60 of those planted positive triple interactions** had sufficient calibration to certify their sign. Under correctly bounded moderate shift, no triple signs were certified because the $2^3\delta$ error allowance overwhelmed the expected interaction magnitude.

![Sign certification for the planted three-way interactions](../assets/stage_j_mobius_certification.png){width=94%}

This demonstrates both the utility and the conservatism of a factorial uncertainty certificate. It does **not** identify a causal edge through intervention, establish new mathematical synergy theory, or demonstrate any phase threshold.

# Implications for an adaptive agent runtime

The mathematically stable claim is now **conditional** and explicit: *given a fixed action library, independently evaluated bounded rewards, a legitimate simultaneous sampling guarantee, fixed comparable costs, and a valid target-domain shift bound, Pegasus could in principle make a provably safe relative-procedure choice*. None of these assumptions can be inferred merely from a valid execution receipt or model-generated confidence.

A practical future research adapter would read only admissible, project-scoped facts, record the specific task population, pre-register the candidate set before collecting its evaluation sample, estimate evaluation uncertainty without test leakage, and report either `certified_best`, `certified_gain`, `fallback`, or `hold`. Any decision to change a live Genome procedure remains separately governed by Pegasus's existing human authorization and paired-trial policies. **This package does not create such an adapter.**

A significant limitation is the required calibration cost: at $n=6400$ and $K=9$, one synthetic decision has **57,600** observed procedure-task outcomes. This is not a realistic free resource for many real-agent workloads. The report does not subtract the cost of gathering those examples from any apparent decision benefit. Real application would need cheaper, valid evaluation or sequentially allocated evidence; that remains research, not an optimization achieved here.

# What is and is not established

| Object | Result | Claim boundary |
|---|---|---|
| Higher-order interactions | Algebraically exact; detected on planted task families in earlier versions | H1 is supported **only in synthetic settings** |
| Distributional certificate | Derived under bounded iid outcomes and justified TV shift | Mathematical statement conditional on assumptions |
| Safe relative change | Strict interval comparison prevents a false gain on a valid joint coverage event | Requires independent evaluator and baseline |
| High-order sign | Conservative $2^k$ error amplification bound | Does not replace causal intervention or account for omitted terms |
| Large or unmeasured shift | Wide valid bound withholds; unknown bound returns HOLD | A valid refusal, not a learning improvement |
| Broken shift assumption | Precise-looking but incorrect certification observed | Refutes unconditional stability claims |
| Agentic crystallization phase transition | No finite-size scaling, hysteresis, susceptibility, or distinct adaptive criticality observed | **H2 remains unestablished** |
| Recursive/self-directed improvement | No live autonomous procedure discovery, safe repeated promotion, or persistent learning-to-learn observed | **H3 remains unestablished** |

**There is no algorithm that is universally perfect for all tasks and unbounded distribution changes.** The appropriate engineering target is reliability and measured improvement **within a declared, testable operating domain**, accompanied by explicit HOLD when the domain assumptions are unavailable.

# Reproduction and research integrity

The package contains previous historical whitepapers and simulations, a verified archival v1.7 ZIP, v1.8 development/exploratory/held-out results, executable source, tests, independent result manifests, charts, and `PACKAGE_SHA256SUMS.json`. A separate v1.7 provenance audit reports a mismatch between a standalone PDF and its originally generated ZIP; the archival ZIP contained the checksum-correct PDF, and the original was preserved without altering its historical receipt.

From the extracted package root, install dependencies and run:

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m agentic_crystallization.stage_j --out experiments/reproduced_holdout --start-seed 20000 --count 240 --stage holdout
python scripts/verify_experiment.py experiments/stage_j_holdout
```

PowerShell uses `$env:PYTHONPATH='src'` and `$env:OPENBLAS_NUM_THREADS='1'` before the same `python -m` calls. **Never overwrite the original held-out folder when reproducing it.** Compare the regenerated raw CSV's SHA-256 against the original manifest. Details and exact commands are in [README](../README.md), [experiment guide](EXPERIMENTS.md), and [agent context](FOR_AGENTS.md).

## References and mathematical ancestry

1. Hoeffding, W. (1963). *Probability inequalities for sums of bounded random variables*. Journal of the American Statistical Association 58, 13–30. [DOI:10.1080/01621459.1963.10500830](https://doi.org/10.1080/01621459.1963.10500830).
2. Classical Möbius inversion and finite differences on Boolean lattices; the factorial interaction definition is standard, not a new mathematical object.
3. Total variation distance and its variational characterization; the present transport result follows from bounded measurable outcomes and stable conditional mechanisms.
4. Original Agentic Crystallization v1.0–v1.7 experiments and paper snapshots retained in this package; see [version history](CONTINUITY_AUDIT.md).
5. Agentic Context Engineering (ACE), GEPA, compositional/meta-learning, network percolation, and nucleation theory provide motivating related work; none supplies evidence of a phase transition in Pegasus.
