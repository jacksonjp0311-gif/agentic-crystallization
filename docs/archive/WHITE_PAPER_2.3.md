# Agentic Crystallization v2.3
## Feedback Integrity, Independent Anchors, and the Common-Mode Impossibility Boundary

**Version:** 2.3.0 · October 2026  
**Research status:** Reproducible synthetic study. No real Pegasus self-improvement, general learning-to-learn, or critical crystallization transition established.

[Mathematical derivations](MATHEMATICS_2.3.md) · [Algorithm card](ALGORITHM_CARD_2.3.md) · [Source](../src/agentic_crystallization/feedback_integrity.py) · [Raw holdout](../experiments/stage_o_holdout/runs.csv) · [Frozen source hashes](../experiments/stage_o_frozen_source.json) · [v2.2 paper](archive/WHITE_PAPER_2.2.md)

## Abstract

Prior Agentic Crystallization releases demonstrated synthetic higher-order procedure interactions, context-dependent transfer, sequential certification, and risk-adaptive verification. Version 2.2 exposed a fundamental vulnerability: deceptive feedback can make an agent confidently adopt harmful procedures. Version 2.3 tests whether a second independently generated measurement channel can identify feedback corruption without giving the controller access to hidden true outcomes. We derive simultaneous finite-horizon concentration bounds, a channel-disagreement test, a conservative two-source certification rule, and a simple observational-equivalence impossibility result. On 1,200 untouched synthetic worlds, the integrity guard detected 1,904 incompatibilities in each single-channel corruption regime and issued zero incorrect fresh certificates in those regimes. Under common-mode corruption, both channels agreed while the guard issued 600 incorrect fresh certificates. Thus cross-checking is useful under explicit independent-honesty assumptions but cannot establish truth from agreement alone. It also incurs substantial verification and abstention costs; simpler policies frequently achieve higher utility when their feedback channel is honest.

## 1. Scientific continuity

Agentic Crystallization is a conditional hypothesis about useful, retained procedure structures—not a physical identity with crystal nucleation. The research claims remain separated:

| Hypothesis | Evidence at v2.3 |
|---|---|
| H1: nonadditive procedure utility | Planted synthetic interactions and exact Möbius identities; no real-agent confirmation |
| H2: nonlinear critical transition in adaptive efficiency | **Not established** |
| H3: validated clusters increase subsequent learning efficiency | Restricted synthetic transfer and closed-loop demonstrations, not a general proof |
| H4 (new): independent measurement can detect some feedback corruption | **Supported conditionally in the synthetic test**; common-mode counterexample |

The v1.0–v2.2 code, raw experiments, original documents, and sealed v2.2 release remain preserved. No prior failure was reclassified as a success.

## 2. Why feedback integrity matters

A certificate about an observed reward stream is not necessarily a certificate about the real deployment environment. Let the true gain of procedure \(a\) at epoch \(t\) be \(g_t(a)\). The agent observes a primary stream \(X^P\) and, when available, an anchor stream \(X^A\). Honest streams have conditional means \(g_t(a)\); a corrupt stream can instead report a biased mean. Neither a large sample size nor internal consistency can correct systematic common-mode bias.

A safe baseline with zero gain is always available. Procedures A and B are finite, whitelisted choices, not arbitrary generated code. The controller never sees hidden \(g_t\) when deciding.

## 3. The mathematical certificate

For two channels, two procedures, and 24 prespecified epochs, a simultaneous two-sided Hoeffding radius for bounded observations in \([-1,1]\) is

\[
\boxed{r_c=\sqrt{\frac{2}{n_c}\log\left(\frac{2\cdot2\cdot2\cdot24}{\alpha}\right)}}.
\]

With \(\alpha=.05\) and \(n_P=n_A=384\), \(r_c\approx0.20733\). Under honest sampling and equal channel expectations, a discrepancy greater than \(r_P+r_A\) rejects the joint honesty model with a familywise false-alarm probability bounded by \(\alpha\) over the prespecified horizon.

For an anchor-preferred action \(a^*\), the condition

\[
\boxed{\widehat g^A_t(a^*)-r_A>\max\{0,\widehat g^A_t(b)+r_A\}}
\]

certifies it as better than the baseline and competing action for the current epoch, **only if the anchor is honest and representative**. The integrity guard additionally requires primary-anchor agreement. A disagreement causes HOLD, not an inference about which source is correct.

The full derivations, calibration intervals, and observational-equivalence proof appear in [MATHEMATICS_2.3.md](MATHEMATICS_2.3.md).

## 4. Training calibration and experiment design

A separate balanced, labeled training set contains 3,000 synthetic changed examples and 3,000 unchanged examples. The estimated warning sensitivity was **0.8550** (simultaneous 95% Hoeffding interval [0.82798, 0.88202]); specificity was **0.89967** ([0.87264, 0.92669]). The environmental-change hazard remains a declared assumption. The calibrated warning parameters are frozen before holdout evaluation. Misleading-warning experiments intentionally violate calibration stationarity.

The independent experiment uses **10 environmental regimes**, **8 policies**, **24 epochs**, and **120 fresh seeds per regime**: 1,200 worlds and 230,400 policy-epoch records. A disjoint 60-seed-per-regime replication contributes 600 additional worlds and 115,200 records. Development used 30 seeds per regime. Source hashes were frozen before holdout. Preliminary development experiments that prompted safety and calibration repairs are retained with their original source hashes, but the superseded source snapshots are not bundled; those diagnostics are not independently reproducible from the final source and are excluded from final claims.

Policies: cross-channel `guard`; dual-channel periodic; anchor-only periodic, risk-based, and always; primary-only risk-based and periodic; and baseline-only. All receive the same exogenous task sequence and per-epoch pre-generated observations. Primary sampling costs 0.002 per observation and anchor sampling 0.006. A two-action audit of each channel uses 384 samples per action. Per-epoch utility is \(80g_t(a_t)\) minus actual audit costs. Missing anchors are not silently replaced by model estimates.

The regimes are stationary, abrupt, gradual, recurrent, deceptive primary, misleading warning, missing anchor, deceptive anchor, common-mode deception, and unlearnable.

## 5. Independent holdout results

![Mean utility by policy and environment](../assets/stage_o_utility.png)

| Environment | Guard utility | Primary periodic | Anchor periodic | Guard false fresh certs | Guard disagreement alarms |
|---|---:|---:|---:|---:|---:|
| Stationary | 26.09 | **27.58** | 26.85 | 0 | 0 |
| Abrupt | 25.73 | **27.62** | 26.85 | 0 | 0 |
| Gradual | 14.47 | **17.03** | 16.23 | 0 | 0 |
| Recurrent | **23.80** | 18.28 | 17.48 | 0 | 0 |
| Deceptive primary | **4.38** | -9.68 | 26.73 | 0 | **1,904** |
| Deceptive anchor | **4.41** | 27.62 | -10.52 | 0 | **1,904** |
| Common-mode corruption | -11.32 | -9.64 | -10.52 | **600** | **0** |
| Missing anchor | 7.48 | 27.58 | 8.91 | 0 | 0 |
| Misleading warning | 20.04 | 27.58 | 26.77 | 0 | 0 |
| Unlearnable | -1.85 | -0.38 | -1.15 | 0 | 0 |

Values are mean **synthetic utility per epoch**; higher is better. Bold highlights a notable comparison, not a global winner. The baseline-only policy has utility zero in every regime. The guard is therefore inferior to the baseline under common-mode corruption and on unlearnable tasks.

**Single-channel corruption:** The guard issued zero incorrect *fresh* certificates in either 120-world single-channel corruption cohort, but held for roughly 1,900 epochs and incurred substantial audit costs. It did not eliminate every harmful *stale* deployment: 16 occurred in each cohort before fresh evidence resolved the change.

**Common-mode corruption:** The guard produced 600 incorrect fresh certificates and 1,920 harmful deployments while reporting zero channel disagreements. This is a direct counterexample to the proposition that agreement certifies truth.

**Utility comparisons:** Guard minus primary-periodic mean utility was +14.06 under deceptive primary (descriptive paired world-bootstrap 95% interval [+13.87,+14.21]), but -23.20 under deceptive anchor ([-23.34,-23.10]). Under recurrence it was +5.52 ([+5.00,+6.03]); under stationarity -1.48 ([-1.55,-1.39]). These intervals are descriptive, not prespecified confirmatory tests.

![Alarms versus false certifications](../assets/stage_o_integrity.png)

## 6. Replication and integrity

The independent 600-world replication preserves the key pattern: **zero** guard false fresh certifications under either single-channel corruption; **289** false fresh certifications under common-mode corruption. The common-mode false-certificate count varies with sampling, but the underlying identifiability failure does not.

All experiments use an oracle solely for *post-decision scoring*. No hidden true gain, regime label, or corruption indicator is passed to the controller. The holdout source, protocol, raw CSV, and summary were reproduced byte-for-byte from the frozen code. The exact SHA-256 source hashes are recorded in [stage_o_frozen_source.json](../experiments/stage_o_frozen_source.json).

## 7. The key impossibility result

Suppose two environments produce identical distributions over all observed primary samples, anchor samples, and warnings, but have opposite true deployment gains. Every algorithm that only sees those observations must have the same decision distribution in both worlds. It cannot guarantee the correct non-baseline decision in both. This is an elementary observational-equivalence argument, not a newly discovered theorem.

Therefore **no amount of internally consistent feedback can establish external correctness without an independently justified link between observations and outcomes**. A true anchor must earn its status through independent provenance, interventions, or external validation—not through being called an anchor.

## 8. Failure cases and limitations

- **Cost:** Dual-channel verification reduces utility in many honest environments; periodic single-channel auditing can be cheaper and better.
- **HOLD:** A disagreement is not a proof of which channel is wrong. The guard abstains, sometimes for long periods.
- **Missing anchor:** When the independent channel is unavailable, the guard loses opportunities rather than inventing evidence.
- **Stale deployment:** Harm can occur between audits, even when fresh certificates are correct.
- **Common-mode corruption:** Both channels can agree and be wrong. No finite sample size solves that without stronger assumptions.
- **Calibration drift:** The warning cue's training sensitivity/specificity can fail after deployment.
- **Synthetic setting:** The generator uses only two procedures and known finite task families. The experiment does not show autonomous skill creation, a real-agent gain, or a physical phase transition.

## 9. Implication for a future agent runtime

The correct architectural lesson is not to add more voting agents and treat consensus as ground truth. It is to distinguish **evidence diversity**, **measurement independence**, **calibration provenance**, **current certification**, **stale reuse**, and **unresolvable uncertainty**. An eventual Pegasus adapter could read authorized receipts and produce an inactive audit recommendation, but this research package grants no runtime authority and modifies no Pegasus code.

## 10. Next research milestone

Version 2.4 should investigate *selective independent audits* that spend less while retaining sensitivity to single-channel corruption; evaluate anchor provenance and failure correlation explicitly; add adversarially correlated corruption, gradual calibration drift, and post-audit deployment shift. The baseline and periodic policies must remain strong competitors. No upgrade should be promoted merely because it adds complexity.

## Reproduction

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_o --out experiments/reproduced_o --start-seed 8000 --count 120
python scripts/verify_package.py .
```

[Algorithm card](ALGORITHM_CARD_2.3.md) · [Mathematics](MATHEMATICS_2.3.md) · [Calibration data](../experiments/stage_o_holdout/calibration.json) · [Raw holdout](../experiments/stage_o_holdout/runs.csv) · [Paired analysis](../experiments/stage_o_holdout/analysis.json) · [Tests](../tests/test_stage_o.py) · [Prior research](archive/WHITE_PAPER_2.2.md)
