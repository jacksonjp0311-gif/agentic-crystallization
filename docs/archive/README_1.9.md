# AGENTIC CRYSTALLIZATION
### v1.9 — Efficient Stability · Sequential Evidence Certificates

> **Stop evaluating when the evidence is sufficient. Refuse certainty when the environment cannot justify it.**

![Actual measurements of procedure evaluations required by fixed and sequential certification](assets/stage_k_evidence.png)

**Status:** Executable, reproducible **synthetic research**. v1.9 establishes a bounded, conditional sequential decision certificate and measures significant savings in simulated evidence consumption. **This is not a claim of a universal crystallization law, observed phase transition, autonomous Pegasus learning, or production readiness.**

[**START HERE**](#what-does-this-software-actually-do) · [**RESULTS**](#new-v19-evidence) · [**THE MATHEMATICS**](docs/MATHEMATICS.md) · [**WHITEPAPER**](docs/WHITE_PAPER.md) · [**EXPERIMENTS**](docs/EXPERIMENTS.md) · [**PYTHON CORE**](src/agentic_crystallization/sequential_certificate.py) · [**TESTS**](tests/) · [**AGENT HANDOFF**](docs/FOR_AGENTS.md)

## What does this software actually do?

Suppose an AI harness has a **fixed, already validated set of candidate procedures**. A candidate can look best after a few trials simply by chance; another task family may favor a different procedure. A naive controller picks the largest average. Version 1.8 required enough data to put simultaneous uncertainty bounds around every candidate, then checked whether the winner truly outranked all others under a declared limit on environment change.

**Version 1.9 improves the evidence workflow.** Instead of waiting for a maximum sample budget, the controller checks at predeclared sample checkpoints. If a candidate's *worst plausible* expected value is above every alternative's *best plausible* expected value, it certifies the winner and stops collecting evaluations. If the environmental shift is unknown or the evidence never separates candidates, it returns **HOLD** rather than inventing certainty.

**Think of it as a verifiable brake for expensive agent evaluation**, not as an autonomous machine that manufactures new cognition.

## New v1.9 evidence

**Fresh sealed final holdout:** 2,800 synthetic worlds; seven environmental regimes; six fixed actions; up to 6,400 evaluations **per action**, for a maximum 38,400 action-outcome evaluations per world.

| Environment | Certified by sequential rule | Evidence saved on *jointly certified* cases | Incorrect certificates |
|---|---:|---:|---:|
| Clear winner, stationary tasks | 400/400 | **98.71%** | 0 |
| Valid moderate task shift | 400/400 | **96.07%** | 0 |
| Valid gradual task shift | 400/400 | **85.61%** | 0 |
| Nearly tied candidates | **0/400** (HOLD) | Not applicable | 0 |
| Known broad shift, no provable separation | 0/400 (HOLD before sampling) | Not applicable | 0 |
| Shift bound unavailable | 0/400 (HOLD before sampling) | Not applicable | 0 |
| **Deliberately false shift bound** | 400/400 | 98.37%, **invalid** | **400/400** |

**Important limitations:** On near-ties, the fixed method obtained **7** certificates, versus **0** for the sequential method. Spending statistical error budget across multiple checkpoints can reduce its final detection power. The serious negative control also shows that a false shift bound makes every confident certificate wrong in the deliberately adversarial worlds. Faster is not safer when the premise is false.

![The invalid-environment counterexample](assets/stage_k_safety_counterexample.png)

[Full per-regime results](experiments/stage_k_holdout/summary.json) · [Raw data](experiments/stage_k_holdout/runs.csv) · [Predeclared final protocol & code hashes](experiments/stage_k_holdout/protocol.json) · [Methodological detail](docs/EXPERIMENTS.md)

## The one equation that matters

With \(K\) frozen procedures, \(J\) predefined sample checkpoints, bounded independently sampled task outcomes, and a per-decision error allowance \(\alpha\), use

\[
r_j=\sqrt{\frac{\log(2KJ/\alpha)}{2n_j}}.
\]

For each action \(a\), with source sample mean \(\widehat\mu_a\), **externally justified** source-to-target total-variation bound \(\delta\), and fixed action cost \(c_a\), define

\[
L_a=\max(0,\widehat\mu_a-r_j-\delta)-c_a,
\quad
U_a=\min(1,\widehat\mu_a+r_j+\delta)-c_a.
\]

Then certify a unique best candidate **only if**

\[
\boxed{L_{a^*}>\max_{b\ne a^*}U_b.}
\]

On the simultaneous concentration/shift coverage event, the certified choice is genuinely best **within the frozen action library**. Under the stated assumptions, that event has probability at least \(1-\alpha\) for the episode. This uses standard Hoeffding/Bonferroni mathematics. The novelty claimed here is **not** the inequality; it is an audited, bounded procedure-selection workflow with measured evidence costs and documented counterexamples.

[Full assumptions and proofs](docs/MATHEMATICS.md) · [Algorithm contract](docs/ALGORITHM_CARD.md)

## Quick start — verify it yourself

Requires **Python 3.10+** and NumPy. No private accounts, GPUs, LLM APIs or network connections are used. Exact byte replay was checked using the pinned `requirements-repro.txt` (NumPy 2.3.5).

**Windows PowerShell:**

```powershell
cd Agentic_Crystallization_1.9
python -m pip install -r requirements-repro.txt
$env:PYTHONPATH='src'
$env:OPENBLAS_NUM_THREADS='1'
python -m unittest discover -s tests -v
python scripts/verify_stage_k.py experiments/stage_k_holdout --root .
python -m agentic_crystallization.stage_k --out experiments/my_replay --start-seed 60000 --count 400 --stage holdout
python scripts/verify_stage_k.py experiments/my_replay --root .
```

**Linux / macOS:**

```bash
cd Agentic_Crystallization_1.9
python3 -m pip install -r requirements-repro.txt
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s tests -v
python3 scripts/verify_stage_k.py experiments/stage_k_holdout --root .
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python3 -m agentic_crystallization.stage_k --out experiments/my_replay --start-seed 60000 --count 400 --stage holdout
python3 scripts/verify_stage_k.py experiments/my_replay --root .
```

The reproduction command writes only to a **new directory**, preserving all sealed historical outputs.

### Reuse just the bounded certificate

```python
from agentic_crystallization.sequential_certificate import select_at_checkpoint

# Illustrative, fictional evaluation receipts, NOT real Pegasus outcomes.
sums = {'baseline': 110, 'candidate': 338, 'alternative': 130}
costs = {'baseline': 0.02, 'candidate': 0.02, 'alternative': 0.02}
report = select_at_checkpoint(
    sums, costs, n=400, look_index=5,
    alpha=0.05, shift_tv_bound=0.08, total_looks=9,
)
print(report['status'], report['action'])
# A certificate holds only if the declared shift/measurement assumptions are TRUE.
```

**Separation of responsibilities:** This module returns a mathematical judgment about fixed candidates. It does not authorize a new skill, write agent memories, modify policies, deploy code, or bypass the host's approval and receipt requirements.

## Research lineage (complete history retained)

| Version | Main research step | Current claim status |
|---|---|---|
| 1.0–1.1 | Planted higher-order interactions, graph structure controls | Restricted synthetic observation, no criticality |
| 1.2–1.3 | Related-transfer gains, negative transfer and learned relevance gates | Restricted synthetic observation, no autonomous cluster discovery |
| 1.4–1.6 | Bayesian updates, value of information and complexity counterexamples | Mixed synthetic performance, no universal policy |
| 1.7 | Deterministic stability certificates under supplied error bounds | Conditional algebraic correctness |
| 1.8 | Simultaneous finite-sample calibration + declared distribution shift | Conditional theorem and false-shift counterexample |
| **1.9** | **Predeclared sequential checkpoints + early HOLD/stop rules** | **Conditional theorem; large synthetic evidence saving, with failure modes exposed** |

You can retrieve original source, experiments and papers without using an older download: the package retains them under `src/`, `experiments/`, earlier PDFs and [`docs/archive/`](docs/archive/). The verified v1.8 ZIP is included. The previously discovered v1.7 historical PDF checksum divergence remains documented; it has not been silently erased. Read the [continuity audit](docs/CONTINUITY_AUDIT.md).

## Research directory

```text
Agentic_Crystallization_1.9/
├── README.md                          Human-facing overview and navigation
├── Agentic_Crystallization_1.9.pdf    Self-contained new whitepaper
├── CHANGELOG.md                       Versioned research history
├── PACKAGE_SHA256SUMS.json            All packaged-file SHA-256 hashes
├── requirements.txt                   Compatible runtime dependencies
├── requirements-repro.txt             Pinned version for exact replay
├── src/agentic_crystallization/
│   ├── sequential_certificate.py      NEW audited statistical decision core
│   ├── stage_k.py                     NEW Stage K simulator/experiment
│   ├── robust_calibration.py          v1.8 fixed-sample baseline
│   └── stage_a.py ... stage_j.py       Previous mathematics & simulations
├── tests/                              All earlier tests + new v1.9 tests
├── experiments/
│   ├── stage_k_development/           New development cohort
│   ├── stage_k_exploratory_observed/   Archived observed preliminary cohort
│   ├── stage_k_holdout/               NEW sealed final holdout
│   └── stage_*/                        All original v1.0–v1.8 results
├── assets/stage_k_*.png               Figures regenerated from FINAL results
├── docs/
│   ├── WHITE_PAPER.md                 Research argument and results
│   ├── MATHEMATICS.md                 Assumptions, theorems, proofs and limits
│   ├── EXPERIMENTS.md                 Frozen design, negatives and splits
│   ├── ALGORITHM_CARD.md              Operational I/O and pseudocode
│   ├── CLAIM_LEDGER.md                Evidence/claim boundaries
│   ├── FOR_AGENTS.md                  Stable context packet for coding agents
│   ├── CONTINUITY_AUDIT.md            Immutable-history integrity audit
│   └── archive/                       Earlier writings and verified releases
└── scripts/
    ├── verify_stage_k.py              Check experiment hashes/scope/code
    ├── plot_stage_k.py                Regenerate figures
    └── verify_experiment.py           Preserved v1.8 experiment verifier
```

## What would make the crystal *actually* stable?

The practical goal is **not** an aesthetically satisfying equation. It is sustained, validated procedural organization that survives new tasks, distribution change, and independent audit. Version 1.9 is a strong step on *decision-evidence efficiency*, not proof of structural or adaptive self-organization. Critical missing work includes defensible shift bounds; independently discovered candidate combinations and causally supported interactions; repeated fresh-task learning curves; and operational receipts and authorization constraints in the eventual host.

**Honest release boundary:** No physical-like critical transition, no autonomous improvements and no measured Pegasus performance gain have been demonstrated. Proceed with further mathematical validation **before** real-agent deployment.

**License:** No license is assigned in this research archive. Choose an explicit license before public publication or redistribution.
