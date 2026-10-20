# Claim and evidence ledger — Agentic Crystallization v1.9

[Whitepaper](WHITE_PAPER.md) · [Raw data](../experiments/stage_k_holdout/runs.csv) · [Code](../src/agentic_crystallization/sequential_certificate.py) · [Historical v1.8 ledger](archive/CLAIM_LEDGER_1.8.md)

| ID | Status | Evidence | Boundaries |
|---|---|---|---|
| C19-01 — finite-checkpoint simultaneous coverage | **Theorem** (established method) | Hoeffding + union bound over fixed K and J | Independent bounded source task vectors, fixed actions/checkpoints, α and sample availability |
| C19-02 — target transfer under shift | **Conditional theorem** | TV bound controls bounded expectations | Valid *joint* P/Q shift upper bound supplied externally; stable fixed action costs |
| C19-03 — optional stopping at declared checkpoints | **Conditional theorem** | Simultaneous event holds before data-dependent stopping | Only permitted checkpoints; new candidate libraries or episodes need new budgets |
| C19-04 — early impossibility when δ≥½ | **Deterministic result** | Interval algebra for equal-cost distinct actions | Not asserted for unequal costs |
| C19-05 — 98.71% clear-world evidence saving | **Synthetic measurement** | 400 held-out final worlds, paired fixed vs finite outcomes | Same action certified; not real compute/latency |
| C19-06 — 96.07% bounded-shift evidence saving | **Synthetic measurement** | 400 final held-out worlds, valid δ=.08 | Shift bound supplied by generator, not estimated |
| C19-07 — 85.61% gradual-shift evidence saving | **Synthetic measurement** | 400 final held-out worlds, valid δ=.10 | **Fails ≥90% stretch target** in this regime |
| C19-08 — no near-tie certificate | **Synthetic negative result** | 0/400 finite; 7/400 fixed certificates | Power loss from multiple checkpoint checks; not universal superiority |
| C19-09 — 400/400 wrong under false shift | **Synthetic negative control** | η=.92, falsely declared δ=.02 | The theorem does NOT apply; invalid certificates can be confidently wrong |
| C19-10 — near-zero observed errors under valid contract | **Synthetic observation** | 0 errors among 2,000 valid-shift worlds | Not a bound on all future worlds and not sufficient to validate external δ |
| C19-11 — H1 higher-order interactions | **Restricted synthetic support from prior work** | Prior planted cases, available in historical package | Stage K does not test interaction estimands |
| C19-12 — H2 critical phase transition | **Unestablished** | No size-scaling or causal criticality evidence here | No physical crystal claim |
| C19-13 — H3 autonomous learning-to-learn | **Unestablished** | No independently generated procedure and repeated long-horizon adaptation | No Pegasus runtime experiment |
| C19-14 — v1.9 mathematical novelty | **Not asserted** | Concentration inequalities and union bounds are established mathematics | The contribution is engineering formulation, strict provenance and falsifiable test |

**No prohibited promotions:** This release does not mutate existing agent authority, approved procedures, cloud systems, permissions, memories, or operator policy. No causal graph threshold, new particle analogy, or intelligence claim is promoted from the Stage K evidence.
