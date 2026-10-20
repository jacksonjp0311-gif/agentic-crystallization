# AGENTIC CRYSTALLIZATION
## v2.3 — Feedback Integrity, Independent Anchors, and an Impossibility Boundary

![Agentic Crystallization research banner](assets/crystal_banner.png)

> **When two validators agree, what justifies believing either one?**

**Research status:** Executable synthetic research. Neither genuine self-sustaining adaptation nor physical crystallization nor Pegasus performance improvements have been demonstrated. The full preceding research history is retained.

[**Results**](#independent-results) · [**Whitepaper**](docs/WHITE_PAPER.md) · [**PDF**](Agentic_Crystallization_2.3.pdf) · [**Formal mathematics**](docs/MATHEMATICS_2.3.md) · [**Algorithm card**](docs/ALGORITHM_CARD_2.3.md) · [**Experiments**](docs/EXPERIMENTS_2.3.md) · [**Claims and limitations**](docs/CLAIM_LEDGER_2.3.md) · [**Agent packet**](docs/FOR_AGENTS.md) · [**Continuity**](docs/CONTINUITY_AUDIT_2.3.md) · [**Version history**](CHANGELOG.md)

### What changed in v2.3

Versions 2.0–2.2 developed a bounded synthetic adaptation loop, fresh revalidation, and risk-adaptive checking. Version 2.3 asks whether the **evaluation feedback itself** can be trusted. Two separately generated channels measure the same two whitelisted procedures. A **guard** rejects a fresh certificate when they strongly disagree, but it never assumes that agreement proves honesty.

The guard is compared against seven simpler controls, including two single-channel periodic policies and a zero-gain safe baseline. The task generator's hidden true gains are used **only to score outcomes after the policy decides**. All code is standalone Python; nothing is integrated into Pegasus.

![Guard utility across synthetic feedback environments](assets/stage_o_utility.png)

## Independent results

**Holdout:** 120 seeds × 10 environmental regimes = **1,200 synthetic worlds**, 24 epochs each, 8 policies: **230,400 policy-epoch records**. **Independent replication:** 60 seeds × 10 regimes = **600 worlds**, another **115,200 records**. Development used separate seeds and the source hash was frozen before holdout.

| Regime | Guard | Primary periodic | Anchor periodic | Guard false fresh certs | Guard alarms | Guard harmful deployments |
|---|---:|---:|---:|---:|---:|---:|
| stationary | 26.09 | 27.58 | 26.85 | 0 | 0 | 0 |
| abrupt | 25.73 | 27.62 | 26.85 | 0 | 0 | 16 |
| gradual | 14.47 | 17.03 | 16.23 | 0 | 0 | 0 |
| recurrent | 23.80 | 18.28 | 17.48 | 0 | 0 | 102 |
| deceptive primary | 4.38 | -9.68 | 26.73 | 0 | 1904 | 16 |
| deceptive anchor | 4.41 | 27.62 | -10.52 | 0 | 1904 | 16 |
| common mode | -11.32 | -9.64 | -10.52 | 600 | 0 | 1920 |
| missing anchor | 7.48 | 27.58 | 8.91 | 0 | 0 | 16 |
| misleading cue | 20.04 | 27.58 | 26.77 | 0 | 0 | 117 |
| unlearnable | -1.85 | -0.38 | -1.15 | 0 | 0 | 0 |

**Utility:** Mean synthetic utility **per epoch**, with 80 tasks per epoch and audit costs charged by actual sampled channel. Higher is better. Baseline-only = 0. The guard does **not** dominate simpler policies.

### What the numbers actually establish

- **Single-channel corruption:** The guard raised **1,904 disagreement alarms** and issued **zero incorrect fresh certificates** in *each* 120-world single-channel corruption regime. It still incurred **16 harmful stale deployments** in each regime before fresh evidence resolved change.
- **Common-mode corruption:** Both channels were biased together. The guard raised **zero disagreement alarms**, issued **600 incorrect fresh certificates**, and incurred **1,920 harmful deployments**. Its mean utility fell below the zero-gain baseline.
- **Honest settings:** Primary-only periodic validation was more economical than the guard in stationary and abrupt regimes. The guard beat primary-periodic in recurring patterns, but its verification cost was significant.
- **Replication:** Both single-channel false-fresh-certificate counts remained **zero**; shared corruption produced **289** incorrect fresh certificates and **zero** disagreement alarms in the separate 600-world replication.

![Channel alarms and fresh certification failures](assets/stage_o_integrity.png)

**Core interpretation:** A disagreement rejects the hypothesis that both channels are accurate. Agreement is insufficient to prove joint honesty. Two observationally indistinguishable worlds with opposite true outcomes cannot be distinguished by any controller that sees only these channels; independent external grounding is required.

## Mathematical core

For action \(a\), epoch \(t\), channel \(c\), and independently bounded observations in \([-1,1]\):

\[
r_c=\sqrt{\frac{2}{n_c}\log\left(\frac{2TKC}{\alpha}\right)}.
\]

Here \(T=24\), \(K=2\) procedures, \(C=2\) channels, \(n_c=384\) observations per action per audit, \(\alpha=0.05\). The radius is approximately **0.2073**. This is a finite-horizon Hoeffding bound for correctly specified channel means, **not** a way to establish that the channels are truthful.

A guard issues a fresh certificate for \(a^*\) only if the anchor lower bound exceeds the baseline and the competing action's upper bound, and the channels agree within their combined radii. **Stale reuse is explicitly recorded and is not a new certificate.** See the [proofs and assumptions](docs/MATHEMATICS_2.3.md).

## Reproduce on Windows

Python 3.10+ required; an internet connection may be needed to install pinned dependencies. A single PowerShell entry point is provided:

```powershell
# In the extracted Agentic_Crystallization_2.3 folder
python -m pip install -r requirements.txt
.\run.ps1 -Action test
.\run.ps1 -Action verify
.\run.ps1 -Action demo
# Optional: a new non-overwriting simulation
.\run.ps1 -Action simulate -StartSeed 90000 -Worlds 3
```

Direct cross-platform commands:

```bash
export PYTHONPATH=src OPENBLAS_NUM_THREADS=1
python -m unittest discover -s tests -q
python scripts/verify_stage_o.py . --cohort stage_o_holdout
python scripts/verify_stage_o.py . --cohort stage_o_replication
python scripts/verify_package.py .
```

The full holdout can be independently regenerated to a **new path**; the original is never overwritten:

```bash
PYTHONPATH=src python -m agentic_crystallization.stage_o --out /tmp/ac23_replay --start-seed 8000 --count 120
```

Check its generated `runs.csv`, `protocol.json`, `summary.json`, and `calibration.json` against the originals by SHA-256. The descriptive paired-world bootstrap analysis has its own fixed random seeds and is recorded in [`analysis.json`](experiments/stage_o_holdout/analysis.json).

## Repository guide

| Path | Purpose |
|---|---|
| [`docs/WHITE_PAPER.md`](docs/WHITE_PAPER.md) | Canonical full paper, including limitations and impossibility proof |
| [`docs/MATHEMATICS_2.3.md`](docs/MATHEMATICS_2.3.md) | Conditional probability bounds and derivations |
| [`docs/ALGORITHM_CARD_2.3.md`](docs/ALGORITHM_CARD_2.3.md) | Exact v2.3 guard / HOLD decisions |
| [`src/agentic_crystallization/feedback_integrity.py`](src/agentic_crystallization/feedback_integrity.py) | Decision and audit algorithm |
| [`src/agentic_crystallization/stage_o.py`](src/agentic_crystallization/stage_o.py) | Deterministic experiment generator |
| [`tests/test_stage_o.py`](tests/test_stage_o.py) | New scientific and runtime regression tests |
| [`experiments/stage_o_frozen_source.json`](experiments/stage_o_frozen_source.json) | Frozen source hashes and seed ranges |
| [`experiments/stage_o_holdout/`](experiments/stage_o_holdout/) | Original independent holdout, receipts, analysis, calibration |
| [`experiments/stage_o_replication/`](experiments/stage_o_replication/) | Disjoint independent replication |
| [`docs/archive/`](docs/archive/) | Preserved historical papers, sealed prior ZIPs and prior notes |
| [`PACKAGE_SHA256SUMS.json`](PACKAGE_SHA256SUMS.json) | Full file inventory and integrity manifest |

## Research ladder and boundaries

- **H1:** Higher-order procedure interactions were observed in planted synthetic tasks, not validated real-agent discoveries.
- **H2:** A critical adaptive crystallization transition remains **unestablished**.
- **H3:** General-purpose self-sustaining learning-to-learn remains **unestablished**; preceding versions demonstrated limited synthetic transfer.
- **H4 (v2.3):** Separate feedback streams detect some single-channel corruption **conditionally**; coordinated or common-mode corruption remains unidentifiable from agreement alone.

The added dual-channel guard incurs real verification cost, cannot eliminate stale harmful actions, and is inferior to cheaper policies in several environments. It is not a basis for granting autonomous authority over tools, files, or code updates. The honest decision in an unidentifiable state may be **HOLD**.

**Next:** Selective independent audits, explicit correlation stress tests, independent anchor provenance and post-audit shift. Require improvements against credible periodic and baseline controls before any deployment proposal.

**Licensing:** No open-source license has been assigned; do not treat the package as permission to redistribute under a particular license.
