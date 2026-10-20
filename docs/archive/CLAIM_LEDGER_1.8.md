# Claim ledger — v1.8

[Overview](../README.md) · [Whitepaper](WHITE_PAPER.md) · [Reproduction](EXPERIMENTS.md)

| ID | Claim | Status | Strongest evidence | What it does **not** establish |
|---|---|---|---|---|
| H1 | Utility of procedure combinations may contain non-additive terms | Supported in planted synthetic worlds, v1.0–1.1 | Known oracle and factorial ablation | New mathematics or real-world synergy |
| H2 | A verified interaction graph crosses a genuine critical adaptive transition | **Open** | No finite-size scaling, order parameter collapse, or hysteresis established | Any phase transition |
| H3 | Prior validated clusters reduce the cost of future learning cycles | **Open** | Related-task synthetic transfer, with unrelated negative transfer | Autonomous repeated self-improvement |
| T1 | Frozen, bounded iid action observations yield simultaneous concentration bound | **Proven conditional theorem** | Hoeffding + union bound | Calibration under dependent/different tasks |
| T2 | Known TV shift transports action-value intervals to target | **Proven conditional theorem** | Variational characterization of TV | Shift bound can be inferred from source alone |
| T3 | Strict interval separation certifies ranking or baseline improvement | **Proven conditional theorem** | Lower bound > upper bound | Future value beyond declared population |
| T4 | Higher-order interaction sign can be certified via sum of subset bounds | **Proven conditional theorem** | Möbius triangle inequality | Causal edges or unmeasured orders |
| N1 | Infinite source data cannot identify best action under completely unrestricted target shift | **Counterexample established** | Two indistinguishable source worlds with opposing target optima | All shift-aware learning is impossible |
| E1 | Correctly bounded shift produces conservative valid certificates in Stage J | **Observed synthetic result** | 4,320-row final holdout | Guaranteed zero mistakes in real workflows |
| E2 | Wrong shift allowance permits high-confidence harmful selection | **Observed synthetic counterexample** | 119 harmful certified gains at n=6400 | Violation of concentration theorem |
| E3 | Unknown shift gives HOLD | **Implemented and tested** | Software tests + Stage J | Utility superiority of fallback |
| E4 | High-order sign certification costs grow exponentially with order | **Mathematical bound and observed limitation** | 60/60 triple signs certified only in favorable matched n=6400 setting | A universal exact sample complexity for all tasks |
| P1 | CrystalGuard improves Pegasus model output in production | **Not tested** | No live Pegasus adapter or model run | Deployability |

All reported intervals rely on frozen-candidate evaluation and declared distribution conditions. The nominal per-world error level is **not** a blanket simultaneous guarantee across thousands of world comparisons or a method for adaptively changing the benchmark.
