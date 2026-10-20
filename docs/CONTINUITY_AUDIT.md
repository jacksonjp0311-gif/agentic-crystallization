# v2.0 research continuity and artifact integrity

- Base release: `/mnt/data/Agentic_Crystallization_1.9_COMPLETE.zip`, **189 ZIP entries**, CRC verification passed; extracted v1.9 tree verified **188 SHA-256 file entries** using its own `scripts/verify_package.py` before any v2.0 modifications.
- The exact original 1.9 ZIP was copied to `docs/archive/Agentic_Crystallization_1.9_VERIFIED.zip`; previous v1.8/1.7 original ZIPs, whitepapers, source modules, experiments, tests, figures and historical records remain intact in the copied tree.
- The v1.9 README, mathematics, whitepaper, experiment instructions, claim ledger, algorithm card, agent context, and audit were copied unchanged into `docs/archive/*_1.9.md` before updating current documents.
- New materials use versioned names `crystal_core.py`, `stage_l.py`, `test_crystal_core.py`, `stage_l_*` experiment directories, and `Agentic_Crystallization_2.0.pdf`. Earlier stages A–K and historical `experiments/stage_*` are never replaced.
- A development cohort was executed and inspected. Then `docs/PREREGISTRATION_STAGE_L.json` froze the final Stage L source checksums and future holdout seed range before running Stage L holdout 80000–80039.
- Final holdout and independent replay CSV/JSON/manifests match byte for byte. This checks deterministic replication of the *same simulated world generator*; it is not an independent real-world dataset.
- The v1.7 historical working-copy PDF discrepancy already recorded by v1.8 remains in the original archived audit. v2.0 makes no attempt to rewrite its history.
- SHA-256 manifests verify accidental integrity only. No detached signature or trusted timestamp is asserted.

[Previous v1.9 continuity audit](archive/CONTINUITY_AUDIT_1.9.md) · [New claim ledger](CLAIM_LEDGER.md) · [Final experiment manifest](../experiments/stage_l_holdout/SHA256SUMS.json)
