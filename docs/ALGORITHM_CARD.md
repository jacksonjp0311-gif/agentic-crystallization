# Agentic Crystallization v2.1 — Algorithm Card

**Name:** `RenewalKernel` 2.1 (research-grade, restricted synthetic procedure family).  
**Entry point:** `agentic_crystallization.stage_m` (`python -m`).  
**Core:** [`renewal_core.py`](../src/agentic_crystallization/renewal_core.py).  
**Tests:** [`test_renewal_core.py`](../tests/test_renewal_core.py).  
**Mathematical contract:** [`MATHEMATICS.md`](MATHEMATICS.md).

### Inputs and authority

- An explicit finite whitelist of XOR procedures; a constant-zero baseline.
- Historical proposal memory carrying `RETAINED`, `NEEDS_RENEWAL`, or `RETIRED` status; no historical promotion authority.
- Independent scout, discovery and validation observations for each applicable block, plus subsequent reported labeled task outcomes.
- Immutable predeclared error budgets, sample checkpoints, resource prices and memory limits.
- Externally provided tasks and revenue. **No execution of generated code, credentials, cloud actions, or source changes.**

### States and decisions

`CERTIFY`: fresh validation supports expected paired gain over baseline in the named **current block**.  
`CLEAR`: no statistically significant deterioration detected *yet*; this is not a certificate of unchanged future conditions.  
`ALARM`: the subsequent paired feedback supports a drop in expected gain relative to the reference batch.  
`HOLD`: evidence insufficient, feedback missing, budget unavailable, or no proposal certified.  
`NEEDS_RENEWAL`: historical knowledge available only for new proposals; no deployment authority.  
`RETIRED`: excluded from memory nominations until independently rediscovered and newly validated.

### Decision loop

```text
for each epoch:
    expire previous certificate authority
    if no safe resource reserve: deploy baseline, receipt, continue
    propose from fresh scout of retained procedures, else bounded discovery
    independently validate one frozen proposal
    if lower_bound <= minimum_gain: HOLD / baseline
    else: certify for first block, retain proposal record, deploy
    operate second block; only AFTER outcomes return, evaluate paired deterioration
    if feedback absent: HOLD for third block
    else if certified deterioration:
         withdraw continuing authority and mark NEEDS_RENEWAL/RETIRED
         optionally propose + independently certify a new third-block procedure
    else:
         continue while declaring the third block an unguaranteed extrapolation
    account actual observations, computation, monitoring, storage, task revenues
    append SHA-256-linked receipt and reconstructible state commitment
```

### Statistical guarantees under assumptions

$$
\Pr(\text{any false positive fresh certification over a run})\le .025,
\qquad
\Pr(\text{any false deterioration alarm over a run})\le .025.
$$

These are *conditional* to independent bounded representative data, proper information separation, honest feedback and the explicitly allocated tests. They do **not** bound damage after unobservable change, missed detection, or arbitrary distribution shift.

### API illustration

```python
from agentic_crystallization.renewal_core import RenewalConfig, RenewalState, renewal_step
from agentic_crystallization.stage_m import make_packet

cfg = RenewalConfig()
state = RenewalState(credits=cfg.base.initial_credits)
packet, hidden_evaluator_audit = make_packet(91000, 1, 'recurrent', cfg)
receipt, state = renewal_step(state, packet, 'crystal', cfg)
assert 'phase0' not in receipt  # simulator truth is not controller input
```

For persistence, use `RenewalLedger(path,cfg).append(receipt)` and `replay()`. Do not use the simulator-only evaluator audit in the agent policy.

### Attack surface, limitations and safe integration boundary

Hash receipts are not signed; use an authenticated, access-controlled ledger for production. Stage M outcomes assume observed paired labels; absent/corrupted labels defeat some guarantees. No live-agent or Pegasus benchmark is present. Do not connect to the Pegasus Genome promotion pathway until a separate review verifies independent evaluation, authorization, rollback, cost budgets, and observable deployment contracts.
