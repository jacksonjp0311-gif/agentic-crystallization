# AGENTIC CRYSTALLIZATION 2.3 — Research Context for Coding Agents

**Research-only package.** Goal: measure when independent evidence can detect corruption of procedure-evaluation feedback. Do not equate internal agreement with external correctness.

## Key files

- [README](../README.md) — human-facing purpose, experiment and commands
- [Whitepaper](WHITE_PAPER.md) — research hypotheses, complete outcomes and failures
- [Mathematics](MATHEMATICS_2.3.md) — conditional concentration theorem, discrepancy rule, best-action certificate, impossibility result
- [Algorithm](ALGORITHM_CARD_2.3.md) — precise state transitions and HOLD behavior
- [Implementation](../src/agentic_crystallization/feedback_integrity.py)
- [Simulation](../src/agentic_crystallization/stage_o.py)
- [Tests](../tests/test_stage_o.py)
- [Frozen code hashes](../experiments/stage_o_frozen_source.json)
- [Holdout protocol](../experiments/stage_o_holdout/protocol.json)
- [Raw holdout](../experiments/stage_o_holdout/runs.csv)
- [Prior v2.2 paper](archive/WHITE_PAPER_2.2.md)

## Scientific invariants

1. H1 (nonadditivity) has only planted synthetic support; H2 (phase transition) and H3 (general learning-to-learn) remain unestablished.
2. The controller receives observed cues and audit samples, never hidden true deployment gain or regime identity.
3. Channel honesty is an assumption. Agreement does not establish honesty.
4. Disagreement cannot identify which channel is corrupted; the guard must HOLD.
5. A fresh certificate is current-epoch only. Stale reuse is explicitly counted, not silently certified.
6. Training calibration is not a guarantee after cue distribution shift. Hazard remains a fixed assumption.
7. Maintain baseline-only, primary-only and anchor-only policies as strong comparators.
8. Preserve the common-mode counterexample, preliminary failed design, original historical receipts, and all HOLDs.
9. Do not modify protected graders, Pegasus authority boundaries, or old experimental results.
10. Preserve exact source hashes, seed ranges, cost definitions, and full policy-epoch denominators.

## Reproduce

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_o --out experiments/reproduced_o --start-seed 8000 --count 120
python scripts/verify_package.py .
```

This is a deterministic synthetic Python experiment, not a validated live agent or physical crystallization phenomenon.
