# AGENTIC CRYSTALLIZATION
### Version 1.2 · Conditional transfer and negative transfer in adaptive procedure search

> **Can validated knowledge make the next improvement easier to find—and when does it make the search worse?**

**Status:** Reproducible synthetic research. No critical phase transition or autonomous self-improvement has been demonstrated.

[Whitepaper](docs/WHITE_PAPER.md) · [Mathematics](docs/WHITE_PAPER.md#2-mathematical-continuity) · [Protocol](docs/WHITE_PAPER.md#3-stage-d-experimental-protocol) · [Results](docs/WHITE_PAPER.md#4-independently-seeded-validation-results) · [Source](src/agentic_crystallization/stage_d.py) · [Tests](tests/test_stage_d.py) · [For agents](docs/FOR_AGENTS.md) · [Prior research](docs/archive/WHITE_PAPER_1.1.md)

![Stage D validation results](assets/stage_d_transfer.png)

## What this means

Imagine an agent that has already validated a useful three-part procedure. If the next problem belongs to the same family, its earlier discovery might help it search. If the next problem is unrelated, blindly reusing that knowledge can waste effort. This package tests that distinction in controlled synthetic worlds without involving a language model.

## Findings across versions

| Version | Scientific question | Evidence |
|---|---|---|
| 1.0 | Can procedure interactions improve selection? | Advantage on deliberately planted pair/triple interactions |
| 1.1 | Is graph connectivity enough? | No; misleading dense graphs did not yield the same advantage |
| **1.2** | Does a prior validated triple improve subsequent discovery? | **Yes on related tasks; harmful on unrelated tasks** |

## New independent validation: 1,200 synthetic worlds

| Next-task relationship | No-prior discovery | Cluster-prior discovery | Difference | Restricted attempts saved |
|---|---:|---:|---:|---:|
| Related | 10.0% | 46.2% | **+36.2 percentage points** | **7.83** |
| Unrelated | 11.0% | 0.0% | **-11.0 percentage points** | **-1.90** |

These outcomes depend on planted latent families and a fixed 40-query limit. The prior first triple is supplied as already validated, so this is **not a full learning-to-learn demonstration**.

## Reproduce

Requires Python 3.10+ and NumPy. From the package root:

**Windows PowerShell**
```powershell
python -m pip install numpy
$env:PYTHONPATH='src'
$env:OPENBLAS_NUM_THREADS='1'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_d --out experiments/reproduced --seeds 200 --budget 40
```

**Linux / macOS**
```bash
python -m pip install numpy
OPENBLAS_NUM_THREADS=1 PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m agentic_crystallization.stage_d --out experiments/reproduced --seeds 200 --budget 40
```

The CLI command reproduces exploratory seeds 0–199. To reproduce the disjoint validation seeds, run:
```python
from pathlib import Path
from agentic_crystallization.stage_d import run
run(Path('experiments/reproduced_validation'), seeds=range(200,400))
```

## Package layout

```text
Agentic_Crystallization_1.2/
├── README.md
├── Agentic_Crystallization_1.2.pdf
├── docs/
│   ├── WHITE_PAPER.md
│   ├── FOR_AGENTS.md
│   └── archive/                   Prior whitepaper and README
├── src/agentic_crystallization/
│   ├── stage_a.py                 v1.0 synthetic interactions
│   ├── stage_b.py                 v1.1 connectivity and controls
│   └── stage_d.py                 v1.2 transfer and ablation
├── tests/                         All versioned tests
├── experiments/
│   ├── stage_a/
│   ├── stage_b/
│   ├── stage_b_validation/
│   ├── stage_d/
│   └── stage_d_validation/
└── assets/                        Reproducible charts
```

## Integrity and next steps

Raw per-world results, manifests, analyses and checksums are included. The source is deterministic; no external model, web service, or Pegasus installation is required. Earlier experiment results are preserved, not replaced.

**Next:** test a learned *when-to-reuse* gate under graded distribution shift, charge for first-cluster acquisition, and include failed/censored search attempts. Keep the next fresh holdout separate from candidate selection.

**License:** Not assigned. Choose an explicit license before public release.
