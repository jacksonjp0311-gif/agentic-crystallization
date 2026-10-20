# Agentic Crystallization v1.9
## Efficient Conditional Stability: Sequential Certificates for Adaptive Procedure Selection

**Research status:** Reproducible mathematical and synthetic engineering study. **No** new physics, phase transition, autonomous self-improvement, or measured Pegasus execution benefit is asserted.

[README](../README.md) · [Complete proofs](MATHEMATICS.md) · [Experimental protocol](EXPERIMENTS.md) · [Algorithm](ALGORITHM_CARD.md) · [Evidence ledger](CLAIM_LEDGER.md) · [Prior version](archive/WHITE_PAPER_1.8.md)

### Abstract

An adaptive agent may retain a procedure because it appears better than competitors, yet finite samples and environmental distribution shift can invalidate that choice. Earlier work (v1.8) provided conditional, simultaneous finite-sample certificates for a fixed library of bounded-outcome procedures, but required substantial evaluation data. Version 1.9 investigates whether a sequential stopping rule can reduce that evidence cost without invalidating its stated confidence guarantee. We use predeclared evaluation checkpoints, a Bonferroni/Hoeffding confidence family, deterministic action costs and an externally justified total-variation bound between source and target task distributions. A second version spends its error probability over an unbounded sequence of checkpoints. The decision rule returns `CERTIFY_BEST`, `CONTINUE`, or `HOLD`; it does not invent a shift bound.

In a frozen held-out experiment with **2,800 independent synthetic worlds** (400 worlds in each of seven environmental regimes), the finite-grid policy reduced evidence consumption by **98.71%** on stationary easy tasks, **96.07%** with a correctly declared moderate shift, and **85.61%** with correctly bounded gradual shift, relative to a single final evaluation at the same 6,400-per-action cap. In those three regimes both methods certified the same target-optimal choice in all 400 cases. The sequential policy could not certify any of 400 near-tie worlds, whereas the fixed-budget policy certified 7; neither policy certified under unknown or provably nonseparating shift bounds. In the deliberately invalid-shift counterexample, **400 of 400 sequential certificates were wrong**. The last result is essential: efficiency is not reliability when the environment contract is false.

This is an application of **established sequential concentration mathematics** with a reproducible evaluation of computational evidence savings. It does **not** demonstrate self-organizing procedure crystallization or independent discovery of higher-order knowledge clusters.

## 1. Research motivation and claim boundary

Agentic Crystallization began as a hypothesis that useful agent procedures might form stable, interacting assemblies under persistent selection pressures. Versions 1.0–1.7 isolated planted nonadditive interactions, connectivity controls, transfer and negative transfer, relevance gating, information acquisition, and deterministic stability certificates. Version 1.8 introduced statistical calibration plus explicit environmental-shift uncertainty, including a negative result under false assumptions.

The v1.9 question is **narrow and falsifiable**: Can a fixed, prevalidated procedure library be ranked with statistically defensible confidence after examining fewer task evaluations than a single fixed-budget certificate? Success would improve a practical component of a governed agent harness. It would **not** prove a phase transition, causal emergence of procedural hypergraphs, or long-run compounding improvement.

We maintain three distinct hypotheses: H1 (nonadditive interactions, observed only in planted settings), H2 (genuine critical adaptive transition, unestablished), and H3 (persistent learning-to-learn, unestablished generally). Stage K evaluates none of H1–H3 directly; it assesses the **cost of evaluating fixed candidate structures**.

## 2. Mathematical object: source, target, and costs

Let a fixed action library be \(\mathcal A=\{a_1,\ldots,a_K\}\), including baseline \(a_0\). Independent and identically distributed source tasks \(X_t\sim P\) yield bounded outcomes \(f_a(X_t)\in[0,1]\). Different actions may be correlated within the same task. Each action has a deterministic, context-stable cost \(c_a\). The target-domain net value is

\[
V_Q(a)=\mathbb E_Q[f_a(X)]-c_a.
\]

The key external assumption is a legitimate total-variation upper bound \(d_{\rm TV}(P,Q)\le\delta\) on the **joint** task-and-outcome law relevant to these evaluations, or an equivalent stability condition supporting \(|\mathbb E_P f_a-\mathbb E_Q f_a|\le\delta\) for every action. This bound is not inferred from the same observations used to select a candidate. It must be obtained and justified separately.

Without \(\delta\), the system returns `HOLD_UNKNOWN_SHIFT`. With equal costs and \(\delta\ge1/2\), the symmetric intervals can never demonstrate a strictly optimal action, even with perfect sampling, so the system returns `HOLD_IMPOSSIBLE_UNDER_BOUNDS` without spending evidence.

## 3. Sequential mathematical certificate

Fix in advance an allowed significance \(\alpha\in(0,1)\) and checkpoints \(n_1<\cdots<n_J\). At checkpoint \(j\) define the empirically estimated source outcome

\[
\widehat\mu_{a,j}=\frac1{n_j}\sum_{t=1}^{n_j} f_a(X_t).
\]

Our finite-checkpoint statistical radius is

\[
\boxed{r_j=\sqrt{\frac{\log(2KJ/\alpha)}{2n_j}}.}
\]

The corresponding target-domain net-value interval is

\[
L_{a,j}=\max(0,\widehat\mu_{a,j}-r_j-\delta)-c_a,
\quad
U_{a,j}=\min(1,\widehat\mu_{a,j}+r_j+\delta)-c_a.
\]

**Theorem (optional-stopping-safe fixed-family selection).** If the frozen-library, source-sampling, cost and shift assumptions are true, the simultaneous interval coverage event has probability at least \(1-\alpha\), uniformly over the \(K\) actions and \(J\) predeclared checkpoints. If the system stops at any data-dependent checkpoint \(\tau\) and certifies action \(a^*\) only when

\[
\boxed{L_{a^*,\tau}>\max_{b\ne a^*}U_{b,\tau},}
\]

then with probability at least \(1-\alpha\) no incorrectly optimal action is certified during this episode.

**Proof sketch.** Hoeffding's inequality bounds each action-and-checkpoint error by \(\alpha/(KJ)\). A union bound ensures all corresponding source means lie within their sampling radii together. Total-variation control expands each interval by \(\delta\), transferring simultaneous coverage to the target. On that event, strict lower-versus-upper separation implies true target-domain superiority. Because the event covers every allowed checkpoint before the stopping index is selected, optional stopping at a checkpoint does not defeat the result. Full proof and edge cases: [MATHEMATICS.md](MATHEMATICS.md).

An alternative predeclared **unbounded-checkpoint** version spends \(\alpha_j=\alpha/[j(j+1)]\), yielding

\[
r_j^{\infty}=\sqrt{\frac{\log(2Kj(j+1)/\alpha)}{2n_j}}.
\]

It is valid across indefinitely many scheduled checkpoint indices, not arbitrary inspections between them. Both are established union-bound approaches; the research contribution is their audited use for conditional procedure selection and their empirical efficiency/failure analysis.

## 4. Evidence-cost objective and stopping states

The fixed comparator collects \(n_{\max}=6{,}400\) samples for each of six actions, for **38,400 evaluated outcomes** on certifiable tasks. It checks one simultaneous Hoeffding bound at the final sample only. The sequential controller checks nine predetermined sample counts:

\[
25,\ 50,\ 100,\ 200,\ 400,\ 800,\ 1{,}600,\ 3{,}200,\ 6{,}400.
\]

It stops on a strict best-action certificate, or at the budget cap if none emerges. `HOLD` explicitly means no certification; it is **not** a claim that baseline is optimal. Both policies receive the same source outcome stream in each world and share the same declared shift bound, baseline, action costs and maximum sample budget. Both apply the same zero-sample `HOLD` preflight for unknown or provably nonseparating shift.

The primary endpoint is **mean proportional reduction of total action-outcome evaluations among worlds in which both fixed and sequential methods certify the same action**. This denominator excludes worlds where neither certifies, preventing unearned savings from mass abstention. We separately report certification frequency, false certificates and hold frequency. Savings in **synthetic outcome evaluations** are not measured CPU wall time, API tokens, energy, or Pegasus latency.

## 5. Controlled experimental design

Stage K uses six frozen candidate actions, equal known costs of 0.02, independently sampled source task vectors, a 5% error budget, and three candidate policies: fixed-horizon, finite-checkpoint sequential, and unbounded-alpha-spending sequential. For all regimes except intentionally unknown shift, the algorithm receives only the **declared** \(\delta\) and observed source outcomes. The grader alone uses the secret target value vector.

The synthetic target distribution is formed as a **mixture of entire task/outcome vectors**:

\[
Q=(1-\eta)P+\eta B.
\]

Consequently \(d_{\rm TV}(P,Q)\le\eta\), so setting \(\delta\ge\eta\) supplies a genuine known-by-construction bound. This is a favorable idealization; a real agent cannot simply know that a task-population shift satisfies such a bound.

The seven regimes are: stationary easy; stationary near-tie; valid moderate shift; randomly graded shift bounded by 0.10; valid wide shift with a 0.55 bound; deliberately invalid shift with true mixture weight 0.92 but falsely declared 0.02; and unknown shift. World-specific parameters are perturbed with separate deterministic random seeds.

Development used seeds 30000–30119. A first inspected 50000–50399 cohort revealed a software interface improvement: the evaluator's hidden target was part of an object passed to the policy (though never accessed). We archived the earlier source and results, changed the interface so only declared shift and observed evidence are accessible to policy, then froze the algorithm and conducted a **new untouched holdout using seeds 60000–60399** (400 worlds per regime). The final holdout protocol includes exact hashes of the two executable algorithms. No policy parameter was tuned on that final cohort.

## 6. Results: the final 2,800-world holdout

| Synthetic environment (400 worlds each) | Fixed-budget best cert. | Finite-sequential best cert. | Mean evidence saved on jointly certified cases | Incorrect sequential certs. |
|---|---:|---:|---:|---:|
| Stationary, clear winner | 400/400 | 400/400 | **98.71%** | 0 |
| Stationary, near-tie | 7/400 | **0/400** | N/A | 0 |
| Valid moderate shift | 400/400 | 400/400 | **96.07%** | 0 |
| Valid gradual shift | 400/400 | 400/400 | **85.61%** | 0 |
| Valid shift too broad to separate | 0/400 | 0/400; immediate HOLD | N/A | 0 |
| **Falsely declared small shift** | 400/400 | 400/400 | 98.37%, **but invalid** | **400/400** |
| No justified shift bound | 0/400 | 0/400; immediate HOLD | N/A | 0 |

For jointly certified worlds, descriptive 95% *paired world-level* bootstrap intervals for evidence reduction are: easy **[98.67%, 98.75%]**; valid moderate **[95.92%, 96.21%]**; valid gradual **[85.03%, 86.22%]**. These intervals summarize sampling over synthetic world seeds; they are not the 95% confidence guarantee of the decision rule, and this investigation is not preregistered external validation.

At valid known shift, **0 incorrect certificates were observed over 2,000 worlds**, including conservative holds. This observation must not be misread as proof of universally zero failure; the theorem supplies a conditional per-world risk bound when all assumptions hold.

![Outcome evaluations by certified procedure policy](../assets/stage_k_evidence.png)

![Safe savings cannot rescue a false shift assumption](../assets/stage_k_safety_counterexample.png)

### Negative findings

1. **Close calls are hard.** The sequential policy certified none of the near-tie cases, while the fixed check certified seven. Repeated checkpoints spend confidence budget and can reduce the final-check power. There is no uniform dominance.
2. **Some uncertainty is irreducible.** When the valid shift bound is wide enough to preclude strict separation, more source data cannot certify a best action. Returning HOLD before measurement is mathematically appropriate.
3. **A false environment guarantee can be catastrophic.** The intentionally violated shift contract produced an incorrect certificate in every world. Those quick decisions are **not valid improvements**.
4. **The source generator is an oracle simplification.** We did not estimate the shift bound, discover the six procedures autonomously, or test real long-horizon memory effects. Finite-sample calibration is not equivalent to adaptive-structure crystallization.

## 7. Practical interpretation

Under the conditions we can mathematically defend, Version 1.9 provides a reliable **stop-when-certain** selection mechanism with substantial evidence savings on clear problems. The 90% evidence-saving target was met for stationary easy and valid moderate-shift tasks. It was **not** met for valid gradual-shift tasks (85.61%) and is inapplicable for near-ties that the method refuses to certify. The 5% false-certification target is supported by a conditional probability theorem under declared assumptions and observed zero errors in the corresponding synthetic regimes—not by a claim that the model internally detects assumption violation.

A deployable governed controller should **never** treat a `CERTIFY_BEST` output as permission to mutate memories, approve a self-modified procedure, or bypass independent evaluation. A certification is a mathematical claim about fixed candidates and stated assumptions. External authorization and receipts remain separate.

## 8. Research status and next falsifiable milestones

**H1:** Planted synthetic higher-order interactions established in earlier work, not retested here. **H2:** No phase transition or scaling law established. **H3:** No independent long-run improvement discovery or learning-to-learn established. **New v1.9 finding:** Strong synthetic evidence savings for conditional decision certificates, with a formal finite-checkpoint coverage result and an explicit high-confidence failure under false shift bounds.

Next: investigate tighter paired-outcome confidence sequences, sensitivity to bounded but unknown costs, defensible *learning or auditing* of domain-shift bounds, and a combined interaction-selection-certification experiment with **fresh unseen task families**. Do not integrate this into Pegasus or call the crystal stable until the shift contract and the candidate-generation process are grounded in actual execution evidence.

## 9. Reproduce and audit

From the extracted package root, Python 3.10+ and NumPy 2.3.5 for exact byte-level replay:

```bash
python -m pip install -r requirements-repro.txt
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m agentic_crystallization.stage_k \
  --out experiments/stage_k_reproduced --start-seed 60000 --count 400 --stage holdout
python scripts/verify_stage_k.py experiments/stage_k_reproduced --root .
```

PowerShell: `$env:PYTHONPATH='src'` and `$env:OPENBLAS_NUM_THREADS='1'` before running the `python -m` commands. Do not write into the sealed `experiments/stage_k_holdout` folder. The replayed `protocol.json`, `runs.csv`, and `summary.json` should hash identically with this package's frozen source and NumPy version.

**Files:** [Python controller](../src/agentic_crystallization/sequential_certificate.py) · [World generator](../src/agentic_crystallization/stage_k.py) · [Final raw CSV](../experiments/stage_k_holdout/runs.csv) · [Frozen protocol](../experiments/stage_k_holdout/protocol.json) · [Manifest](../experiments/stage_k_holdout/manifest.json) · [Mathematical details](MATHEMATICS.md) · [Claim ledger](CLAIM_LEDGER.md) · [Source/version continuity](CONTINUITY_AUDIT.md).
