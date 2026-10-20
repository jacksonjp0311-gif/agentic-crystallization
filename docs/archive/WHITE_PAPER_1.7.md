# Agentic Crystallization v1.7
## Certified Decision Stability and Bounded Higher-Order Interaction Error

**Status:** Mathematical consolidation and reproducible synthetic audit. No physical crystallization, phase transition, or autonomous self-improvement has been demonstrated.

### Abstract
Versions 1.0–1.6 isolated planted higher-order procedure interactions, misleading connectivity, conditional transfer, Bayesian updates, and the context-dependent value of information. Version 1.6 found no improvement from an added safety margin. Version 1.7 derives two exact conditional stability results: a finite-action decision certificate and a conservative error bound on Möbius interaction coefficients. We audit these results on 1,000 synthetic decision worlds under known bounded perturbations. These are mathematical and implementation checks, not claims of learning or phase transitions.

### 1. Decision stability theorem
Let A be a finite permitted action set. For each a, suppose the true net utility Q(a) and estimate Qhat(a) satisfy **simultaneously** valid deterministic bounds:

\[|Q(a)-\widehat Q(a)|\le e(a),\quad e(a)\ge0,\quad\forall a\in A.\]

Let a* maximize Qhat with a deterministic tie break. Define

\[M(a^*)=\widehat Q(a^*)-e(a^*)-\max_{b\ne a^*}(\widehat Q(b)+e(b)).\]

**Theorem 1:** If M(a*)>0, then a* is the unique maximizer of true Q over the permitted actions for every vector Q inside the stated rectangular uncertainty set.

**Proof:** For each rival b, Q(a*) is at least Qhat(a*)-e(a*), which strictly exceeds Qhat(b)+e(b), which is at least Q(b). Therefore Q(a*)>Q(b). QED.

With uniform e(a)=epsilon, an estimated winner-runner-up gap greater than 2 epsilon is sufficient. Equality is not certified because a true tie remains possible. For a singleton action set the ranking is trivially certified only within that set. Under unconstrained rectangular intervals the strict inequality is also sharp: if it fails, a rival can tie or win at allowed interval endpoints.

**Important:** Individually reported statistical confidence intervals do not automatically satisfy simultaneous coverage. Error bounds cannot be taken from uncalibrated model confidence scores. For real data, valid joint coverage and protection against repeated selection are prerequisites.

### 2. Higher-order interaction uncertainty
For disjoint baseline S and group T, the standard Möbius interaction is

\[\Gamma_T(S)=\sum_{B\subseteq T}(-1)^{|T|-|B|}J(S\cup B).\]

If each involved utility estimate Jhat(S union B) has absolute error at most e_B, then by the triangle inequality,

\[|\widehat\Gamma_T(S)-\Gamma_T(S)|\le\sum_{B\subseteq T}e_B.\]

For uniform epsilon and |T|=k, this yields 2^k epsilon. The sign of an estimated interaction is certified only if its absolute magnitude strictly exceeds that total bound. This is conservative; correlated errors can cancel, but cancellation cannot be assumed. The exponential error growth highlights a real cost of certifying higher-order relationships.

**Crucial limitation:** Bounds on included low-order interactions do not bound omitted higher-order terms. A full cluster utility certificate must account for model truncation and unmodeled interactions.

### 3. Three distinct notions of stability
- **Decision:** action ranking is invariant under declared uncertainty (Theorem 1).
- **Structural:** validated causal edges or hyperedges persist under declared interventions and perturbations; not implied by Theorem 1.
- **Adaptive:** retained procedures continue improving future independently graded utility at acceptable cost and under distribution shift; not implied by the first two.

A stable decision can still be poor in absolute terms. A stable graph can be useless. A genuinely useful policy can legitimately change action when the task changes.

### 4. Stage I reproducible experiment
Generate six true action values per world from Uniform[-1,1]. Perturb each with independent Uniform[-epsilon,+epsilon] noise. The generator supplies epsilon as a **known correct bound**; the oracle knows true Q solely for grading. Run 500 deterministic seeds at epsilon=0.15 and 500 at epsilon=0.30. Certify the estimated winner when the robust margin is positive. Record whether any certified choice differs from the true maximizer.

| Perturbation | Worlds | Certified | Uncertified | Certified wrong | Mean regret of estimated winner |
|---|---:|---:|---:|---:|---:|
| +/-0.15 | 500 | 213 | 287 | 0 | 0.00909 |
| +/-0.30 | 500 | 74 | 426 | 0 | 0.03431 |

The synthetic audit evaluates the estimated winner even when uncertified, so these data do not demonstrate a useful deployed fallback policy. The separate `choose_with_fallback` API returns a named baseline instead. Zero certified mistakes are expected from the proved theorem and generator's valid bounds. This is not evidence of calibrated uncertainty in Pegasus.

### 5. Claim ledger
- **H1:** Planted synthetic procedure interactions can be exploited. Supported in the restricted benchmarks from earlier versions.
- **H2:** Critical adaptive phase transition. Not established; no finite-size scaling or hysteresis evidence.
- **H3:** Autonomous persistent learning-to-learn. Not established.
- **v1.7 theorem:** robust finite-action ranking under valid deterministic simultaneous bounds. Proven.
- **v1.7 bound:** finite-difference interaction error bounded by sum of term errors. Proven.
- **Open risk:** uncalibrated or distribution-shifted error bounds invalidate certificates.

### 6. Next falsifiable experiment
Evaluate simultaneous empirical coverage of action-value intervals under graded distribution shift and repeated decisions. Compare an uncertainty-aware abstain/fallback controller against the simpler static and VOI policies on untouched seeds, including actual resource cost. Separately test H2 with causal hyperedge density and finite-size scaling, without confusing structural connectivity with adaptive performance.

### 7. Reproduction
Run `PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v`, followed by `PYTHONPATH=src python -m agentic_crystallization.stage_i --out experiments/reproduced_i --seeds 500 --eps 0.15`. On Windows PowerShell, set `$env:PYTHONPATH='src'` and `$env:OPENBLAS_NUM_THREADS='1'` before the Python commands.

[Source](../src/agentic_crystallization/stability.py) · [Audit](../src/agentic_crystallization/stage_i.py) · [Tests](../tests/test_stability.py) · [Raw data](../experiments/stage_i/runs.csv) · [Prior paper](archive/WHITE_PAPER_1.6.md).

**Originality boundary:** robust interval comparisons, triangle inequalities, and Möbius algebra are established mathematics. Their synthesis as an auditable procedural-selection contract is the proposed engineering contribution, not a new physical law.
