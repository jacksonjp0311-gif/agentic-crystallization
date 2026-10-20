# External evidence API preview

`Protocol`, `Measurement`, `Evidence`, `Receipt`, `evaluate`, and `ReceiptLedger`
are defined in `agentic_crystallization.evidence_api`. The preview accepts exactly
two candidates relative to a declared baseline, and primary/anchor/reference channels.
Inputs contain actual paired gain samples, not unverifiable sample-count claims.
Each gain must be in [-1,1]; normalize a different bounded reward scale in an audited
upstream producer. Sample counts are fixed per channel before observation.

Identity includes task, evaluator/context digest, protocol and baseline. The protocol
includes confidence budget and finite epoch horizon, sampling design, within-stream
independence and explicit reference-honesty assumption. Timestamps establish protocol
commitment and audit request before measurement/revelation, with an expiration time.
These are declarations, not cryptographic proof of collection order.

The caller supplies trusted current time, epoch and context. An expired certificate,
different epoch, or changed context is STALE. Gross disagreement is ALARM and demands
quarantine. Incomplete, unsupported or insufficient evidence is HOLD. A corroborated,
strictly positive and superior winner is CERTIFY_CURRENT conditional on assumptions.
ALARM does not identify which channel is dishonest. Even valid timestamps cannot prove
that the task distribution has remained unchanged.

Every result includes a machine-readable reason, bounds, accounted costs, evidence
digest and assumptions. Malformed evidence may have unknown total cost (`null`).
Invalid caller time raises ValueError because no honest evaluation receipt can be dated.
This API never fetches data or executes recommendations.

`ReceiptLedger(path).record(evidence, receipt)` atomically rejects repeated IDs and
protocol/epoch decisions. `replay()` restores stored JSON recommendations, not current
certification; call evaluate with current context/time for a new validity assessment.
Ledger hashes are not signatures. Use one durable ledger for a collection campaign.
An untrusted producer can relabel evidence: external identity and protocol governance
are mandatory. Confidence budgets across separate protocols are not automatically composed.

The ledger stores caller-produced receipts and does not authenticate them. Recommendation
consumers must obtain receipts from the trusted evaluator and verify their evidence binding.
Never use ledger membership alone as authorization.

Missing-channel acquisition costs should be accounted in the producer's collection
ledger; this API cannot infer costs of absent measurements.
Pegasus adapter behavior, permissions and disabled mode are specifications only.
