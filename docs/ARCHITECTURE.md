# Architecture

The historical modules retain their original identities and imports. `adaptive_trust` and
`feedback_integrity` implement the two-candidate synthetic controller. `stage_p` generates
worlds and scores policies; hidden truth is confined to generation/scoring.

The new `evidence_api` consumes externally collected paired gains, with an explicit finite
catalog and measurement context. It produces deterministic JSON receipts without importing
the simulator or changing any agent. It supports exactly two candidates and three channels.
Receipt storage is an optional caller-selected SQLite ledger with atomic duplicate rejection.

External producer → frozen protocol → bounded paired samples → validation → corroboration
→ CERTIFY_CURRENT / HOLD / STALE / ALARM → recommendation receipt.

Cross-channel independence is not needed for the union bound. Independence within each
candidate/channel sample stream and unbiased measurement of the target are required.
All-three-channel corruption remains undetectable from agreement alone.
