# AGENTIC CRYSTALLIZATION
### v1.6 · A reproducible stability audit of adaptive computation

> **Progress means rejecting complexity that does not survive independent testing.**

**Status:** Synthetic research. No critical crystallization threshold or Pegasus self-learning demonstration.

[Whitepaper](docs/WHITE_PAPER.md) · [Mathematics](docs/WHITE_PAPER.md#3-tested-algorithm) · [Experiment](docs/WHITE_PAPER.md#4-experiment-protocol) · [Results](docs/WHITE_PAPER.md#5-results) · [Source](src/agentic_crystallization/stage_h.py) · [Tests](tests/test_stage_h.py) · [For agents](docs/FOR_AGENTS.md) · [Prior paper](docs/archive/WHITE_PAPER_1.5.md)

![Stage H held-out results](assets/stage_h_results.png)

## What we learned
A trained safety margin was intended to reduce unnecessary information-gathering. It selected a margin of 0.5, but on **two separate cohorts of 720 synthetic worlds each**, the margin made the **same decisions as the original zero-margin controller**. We therefore do not recommend adding it to Pegasus.

| Regime | Margin minus static Bayes utility | Margin minus original VOI |
|---|---:|---:|
| First cohort, 25% related | -0.016 | 0.000 |
| First cohort, 75% related | +1.037 | 0.000 |
| Replication, 25% related | -0.120 | 0.000 |
| Replication, 75% related | +1.042 | 0.000 |

## Version history
| Version | Result |
|---|---|
| 1.0 | Synthetic higher-order procedure interactions |
| 1.1 | Dense noncausal graph connections are not enough |
| 1.2 | Positive and negative transfer from retained procedures |
| 1.3 | Learned relevance gating is context-dependent |
| 1.4 | Bayesian evidence updates and paid observations |
| 1.5 | One-step VOI selection; distribution-shift sensitivity |
| **1.6** | **Trained safety margin provides no improvement** |

## Reproduce
Python 3.10+; NumPy required by historical experiments. From this folder:

```powershell
$env:PYTHONPATH='src'
$env:OPENBLAS_NUM_THREADS='1'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_h --out experiments/reproduced_stage_h --start-seed 10000 --count 120
```

Linux/macOS: prefix both commands with `PYTHONPATH=src OPENBLAS_NUM_THREADS=1`.

## Package contents
- `src/agentic_crystallization/`: Stage A–H Python simulations and policies
- `tests/`: previous and new invariant tests
- `experiments/`: preserved historical experiments, new holdout and replication, frozen manifests and CSVs
- `docs/WHITE_PAPER.md`: mathematical assumptions, methods, results, limitations
- `docs/archive/`: earlier complete whitepaper versions
- `docs/FOR_AGENTS.md`: agent-facing research context and claim boundaries
- `assets/`: figures
- `PACKAGE_SHA256SUMS.json`: file hashes

## Next step
Test continuous distribution shift and empirical VOI calibration. Keep live Pegasus routing, memory admission and Genome promotion unchanged. A simpler policy remains preferable unless a more complex one earns its cost on independent real-task evaluations.

**License:** not yet selected; choose one before public release.
