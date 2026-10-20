# Version 2.4 — Claim Ledger

| ID | Statement | Status | Evidence / limitation |
|---|---|---|---|
| C01 | Under honest bounded reference observations, simultaneous Hoeffding intervals control fresh miscertification risk over a prespecified horizon. | PROVED UNDER ASSUMPTIONS | Mathematics v2.4, Theorem 1 and Corollary 1 |
| C02 | A reference stream independent of the original two can reveal their common-mode corruption when honest. | DEMONSTRATED SYNTHETICALLY | Holdout common_mode; 0 fresh incorrect triad certificates, 479 alarms |
| C03 | Three mutually agreeing channels must therefore be truthful. | FALSE | All-corrupt holdout 320 incorrect fresh triad certificates, 0 alarms |
| C04 | Risk-adaptive audit scheduling beats a simpler fixed schedule. | NOT SUPPORTED | Tuned age 4, cue off; all holdout outcomes identical to triad_periodic |
| C05 | Additional independent audits improve utility in every environment. | FALSE | Honest, recurrent and reference-compromised regimes worse than v2.3 guard |
| C06 | Sampled disagreement counters can certify the real-world error rates of channels. | NOT ESTABLISHED | Selective sampling, label error and nonstationarity violate calibration assumptions |
| C07 | Retained procedures remain correct between fresh audit epochs. | NOT PROVED | Stale deployments tracked separately; changing environments can invalidate them |
| C08 | Agentic Crystallization is a physical phase transition or a self-sustaining intelligence. | NOT ESTABLISHED | No causal criticality, general autonomous learning or real task evaluation |
| C09 | Complete v1.0–v2.3 package context is preserved. | AUDITABLE ARTIFACT | Prior source/history retained and sealed v2.3 archive copied unchanged |
| C10 | v2.4 improves Pegasus. | NOT TESTED | No Pegasus integration performed |

**Promotion decision:** v2.4 is a verified research experiment, **HOLD for live Pegasus/agent promotion**. Keep the simpler periodic triad as an experimentally grounded reference policy; do not automatically deploy it.
