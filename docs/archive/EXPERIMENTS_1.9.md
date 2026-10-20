# Stage K experimental protocol — v1.9

[README](../README.md) · [Whitepaper](WHITE_PAPER.md) · [Mathematical proof](MATHEMATICS.md) · [Final manifest](../experiments/stage_k_holdout/manifest.json) · [Source](../src/agentic_crystallization/stage_k.py)

## Question and endpoints

**Question:** On a frozen, finite library of candidate procedures under valid, predeclared total-variation shift constraints, can sequential statistical certification require fewer **evaluated procedure outcomes** than a final-only certificate, without asserting unsupported superiority?

- **Primary:** proportional reduction in total procedure outcomes on **paired worlds where both the fixed and finite-sequential methods certify the same best action**. Numerator uses 6*n at the sequential stop, denominator uses 6*6400 at fixed finish. This excludes abstention-only cases.
- **Secondary:** best-certification rate, false best certificates versus hidden target utilities, joint interval coverage at the last look, hold frequency, mean total evaluations, regret of default baseline decisions, and finite vs unbounded checkpoint error-spending policy.
- **Negative controls:** near ties; δ≥0.5 equal-cost proof of impossibility; δ unavailable; actively *false* δ where the hidden target reverses source rankings.
- **Reporting:** preserve negative and null results. Exploratory statistics are descriptive and world-paired; no confirmatory p-values or real model comparison.

## Frozen world generator

| Parameter | Value |
|---|---|
| Candidates | baseline, a, b, c, d, e (K=6, names fixed) |
| Action costs | 0.02 each, known deterministic |
| Bounded source outcome | Each action scored in [0,1], Bernoulli in Stage K |
| Correlation | Policies share exactly the same outcomes per world; i.i.d. task vectors |
| Target law | Mixture Q=(1−η)P+ηB of **joint** task/outcome laws; TV ≤ η |
| Finite controller checkpoints | 25,50,100,200,400,800,1600,3200,6400 per action |
| Confidence budget | α=0.05 **per independent world/episode** |
| Fixed comparator | One check at 6400 evaluations per action, same error budget |
| Unbounded comparator | α_j=α/[j(j+1)] at the same sampled checkpoint schedule |
| Source seed | SHA256 derived from synthetic world ID, regime name, and operation |
| Unknown target | Only grader can read target means; policy function receives declared shift & source sample sums |

The source population P is an independent Bernoulli vector model for candidate outcomes. The adversarial component B is an independent Bernoulli vector model with means chosen to favor an alternative candidate. Target law Q mixes **entire outcome vectors**, ensuring the declared total-variation bound is exactly meaningful (provided δ ≥ η). The target law is never sampled to tune the procedure or decide whether to stop.

## Seven regimes and required outcomes

| Regime | Shift provided | Truth about bound | Stress question |
|---|---|---|---|
| `stationary_easy` | δ=0 | valid | Can the controller certify clearly superior procedure early? |
| `stationary_near_tie` | δ=0 | valid | Does it abstain instead of inventing separation? |
| `bounded_shift` | δ=.08 | valid, η=.08 | Is uncertainty accounted for under task-population change? |
| `gradual_shift` | δ=.10 | valid, η randomly ≤.10 | Can the controller still save evidence under continuous shift magnitudes? |
| `wide_valid_shift` | δ=.55 | valid, η=.45 | Is strict best certification provably impossible at zero data? |
| `violated_shift` | **δ=.02** | **false, η=.92** | Does an incorrect environmental contract invalidate apparently confident decisions? |
| `unknown_shift` | δ unavailable | cannot assess | Does the controller decline unsupported certification? |

Each of 400 final seeds is tested across all seven regimes, giving 2,800 condition-world rows. *Rows sharing a seed across regimes are not pooled as statistically independent replicates for a cross-regime population inference*; all estimates and bootstrap CIs in the report are conditioned within regimes. No claim is made about the probability distribution of real-world tasks.

## Splits and transparent inspection history

1. **Development:** 120 seeds, 30000–30119, frozen algorithm and chosen nine-checkpoint schedule. Inspect results for logic and gross efficiency. No use of the final world parameters.
2. **Observed preliminary holdout:** 400 seeds, 50000–50399. Inspection exposed a *software interface* concern: although the policy never accessed target oracle values, it previously received the containing world object. Prior source snapshot and full results are archived as `docs/archive/STAGE_K_PRESEAL_SOURCE.py` and `experiments/stage_k_exploratory_observed/`; this cohort is marked **observed exploratory**, not represented as untouched.
3. **Seal:** Modify the policy signature to accept **only** the declared shift bound and source sample prefix array, and execute the historical/new test suite. Model mathematics, checkpoint schedule, world-generation regimes and endpoints unchanged. Exact executable SHA-256 recorded in the final protocol.
4. **Untouched final holdout:** 400 independent new seeds, 60000–60399, 2,800 rows, `experiments/stage_k_holdout/`. This is the only primary confirmatory-style result within this synthetic release, albeit without external preregistration.

The historical research remains unchanged, including the v1.8 archived ZIP and identified v1.7 provenance caveat.

## Detailed final results

| Regime | Fixed certification rate | Finite certification rate | Infinite certification rate | Paired saving fraction | Wrong finite certificates |
|---|---:|---:|---:|---:|---:|
| Stationary easy | 100.00% | 100.00% | 100.00% | .987109 | 0 |
| Near tie | 1.75% | 0.00% | 0.00% | N/A | 0 |
| Bounded shift | 100.00% | 100.00% | 100.00% | .960703 | 0 |
| Gradual shift | 100.00% | 100.00% | 100.00% | .856094 | 0 |
| Wide valid shift | 0% | 0% | 0% | N/A; no samples | 0 |
| Violated shift | 100% | 100% | 100% | .983730 (**invalid**) | 400 |
| Unknown shift | 0% | 0% | 0% | N/A; no samples | 0 |

The main success criteria were **≥90% evidence reduction** on readily certifiable cases and no unjustified results under valid declared uncertainty. The evidence reduction target was met on easy and moderate-shift regimes, **not** gradual shift. False certificates were observed in **none** of the 2,000 worlds with valid shift bounds, but in **all** 400 falsely-bounded worlds. Interpretation is conditional on the synthetic process and its assumptions.

World-level descriptive bootstrap 95% reduction intervals (3,000 paired-world resamples): easy `.986738–.987480`, bounded `.959219–.962070`, gradual `.850313–.862187`. These intervals are summaries of synthetic effect variability, **not** the algorithm's per-world 1−α simultaneous-coverage guarantee.

## Reproduction procedure and provenance

```powershell
# Execute from package root, preserving the sealed originals.
python -m pip install -r requirements-repro.txt
$env:PYTHONPATH='src'
$env:OPENBLAS_NUM_THREADS='1'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_k --out experiments/my_reproduction --start-seed 60000 --count 400 --stage holdout
python scripts/verify_stage_k.py experiments/my_reproduction --root .
python scripts/verify_stage_k.py experiments/stage_k_exploratory_observed --root . --preseal
python scripts/plot_stage_k.py --summary experiments/my_reproduction/summary.json --out assets/my_reproduction
```

The frozen `protocol.json` includes stage source hashes, candidate names, costs, checkpoints, alpha, RNG protocol, generator assumptions, and world seed range. `manifest.json` records SHA-256 of source-independent experiment data. Exact byte reproduction of NumPy RNG outputs is established only for the pinned `requirements-repro.txt` environment (NumPy 2.3.5); implementations or versions may vary.

A valid verifier must check the actual **code hashes** against the frozen protocol, not only the hash of a CSV. A full replay is stronger than the checksum integrity check, although neither substitutes for an external model evaluation.

## Threats to validity and boundary conditions

- Source outcomes are independent and bounded; many real agent evaluation streams are nonstationary, correlated across tasks, and subject to selection bias.
- Distributional shift bounds are supplied by a synthetic oracle. The controller does not infer or test their truth.
- Candidates are frozen, supplied up front; there is no proposal generation, self-improvement loop, or incremental candidate expansion. Any data-dependent new candidates require fresh validation budgets.
- Equal action evaluation costs simplify comparisons. Performance under heterogeneous real procedure costs is untested, though mathematical core supports fixed unequal costs.
- Repeated peeking is valid **only** at scheduled checkpoints, not continuously at every token or tool event.
- Evidence savings count procedure outcome evaluations. They are not measured wall-clock, API cost, token reduction, or energetic cost.
- The certificate gives a ranking among the *specified* actions, not a global optimum over arbitrary algorithms.
- Error guarantee is **per episode** with α=.05, not 5% simultaneous across all 2,800 worlds or infinitely many future decisions.
- Confidence intervals and rigorous abstention are not evidence for a physical crystal, biological evolution, consciousness, or a new mathematical phase transition.
