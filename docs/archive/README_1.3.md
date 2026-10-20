# Agentic Crystallization v1.3
### Learned relevance gating, negative transfer and full acquisition cost

> **Does past validated knowledge help with the next problem, and can an agent learn when not to use it?**

**Research status:** Deterministic synthetic experiments only. No demonstrated physical crystallization, adaptive phase transition, or Pegasus self-improvement.

[Whitepaper](docs/WHITE_PAPER.md) · [Math](docs/WHITE_PAPER.md#2-mathematics-carried-forward) · [Protocol](docs/WHITE_PAPER.md#4-experimental-design) · [Results](docs/WHITE_PAPER.md#5-held-out-results) · [Python implementation](src/agentic_crystallization/stage_e.py) · [Tests](tests/test_stage_e.py) · [Agent context](docs/FOR_AGENTS.md) · [Previous whitepaper](docs/archive/WHITE_PAPER_1.2.md)

![Held-out comparison](assets/stage_e_utility.png)

## What changed

- v1.0: detected planted pairwise and higher-order procedure interactions.
- v1.1: confirmed functional interactions matter more than misleading graph density.
- v1.2: prior validated triples helped related-task discovery but harmed unrelated-task discovery.
- **v1.3: trained a relevance gate on separate worlds, charged the first-discovery cost, and measured its benefit and limitations on 1,800 new worlds.**

## The result

| Next-task mixture | Learned gate vs no prior | Learned gate vs always reuse |
|---|---:|---:|
| 25% related | +2.123 utility | +1.546 utility |
| 75% related | +9.494 utility | **−0.906 utility** |

The gate is not universally optimal. When most tasks are related, unconditional reuse beats it in this benchmark. All outcomes are synthetic and oracle-graded; planted latent groups and a noisy binary relevance cue are assumptions.

## Reproduce

Python 3.10+ required. The experiment and tests use the Python standard library; optional visualization scripts use NumPy and Matplotlib.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m agentic_crystallization.stage_e --out experiments/reproduced_stage_e --start-seed 2000 --count 300
```

On Windows PowerShell, set `$env:PYTHONPATH='src'` and then run the two `python -m` commands without the inline environment prefix.

## Project layout

```text
src/agentic_crystallization/   Versioned simulation implementations
  stage_a.py                  Ground-truth interactions (v1.0)
  stage_b.py                  Density/negative controls (v1.1)
  stage_d.py                  Fixed prior transfer (v1.2)
  stage_e.py                  Learned relevance gate (v1.3)
tests/                        All versioned tests
experiments/                  Raw per-world data, analyses, manifests, checksums
assets/                       Figures
docs/WHITE_PAPER.md           Current mathematics, results, caveats
docs/archive/                 Prior papers and README
PACKAGE_SHA256SUMS.json       Complete package integrity manifest
```

## Scientific contract

Each version retains prior code and data, adds tests before changing claims, and records failures and counterexamples. The original v1.2 results are preserved. The gate never sees held-out targets during training. The score includes first-discovery acquisition costs. The study does not claim a new physical force, a universal threshold, or autonomous self-improvement.

**Next research direction:** graded relatedness, posterior updating after failed queries, and controlled finite-size threshold experiments. **License:** not assigned; select one before publication.
