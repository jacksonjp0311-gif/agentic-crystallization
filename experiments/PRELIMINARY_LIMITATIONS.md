# Preliminary Stage O diagnostics — not final results

Two exploratory development snapshots are preserved under `stage_o_development_preliminary/` and `stage_o_development_precalibration/`.

- The **first** preliminary design sometimes accepted an anchor-only fresh certificate. Under a deceptive anchor, that could certify harmful procedures. The final guard therefore requires both primary and anchor measurements before issuing a fresh certificate.
- The **second** preliminary design used declared cue sensitivity/specificity instead of the frozen training estimates. The final experiment calibrates these parameters from independent labeled synthetic data and keeps the test-world cue mechanism fixed.
- Their protocol files preserve source hashes and observed results, but the exact superseded source files are **not bundled**; those preliminary cohorts are not claimed to be independently reproducible from the final source. They are retained solely as negative design history.
- The final development cohort, frozen-source holdout, and independent replication have matching source hashes and are reproducible with the packaged final implementation.

Neither preliminary result is counted as a final test of the v2.3 claim.
