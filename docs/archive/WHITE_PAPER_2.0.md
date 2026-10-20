# Agentic Crystallization v2.0
## A Governed Closed-Loop Prototype for Conditional Procedure Discovery, Certification, and Retention

**Version:** 2.0.0  
**Research status:** Executable synthetic prototype; conditional mathematical guarantees; no literal phase transition or general self-improvement established.  
**Continuity:** All v1.0–v1.9 sources, experiments, mathematical papers, and audited v1.9 ZIP are preserved.  

[Precise proofs](MATHEMATICS.md) · [Algorithm](ALGORITHM_CARD.md) · [Complete protocol](PREREGISTRATION_STAGE_L.json) · [Raw results](../experiments/stage_l_holdout/runs.csv) · [Original v1.9 paper](archive/WHITE_PAPER_1.9.md)

### Abstract

Agentic Crystallization investigates whether interacting, validated computational procedures can form persistent, useful structures that lower the cost of adapting to future tasks. Versions 1.0–1.9 isolated higher-order utility interactions, environmental negative transfer, Bayesian relevance estimates, bounded-error decision certificates, and sequential evidence stopping. However, these studies did not produce an autonomous procedure-discovery/retention lifecycle. Version 2.0 implements a finite, controlled loop that proposes XOR compositions without access to the hidden target, evaluates a single preselected candidate on independent observations, certifies positive expected benefit using a lifetime error-spending rule, durably retains eligible compositions, prunes or revalidates memory after drift, and charges task-feedback and computational costs against a nonnegative resource account. A separate synthetic test harness provides recurring, abruptly changing, four-way-unlearnable, appropriately bounded-shift, unknown-shift, and deliberately falsified-shift worlds. The new artifact is a reproducible **closed-loop prototype**, not evidence that arbitrary digital information self-organizes by itself or that the system can run indefinitely without external energy and rewards.

## 1. Why v2.0 and what would count as success?

A system cannot be considered self-sustaining merely because it has a memory database, a reward estimator, and an agent loop. Those components can accumulate stale, incorrect procedures. We require an explicit feedback mechanism that autonomously performs all five steps, without a human directing each individual episode:

1. Propose candidates from a permitted procedure algebra.
2. Evaluate a proposal using observed task outcomes, not privileged generator truth.
3. Certify or HOLD on statistically independent evidence with externally justified shift assumptions.
4. Retain, revalidate, reactivate, and prune procedural structures under bounded capacity.
5. Account for computation, maintain a durable replayable state, and refuse unaffordable or unjustified work.

Even all five properties demonstrate only **bounded operational closure**. They do not prove unbounded survival or emergent consciousness. The experiment tests whether the components work together in finite, observable trajectories.

## 2. Mathematical object and interaction substrate

Define a bounded computational crystal $\mathcal C=(\mathcal P,\mathcal G,M,\mathsf Cert,B,L)$, where $\mathcal P$ is a whitelisted procedure family, $\mathcal G$ an evidence-conditioned candidate generator, $M$ bounded procedural memory, $\mathsf Cert$ a conditional sequential decision certificate, $B$ task-feedback credits, and $L$ a hash-linked receipt ledger. The state evolves as $s_{t+1}=T(s_t,o_t)$ as the task stream supplies fresh observations $o_t$.

Our control environment plants a three-way parity relation in eight independent binary features. No one-feature or two-feature subset predicts the target better than chance. A candidate XOR of the correct three features achieves perfect accuracy on the source law. Defining $J(S)$ as the Bayes-optimal prediction accuracy using only a feature subset $S$, the triple Möbius interaction is exactly $+1/2$, with zero empty-baseline pairwise terms. This is standard finite-difference mathematics on a synthetic constructed task. It is **not** a discovery of a natural crystallization force or critical exponent.

The permitted runtime search space includes 92 XOR expressions of order one, two, or three, plus a constant baseline. A four-way parity task is a structural **negative control**: it has no exact solution in this fixed candidate family. Crucially, the runtime does not receive the true parity indices. It must rank candidates using exploratory labeled examples.

## 3. Fresh certification and lifetime risk budget

Fix a candidate $\pi_e$ **before** seeing its independent validation stream. Define paired gain over baseline $D_e=1\{\pi_e(X)=Y\}-1\{\pi_0(X)=Y\}\in[-1,1]$. Let a trusted environment contract supply a direct bound on the change of its mean from validation to deployment, $|\mu_{P,e}-\mu_{Q,e}|\le\Delta_e$, otherwise return HOLD.

Allocate lifetime error allowance $\alpha=0.05$ across episodes as $\alpha_e=\alpha/[e(e+1)]$, and across four predeclared validation checkpoints $n\in\{64,128,256,512\}$. A lower confidence bound is

$$
\boxed{L_{e,j}=\widehat\mu_{e,j}-\sqrt{\frac{2\log(4/\alpha_e)}{n_j}}-\Delta_e.}
$$

Certify **positive gain relative to baseline** only if $L_{e,j}>\varepsilon$ with $\varepsilon=0.025$. Under fresh conditional IID within each episode, honest bounded gains, independent proposal/validation, a correct shift allowance, and a never-reset epoch/error ledger,

$$
\boxed{\Pr(\exists\text{ an incorrectly promoted episode over the lifetime})\le\alpha.}
$$

The proof is a one-sided Hoeffding bound unioned across checkpoints and the telescoping sequence of episode budgets. It is a conditional standard statistical guarantee; it does not claim globally optimal procedure selection. Detailed proof and all conditions: [MATHEMATICS.md](MATHEMATICS.md).

### Independent structure versus adaptive accumulation

A stored procedure is never considered certified in a new epoch. It is only nominated via a fresh contextual scout sample, then must pass the fresh certificate. A new task pattern triggers exhaustive search of the bounded procedure family. A recurring pattern can reactivate a previously stored candidate and avoid the full discovery search. Entries that cease receiving successful certificates expire or are evicted; at all times the memory size is at most four.

This gives a reproducible, operational meaning to *selective crystallization*: validated structural combinations are retained only when there is fresh evidence that they help in the present context. It does not assume permanent validity from past success.

## 4. Credits, retention, and the scope of “self-sustaining”

The state carries an evaluation credit balance $B_e$, with expenditure $C_e$ and nonnegative task-delivery revenue $R_e$. Its update is $B_{e+1}=B_e-C_e+R_e$, with a guard that enforces $0\le C_e\le B_e$. Therefore $B_e\ge0$ by induction from $B_0\ge0$. This is a **no-overdraft invariant**, not a free-energy theorem or a proof of indefinitely positive gains.

The benchmark separately measures *task utility improvement over the baseline minus evaluation, computation and memory expenses*. Those resource and utility units are synthetic. External tasks replenish the budget: the loop is **not closed with respect to matter, energy, or external information**. If there are no tasks, rewards, power, or justified environmental assumptions, the system cannot claim self-sustaining operation.

### Receipts and recovery

Each completed episode emits an immutable-intent JSONL receipt containing selected candidate, certificate status and interval, charged observations, procedure evaluation operations, outcome digest, resource movement, prior record hash, and pre-/post-state commitments. Restart reconstructs the state deterministically from the receipts. Truncation, reordered receipts, and changed bytes fail closed. The chain is **not** a trusted digital signature, is single-writer only, and does not authenticate untrusted originators; its replayability is still valuable for reproducibility and debugging.

## 5. Frozen experimental contract

Stage L compares four policies on the **same synthetic worlds**:

| Policy | Definition |
|---|---|
| `crystal` | Bounded generation + remembered candidate scout + fresh certification + bounded retention |
| `memoryless` | Full bounded candidate search in every epoch + the same fresh certification |
| `reuse_only` | Learn one initial candidate and never revise the candidate pool; fresh validation still required |
| `baseline` | Constant-zero procedure, no adaptive search |

Seven named regimes distinguish stable patterns, recurrence, abrupt concept changes, a four-way unlearnable pattern, known limited within-epoch shift, missing shift justification, and a deliberately false shift declaration. Each world contains **12 epochs**. The source/validation/live splits are disjoint pseudo-random streams derived from stable seed labels. The simulator sees the hidden task configuration; candidate-generation code receives only labeled examples and the declared shift allowance.

The complete final sample selection, locked code SHA-256 values, metrics, and negative controls are [preregistered here](PREREGISTRATION_STAGE_L.json). A separate development cohort was examined before freezing code. **Experiment outcomes and their limitations are reported below, including failed cases; do not optimize the code on holdout outcomes and then call the same cohort independent.**

## 6. Experimental results

_See [Stage L holdout summary](../experiments/stage_l_holdout/summary.json), [raw paired per-epoch results](../experiments/stage_l_holdout/runs.csv) and [figure](../assets/stage_l_results.png). The consolidated numeric table in the README is generated from these files._

![Final held-out utility comparison](../assets/stage_l_results.png)

![Candidate evaluation cost on unseen worlds](../assets/stage_l_search_cost.png)

The main performance contrast is whether memory-conditioned reactivation saves observations and procedure-prediction operations relative to rediscovering from scratch while maintaining the same opportunity to certify. A second essential contrast is whether a fixed initial procedure loses utility when target patterns change. No certification in the four-way negative control is a guard against overfitting. Missing shift justification must produce HOLD without fabricated confidence.

![Failure case under invalid shift bound](../assets/stage_l_shift_failure.png)

The false-shift case intentionally violates the theorem's premise. A successful negative control here is **observable erroneous certifications**. Reporting this failure is necessary to delimit every positive result.

## 7. What has *not* crystallized

We do **not** claim any observed computational phase transition, a self-organizing physical crystal, open-ended agent intelligence, an automatically valid drift bound, optimization over arbitrary programs, or real Pegasus productivity gains. The procedure family, source generator, proposal heuristics, checkpoint schedule and simulated credit exchange rates are chosen by the designers. Their usefulness for real agents would require new independent task and calibration data.

The proven ingredients are conditional error bounds and finite-memory/resource invariants. The observed ingredient is the autonomous finite loop in a controlled synthetic environment. Neither implies indefinite positive growth or self-sufficiency without external tasks.

## 8. Next research milestone and falsifiers

For v2.1, the relevant question is whether the same loop remains useful when *the proposal family expands, feedback arrives late, context drift must be estimated rather than provided, and evaluation costs vary*. A negative result is acceptable. No new mathematics should be promoted if it improves a single benchmark while violating safeguards or losing to simpler baselines.

A general self-sustaining computation claim would require a justified environmental-shift mechanism, replay-safe distributed receipts, accepted production data, positive amortized utility after **all** costs, long-horizon recovery, strong adaptive and causal baselines, and stable failure controls. v2.0 deliberately makes no such claim.

## Reproduce and inspect

```bash
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPATH=src python -m agentic_crystallization.stage_l --out experiments/local_run --start-seed 90000 --count 10 --demo-seed 2020
python scripts/verify_stage_l.py experiments/local_run --repo .
python scripts/verify_package.py .
```

Do not write to sealed experiment folders. [Human-facing README](../README.md) · [Full equations](MATHEMATICS.md) · [For agents](FOR_AGENTS.md) · [Historical v1.9 whitepaper](archive/WHITE_PAPER_1.9.md).

### An impossibility result that limits open-ended autonomy

Two hypothetical deployment environments can supply identical source observations but have inverted deployment outcomes. The learner will make the same source-based decision in both, while a source-perfect XOR procedure's expected gain changes from $+1/2$ to $-1/2$. Therefore no algorithm using only those identical source observations can uniformly guarantee a nontrivial positive-gain certificate under unrestricted deployment change. This is a simple observational-indistinguishability argument, not a newly discovered physical law. It explains why a truly autonomous system needs **trustworthy new target-domain feedback or a valid shift/invariance contract**; a more sophisticated mathematical score cannot substitute for missing information. See [the proposition and proof](MATHEMATICS.md#8-impossibility-of-assumption-free-deployment-certification).
