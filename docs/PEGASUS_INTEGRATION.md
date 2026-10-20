# Pegasus integration — rc2 isolated adapter status

The subsequent hardening task authorized an implementation. An optional read-only adapter
now exists on PEGASUS branch `feature/agentic-crystallization-readonly`, based on inspected
remote main `f1383e14fc677b7d2bee52946f4f99a60e933da3`. It is unmerged and uninstalled.
It is not registered in startup, tools or UI. Disabled mode performs no evidence reads.
An enabled call accepts one host-authorized export and governed campaign/protocol allocation,
then emits an auditable recommendation with no authority. Native execution receipts without
paired measurements return HOLD/`missing_paired_measurement_contract`.
Synthetic contract tests are not real Pegasus task validation.
See the adapter branch's `docs/CRYSTALLIZATION-ADAPTER.md` and this package's API.md.

The following is the preserved initial planning record; its implementation status was
superseded by the explicitly authorized rc2 task.

## Initial specification — plan only

Status: NO IMPLEMENTATION, NO INSTALLATION, NO PEGASUS MODIFICATIONS.

## Inspected boundary
Local source inspection covered `integrations/run_receipt.py` and `integrations/evolution_lab.py`.
The checkout HEAD was `4a783e38cd67be023920175a3efbdf8cc3c05591`, with existing uncommitted
changes. Those changes were left untouched. Run receipts contain execution evidence and
bounded trajectory metadata; their own documentation says metadata does not establish answer
correctness. Evolution Lab describes host-graded experiments with no automatic promotion.
This inspection is not a complete Hermes/Genome/RecallTree audit; re-inspection is required
before implementing an adapter against the eventual pinned host revision.

## Proposed minimal interface
An optional, disabled-by-default command accepts an explicit directory of sanitized exported
evaluation receipts. Disabled mode returns HOLD without opening that directory.
The adapter has no network, host-tool, instruction, promotion, evaluator-write or memory permissions.
It never imports Pegasus at module import time.

Require a versioned mapping from host run IDs, candidate/baseline identities, task distribution,
evaluator revision and context digest into the independent evidence protocol. Existing execution
success must never be converted into a bounded reward sample without a defined paired evaluator.
Missing independent audit-reference evidence means HOLD. Raw private transcripts and RecallTree
records must never be copied into this repository.

## Collection protocol
Freeze candidates, sample counts, epoch horizon, confidence budget, evaluator versions and
task sampling distribution before observation. Commit the audit request before revealing
reference data. Use paired candidate-versus-baseline outcomes with explicitly justified
normalization to [-1,1]; include provenance and external reference-honesty justification.
Account for all evaluation and reference costs, including failed acquisition.

## Authority and review
Emit recommendations and receipts only. Never promote a Genome, change Hermes instructions,
rewrite an evaluator, alter RecallTree identity/family/project scope or affect desktop UX.
No recommendation implies improved agent performance. Promotion would require a separate
authorized isolated paired baseline/candidate trial, independent grading and rollback design.

## Required implementation gates
Test disabled mode with filesystem access mocked to fail; malformed/missing data; duplicate
run IDs; mismatched candidate/context; stale evidence; correlated corruption; cost accounting;
reference reveal ordering; concurrent receipt replay; and explicit denied authority paths.
Pin the host revision and receipt schema. Implement in an isolated feature branch only after
authorization; no main merge or installation without approval.

Decision: HOLD for implementation/deployment. The requested plan is provided.
