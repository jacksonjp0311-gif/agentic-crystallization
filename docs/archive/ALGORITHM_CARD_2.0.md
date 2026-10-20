# CrystalKernel v2.0 — Algorithm card

**Objective:** Autonomous, bounded procedure discovery with fresh certification, conditional reuse, durable receipts, and budget-preserving fallback. No authority to modify the host or promote code changes.

[Read the proofs](MATHEMATICS.md) · [Run the tests](../tests/test_crystal_core.py) · [Controller](../src/agentic_crystallization/crystal_core.py) · [Simulator](../src/agentic_crystallization/stage_l.py)

## State

`State = (epoch, memory[procedure -> {last_certified,count}], optional_first_anchor, credits)`.

`Memory` is a shortlist, not an approval list. Capacity four, time-to-staleness five epochs. Candidate family is exactly 92 XOR-of-1/2/3-feature expressions plus a constant-zero baseline.

## Inputs per epoch

```
exploration_scout: 24 labeled tasks, independent of validation
exploration_discovery: 96 labeled tasks, independent of validation
validation: 512 new labeled tasks, visited at n=64,128,256,512
shift_allowance: external upper bound on shift in expected paired gain, or None
live: independent scoring tasks supplied ONLY after decision
```

## Loop

```text
FOR EACH externally supplied task epoch e:
  verify last receipt and reconstruct state
  IF environmental shift allowance is unavailable: HOLD -> baseline
  IF a safe worst-case evaluation budget is unavailable: HOLD -> baseline
  shortlist retained procedures on separate scout data
  IF a remembered procedure fits context: freeze it as the candidate
  IF not: generate bounded XOR compositions and rank using discovery data
  IF discovery has no promising candidate: HOLD -> baseline
  certify ONE frozen candidate on independent validation examples
    use alpha_e = alpha_total / (e*(e+1))
    FOR checkpoint n_j in [64,128,256,512]:
      r=sqrt(2*ln(J/alpha_e)/n_j)
      lower=mean_paired_gain - r - shift_allowance
      IF lower > minimum_gain: CERTIFIED -> STOP
    IF no certificate: HOLD -> baseline
  IF CERTIFIED: retain/update candidate (subject to capacity/age)
  deploy only the selected permitted expression or baseline
  debit evaluation costs; credit externally observed task rewards
  append one receipt (hash chain + before/after state commitments)
  advance epoch, never recycle its alpha budget
```

## Contract

**A CERTIFIED outcome guarantees positive expected gain relative to baseline with lifetime false-promotion probability at most alpha_total ONLY under the explicit assumptions in MATHEMATICS.md.** It does not certify best-in-library, optimize total compute cost, prove distribution shift bounds, or authorize external actions. Unknown assumptions are HOLD.

**Observed failure mode:** A false shift allowance can make the system confidently select a candidate with *negative* deployment gain. Keep this negative control forever.

## Integration boundary

This is a standalone Python simulation and mathematical decision module. To adapt to Pegasus, a future read-only harness would supply external task data, deterministic preapproved procedures, a trusted shift contract, and a host-side authorization layer. Do not allow this module to mutate Pegasus memory, agent instructions, or runtime permissions without an independent governance process.
