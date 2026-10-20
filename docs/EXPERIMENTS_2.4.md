# Agentic Crystallization v2.4 — Experiment Record

## Frozen design

- Development: seeds 4200–4217, nine regimes, eight parameter configurations, chosen before holdout.
- Holdout: seeds 9000–9079, 13 regimes, 24 epochs, eight policies, **199,680 policy-epoch records**.
- Independent replication: seeds 11000–11039, **99,840 policy-epoch records**.
- No true gains in policy inputs. Paid-reference scheduling commits before reference means are supplied to the decision function.
- Unknown or compromised reference produces no guarantee; all-corrupt environment is an explicit required failure case.

## Experimental policy results

| Regime | v2.4 triad | v2.3 guard | Primary only | Reference only | Triad false fresh | Triad alarms |
| --- | --- | --- | --- | --- | --- | --- |
| Stationary | +23.37 | +25.99 | +27.62 | +24.93 | 0 | 0 |
| Abrupt change | +23.29 | +25.82 | +27.56 | +24.93 | 0 | 0 |
| Gradual drift | +9.66 | +14.69 | +17.41 | +16.01 | 0 | 0 |
| Recurring patterns | +13.84 | +24.09 | +18.22 | +15.59 | 0 | 0 |
| Corrupted primary | +3.16 | +4.49 | -9.72 | +24.93 | 0 | 479 |
| Corrupted anchor | +3.19 | +4.49 | +27.62 | +24.93 | 0 | 480 |
| Shared primary + anchor error | +3.16 | -11.31 | -9.66 | +24.93 | 0 | 479 |
| Compromised reference | +3.16 | +25.82 | +27.56 | -12.41 | 0 | 479 |
| All three compromised | -13.96 | -11.31 | -9.66 | -12.41 | 320 | 0 |
| Reference missing | +7.76 | +25.82 | +27.56 | +8.31 | 0 | 0 |
| Anchor missing | +4.31 | +7.49 | +27.56 | +24.93 | 0 | 0 |
| Misleading warning | +23.39 | +20.04 | +27.62 | +24.93 | 0 | 0 |
| No learnable advantage | -6.14 | -1.89 | -0.38 | -4.10 | 0 | 0 |

## Verify all source, data and receipt constraints

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -q
python scripts/verify_stage_p.py . --cohort stage_p_holdout
python scripts/verify_stage_p.py . --cohort stage_p_replication
python scripts/verify_package.py .
```

## Independent replay (optional; creates a new folder)

```powershell
$env:PYTHONPATH='src'
python -m agentic_crystallization.stage_p --out experiments/reproduced_stage_p --start-seed 9000 --count 80 --max-age 4 --no-cue
```

Compare the SHA256 hashes of `runs.csv`, `summary.json`, `protocol.json` and `SHA256SUMS.json` with the frozen holdout. Do not overwrite the authoritative experiment folder.

## Research-integrity boundary

The frozen source hashes protect provenance **within the artifact**, not against a malicious party replacing both the data and checksum files. The SHA256 manifest is not a digital signature. Trustworthiness of the reference channel is an **assumption under study**, not established by manifest checks.

[Holdout manifest](../experiments/stage_p_holdout/SHA256SUMS.json) · [Replication manifest](../experiments/stage_p_replication/SHA256SUMS.json) · [Tuning record](../experiments/stage_p_tuning/tuning.json) · [Source freeze](../experiments/stage_p_frozen_source.json) · [Comparative uncertainty analysis](../experiments/stage_p_analysis.json)
