# Agentic Crystallization v1.5
## Cost-Aware Information Acquisition: A Falsifiable Adaptive-Procedure Study

**Status:** Reproducible synthetic research. No phase transition or autonomous Pegasus self-improvement established.

### Abstract
Versions 1.0–1.4 examined planted higher-order procedure interactions, misleading connectivity, conditional transfer, negative transfer, and Bayesian updates. Version 1.5 introduces a **one-step value-of-information (VOI) controller** deciding whether a paid relevance cue is worth requesting. Across 720 new held-out synthetic worlds, the controller improves mean utility relative to static Bayes when 75% of tasks are related (+1.597), but loses when 25% are related (−0.699). This isolates a genuine limitation of using an imperfect prior to value additional computation.

### 1. Hypothesis ledger
- **H1:** Nonadditive procedure value can be measured; supported on planted synthetic cases only.
- **H2:** A nonlinear critical adaptive transition; not demonstrated.
- **H3:** Validated clusters improve later learning; only restricted synthetic transfer has been observed.
- **Product question:** Can a bounded controller avoid unproductive tool calls? Tested here in an oracle simulation only.

### 2. Mathematical continuity
For procedure utility J(S;D), the higher-order finite-difference interaction is

\[
\Gamma_T(S)=\sum_{A\subseteq T}(-1)^{|T|-|A|}J(S\cup A;D).
\]

A three-way AND task has a nonzero triple interaction at the empty baseline but zero empty-baseline pairwise terms. This is standard Möbius algebra, not a novel identity.

The proposed engineering potential

\[
F(S)=\alpha B(S)+\kappa V(S)-\beta U(S)
\]

relates measured coordination, verification and future utility. It is **not** thermodynamic free energy. Graph connectivity and adaptation efficiency remain separate.

### 3. New exact one-step VOI derivation
Let R be binary task-family relatedness, q=P(R=1|h), and L_r(t) the conditional probability of remaining candidate t under R=r. The candidate probability is

\[
p(t|h)=(1-q)L_0(t)+qL_1(t).
\]

For a candidate order \(\pi=(t_1,\ldots,t_k)\), a remaining query budget b, success reward W=40 and query cost c=0.1, expected continuation utility is

\[
V_b(\pi,p)=W\sum_{i=1}^{k}p(t_i)-c\left[\sum_{i=1}^{k}i\,p(t_i)+k\left(1-\sum_{i=1}^{k}p(t_i)\right)\right],
\quad k=\min(b,|\pi|).
\]

This accounts for failed and censored searches. Sorting candidates by descending p is optimal under this equal-cost exact-match model.

A binary cue C with accuracy a updates q through Bayes' rule:

\[
q_c=\frac{qP(C=c|R=1)}{qP(C=c|R=1)+(1-q)P(C=c|R=0)}.
\]

The **model-estimated net value of probing** is

\[
\operatorname{VOI}(h)=\sum_c P(C=c|h)\max_\pi V_{b-1}(\pi,p_c)-c-\max_\pi V_b(\pi,p).
\]

Probe only when VOI>0, **before** observing C. The cue consumes one of the same 40 attempts. The controller does not see the hidden target or latent relatedness.

Under a fixed correct joint target distribution, eliminating wrong exact-match candidates only renormalizes survivors; it cannot reorder their relative probabilities. A new cue can reorder them.

### 4. Experiment contract
- **Training:** frozen Stage F conditional likelihood, seeds 3000–3399; no Stage G holdout updates.
- **Holdout:** seeds 8000–8119; three catalog sizes 12,15,18; prevalence 0.25 and 0.75; 720 synthetic worlds.
- **Oracle:** exact triple match. First validated triple is supplied, with discovery cost charged equally across policies.
- **Cue:** independent synthetic 80%-accurate relevance signal, only revealed if paid for.
- **Policies:** no prior, always reuse, static Bayesian, always probe after eight misses, and VOI.
- **Budget:** 40 attempts including any paid cue.
- **Utility:** 40*found − 0.1*(first discovery cost + second attempts).
- **Data:** world-paired rows, fixed seeds, manifests, and SHA-256 receipts.

### 5. Results
| Related-task prevalence | Static success | Always-probe success | VOI success | VOI probe rate | VOI minus static utility | VOI minus always-probe |
|---|---:|---:|---:|---:|---:|---:|
| 25% | 24.17% | 22.50% | 22.50% | 70.56% | **−0.699** | +0.005 |
| 75% | 37.50% | 41.11% | 41.39% | 48.06% | **+1.597** | +0.127 |

Descriptive paired bootstrap intervals across worlds (3,000 resamples, not confirmatory):
- 25%: VOI − static −0.699 [−1.753,+0.330]; VOI − always probe +0.005 [+0.003,+0.008].
- 75%: VOI − static +1.597 [+0.790,+2.514]; VOI − always probe +0.127 [+0.013,+0.354].

![Stage G results](../assets/stage_g_results.png)

### 6. Interpretation and falsification
**Positive:** In the high-relatedness regime, an explicitly priced information decision improves mean utility over both the static and fixed-probe policies.

**Negative:** In the low-relatedness regime, VOI probes too often relative to static Bayesian search. A model-positive VOI does not guarantee a positive realized value under prior mismatch. This falsifies any claim of universal advantage for the proposed controller.

**Important:** The likelihood model uses a pooled relatedness prior trained on different mixtures; it does not know the true test prevalence. These results do not demonstrate phase transitions, autonomous procedure discovery, learning-to-learn, or performance gains in Pegasus.

### 7. Next experimental step
Test calibrated, distributionally robust VOI: estimate task-relatedness prevalence from training-visible context, include cue reliability uncertainty, require a conservative positive margin, and compare with strong static/adaptive controls on untouched gradual-overlap and shifted distributions. Track regret, cost, failed attempts, and abstentions. Study H2 independently with graph/hypergraph finite-size sweeps.

### 8. Reproduction
```bash
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPATH=src python -m agentic_crystallization.stage_g --out experiments/reproduced_stage_g --start-seed 8000 --count 120
```
On Windows PowerShell: `$env:PYTHONPATH='src'` then run the two `python -m` commands.

[Source](../src/agentic_crystallization/stage_g.py) · [Tests](../tests/test_stage_g.py) · [Raw data](../experiments/stage_g_holdout/runs.csv) · [Manifest](../experiments/stage_g_holdout/manifest.json) · [Prior paper](archive/WHITE_PAPER_1.4.md).
