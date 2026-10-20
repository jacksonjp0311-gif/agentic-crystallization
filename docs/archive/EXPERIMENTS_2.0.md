# v2.0 Stage L — Audited experimental protocol and measured outcomes

[README](../README.md) · [Theorems](MATHEMATICS.md) · [Whitepaper](WHITE_PAPER.md) · [Preregistered holdout contract](PREREGISTRATION_STAGE_L.json) · [Final holdout results](../experiments/stage_l_holdout/summary.json) · [Raw CSV](../experiments/stage_l_holdout/runs.csv) · [Paired analysis](../experiments/stage_l_analysis.json)

## Scope and frozen sources

The final executable core `crystal_core.py` and synthetic evaluator `stage_l.py` were SHA-256 frozen in `docs/PREREGISTRATION_STAGE_L.json` **before** examining the final 40-world cohort. The final protocol and source hashes are included in `experiments/stage_l_holdout/protocol.json` and verified by `scripts/verify_stage_l.py`.

- **Exploratory preseal smoke:** world seeds 100–101. These results preceded the final conservative budget reserve fix and are marked PRESEAL, not independent data.
- **Development cohort:** world seeds 1000–1011, 12 worlds, inspected prior to the preregistration. This cohort predates addition of protocol source hashes but uses the final algorithmic logic; do not label it final verification.
- **Independent final holdout:** seeds **80000–80039**, 40 worlds, 12 epochs, 7 environmental regimes, 4 policies: **13,440 policy-epoch rows**.
- **Independent exact replay:** same frozen source and seeds regenerated to `experiments/stage_l_independent_replay` and produced byte-identical `runs.csv`, `summary.json`, `protocol.json`, and `SHA256SUMS.json`.
- **Separate demonstration ledger:** synthetic seed 2020, recurrent regime, 12 episodes; complete JSONL receipts and deterministic recovery.

All scientific output is fully synthetic and reproducible on Python 3.10+ using standard-library modules for the new Stage L code. Original v1.0–v1.9 experiments and dependencies remain in the package.

## Generator: what the runtime actually sees

The simulator selects four distinct hidden XOR-of-three target tuples from eight independent fair bits; the runtime **never receives** the target tuple. A fifth hidden task is parity of four bits, which the candidate family cannot represent. The runtime has access to task-labeled scout observations (24), task-labeled discovery observations (96), and a fresh independent validation stream of length 512. Its allowed proposals are precisely 92 XOR expressions with 1, 2 or 3 feature indices. The deployment stream (256 independent tasks per epoch) is scored *after* a candidate is frozen. The third stream is not used for selecting or certifying candidates.

Every policy is evaluated on identical per-world/per-epoch source and deployment task data. Different exploration policies legitimately consume different numbers of observations and candidate prediction calls. Both types are charged in the synthetic utility model. A retained procedure cannot bypass current-epoch validation.

### Environmental regimes

| Regime | Programmed trajectory | Grounded expected behavior |
|---|---|---|
| Stationary | The same 3-feature task for 12 epochs | Remembered/fixed solutions cheap to reuse |
| Recurrent | A,A,B,B,A,A,C,C,A,B,A,A | Revalidate retained memories as patterns return |
| Abrupt | A,B,C,D,A,B,C,D,A,B,C,D | Recover through bounded rediscovery when catalog patterns switch |
| Noise | A,A,N,N,A,A,N,N,A,A,N,N, where N is 4-way parity | No false promotion of unavailable procedures on N |
| Bounded shift | Recurrent tasks; deployment 6% mixture with a distinct concept | Direct gain-shift allowance 0.06 valid for the synthetic candidate family |
| Unknown shift | Recurrent patterns, but no justified allowance supplied | HOLD with zero charged evaluation queries |
| False shift | Validate on A, deploy on **label inversion of A**, falsely claim allowance zero | Confident failures expose assumption dependence |

**Clarification about bounds:** The shift allowance is an externally supplied direct bound on the candidate-minus-baseline **mean gain**. In the 6%-mixture environment, the constructed parity functions permit bound 0.06. For a general bounded difference in [-1,1] and an arbitrary total-variation bound δ, the generic valid allowance is up to **2δ**, not δ. The false-shift setting intentionally violates the supplied allowance.

### Policies and comparable costs

- `crystal`: remembered-candidate scout (if memory available), otherwise bounded 92-candidate search; independent certification; memory capacity 4; stale_after 5 epochs; resource debit/credit.
- `memoryless`: same bounded search and independent certification each epoch, but no memory stored.
- `reuse_only`: discover and certify first procedure, then never search for another; must still revalidate its frozen anchor in every subsequent episode.
- `baseline`: constant 0, no experimentation.

All policies use the same sequential certificate, except baseline, which doesn't certify. Validation checkpoints `n=64,128,256,512`; lifetime type-I budget α=0.05 per **independently started controller trajectory**, allocated as α/[e(e+1)] over epochs. The testbed supplies 256 independent scoring examples per epoch and assigned synthetic revenue/compute prices. The payoff units **are arbitrary benchmark utility**, not money, energy or observed operational cost.

## Final held-out results

| Environment | Crystal certified | False cert. | Memory reactivations | Queries: crystal / memoryless | Ops: crystal / memoryless | Net synthetic utility per episode: crystal / memoryless / fixed reuse |
|---|---:|---:|---:|---:|---:|---:|
| Stationary | 480/480 | 0 | 440 | 65,472 / 97,152 | 414,912 / 4,290,432 | 1022.61 / 1020.89 / **1023.26** |
| Recurrent | 480/480 | 0 | 360 | 73,216 / 97,216 | 1,134,976 / 4,290,496 | **1021.60** / 1020.42 / 589.12 |
| Abrupt | 480/480 | 0 | 320 | 77,184 / 97,344 | 1,500,864 / 4,290,624 | **1022.35** / 1021.50 / 245.23 |
| Unlearnable interleaved | 240/480 | 0 | 200 | 162,240 / 170,880 | 2,608,320 / 4,364,160 | 502.87 / 502.43 / **503.62** |
| Valid 6% shift | 480/480 | 0 | 360 | 87,296 / 111,296 | 1,149,056 / 4,304,576 | **954.85** / 953.67 / 551.49 |
| Shift unknown | 0/480 | 0 | 0 | 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| **False shift bound** | **440/480** | **440** | 400 | 59,712 / 88,960 | 409,152 / 3,932,800 | **−944.36** / −945.76 / −1016.22 |

The unlearnable regime contains 240 learnable A epochs and 240 four-way N epochs. The crystal correctly declines to certify every N epoch. In the adverse false-shift regime, **every** issued crystal certificate is wrong: 440 false out of 440 certifications.

### Predeclared primary comparison: recurrent tasks

Relative to `memoryless`, the crystal saves exactly 600 task observations and 78,888 candidate-prediction operations per 12-epoch world in this deliberately structured benchmark. Aggregated over all worlds this is **24.69% fewer queries** and **73.55% fewer candidate operations**, with both policies certifying 480/480 episodes. The average synthetic net surplus difference is +1.1731 per epoch, attributable to reduced search cost, not a new prediction-accuracy gain. World-bootstrap descriptive 95% interval is [1.1731,1.1731] because this constructed benchmark produces the identical saving per world; **do not interpret that degenerate interval as evidence of robust generalization outside the generator**.

Relative to `reuse_only` in the recurrent condition, the crystal's mean net advantage is +432.4813 units per epoch, with world-bootstrap descriptive interval approximately [+428.8746,+435.9879]. Unlike the fixed policy, the crystal can discover new allowed procedures and revalidate them when previously encountered task patterns return.

### Interpretive details and negative findings

1. **Stationary fixed reuse can win.** In stationary worlds the `reuse_only` policy yields 1023.26 versus 1022.61 utility for the crystal; maintaining richer memory is an unnecessary cost in this simple setting. A universal *crystal is always best* claim is false.
2. **Novelty is bounded.** The search enumerates 92 fixed XOR candidates; it doesn't invent its own primitive operators, agent policies, or verification tests. Correct latent procedures are guaranteed representable in the constructed positive regimes.
3. **The shift assumption is fundamental.** The adversarially invalid declaration causes 440 wrong certificates. Finite-sample concentration does not solve missing target-domain information.
4. **No source-free learning.** The simulator's rewards and labeled task examples drive every change. The "resource" account is replenished by **externally supplied task reward**.
5. **No measured criticality.** The experiment neither sweeps connectivity nor estimates critical thresholds, scaling laws or hysteresis; H2 remains unproven.
6. **Not a general learning-to-learn claim.** Savings demonstrate narrow procedure reactivation inside a planted bounded task family, not sustained improvement on arbitrary unseen tasks.

## Reproduction and provenance commands

From the package root:

```bash
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
python scripts/verify_stage_l.py experiments/stage_l_holdout --repo .
PYTHONPATH=src python -m agentic_crystallization.stage_l --out experiments/my_independent_replay --start-seed 80000 --count 40
python scripts/verify_stage_l.py experiments/my_independent_replay --repo .
# Check deterministic content, not file creation timestamps:
cmp experiments/stage_l_holdout/runs.csv experiments/my_independent_replay/runs.csv
```

PowerShell equivalents are in [the root README](../README.md) and [run.ps1](../run.ps1). In the packaged copy, the exact independent replay already exists under `experiments/stage_l_independent_replay`.

[Code](../src/agentic_crystallization/crystal_core.py) · [World simulator](../src/agentic_crystallization/stage_l.py) · [Unit tests](../tests/test_crystal_core.py) · [SHA verifier](../scripts/verify_stage_l.py) · [Statistical report](../experiments/stage_l_analysis.json).
