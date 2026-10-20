# Agentic Crystallization v1.6
## Stability Audit: A Trained Safety Margin for Cost-Aware Information Acquisition

**Research status:** Reproducible synthetic results. No phase transition or real-agent self-improvement established.

### Abstract
Version 1.6 preserves all prior code and data, and tests whether a trained conservative margin improves the v1.5 Bayesian value-of-information (VOI) controller. The margin is selected on 360 training worlds, then frozen for two separate 720-world holdout cohorts. The selected margin (0.5 utility units) makes exactly the same decisions as the original zero-margin VOI controller in both cohorts. **Added complexity provides no measured improvement.** The v1.5 policy retains a context-dependent mean advantage over static Bayesian selection in the 75%-related environment but not the 25%-related environment. The evidence favors retaining the simpler controller, not asserting a stable crystallization threshold.

### 1. Hypothesis ledger
- **H1:** Nonadditive procedure interactions. Supported only within planted synthetic benchmark families.
- **H2:** Critical transition in adaptive efficiency. Not demonstrated.
- **H3:** Autonomous, persistent learning-to-learn. Not demonstrated.
- **Engineering target:** Better accepted utility per unit of computation under shifting task distributions. Not yet demonstrated in Pegasus.

### 2. Mathematical continuity
For disjoint procedure sets S and T, the higher-order finite-difference interaction is:

\[\Gamma_T(S)=\sum_{A\subseteq T}(-1)^{|T|-|A|}J(S\cup A).\]

The three-way AND task has a nonzero triple interaction at the empty baseline while its empty-baseline pairwise terms vanish. This is established Mobius algebra, not new mathematics. A candidate *engineering* potential is

\[F(S)=\alpha B(S)+\kappa V(S)-\beta U(S),\]

where B is boundary/coordination cost, V is verification cost, and U is independently measured future utility. It is not physical free energy. Structural graph connectivity and adaptive benefit are separate estimands.

### 3. Tested algorithm
Given current evidence h and remaining budget b, the model-estimated one-step value of a new cue C is:

\[\operatorname{VOI}(h)=\mathbb E_C[\max_\pi V_{b-1}(\pi\mid h,C)]-c_{probe}-\max_\pi V_b(\pi\mid h).\]

Version 1.6 tests the decision rule:

\[\operatorname{Probe}(h;m)=\mathbf 1\{\operatorname{VOI}(h)>m\}.\]

The margin m is selected from {0,0.1,0.5,1,2,4} on training-only data, maximizing mean utility with a conservative tie-break toward larger m. The selected m=0.5 is frozen before evaluation. No hidden target, latent relatedness, or second cue is passed to the controller before its decision. The cue consumes one of the same 40 attempts.

### 4. Experiment protocol
- Catalog sizes: 12, 15, 18. Related-task mixture: 25% or 75%.
- Model training seeds 3000–3399 (carried forward from v1.4).
- Margin training seeds 9000–9059: 360 worlds total.
- Holdout 1 seeds 10000–10119: 720 worlds total.
- Holdout 2 seeds 11000–11119: 720 worlds total, independent from holdout 1.
- Policies: no prior, static Bayesian, always probe, original zero-margin VOI, trained-margin VOI.
- Fixed exact-match oracle, paired worlds, 40-attempt budget, first validated procedure discovery cost charged to all policies.
- Utility = 40*found - 0.1*(first discovery attempts + second attempts including probes).
- No model inference, Pegasus runtime, live self-modification, or procedure promotion.

### 5. Results
**First holdout (360 worlds per mixture)**

| Relatedness | Static success | Original VOI success | Margin success | Margin minus static utility | Margin minus VOI utility |
|---|---:|---:|---:|---:|---:|
| 25% | 21.11% | 21.11% | 21.11% | -0.016 | 0.000 |
| 75% | 33.89% | 36.39% | 36.39% | +1.037 | 0.000 |

**Independent replication (360 worlds per mixture)**

| Relatedness | Margin minus static utility | Margin minus original VOI | Margin minus always probe |
|---|---:|---:|---:|
| 25% | -0.120 | 0.000 | -0.107 |
| 75% | +1.042 | 0.000 | +0.239 |

Descriptive paired bootstrap 95% interval, first holdout, margin minus static: 25% related [-1.147,+1.114]; 75% related [-0.106,+2.241]. These are exploratory intervals, not preregistered confirmatory claims. The margin and original VOI have identical outcomes in both cohorts.

![Held-out results](../assets/stage_h_results.png)

### 6. Scientific interpretation
The fitted margin fails to improve the original decision rule on these worlds. This is a **negative model-selection result**: retain the simpler algorithm. The VOI controller itself is not robustly validated under continuous distribution shift. A mean advantage under one synthetic mixture is not a coherence threshold, learning-to-learn, or evidence of a universal self-organizing principle.

A proposed product acceptance criterion is externally verified improvement over a strong static baseline on untouched tasks, no unacceptable negative transfer under specified shifts, bounded compute and latency, and preserved permissions and receipts. Those criteria are not met by these experiments.

### 7. Next research target
Before adding parameters, measure posterior calibration and probe-value estimation error under graded overlap and changing task distributions. Introduce a robust fallback only if it beats the simpler controller on independent holdouts. Independently test H2 using size-dependent causal hyperedge sweeps and finite-size scaling, with null models. Do not conflate smooth sigmoid fits with criticality.

### 8. Reproduce
```bash
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPATH=src python -m agentic_crystallization.stage_h --out experiments/reproduced_stage_h --start-seed 10000 --count 120
```
On Windows PowerShell, set `$env:PYTHONPATH='src'` and `$env:OPENBLAS_NUM_THREADS='1'` before running the Python commands.

[Source](../src/agentic_crystallization/stage_h.py) · [Tests](../tests/test_stage_h.py) · [Holdout CSV](../experiments/stage_h_holdout/runs.csv) · [Replication CSV](../experiments/stage_h_replication/runs.csv) · [v1.5 paper](archive/WHITE_PAPER_1.5.md).
