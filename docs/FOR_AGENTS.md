# v2.4 Agent Research Context — Read Before Modifying

Objective: explore auditable, bounded adaptation with selective retention, cost-aware verification and honest uncertainty. This is **synthetic research**, not AGI or physical crystallization.

Current v2.4 result: conditional third-party audit detects paired-channel corruption if audit reference is honest; fails if all 3 channels are corrupt; costs substantial utility in honest environments. A tuning sweep chose a 4-epoch interval with cue disabled, and this heuristic policy matched simple periodic checking exactly on the final holdout. Do not misrepresent that as an adaptive scheduling breakthrough.

**Entry points:** `src/agentic_crystallization/adaptive_trust.py` (decision algorithm), `src/agentic_crystallization/stage_p.py` (independent simulator and evaluator), `tests/test_stage_p.py` (regressions), `scripts/verify_stage_p.py` (integrity verifier). Read `docs/MATHEMATICS_2.4.md` before changing bounds or authority.

**Research invariants:** the hidden true gain never reaches `decide`; the paid independent reference is gated by `request_reference` before results are shown; fresh != stale; all-corrupt is a non-negotiable failure case; reference honesty must be independently justified; source hashes frozen pre-holdout; seed cohorts disjoint; prior packages preserved. All candidate actions remain whitelisted A/B; no arbitrary code execution or Pegasus integration.

Next question: independent outcome audit provenance, cost-aware arbitration, reference sensor compromise, adversarial slow corruption and calibrated false discoveries under shifting task families. Maintain strong lower-cost baselines.

[README](../README.md) · [Paper](WHITE_PAPER.md) · [Experiment protocol](../experiments/stage_p_holdout/protocol.json) · [Claim ledger](CLAIM_LEDGER_2.4.md)
