# CrystalGuard 1.9 — Algorithm card

[Readable overview](../README.md) · [Proof](MATHEMATICS.md) · [Python API](../src/agentic_crystallization/sequential_certificate.py) · [Complete paper](WHITE_PAPER.md)

**Category:** Fixed-library sequential procedure-value certification under externally bounded task-distribution shift.

**Inputs:** A frozen list of K procedures including a named baseline; known per-action costs; a predeclared sequence of sample counts; bounded source task outcomes f_a(x)∈[0,1]; an externally supported joint shift bound δ (or unknown); a statistical error allowance α.

**Outputs:** `CERTIFIED_BEST(action, margin)`; an optional weaker `CERTIFIED_GAIN_OVER_BASELINE`; `CONTINUE`; or `HOLD` for unknown shift, nonseparating bounds, or exhausted budget. No memory write, training, or procedure activation is implied.

**Algorithm (finite J checkpoints):**

```text
Preflight: freeze actions, costs, alpha, checkpoints and shift bound.
If shift bound missing: HOLD_UNKNOWN_SHIFT; evaluate nothing.
If all costs equal and delta >= 1/2 and K>1:
    HOLD_IMPOSSIBLE_UNDER_BOUNDS; evaluate nothing.

For each prespecified checkpoint j with n_j task vectors:
    For each frozen action a:
        mean[a] = sum of n_j bounded outcomes / n_j
        radius = sqrt(log(2*K*J/alpha)/(2*n_j))
        low[a] = max(0, mean[a] - radius - delta) - cost[a]
        high[a] = min(1, mean[a] + radius + delta) - cost[a]
    candidate = action with highest estimated net mean
    If low[candidate] > max(high[other] for other != candidate):
        CERTIFIED_BEST(candidate, separation margin); STOP
    Optionally, if gain-only objective and any action low > high[baseline]:
        CERTIFIED_GAIN_OVER_BASELINE(action); STOP
    If more checkpoints: CONTINUE (take more independent samples)
HOLD_BUDGET (do not claim superiority)
```

**Alternative:** For unlimited checkpoints, replace finite radius with `sqrt(log(2*K*j*(j+1)/alpha)/(2*n_j))`. Confidence applies only to checkpoint indices; a continuous sequence of unseen checkpoints cannot borrow this guarantee.

**Mathematical contract:** Hoeffding + union bound across frozen actions/checkpoints; TV mean shift ≤δ; strict lower/upper separation. Under valid assumptions, probability of any false best-action certificate is ≤α per episode. This is not an empirical guarantee when δ is guessed or the data stream is non-iid.

**Costs:** O(K) stored sufficient statistics, O(KJ) checkpoint arithmetic, O(K n_stop) evaluated action outcomes. This excludes expensive outcome generation and oracle calibration of δ.

**Evaluation:** Final Stage K holdout 2,800 synthetic worlds; maximum K*6400=38,400 evaluations/world when sampling is possible. Saved 98.71% evidence for clear easy cases, 96.07% with valid bounded shift, 85.61% with valid gradual shift, compared to fixed sampling on jointly certified cases. All 400 falsely-bounded worlds certified the wrong best action, illustrating assumption risk.

**Release gate:** Before using in Pegasus or any other harness, validate the sampling mechanism, shift bound, evaluator provenance, procedure/receipt boundaries and error-budget governance. Until then, **research-only**.
