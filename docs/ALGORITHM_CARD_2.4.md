# Agentic Crystallization v2.4 — Algorithm Card

**Object:** audited two-candidate bounded synthetic procedure selector. No Pegasus integration or promotion authority.

### Inputs
`policy`, `epoch`, `warning`, retained `TrustState`, observed primary/anchor means and *only if purchased* reference means, `TrustConfig`.

### State
Selected action or baseline, last reference audit epoch, disagreement/quarantine status, capped exponential retry epoch, last observed gain, per-channel discrepancy counts, separate historical v2.3 guard state.

### Outputs
Selected action, whether a **fresh** current-epoch certificate was issued, stale deployment indicator, HOLD, channel-disagreement alarms, paid audit counters, net audit cost, and retained state.

### Two-phase procedure

1. `request_reference()` commits to a paid independent reference audit from prior state, time, cue and costs, **before** seeing the new reference result. If no audit is purchased, the decision function receives `None` for the reference.
2. On audit, obtain reference outcomes and, for triad policies, primary and anchor outcomes. If either mandatory channel is unavailable, return HOLD.
3. Compute simultaneous Hoeffding radii for every sample source, action, epoch. If primary/reference or anchor/reference intervals are disjoint, HOLD and quarantine. Neither disagreement nor agreement identifies the honest source.
4. Issue **fresh** certificate only if every channel independently certifies the same action over the fallback and competing action, with no gross discrepancy. On failure, HOLD and back off costly rechecks at a bounded rate.
5. Between audits, retain decisions only while age is bounded, mark them as **stale** and never call them fresh. On expiry or contradiction, HOLD.
6. Charge actual audit costs and record all outcomes. The synthetic hidden true gain is accessed **only after policy decision**, for evaluation.

### Selected research policy
Development-only grid search chose `max_age=4`, `use_cue=False`. In the independent holdout this adaptive policy exactly matched simple `triad_periodic` with four-epoch intervals. **Prefer the simpler implementation unless a future independent experiment proves the heuristic helps.**

### Correctness premises
Prespecified finite horizon and candidate catalog, bounded independent outcomes within the honest reference, exact current gain expectation, no post-hoc use of ground truth or holdout tuning. Under these premises, current-epoch fresh miscertification risk is controlled by the simultaneous concentration bound. Stale reuse has no such guarantee.

### Documented failure cases
Shared corruption of all channels → confident incorrect certification. Reference compromised → HOLD costs and lost task utility. Missing channel → HOLD. Unlearnable tasks → excess audit costs. Unanticipated drift between audits → stale harm. Selected audits and nonstationarity make posterior mismatch rates *not* automatically calibrated.

[Formal proof](MATHEMATICS_2.4.md) · [Full whitepaper](WHITE_PAPER.md) · [Executable tests](../tests/test_stage_p.py) · [Source](../src/agentic_crystallization/adaptive_trust.py)
