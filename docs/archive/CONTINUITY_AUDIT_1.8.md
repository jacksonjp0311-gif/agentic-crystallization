# Continuity and provenance audit — Version 1.8

## Historical research preserved

- Agentic Crystallization v1.0 through v1.7 Python algorithms and simulations retained in `src/` and `experiments/`.
- Original v1.7 `README.md` and `docs/WHITE_PAPER.md` archived as `docs/archive/README_1.7.md` and `docs/archive/WHITE_PAPER_1.7.md`.
- The exact historical v1.7 ZIP is included as `docs/archive/Agentic_Crystallization_1.7_VERIFIED.zip`.
- Earlier PDFs and whitepapers are preserved in their historical locations. No source was upgraded to PASS by altering historical results.
- Current Stage J protocol and code hashes are sealed in `experiments/stage_j_holdout/protocol.json` and its manifest.

## v1.7 checksum divergence — reported, not erased

A check of `/mnt/data/Agentic_Crystallization_1.7/PACKAGE_SHA256SUMS.json` found that the **working-directory v1.7 PDF** did not match its recorded SHA-256. The **PDF inside the original v1.7 ZIP** *did* match, and the ZIP passed CRC inspection. We extracted the archived ZIP into the v1.8 baseline and retained both the verified ZIP and a machine-readable account in [`V1_7_PROVENANCE_AUDIT.json`](archive/V1_7_PROVENANCE_AUDIT.json). This is a provenance discrepancy; we did not infer a scientific-result change or rewrite original calculations from it.

## New code and experimental splits

| Stage | Seed range | World IDs | Condition rows | Meaning |
|---|---|---:|---:|---|
| Initial developmental | 4000..4079 | 80 | 1,440 | Original code snapshot; exploratory only |
| Initial observed comparison | 10000..10159 | 160 | 2,880 | Inspected prior to additional input validation; **not** untouched holdout |
| Final-code development | 4000..4199 | 200 | 3,600 | Prespecified final code, exploratory/model checks |
| **Final frozen holdout** | **20000..20239** | **240** | **4,320** | Fresh independent world parameters; predeclared code/protocol |

The final Stage J algorithm modules were not changed after the fresh holdout. A complete software test run, PDF creation and documentation production follow the holdout as release quality checks. Publication of this package must not imply that an algorithm using many real agent evaluations is economical or that new live memories were learned.

## Integrity limits

`PACKAGE_SHA256SUMS.json` and per-stage manifests provide checksums for replication; they are not cryptographic signatures against a process that can rewrite the entire package. Reviewer source references remain source-level verification, not proof of real-world performance.
