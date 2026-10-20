# Agentic Crystallization

![Agentic Crystallization v2.0 — governed adaptive procedure structure](assets/crystal_banner.png)

### Version 2.0 — Operational Crystal: an autonomous, bounded procedure-learning loop

> **A useful computational structure is not one that never changes. It is one that can discover, justify, retain, and safely relinquish what it has learned.**

**A runnable scientific software package.** Generates allowed procedure combinations, evaluates candidates on task feedback, certifies gains under clearly stated mathematical conditions, retains reusable structures, and repeats automatically. v2.0 includes a persistent JSONL ledger, resource budget, controlled drift tests, an audited experiment, and the entire v1.0–v1.9 research history.

**Research status:** A real, executable closed-loop **synthetic prototype**. Not a newly discovered physical law; not a demonstrated thermodynamic crystal, AGI, perpetual self-sustaining computer, phase transition, or Pegasus integration.

[**START HERE**](#what-is-this) · [**RESULTS**](#what-the-experiments-show) · [**THE MATH**](docs/MATHEMATICS.md) · [**WHITEPAPER**](docs/WHITE_PAPER.md) · [**ALGORITHM**](docs/ALGORITHM_CARD.md) · [**EXPERIMENTS**](docs/EXPERIMENTS.md) · [**RAW DATA**](experiments/stage_l_holdout/runs.csv) · [**CODE**](src/agentic_crystallization/crystal_core.py) · [**TESTS**](tests/test_crystal_core.py) · [**FOR AGENTS**](docs/FOR_AGENTS.md)

## What is this?

Imagine an agent that repeatedly encounters problems. Rather than merely storing transcript snippets or assuming its previous answers were good, it develops reusable *procedures*. It only retains a procedure after an independent test indicates that it improves performance relative to a named baseline. When circumstances change, a historical procedure can be proposed again, but **must earn a new certificate** before it is used. If the evidence is unconvincing or the environment-shift assumptions are unsupported, the agent returns **HOLD** and deploys the safe baseline.

This is a minimal operational analogue of crystallization: individual building blocks form higher-order, reusable structures under selection pressure. Unlike physical atoms, the building blocks here are explicitly programmed candidate procedures. Unlike a physical lattice, the resulting knowledge organization can adapt when its task environment changes.

### What's actually automated?

```text
External task stream + observable outcome feedback
                    │
           [PERMITTED PRIMITIVES]
                    │
          generate bounded proposals
                    │
       Scout old memory / search new triples
                    │
      Independent validation (fresh samples)
                    │
      ┌──────── CERTIFY positive gain? ────────┐
      │                                       │
    YES                                      NO
      │                                       │
  Retain/revalidate                              HOLD
      │                                       │
  Use certified candidate              Use baseline
      └───────────────┬───────────────────────┘
                      │
          Account for consumed feedback
          and rewards from external tasks
                      │
             Write chained receipt
                      │
              Restart / next task
```

The core will **not** execute arbitrary code, rewrite its own source, spawn agent processes, connect to cloud APIs, or change authorization policy. It composes a finite whitelist of simple XOR procedures in a scientific testbed. This limitation is intentional: mathematical and behavioral correctness first.

## What the experiments show

**Independent, frozen-code Stage L holdout:** 40 simulated worlds × 12 consecutive epochs × 7 environmental regimes × 4 policies = **13,440 measured policy-epoch decisions**. The entire final experiment was reproduced from frozen code: the raw CSV, summary, protocol and checksums matched **byte for byte**.

![Mean net utility of four policies in the final Stage L holdout](assets/stage_l_results.png)

| Environment | Crystal certificates | Reused memory, certified | Crystal utility/epoch | Fixed-reuse utility/epoch | Scientific conclusion |
|---|---:|---:|---:|---:|---|
| Stable pattern | 480/480 | 440 | 1022.61 | **1023.26** | Simple fixed reuse is marginally cheaper |
| **Recurring patterns** | **480/480** | **360** | **1021.60** | 589.12 | Memory reactivation avoids needless rediscovery |
| Abrupt changes | 480/480 | 320 | 1022.35 | 245.23 | Controller can rediscover permitted structures |
| Four-way unlearnable controls | 240/480 | 200 | 502.87 | **503.62** | Holds rather than promoting unsupported 4-way relations |
| Valid limited drift | 480/480 | 360 | 954.85 | 551.49 | Conditional transfer survives the bounded constructed shift |
| Unjustified shift | **0/480** | 0 | 0.00 | 0.00 | No guess: HOLD without charged evidence |
| **False shift assumption** | **440/480** | 400 | **−944.36** | −1016.22 | **440/440 issued certificates wrong** |

**Utility units are synthetic.** They combine independently measured task-prediction gains with sample, candidate-evaluation and memory charges. They are not dollars or physical energy.

### The practical gain: less redundant evaluation

When tasks return to previously encountered patterns, the crystal's recurrent-task performance matches the fully memoryless learner (**480 certified episodes out of 480**) while using:

<details>
<summary>Detailed paired recurring-task comparison</summary>

| Metric | Crystal | Memoryless | Difference |
|---|---:|---:|---:|
| Certified episodes | 480 | 480 | No change |
| Task observations | 73,216 | 97,216 | **24.69% reduction** |
| Candidate prediction operations | 1,134,976 | 4,290,496 | **73.55% reduction** |
| Mean synthetic surplus / epoch | 1021.60 | 1020.42 | **+1.17 units** |

The **small** utility difference comes from saved computation, not better prediction accuracy. In this deliberately easy constructed recurrence, every world's cost saving is identical, so world-bootstrap descriptive uncertainty intervals on this contrast are degenerate. Do not generalize the percentages to real agent tasks.

</details>

![Measured candidate-prediction work on independent held-out worlds](assets/stage_l_search_cost.png)

### The mandatory failure experiment

![False environmental assumptions undermine all statistical certificates](assets/stage_l_shift_failure.png)

The deliberate false-shift condition trains the learner on one relation and then deploys it in a world with **inverted answers**. The environment falsely declares zero change. As predicted by the impossibility argument, the controller has no way to know this from its unchanged validation sample; **all 440 certificates issued by the crystal are incorrect**. Increasing the number of source samples would not repair the missing information.

Read the [complete protocol, controls, side-by-side benchmarks and caveats](docs/EXPERIMENTS.md). This failure is part of the research result, not a defect hidden by a headline success rate.

## The mathematics that holds the system together

For episode $e$, select **one candidate** using exploratory samples. On an independent validation batch, measure its paired benefit over baseline, $D_e\in[-1,1]$. Use lifetime error spending $\alpha_e=\alpha/[e(e+1)]$ and a justified direct gain-shift bound $\Delta_e$:

$$
\boxed{L_{e,j}=\widehat\mu_{e,j}-\sqrt{\frac{2\log(J/\alpha_e)}{n_j}}-\Delta_e.}
$$

**CERTIFY** only when $L_{e,j}>\varepsilon$, at one of the predeclared checkpoints. **HOLD** if no checkpoint certifies, if the shift allowance is unavailable, or if the resource reserve is insufficient.

**Conditional theorem:** under bounded, independent within-episode validation data, honest source-to-deployment gain-shift bounds, separation of candidate choice from validation evidence, and a never-reset lifetime error budget, the probability of **ever** falsely certifying gain $\le\varepsilon$ over the controller's lifetime is at most $\alpha=0.05$. This is standard concentration and union-bound mathematics applied to the closed loop, **not** a novel law or unconditional guarantee.

The state also satisfies two deterministic guards: $|M_e|\le4$ retained procedures, and $B_e\ge0$ spendable evaluation credits after every transaction. The credits are replenished by **external task rewards**. Neither invariant implies infinite autonomy.

[Proofs, assumptions and the shift impossibility argument](docs/MATHEMATICS.md) · [Detailed state transition contract](docs/ALGORITHM_CARD.md).

## Run it on Windows

Requires **Python 3.10+**, **PowerShell 5.1+** for the optional single-entry helper, and NumPy for some historical tests. The new v2.0 loop, simulator and SHA verifier use only the Python standard library; there is no API key, internet connection or GPU requirement.

```powershell
# Extract the full ZIP and open PowerShell in Agentic_Crystallization_2.0
python -m pip install -r requirements-repro.txt

# One canonical entry script; returns to the starting folder after running:
.\run.ps1 -Action test
.\run.ps1 -Action verify
.\run.ps1 -Action demo
.\run.ps1 -Action simulate -Worlds 3 -StartSeed 90000
```

Or use Python directly:

```bash
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPATH=src python -m agentic_crystallization.stage_l --out experiments/new_experiment --start-seed 90000 --count 3 --demo-seed 90000
python scripts/verify_stage_l.py experiments/new_experiment --repo .
PYTHONPATH=src python scripts/verify_crystal_ledger.py demos/recurrent/ledger.jsonl
python scripts/verify_package.py .
```

**Important:** Never direct a new run into the sealed holdout directory. The program deliberately refuses to overwrite populated experiment folders. The included demonstration ledger can be independently replayed and checked for state integrity.

## Evidence, code and complete version history

```text
Agentic_Crystallization_2.0/
├── README.md                        Human-facing entry point
├── Agentic_Crystallization_2.0.pdf  Research whitepaper with mathematical formulas
├── run.ps1                           One-command Windows workflow
├── docs/
│   ├── WHITE_PAPER.md               Context, methods, limitations and results
│   ├── MATHEMATICS.md                Rigorous bounds, proofs, impossibility argument
│   ├── ALGORITHM_CARD.md            Complete state transition contract
│   ├── EXPERIMENTS.md               Experimental protocol, controls, comparisons
│   ├── CLAIM_LEDGER.md              Supported claims vs hypotheses
│   ├── FOR_AGENTS.md                Scope and invariants for research agents
│   ├── PREREGISTRATION_STAGE_L.json  Final preregistered source hashes
│   ├── CONTINUITY_AUDIT.md          Version and artifact provenance
│   └── archive/                     Full v1.0–v1.9 papers/verified archives
├── src/agentic_crystallization/
│   ├── crystal_core.py              v2.0 discovery, certification, memory, ledger
│   ├── stage_l.py                  v2.0 scenario generator and fixed baselines
│   └── stage_a.py ... stage_k.py   ALL earlier research source
├── tests/                            Full historical and v2.0 regression suite
├── experiments/
│   ├── stage_l_holdout/            Sealed final 13,440-row experiment
│   ├── stage_l_independent_replay/ Byte-for-byte independent reproduction
│   ├── stage_l_analysis.json       Paired world-level descriptive statistics
│   ├── stage_l_development*/       Explicitly preliminary cohorts
│   └── stage_*/                    ALL prior v1.0–v1.9 experiment data
├── demos/recurrent/                 Persistent 12-epoch JSONL ledger + state
├── assets/                           Plots and graphic derived from real results
├── scripts/                          Reproduction, SHA verification, plot creation
├── CHANGELOG.md                      All original entries + new release
└── PACKAGE_SHA256SUMS.json           Exact contents; not a digital signature
```

**Earlier science remains directly accessible.** [v1.9 proofs](docs/archive/MATHEMATICS_1.9.md), [v1.9 paper](docs/archive/WHITE_PAPER_1.9.md), [v1.9 original verified ZIP](docs/archive/Agentic_Crystallization_1.9_VERIFIED.zip), previous stage simulators, original experimental data and negative outcomes are all retained. [Full continuity audit](docs/CONTINUITY_AUDIT.md).

## What is—and isn't—self-sustaining?

**What we have achieved:** A standalone controller that automatically proposes, independently certifies or refuses, retains useful procedures, revisits them under recurrent task patterns, prunes expired entries, accounts for costs, writes recoverable receipts, and advances through multiple synthetic episodes without handholding.

**What we have not achieved:** Self-powering computation, self-generated labeled task feedback, unrestricted algorithm invention, guaranteed lifetime economic profitability, adaptation under arbitrary unknowable environmental shift, autonomous Pegasus improvement, or a new natural crystallization law. The hidden synthetic task family is deliberately simple and known to contain the correct answer in the positive regimes.

A useful theory must allow failure. In particular, **two deployment worlds can present identical source evidence but demand opposite decisions**. No source-only controller can guarantee nontrivial correct certification in both worlds. Read the [short impossibility proof](docs/MATHEMATICS.md#8-impossibility-of-assumption-free-deployment-certification).

### Next mathematical milestone

**v2.1 should investigate the minimum fresh target-domain feedback needed to justify a dynamic shift allowance**, then compare the full loop against stronger changing-task strategies and a larger procedure algebra. No forced new version when the data do not justify it.

**License:** No license has been assigned yet. Do not assume public redistribution rights without permission.
