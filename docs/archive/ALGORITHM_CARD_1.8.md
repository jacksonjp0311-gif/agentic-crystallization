# Algorithm Card: CrystalGuard-1.8

[README](../README.md) · [Proofs](MATHEMATICS.md) · [Code](../src/agentic_crystallization/robust_calibration.py) · [Tests](../tests/test_robust_calibration.py)

**Purpose:** Choose a procedure only when independent, bounded evaluation provides a simultaneous certificate under a separately justified target-distribution shift allowance.

**Inputs:** A frozen set of $K$ allowed actions, named baseline, mean bounded calibration outcomes per action $\widehat p_a\in[0,1]$, fixed cost $c_a\in[0,1]$, sample count $n>0$, error level $\alpha$, and known TV upper bound $\delta$ or missing marker.

**Decision math:**

$$\varepsilon=\sqrt{\log(2K/\alpha)/(2n)},\quad L_a=\max(0,\hat p_a-\varepsilon-\delta)-c_a,\quad U_a=\min(1,\hat p_a+\varepsilon+\delta)-c_a.$$

**Pseudocode**

```text
if target_shift_bound is unknown: return HOLD
construct all simultaneous intervals for frozen candidates
winner := argmax empirical net utility (fixed deterministic tie break)
if L[winner] > max(U[other]): return CERTIFIED_BEST(winner)
for candidate in allowed actions other than baseline:
    if L[candidate] > U[baseline]: mark certified baseline gain
if any gains:
    return CERTIFIED_GAIN(candidate with maximal lower bound)
return FALLBACK_BASELINE (not a proof of optimality)
```

**Evidence origin:** Calibrated sample outcomes (not agent self-grades); known comparable resource costs; externally defended drift allowance. The source-to-target conditional outcome mechanism must be stable unless the TV bound covers the joint process.

**Failure modes:** Unknown or false shift bound; evaluator tampering; unequal computation between actions; candidate invention after calibration; temporal dependence among tasks; missing/revoked source receipts; repeated optional stopping without error spending; extrapolation beyond the authorized task population.

**Status:** Validated mathematical component in a standalone synthetic package. No live Pegasus interface, model-weight learning, automatic promotion, or universal coherence threshold.
