# AGENTIC CRYSTALLIZATION
### Version 1.1 · Reproducible research into higher-order procedure interactions

> **Can interacting procedures provide a measurable advantage—and is graph connectivity alone enough?**

**Status:** Reproducible synthetic experiments. **No critical phase transition or autonomous self-improvement demonstrated.**

[Whitepaper](docs/WHITE_PAPER.md) · [Mathematics](docs/WHITE_PAPER.md#2-interaction-mathematics) · [Experimental protocol](docs/WHITE_PAPER.md#5-new-stage-bc-protocol) · [Results](docs/WHITE_PAPER.md#6-executed-results) · [Stage B source](src/agentic_crystallization/stage_b.py) · [Tests](tests/test_stage_b.py) · [Agent context](docs/FOR_AGENTS.md)

![Measured synthetic density sweep](assets/stage_b_density.png)

## What we learned

Some tasks reward **combinations** of procedures. A learner modeling three-way combinations can choose better than one that scores each procedure independently. We planted those combinations in synthetic tasks and checked whether a learner could exploit them without being told which triples were active. It could, in these experiments. We also made dense but irrelevant metadata graphs; **connectivity alone produced no advantage**.

| Study | Scale | Result |
|---|---|---|
| Stage A, preserved from v1.0 | 180 synthetic worlds | Pairwise and triple interaction benchmarks under generous complete-factorial training |
| Stage B/C exploratory | 252 worlds; 5 policies | +0.1775 average advantage in planted-triple worlds |
| Disjoint-seed validation | 252 worlds; 5 policies | +0.1655 average advantage in planted-triple worlds |
| Negative controls | Additive and misleading graphs | Approximately zero or slightly negative advantage |
| Unit tests | 9 tests | Passed in this package |

These are **descriptive synthetic results**, not proof of a new physical law, a learning-to-learn effect, or a threshold.

## Reproduce

Python 3.10+ with NumPy. In Windows PowerShell:

```powershell
python -m pip install numpy
$env:PYTHONPATH='src'
$env:OPENBLAS_NUM_THREADS='1'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_b --out experiments/reproduced --seeds 8 --train 160 --tests 30
```

Linux/macOS:

```bash
python -m pip install numpy
PYTHONPATH=src python -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 PYTHONPATH=src python -m agentic_crystallization.stage_b --out experiments/reproduced --seeds 8 --train 160 --tests 30
```

The combined CLI run uses seeds 0–7. The archived exploratory and validation cohorts were executed separately using the Python `run()` API with seeds 0–3 and 4–7. Floating-point text formatting can vary by platform.

## Directory

```text
Agentic_Crystallization_1.1/
├── README.md
├── docs/
│   ├── WHITE_PAPER.md
│   └── FOR_AGENTS.md
├── src/agentic_crystallization/
│   ├── stage_a.py
│   └── stage_b.py
├── tests/
│   ├── test_stage_a.py
│   └── test_stage_b.py
├── experiments/
│   ├── stage_a/                 Archived v1.0 results
│   ├── stage_b/                 Exploratory cohort
│   └── stage_b_validation/      Disjoint-seed validation
├── assets/stage_b_density.png
└── Agentic_Crystallization_1.1.pdf
```

## Scientific limits and next question

No real model or Pegasus agent ran. The hypergraph is synthetic, procedure interactions were planted, and the graph did not evolve across successive learning cycles. No discontinuity, hysteresis, finite-size collapse, or learning-to-learn was established. The next experiment must measure whether a *first validated cluster makes the next independently validated improvement cheaper* under matched resources.

**License:** Not assigned; select an explicit license before public release.
