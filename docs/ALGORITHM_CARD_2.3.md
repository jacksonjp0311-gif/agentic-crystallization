# Agentic Crystallization v2.3 — Feedback Integrity Algorithm Card

**Input:** `epoch`, `warning`, two bounded sample-mean dictionaries, anchor availability, retained policy state, finite-horizon configuration.

**Output:** `selected` (`A`, `B`, or `baseline`), `fresh_certificate`, `stale_deployment`, `disagreement_alarm`, `held`, `audit_cost`, and updated state.

## Guard rule

1. Schedule a primary audit using the inherited risk/age rule.
2. Schedule an independent anchor audit on first use, maximum anchor age, positive warning, unresolved suspicion, or a change in the primary recommendation.
3. **Whenever an anchor audit is scheduled, audit the primary too.** Never issue a fresh guard certificate from a single channel.
4. If the required anchor is unavailable: HOLD; retain the failure as a receipt.
5. If channel means disagree by more than the sum of simultaneous radii: HOLD; mark the primary/anchor pair as incompatible. Do not guess which is honest.
6. If the channels agree and the anchor's lower bound exceeds both the baseline and the competing action's upper bound: certify the anchor's best procedure for the current epoch.
7. Between audits, previously selected procedures may be reused only as explicitly **stale** decisions; no fresh certificate is inferred.
8. On expiration or unresolved contradiction: HOLD and require new evidence.

## Statistical assumptions

Independent bounded observations **within** each honest channel/action/epoch; declared expectations equal current deployment gains; prespecified finite horizon and candidate catalog. These assumptions are not automatically verifiable from the observed streams.

## Do not claim

- A discrepancy proves which channel is corrupt.
- Agreement proves both channels are honest.
- A current certificate guarantees future outcomes.
- A synthetic improvement demonstrates a Pegasus self-learning gain.
- This controller is optimal or solves common-mode corruption.

## Exact API

`feedback_integrity.IntegrityConfig`, `IntegrityState`, `radius`, `certified_best`, `disagreement`, `decide`, `cue_calibration`; experiment driver `stage_o.run(out, start_seed, count, cfg=None)`.

**Policies:** `guard`, `dual_periodic`, `anchor_periodic`, `anchor_risk`, `anchor_always`, `primary_risk`, `primary_periodic`, `baseline`.

**No integration or promotion authority:** Research-only Python package. No changes to Pegasus, Hermes, RecallTree, Genome, or protected evaluators.

[Mathematics](MATHEMATICS_2.3.md) · [Whitepaper](WHITE_PAPER.md) · [Tests](../tests/test_stage_o.py) · [Holdout](../experiments/stage_o_holdout/protocol.json)
