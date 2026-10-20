# Claim ladder and unresolved research hypotheses — v2.0

[README](../README.md) · [Full mathematical assumptions](MATHEMATICS.md) · [Whitepaper](WHITE_PAPER.md) · [Raw holdout](../experiments/stage_l_holdout/runs.csv)

| ID | Hypothesis / claim | Evidence class | Current status |
|---|---|---|---|
| H0 | Ordinary caching, search amortization, conditional concentration, and known shift bounds explain observed effects | Established mechanisms | **Not rejected**; much of v2.0 is an integration of these mechanisms |
| H1 | Higher-order procedure combinations can have nonadditive utility | Exact Möbius algebra and planted XOR task | **Supported only in constructed synthetic tasks** |
| H2 | Causal interaction topology induces a reproducible nonlinear *critical* adaptive crystallization transition | No criticality experiment in v2.0 | **Unestablished** |
| H3 | Retained validated procedure structures reduce future adaptation cost | 40-world recurring-task holdout, fewer queries/ops vs memoryless | **Demonstrated only for bounded synthetic recurrence**; not autonomous open-ended learning-to-learn |
| C1 | Single-epoch source validation certifies target gain over baseline with lifetime error ≤ α | Hoeffding one-sided + alpha spending + externally justified direct gain-shift bound | **Conditional theorem; code verified; premise not learned** |
| C2 | Memory size stays bounded; credit ledger cannot overdraft completed transitions | State transition invariants and regression tests | **Invariant under trusted code and receipt inputs** |
| C3 | An autonomous finite lifecycle of propose/evaluate/certify/retain/revalidate/prune is executable | v2.0 simulation + durable 12-epoch ledger + replay | **Demonstrated in a closed-loop synthetic prototype** |
| C4 | A single policy is universally superior | Stationary fixed-reuse control is slightly better | **Falsified in this benchmark** |
| C5 | Unrestricted environment shift can be certified from unchanged source data | Opposite deployment outcomes with observationally identical source data | **Not identifiable without more information** |
| C6 | v2.0 is fully self-sustaining, requires no external tasks/resources, or indefinitely adapts | No such evidence; generator provides tasks/revenue | **Not established and not claimed** |
| C7 | v2.0 improves live Pegasus, LLM coding, or real tool use | No real integration experiment | **Not measured** |

### Mandatory caveats

- No empirical zero-error result can substitute for proving the shift allowance or IID conditions.
- A receipt checksum chain detects accidental corruption, not malicious full-ledger rewrite or unauthorized tools.
- The synthetic credit ledger receives outside reward. It demonstrates budget accounting, **not** free computation.
- Certificate scope is *gain over baseline*, not global best or optimal action policy.
- The runtime enumerates a fixed finite library, not arbitrary new algorithms.
- A false shift premise produces many confident failures; **never omit this negative control**.

### Version-to-version mathematical path

| Version | Contribution |
|---|---|
| 1.0–1.1 | Synthetic higher-order interactions and graph-connectivity controls |
| 1.2–1.3 | Conditional transfer, negative transfer, learned relevance gate |
| 1.4–1.6 | Bayesian evidence acquisition, costs and model mismatch |
| 1.7 | Deterministic robust preference certificates |
| 1.8 | Simultaneous finite-sample confidence under justified shift |
| 1.9 | Sequential checkpoints and reduced evidence cost |
| **2.0** | **Closed-loop procedure proposal, fresh lifetime-risk certification, bounded retention, receipts and resource accounting** |

**Next falsifiers:** Unknown or time-varying target-domain shift, non-XOR tasks, delayed or corrupted feedback, expanding candidate family, competitive cost-aware baselines, and longer horizons. No automatic promotion into Pegasus without these tests.
