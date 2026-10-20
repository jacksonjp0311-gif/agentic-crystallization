# Reproducible Experiments — Stage J, Agentic Crystallization v1.8

[Main README](../README.md) · [Full whitepaper](WHITE_PAPER.md) · [Mathematical guarantees](MATHEMATICS.md) · [Raw data](../experiments/stage_j_holdout/runs.csv) · [Frozen protocol](../experiments/stage_j_holdout/protocol.json)

## 1. Primary research question

Can statistically simultaneous procedure-value intervals provide useful **conditional** decision and high-order-interaction certificates when task-distribution shift is correctly bounded, and how do those certificates behave when the shift assumption is false or unavailable?

We deliberately did not attempt to prove a new phase transition in this experiment. H2/H3 remain separate research hypotheses.

## 2. Split and source-freezing discipline

The Stage J implementation, candidate library, fixed costs, oracle and shift regimes were selected during development. The initial preliminary measurements used seeds 4000–4079 and 10000–10159; they were inspected before adding a stricter factorial-input validator. To preserve honest provenance, those runs remain under `stage_j_initial_development` and `stage_j_exploratory_observed` and are **not** called final held-out tests. Their manifests retain the source hashes present at execution; they cannot be used to claim that later code was frozen before those runs.

The final current code was then frozen before running:

- **Development:** seeds 4000–4199, 200 distinct world parameters across conditions, under the final source revision.
- **Final holdout:** seeds 20000–20239, 240 distinct, previously unexamined world parameters under the frozen final source revision.
- Each world appears under **six** prespecified shift regimes and **three** sample sizes; therefore the final holdout has **4,320 condition rows**, not 4,320 independent underlying world parameters.
- The result summaries resample the **240 world IDs**, not tool calls or the nine correlated per-task arm outcomes.
- Source and protocol hashes are recorded before drawing final results. No new model code was introduced after the final evaluation.

The final protocol hashes the two relevant code modules and the complete scientific configuration. The verifier compares the packaged source to those exact hashes. Tests and documentation were finalized afterward without modifying the frozen algorithm source.

## 3. Synthetic generator

The catalog is fixed: `baseline`, `a`, `b`, `c`, `ab`, `ac`, `bc`, `abc`, and `d` (procedure sets of up to three members and one independent competitor). Each action receives a deterministic cost $0.025+0.035\times |S|$. The hidden two-context success probabilities are generated reproducibly from a per-world seed. The four worlds' functional families cycle evenly:

1. **Additive:** only procedure main effects; empty-baseline higher-order interactions vanish.
2. **Pairwise:** an added effect for $\{a,b\}$; no planted three-way interaction.
3. **Triple:** a true three-way effect for $\{a,b,c\}$, with opposite performance under unrelated context.
4. **Misleading graph:** dense metadata-only connectivity without causal interaction; same type of utility as additive.

The oracle produces binary task success for each procedure. At every calibration task all nine actions are scored under the **same sampled latent task context**, enabling paired comparisons. Per-action Bernoulli noise is independent conditionally on context. Tasks are independent across calibration steps. The target expected net utilities are computed from known true parameters **for grading only** and are never provided to the selection code.

## 4. Six shift conditions

| Regime | Source $p(z=1)$ | Target $q(z=1)$ | Declared upper bound | Truth |
|---|---:|---:|---:|---|
| `iid_related` | .10 | .10 | 0 | Valid, matched |
| `iid_unrelated` | .85 | .85 | 0 | Valid, matched |
| `bounded_shift` | .10 | .18 | .08 | Valid, moderately shifted |
| `wide_valid_shift` | .10 | .45 | .35 | Valid, high uncertainty |
| `violated_shift` | .10 | .92 | **.05** | **False**; actual TV=.82 |
| `unknown_shift` | .10 | .18 | None | Information unavailable; HOLD |

Within each world, the response distribution conditional on the observed binary context is fixed. Therefore total variation between the source and target context distributions is exactly $|p-q|$. This fact is provided to the experimental auditor, not inferred by the algorithm. In a real deployment such a bound would need independent evidence and an explicit model of which features remain stable.

## 5. Independent comparison arms and measured outputs

The **greedy** comparator selects maximum empirical net utility, ignoring calibration and drift uncertainty. The **CrystalGuard** arm certifies a unique winner only if its lower interval exceeds every rival upper interval; otherwise it selects a candidate certifiably better than the baseline; otherwise it retains the baseline or returns HOLD when drift is unknown. The **oracle** best action is computed from the inaccessible true target utilities for regret measurement only.

The factorial interaction test observes all eight subsets of `abc` and certifies the sign of $\Gamma_{abc}$ only when its simultaneous error radius does not cross zero. It is not a selection authority.

The raw CSV retains source/target prevalence, actual/declared drift, true expected net reward per chosen action, interval-coverage status, certificates and mistakes, oracle regret, planted family, sample count, interaction estimate/sign, and calibration observations. The CSV explicitly marks unknown coverage with an empty value, not zero. The full output is purposefully synthetic; no private model traces are present.

## 6. Held-out results (all sample sizes)

| Scenario | $n$ | Joint coverage | Unique-best cert. | Gain cert. | False-best | Harmful certified gain |
|---|---:|---:|---:|---:|---:|---:|
| Matched related | 200 | 240/240 | 32/240 | 66/240 | 0 | 0 |
| Matched related | 1,000 | 240/240 | 60/240 | 121/240 | 0 | 0 |
| Matched related | 6,400 | 239/240 | 60/240 | 206/240 | 0 | 0 |
| Matched unrelated | 200 | 239/240 | 0 | 4/240 | 0 | 0 |
| Matched unrelated | 1,000 | 239/240 | 216/240 | 221/240 | 0 | 0 |
| Matched unrelated | 6,400 | 240/240 | 240/240 | 240/240 | 0 | 0 |
| Bounded shift | 200 | 240/240 | 0 | 2/240 | 0 | 0 |
| Bounded shift | 1,000 | 240/240 | 21/240 | 55/240 | 0 | 0 |
| Bounded shift | 6,400 | 240/240 | 60/240 | 64/240 | 0 | 0 |
| Wide valid shift | 200/1,000/6,400 | 240/240 each | 0 | 0 | 0 | 0 |
| **Broken shift** | 200 | 48/240 | 0 | 13/240 | 0 | **13** |
| **Broken shift** | 1,000 | 0/240 | 59/240 | 72/240 | **59** | **72** |
| **Broken shift** | 6,400 | 0/240 | 60/240 | 119/240 | **60** | **119** |
| Unknown bound | All sizes | **Uncertifiable** | 0 | 0 | Not asserted | Not asserted |

These descriptive proportions are **not** a global 95% guarantee across all worlds. Each independently frozen comparison has a nominal $\alpha=0.05$ simultaneous error guarantee, assuming the premises. Several observed valid-case coverages are below 100%, as finite-sample confidence theory permits. No tested valid-shift certificate was harmful in this cohort; that does not make the false-certification probability mathematically zero.

The conditional safety guarantee comes at a real opportunity cost: under valid moderate shift, the robust policy's mean net utility was approximately **0.0545 below greedy** at $n=6400$ because it withheld uncertain gains. Under a wide valid shift it refused all proposed gains. This is not a claim that the conservative controller optimizes mean utility in the deployment population.

## 7. Higher-order sign certification

In each 240-world condition, exactly 60 are triple-interaction worlds. At $n=6400$ in the matched related regime, all **60/60** planted positive triple interactions had a positive sign certificate; at $n=200$ or 1,000 there were none. Under the correctly bounded moderate or wide shift, no triple signs were certified at the three tested sample sizes. This is expected from the eight-term uncertainty accumulation.

## 8. Falsification and limitations

The broken-shift scenario demonstrates an actual failure of the *assumptions*, not a failure of Hoeffding's theorem. More samples cannot fix an incorrect shift model. An unknown-bound scenario produces an explicit HOLD; this is a refusal to certify, not an observed system failure or proof of robust future performance.

The experiment requires scoring **all nine procedures** on each calibration task, with $nK$ recorded outcomes; at $n=6400$, that means **57,600** oracle observations per world. This has not been charged against downstream learning benefit. Real tools may not permit full counterfactual scoring and may produce temporally dependent outcomes. The benchmark does not investigate distribution-free conformal prediction, model-driven reward estimation, agent-generated candidates, online optional stopping, real task streams, phase transitions, or reusable self-improvement across restarts.

## 9. Reproduction, manifests, and independent checks

From root:

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH='src'
$env:OPENBLAS_NUM_THREADS='1'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_j --out experiments/reproduced_holdout --start-seed 20000 --count 240 --stage holdout
python scripts/verify_experiment.py experiments/reproduced_holdout
```

Each Stage J directory contains `protocol.json` (frozen assumptions + source hashes), `runs.csv` (every condition), `summary.json` (world-level descriptive statistics and bootstrap intervals), and `manifest.json` (hashes of protocol, runs, summary and scope). The manifest is not a cryptographic signature against a malicious actor who can rewrite all files; it provides reproducible file identity.

The archive's previous v1.7 ZIP is itself preserved, with its original correct PDF hash. The prior extracted PDF divergence is explicitly disclosed in [continuity audit](CONTINUITY_AUDIT.md). Do not silently relabel earlier exploratory results as new held-out outcomes.
