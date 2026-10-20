# AGENTIC CRYSTALLIZATION
### v1.8 · Calibrated stability and the limits of procedure certification

> **Can an adaptive agent identify a procedure improvement it can actually trust - and recognize when its environment makes certainty impossible?**

![Calibration and stability results from 4,320 held-out synthetic evaluations](assets/stage_j_certified_gain.png)

**Scientific status:** A complete, executable research package. We have a new **conditional statistical stability contract** and a negative result showing that incorrect distribution-shift assumptions defeat certification. **No real Pegasus learning gain, physical phase transition, or autonomous learning-to-learn is claimed.**

[**Full whitepaper**](docs/WHITE_PAPER.md) · [**Mathematics & proofs**](docs/MATHEMATICS.md) · [**Experiments & controls**](docs/EXPERIMENTS.md) · [**Scientific claim ledger**](docs/CLAIM_LEDGER.md) · [**Algorithm source**](src/agentic_crystallization/robust_calibration.py) · [**Simulation source**](src/agentic_crystallization/stage_j.py) · [**For agents**](docs/FOR_AGENTS.md) · [**Version history**](docs/CONTINUITY_AUDIT.md)

## The short explanation

Imagine Pegasus has already tested nine ways to do a task. The best-looking one may only be ahead because of noise, and the future workload may differ from the past. **CrystalGuard-1.8** asks whether the advantage survives all uncertainty that we can legitimately bound. If so, it can certify a superior choice or a narrower gain over a baseline; if not, it refuses to claim certainty.

That is the direction of Agentic Crystallization: useful procedures should be retained because evidence supports them, not because they are highly connected, frequently repeated, or intuitively convincing.

## What changed in 1.8

| Earlier versions | New step in 1.8 |
|---|---|
| 1.0-1.1: planted interactions and negative graph controls | Retains the factorial estimand; does **not** infer a transition from graph density |
| 1.2-1.3: related transfer, unrelated negative transfer, relevance gate | Makes task-distribution drift a required uncertainty input |
| 1.4-1.6: Bayesian and cost-aware decisions, mixed outcomes | Separates nominal utility from reliably justified decisions |
| 1.7: deterministic interval ranking, assuming valid error bounds | Derives simultaneous finite-sample bounds and their shift conditions |
| **1.8** | **HOLD on unknown drift, strict relative-improvement certificate, factorial sign certificate, adversarial false-shift test** |

## New experiment: 4,320 held-out evaluations

The final held-out experiment uses 240 independently seeded synthetic worlds, six environmental conditions, and three sample sizes (200, 1,000, 6,400 tasks per procedure). All procedures receive the *same calibration task population*. The hidden target distribution and true utility are used solely to grade outputs.

At 6,400 calibration tasks per procedure:

| Environment | Joint coverage | Certified improvement over baseline | Harmful certified improvements |
|---|---:|---:|---:|
| Source and target match (related) | 239/240 | 206/240 | 0 |
| Source and target match (unrelated) | 240/240 | 240/240 | 0 |
| Moderate shift, valid bound | 240/240 | 64/240 | 0 |
| Large shift, valid bound | 240/240 | 0 | 0 |
| **Huge shift, falsely declared small** | **0/240** | 119/240 | **119** |
| Shift bound unavailable | HOLD | 0 | not asserted |

![Broken shift assumptions make precise-looking decisions unsafe](assets/stage_j_assumption_failure.png)

**The negative result is central:** increasing calibration samples does not fix a false shift assumption. For the deliberately violated bound, 60 claims of a uniquely optimal procedure were false at the largest sample size. A good uncertainty model is a real engineering requirement, not a decorative confidence number.

## The central equation

For a fixed library of $K$ procedure choices, each with bounded evaluation outcome in $[0,1]$, and $n$ independent calibration tasks, a simultaneous sampling radius at error level $\alpha$ is:

$$
\varepsilon = \sqrt{\frac{\log(2K/\alpha)}{2n}}.
$$

With a **justified** target/source total-variation upper bound $\delta$ and known action cost $c_a$, each procedure has a target-domain expected utility interval:

$$
L_a=\max(0,\widehat p_a-\varepsilon-\delta)-c_a,\qquad
U_a=\min(1,\widehat p_a+\varepsilon+\delta)-c_a.
$$

If $L_a>U_{\mathrm{baseline}}$, the candidate is certified to have higher expected net utility than the baseline on the simultaneous coverage event. If $\delta$ is unknown, **the code refuses certification**. A stricter comparison against every other action can certify unique optimality.

For higher-order interactions, the sign-certification radius grows as $2^k(\varepsilon+\delta)$ for $k$ procedures. Even when the planted interactions are real, a broad but correct drift bound can prevent certification.

[Formal assumptions, proofs, and no-free-lunch counterexample →](docs/MATHEMATICS.md)

## Reproduce in minutes

The simulation **never uses a language model, cloud service, or private Pegasus account**. Requires Python **3.10+** and NumPy. Other figures were generated with Matplotlib but do not need to be rebuilt to rerun the experiment.

**Windows PowerShell** (from the extracted package root):

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH='src'
$env:OPENBLAS_NUM_THREADS='1'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_j --out experiments/reproduced_holdout --start-seed 20000 --count 240 --stage holdout
python scripts/verify_experiment.py experiments/reproduced_holdout
```

**Linux / macOS:**

```bash
python3 -m pip install -r requirements.txt
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s tests -v
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python3 -m agentic_crystallization.stage_j --out experiments/reproduced_holdout --start-seed 20000 --count 240 --stage holdout
python3 scripts/verify_experiment.py experiments/reproduced_holdout
```

Do not rerun into the frozen `experiments/stage_j_holdout` directory. A fresh reproduction should produce the same `runs.csv` and `summary.json` hashes as the original **when run from unchanged source on a compatible NumPy environment**. Exact saved source hashes and counts are provided in each output manifest.

For the new calibration API itself:

```python
from agentic_crystallization.robust_calibration import bounds, select_action

observed = {'baseline': 0.45, 'validated_cluster': 0.82}
costs = {'baseline': 0.04, 'validated_cluster': 0.11}
report = bounds(observed, costs, n=6400, alpha=0.05, shift_tv_bound=0.02)
choice = select_action(report)
print(choice)  # May be certified_best or certified_gain, conditional on inputs.
```

The numbers above are **illustrative inputs**, not receipt-verified Pegasus measurements. The named drift bound is a required external assumption; the library does not infer it.

## What is in the package

```text
Agentic_Crystallization_1.8/
├── README.md                         Human overview, reproducibility, navigation
├── Agentic_Crystallization_1.8.pdf   Complete math whitepaper
├── CHANGELOG.md
├── requirements.txt
├── PACKAGE_SHA256SUMS.json
├── src/agentic_crystallization/
│   ├── robust_calibration.py         NEW joint uncertainty & safe selection
│   ├── stage_j.py                    NEW shift-stress experiment
│   └── stage_*.py, stability.py      Original v1.0-v1.7 research code
├── tests/                            Entire historical suite + 17 v1.8 checks
├── experiments/
│   ├── stage_j_development/          Fresh development split (3,600 rows)
│   ├── stage_j_holdout/              FINAL frozen holdout (4,320 rows)
│   ├── stage_j_exploratory_observed/  Earlier inspected trial, labeled exploratory
│   └── stage_*/                      Original v1.0-v1.7 measurements
├── assets/stage_j_*.png              Data-driven figures
├── docs/
│   ├── WHITE_PAPER.md, MATHEMATICS.md, EXPERIMENTS.md
│   ├── CLAIM_LEDGER.md, FOR_AGENTS.md, CONTINUITY_AUDIT.md
│   └── archive/                      Prior publications + verified v1.7 ZIP
└── scripts/verify_experiment.py      Integrity, scope, and result verifier
```

### Reusable research outputs

- [Read the whitepaper](docs/WHITE_PAPER.md) and its [full PDF](Agentic_Crystallization_1.8.pdf).
- [Inspect mathematical proofs](docs/MATHEMATICS.md) and the [algorithm card](docs/ALGORITHM_CARD.md).
- [Inspect the exact experimental protocol](docs/EXPERIMENTS.md).
- [Analyze raw held-out data](experiments/stage_j_holdout/runs.csv) and [all-strata summaries](experiments/stage_j_holdout/summary.json).
- [Inspect original results](experiments/) and [prior mathematics](docs/archive/WHITE_PAPER_1.7.md).
- [Read continuity and integrity audit](docs/CONTINUITY_AUDIT.md).

## Scientific boundaries and product readiness

The package provides a mathematically defensible **conditional certificate**, not a magical self-organizing force. It does not derive a universal crystallization threshold, does not learn new skills from real receipts, does not establish lower future learning costs in Pegasus, and does not automatically activate procedures. The *most important missing input* for a real deployment is a credible bound on how its future task population and measurement process can differ from its calibration population.

**Next research:** compare cheaper sequential/anytime-valid evaluation procedures while preserving fresh task and candidate boundaries; test controlled intervention on procedure dependencies separately from this calibration research. A live Pegasus adapter should remain read-only until those assumptions can be validated.

**License:** No explicit license is supplied. Select one before public redistribution.
