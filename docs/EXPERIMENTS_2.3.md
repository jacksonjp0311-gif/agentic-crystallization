# Stage O — v2.3 Independent Experiment and Replication

[README](../README.md) · [Formal paper](WHITE_PAPER.md) · [Mathematics](MATHEMATICS_2.3.md) · [Frozen source](../experiments/stage_o_frozen_source.json)

## Experiment design

- **Question:** Can a guarded dual-channel evaluator detect evidence corruption without falsely converting channel agreement into proof of correctness?
- **Primary/anchor:** Independently generated audit samples in honest worlds; either or both can be systematically corrupted.
- **Actions:** Two whitelisted procedures and a safe zero-gain baseline; hidden true outcomes score decisions post hoc.
- **Training:** 3,000 balanced labeled positives and 3,000 negatives from seeds 1000–3999 for cue sensitivity and specificity; prior hazard is declared, not fitted.
- **Development:** Seeds 4000–4029, 30 worlds per regime. Interim repaired designs archived as diagnostics, not confirmed results.
- **Frozen holdout:** Seeds 8000–8119 inclusive, 120 worlds per regime, 10 regimes, 8 policies, 24 epochs, 230,400 receipts.
- **Independent replication:** Seeds 10000–10059 inclusive, 60 per regime; 115,200 receipts.
- **Fixed costs:** 384 samples **per candidate** per channel audit; primary cost 0.002/sample; anchor 0.006/sample; task reward 80 × true gain.
- **Statistics:** Paired-world descriptive bootstrap intervals, not preregistered confirmatory significance tests. Common world draws used for matched policy comparison.

## Results (mean synthetic utility per epoch)

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

Notes: The guard records a *fresh* certificate separately from a *stale* deployment. It cannot determine which channel is wrong when they disagree. Honest channel equality is an assumption, and the false-alarm probability is a finite-horizon familywise bound contingent on valid honest sampling. The guard spends more on auditing than single-channel comparators.

### Negative controls

- **Deceptive primary:** Guard fresh false certs 0, alarms 1,904, harmful deployments 16.
- **Deceptive anchor:** Guard fresh false certs 0, alarms 1,904, harmful deployments 16.
- **Common-mode:** Guard fresh false certs **600**, alarms **0**, harmful deployments **1,920**, mean utility **-11.31782**.
- **Unavailable anchor:** No silent substitution of primary for anchor; HOLD and lost opportunity are explicitly charged.
- **Unlearnable:** No fresh positive certification, but verification still costs resources, so baseline is superior.

### Independent replication

Shared corruption again bypassed the agreement test: 289 incorrect fresh certificates with 0 alarms. In each isolated-corruption regime, guard false fresh certificates remained zero and guard alarm count was 958.

## Evidence and integrity files

- [Holdout raw receipts](../experiments/stage_o_holdout/runs.csv)
- [Holdout protocol with frozen source hashes](../experiments/stage_o_holdout/protocol.json)
- [Holdout detailed summary](../experiments/stage_o_holdout/summary.json)
- [Holdout paired analysis](../experiments/stage_o_holdout/analysis.json)
- [Holdout calibration](../experiments/stage_o_holdout/calibration.json)
- [Replication raw receipts](../experiments/stage_o_replication/runs.csv)
- [Replication summary](../experiments/stage_o_replication/summary.json)
- [Freeze record](../experiments/stage_o_frozen_source.json)

### Run the integrity checks

```bash
python scripts/verify_stage_o.py . --cohort stage_o_holdout
python scripts/verify_stage_o.py . --cohort stage_o_replication
```

Verifier checks source hashes, stored file SHA-256, unique receipt keys, exact cohort denominators, and summary reconciliation; **it does not prove that a simulated feedback channel represents ground truth**.
