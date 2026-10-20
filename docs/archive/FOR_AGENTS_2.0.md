# Agentic Crystallization v2.0 — Research-agent handoff

**Purpose:** Standalone, repeatable research on an autonomous *bounded* procedure-selection and retention loop, not a self-modifying general intelligence. This package contains the complete prior v1.0–v1.9 archive and a verified final v2.0 research cohort.

## Research authority boundaries

1. No Pegasus integration, external action rights, skill self-installation or autonomous code deployment. Do not infer them.
2. New `crystal_core.py` admits **only whitelisted XOR procedures**, never shell/Python expressions or arbitrary tool calls.
3. Certification is a conditional statistical statement of **gain over baseline** only. It requires **independent fresh validation** and a **justified direct gain-shift bound**; absent bound means HOLD.
4. Retained memory is historical context and candidate discovery acceleration, **not lasting authority**. Every new epoch needs a fresh certificate.
5. Error budget is allocated as α/[e(e+1)] for unlimited potential episodes of one lifecycle. Never reset epoch count to conceal earlier certifications.
6. No external data/work can be inferred from local world generator. Expected performance on real agents is **unmeasured**.
7. Negative controls including mislabeled shift and unrepresentable four-way parity are primary, not optional; preserve them.
8. Protect historic archived files and SHA manifests; never change or suppress failures to improve a release score.

## Files in research order

[Human README](../README.md) → [Detailed mathematics](MATHEMATICS.md) → [Algorithm card](ALGORITHM_CARD.md) → [Whitepaper](WHITE_PAPER.md) → [Experiment design](EXPERIMENTS.md) → [Claim ledger](CLAIM_LEDGER.md) → [Core](../src/agentic_crystallization/crystal_core.py) → [World generator](../src/agentic_crystallization/stage_l.py) → [Regression tests](../tests/test_crystal_core.py) → [Final raw results](../experiments/stage_l_holdout/runs.csv).

## Exact final experiment

- `stage_l_holdout`: seeds 80000–80039; 40 worlds × 12 epochs × 7 regimes × 4 policies = 13,440 rows.
- `stage_l_independent_replay`: reproduced from frozen source; the four data/protocol/manifest artifacts match byte-for-byte.
- `docs/PREREGISTRATION_STAGE_L.json`: code hashes and comparisons written before the final run.
- `demos/recurrent/ledger.jsonl`: 12 unattended synthetic episodes and replayable state.

Recurrent: crystal certifies 480/480 epochs with 360 memory reactivations, uses approximately 25% fewer task observations and 74% fewer procedure-prediction operations than memoryless. Fixed reuse certifies 280/480. Stationary fixed reuse has slightly **higher** net synthetic utility than the crystal. **False shift: 440 false out of 440 crystal certificates** in a deliberately impossible environment contract. Unknown shift: HOLD without charged evidence.

## Developer commands

```bash
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
python scripts/verify_stage_l.py experiments/stage_l_holdout --repo .
PYTHONPATH=src python scripts/verify_crystal_ledger.py demos/recurrent/ledger.jsonl
PYTHONPATH=src python -m agentic_crystallization.stage_l --out experiments/new_runs --start-seed 95000 --count 3
```

In PowerShell: `./run.ps1 -Action test`, `./run.ps1 -Action verify`, `./run.ps1 -Action demo`.

## Future experiments

Learn a robust and auditable shift bound using independent target-environment reference tasks; study refusal/coverage tradeoffs under unknown shift, candidate class expansion, non-IID data, and delayed feedback. Keep all new simulator/evaluator seed ranges disjoint. Do not claim new scientific laws or autonomous self-learning until demonstrated on independent data and reproducible real workloads.
