# AGENTIC CRYSTALLIZATION v1.7
### Certified Decision Stability · Complete Versioned Research Package

> **When can we prove that uncertainty cannot reverse an agent's selected action?**

**Status:** Reproducible synthetic mathematical audit. No real Pegasus integration, self-organizing phase transition or autonomous learning-to-learn has been demonstrated.

[Whitepaper](docs/WHITE_PAPER.md) · [Theorem](docs/WHITE_PAPER.md#1-decision-stability-theorem) · [Higher-order interactions](docs/WHITE_PAPER.md#2-higher-order-interaction-uncertainty) · [Experiment](docs/WHITE_PAPER.md#4-stage-i-reproducible-experiment) · [Code](src/agentic_crystallization/stability.py) · [Tests](tests/test_stability.py) · [Agent context](docs/FOR_AGENTS.md) · [Prior whitepaper](docs/archive/WHITE_PAPER_1.6.md)

## Human-facing finding

We have separated *a stable decision* from *a useful procedure*. If the estimated best action's worst-case value still exceeds every rival's best-case value, its ranking is mathematically certified **provided the error bounds are correct**. When uncertainty doubles, the number of decisions we can certify falls sharply.

| Known synthetic error | Worlds | Certified | Rate | Certified errors |
|---|---:|---:|---:|---:|
| +/-0.15 | 500 | 213 | 42.6% | 0 |
| +/-0.30 | 500 | 74 | 14.8% | 0 |

Zero errors are guaranteed by the assumptions, not a surprising discovery. The hard problem is obtaining valid error bounds from real agent evidence.

## Research continuity

| Version | Main result |
|---|---|
| 1.0 | Planted higher-order synergy |
| 1.1 | Noncausal connectivity negative control |
| 1.2 | Positive and negative transfer |
| 1.3 | Learned contextual reuse gate |
| 1.4 | Bayesian updates and paid observations |
| 1.5 | Cost-aware VOI |
| 1.6 | Added margin failed to improve |
| **1.7** | **Exact action stability and interaction-error certificates** |

## Reproduce

Python 3.10+; NumPy for historical experiments. On Windows PowerShell:

```powershell
python -m pip install numpy
$env:PYTHONPATH='src'
$env:OPENBLAS_NUM_THREADS='1'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_i --out experiments/reproduced_i --seeds 500 --eps 0.15
python -m agentic_crystallization.stage_i --out experiments/reproduced_i2 --seeds 500 --eps 0.30
```

## Package navigation

- `src/agentic_crystallization/stability.py` — pure mathematical certificate APIs.
- `src/agentic_crystallization/stage_i.py` — deterministic audit and receipts.
- `tests/test_stability.py` — theorem, adversarial corners, determinism.
- `experiments/stage_i/`, `stage_i_replication/` — new CSV, JSON and manifest outputs.
- `docs/WHITE_PAPER.md` — derivations, proofs, limitations and next tests.
- `docs/archive/` — earlier full papers and README snapshots.
- `PACKAGE_SHA256SUMS.json` — integrity index.

**Next:** independently calibrate simultaneous error coverage under drift. Do not promote an algorithm into Pegasus until real task evaluation supports its utility and safety.
