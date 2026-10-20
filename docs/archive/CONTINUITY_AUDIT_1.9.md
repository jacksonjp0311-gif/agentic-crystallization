# Continuity and integrity audit — v1.9

## Provenance objective

Each new version is a **complete research package** containing the prior runnable algorithms, original recorded datasets, original experiment manifests, earlier whitepapers and PDF reports, not merely a changed algorithm snippet. Historical results should not be silently corrected, reinterpreted as stronger evidence or overwritten.

## Preserved v1.8 baseline

- The original v1.8 working tree was copied into the v1.9 folder before new research was added.
- The exact `Agentic_Crystallization_1.8_COMPLETE.zip` is preserved at `docs/archive/Agentic_Crystallization_1.8_VERIFIED.zip`, and its internal integrity was verified.
- Original 1.8 README, mathematical document, whitepaper, experiments, claims, algorithm card, agent packet and continuity audit were archived with `_1.8` names.
- All old Python source modules and all preexisting `experiments/stage_*` results are preserved without altering their scientific results.
- Original earlier PDFs remain at package root, and all earlier research whitepapers remain archived.
- A preexisting **v1.7 PDF checksum divergence** between one loose working-directory artifact and the verified historical ZIP was documented by v1.8; this remains a recorded provenance caveat, not erased history. See `docs/archive/V1_7_PROVENANCE_AUDIT.json`.

## v1.9 source isolation and experiment splits

| Cohort | World seed range | Rows | Interpretation |
|---|---|---:|---|
| Development | 30000–30119 | 840 | Inspected exploratory development |
| Observed preliminary | 50000–50399 | 2,800 | Archived **observed exploratory**, before interface isolation |
| **Final holdout** | **60000–60399** | **2,800** | Fresh, independent final result with isolated decision API and frozen source hashes |

The observed preliminary source and its controller are preserved in `docs/archive/STAGE_K_PRESEAL_SOURCE.py` and `docs/archive/SEQUENTIAL_CERTIFICATE_PRESEAL_SOURCE.py`. The observed preliminary manifest intentionally references this earlier code snapshot and therefore cannot be verified against *current* Stage K source hashes as if it were the final holdout. The explicit `--preseal` verifier option checks the archived source snapshot and the preserved per-output hashes: `python scripts/verify_stage_k.py experiments/stage_k_exploratory_observed --root . --preseal`. The final cohort uses the current source and is separately verified by `scripts/verify_stage_k.py`.

The preseal interface accepted the world object but read only its `declared_shift` and source prefix outcomes; subsequent code removed even *potential* access to the hidden target by changing the `_policy()` signature to receive only the declared shift and measured outcomes. The underlying mathematical equations, alpha, checkpoints and named regimes remained unchanged. This isolation improvement occurred **before** generating the final holdout.

## What checksums prove

`experiments/stage_k_holdout/manifest.json` hashes `protocol.json`, `runs.csv` and `summary.json`. The frozen protocol also includes SHA-256 of the executable Stage K source and sequential certification source. `PACKAGE_SHA256SUMS.json` hashes every regular file in this complete release except itself. These checks detect accidental data and code mutations. They are not digital signatures and do not prevent someone from recomputing all hashes after malicious tampering.

An independent reproduction that regenerates **byte-identical** raw results from the frozen source/seed protocol is a stronger scientific integrity check than checksums alone, though it does not establish external applicability or truthful real-world shift bounds.

## Claim constraints carried forward

We preserve the synthetic H1 interaction findings and negative transfer evidence from past versions. H2 criticality and H3 autonomous learning-to-learn remain unestablished. v1.9 is specifically an efficient statistical evaluation **subcomponent**, not a conclusion that digital data necessarily crystallizes under all environmental pressures.
