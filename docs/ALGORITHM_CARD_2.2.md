# Agentic Crystallization v2.2 — Algorithm card

**Function:** `choose(policy, epoch, state, cue, audit_means, config)` in [`risk_verification.py`](../src/agentic_crystallization/risk_verification.py).

**Inputs:** Two permitted candidate procedures, baseline, optional change warning, independent current-epoch paired audit samples if purchased, fixed audit budget and confidence allocation.

**State:** Last selected procedure, last audit epoch, audit count, certification count, HOLD count.

**Selection:** On first use, after age expiry, missing-warning fallback, or nominal expected-loss threshold: audit both. Certify only a candidate whose simultaneous current-epoch lower confidence bound is positive. Otherwise HOLD baseline. If not auditing, mark deployment **stale**.

**Outputs:** Decision and receipt fields, including audit flag, fresh certification, stale deployment, costs and warning. The hidden true gain is used **only by the external experiment evaluator**.

**Claim boundary:** Conditional finite-horizon current-epoch statistical certificate. No guarantee on stale deployment or deceptive channels. No new agent permissions, self-modifying code, or real Pegasus execution.
