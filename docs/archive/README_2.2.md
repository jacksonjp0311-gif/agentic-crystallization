# AGENTIC CRYSTALLIZATION
### Version 2.2 — Risk-Adaptive Verification

![Risk-adaptive verification across synthetic environments](assets/stage_n_policy_utility.png)

> **When should an adaptive agent verify a retained procedure before using it again?**

**Status:** An executable, reproducible **synthetic research system**, not a proven self-sustaining AI or physical crystallization phenomenon. All prior v1.0–v2.1 research is preserved.

[**Start**](#what-this-does) · [**Results**](#independent-experiment) · [**Whitepaper**](docs/WHITE_PAPER.md) · [**Mathematics**](docs/MATHEMATICS_2.2.md) · [**Algorithm**](docs/ALGORITHM_CARD_2.2.md) · [**Source**](src/agentic_crystallization/risk_verification.py) · [**Tests**](tests/test_stage_n.py) · [**For agents**](docs/FOR_AGENTS.md) · [**v2.1 paper**](docs/archive/WHITE_PAPER_2.1.md)

## What this does

Agentic Crystallization studies how agents can discover and retain useful procedure combinations, while maintaining evidence of their utility. The v2.2 instrument addresses a narrower problem: *when should a previously useful procedure be checked again?* It compares a risk-triggered predeployment audit with fixed schedules, blind reuse, cue-only switching, and a safe baseline.

The system uses two finite whitelisted procedures and an independent oracle-generated task stream. It does not execute arbitrary generated code, modify model weights, access Pegasus, or grant new permissions.

## Independent experiment

**900 held-out synthetic worlds** × 24 epochs × 7 policies = **151,200 policy-epoch records**, plus a separate 450-world replication. All policies face the same exogenous task sequence, warning, and audit samples within a world. The hidden true gain is never passed to the decision algorithm.

| Environment | Risk-adaptive utility | Periodic verification | Always verify |
|---|---:|---:|---:|
| Stationary | 27.53 | 27.62 | 26.44 |
| Abrupt change | 27.20 | 27.62 | 26.46 |
| Gradual drift | 17.49 | 17.42 | 16.92 |
| Recurring patterns | **25.96** | 18.28 | 26.44 |
| Misleading warning | 24.17 | **27.62** | 26.45 |
| Deceptive audit | **−9.86** | −9.72 | −10.88 |
| Unlearnable | −0.47 | −0.38 | −1.54 |

Higher is better. All values are **synthetic mean utility per epoch**. The risk controller helps on recurring patterns relative to periodic checks, but does not dominate every comparator. Under deliberately false audit evidence, every auditing policy can certify harmful behavior. See the [full results and confidence intervals](docs/WHITE_PAPER.md#5-independent-holdout-results).

## Mathematical contribution

The v2.2 algorithm combines a *finite-horizon simultaneous current-epoch certificate* with a **nominal** Bayesian warning score and a bounded audit-cost decision. It explicitly labels any reuse without a fresh audit as **stale**, even when that reuse happens to succeed.

The important limitation: a correct statistical bound for an honest audit channel does not guarantee that the channel represents the real environment, nor that an action remains good after the audit.

## Reproduce

Requires Python 3.10+ and NumPy for historical tests. From the extracted package root:

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_n --out experiments/replay_n --start-seed 5000 --count 100
python scripts/verify_package.py .
```

On Linux/macOS, prefix Python commands with `PYTHONPATH=src` rather than setting `$env:PYTHONPATH`.

`experiments/stage_n_holdout/` contains the exact raw results, source hashes, protocol, summary, and SHA-256 checksums. Reproduction must use an empty output directory; the runner refuses to overwrite results.

## Repository navigation

```text
README.md                          Human-facing research guide
Agentic_Crystallization_2.2.pdf  Full whitepaper
src/agentic_crystallization/
  risk_verification.py            New risk-audit decision and certificate
  stage_n.py                      Synthetic world generator and experiment
  renewal_core.py                 Preserved v2.1 self-regulation
  crystal_core.py                 Preserved v2.0 closed-loop prototype
  stage_*.py                      Earlier experiments
experiments/
  stage_n_development/            Development cohort
  stage_n_holdout/                Frozen held-out cohort
  stage_n_replication/            Independent replication
  stage_m_holdout/                v2.1 evidence
  ...                             Historical research retained
docs/
  WHITE_PAPER.md                  Complete current research paper
  MATHEMATICS_2.2.md              Derivations, assumptions and counterexamples
  ALGORITHM_CARD_2.2.md           Agent-facing implementation contract
  FOR_AGENTS.md                   Research context and claim boundaries
  archive/                        Historical papers
assets/                            Charts and prior figures
tests/                             Historical and new tests
PACKAGE_SHA256SUMS.json           File-integrity inventory
```

## What comes next

A stronger next experiment would **calibrate** the warning likelihood and change hazard from independently labeled data, carry uncertainty through the audit decision, and evaluate conservative abstention under feedback-integrity failures. Structural phase-transition research remains a separate, unproven hypothesis.

**License:** Not assigned. Select a license before public publication.

## Sealed historical release

The complete [v2.1 ZIP](docs/archive/Agentic_Crystallization_2.1_COMPLETE.zip) and [v2.1 PDF](docs/archive/Agentic_Crystallization_2.1.pdf) are included without modification, in addition to the unpacked historical code and experiment data.
