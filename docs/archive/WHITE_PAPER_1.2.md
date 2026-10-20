# AGENTIC CRYSTALLIZATION v1.2
## Conditional Transfer, Negative Transfer, and the Boundary of Learning-to-Learn

**Research status:** Reproducible synthetic experiments; no observed phase transition, autonomous self-improvement, or physical crystallization.

**Continuity:** v1.0 Stage A and v1.1 Stage B/C source, tests, results and figures are retained. See [the full archived v1.1 paper](archive/WHITE_PAPER_1.1.md).

## Abstract

The earlier experiments established that interaction-aware selection can exploit planted triple dependencies without receiving a benefit from dense but noncausal graph metadata. Version 1.2 investigates a separate claim: whether knowledge of one validated procedure can reduce the search required to validate the next procedure. A deterministic exact-match oracle, matched candidate universe, 40-query budget and paired seeds permit a controlled synthetic comparison. We find positive transfer when the next target belongs to the same planted latent family, but negative transfer when the family changes. The outcome is conditional transfer, not generalized learning-to-learn or a critical coherence threshold.

## 1. Hypothesis ladder and claim ledger

- **H0:** Independent procedure benefits, caching, smooth optimization, or matched compute explain any advantage.
- **H1:** Some procedure sets exhibit nonadditive utility. Supported algebraically and detected in planted synthetic cases.
- **H2:** Functional connectivity causes a reproducible nonlinear adaptive transition beyond smooth nulls. **Not established.**
- **H3:** A validated cluster makes the next independently validated improvement easier or cheaper. **Only a restricted synthetic precursor tested here**; first-cluster discovery is supplied by the world generator.

An experiment can measure useful interactions without discovering a new law of physics or intelligence.

## 2. Mathematical continuity

Let J(S;D) be independently measured expected task utility from procedure set S. The finite-difference/Möbius interaction for disjoint S,T is

\[
\Gamma_T(S)=\sum_{A\subseteq T}(-1)^{|T|-|A|}J(S\cup A;D).
\]

For a pure three-way AND dependency, the three-way coefficient at the empty baseline is one, while every empty-baseline pairwise coefficient is zero.

A candidate *engineering* cost potential is

\[
F(S)=\alpha B(S)+\kappa V(S)-\beta U(S),
\]

where B is measured boundary/coordination cost, V is verification and maintenance, and U is independently measured future utility. This is not physical free energy. Structural connected-component fraction and adaptive efficiency must be measured independently. Neither has an established critical threshold in this project.

## 3. Stage D experimental protocol

For each catalog size n in {12,15,18}, the generator samples two disjoint latent families A and B of six procedures each. The first validated triple comes from A. The next hidden target comes from A in the **related** condition (but is a different triple) or from B in the **unrelated** condition.

The procedure catalog is the same for all policies: every three-element subset of the n procedures. The same shuffled base ordering is shared across policies. A query to the deterministic oracle costs one attempt and succeeds only when the queried triple equals the target. The search stops at success or 40 attempts.

**Policy arms:** no-prior random search; cache-only (replay first triple then random); cluster-prior (rank by overlap with first triple); sham-prior (rank by overlap with a random unrelated-to-target-knowledge triple); ablated-prior (no-prior identity); restored-prior (cluster-prior identity). The hidden target and latent family membership are never passed to a policy.

The precise intervention is changing the *candidate ordering* based on an already validated first triple. It is not a causal intervention on a learned graph or a self-modifying runtime. Discovery time is right-censored after 40 queries. The cost outcome is restricted attempts min(T,40), not an imputed time to success for failures.

Exploratory seeds 0–199 and disjoint validation seeds 200–399 produce 600 worlds per condition in each cohort. Bootstrap percentile intervals resample worlds as paired units (3,000 replicates, seed 41); these are descriptive rather than preregistered confirmatory inference.

## 4. Independently seeded validation results

| Condition | No prior success | Cluster prior success | Sham prior success | Paired success difference (95% bootstrap) | Restricted attempts saved (95% bootstrap) |
|---|---:|---:|---:|---|---|
| Related | 0.100 | 0.462 | 0.093 | +0.362 [+0.320, +0.405] | +7.83 [+6.85, +8.87] |
| Unrelated | 0.110 | 0.000 | 0.128 | -0.110 [-0.135, -0.085] | -1.90 [-2.42, -1.38] |

The exploratory cohort independently shows the same direction: related +0.357 discovery probability; unrelated -0.110. Ablation exactly reproduces the no-prior ordering and restoration exactly reproduces the cluster-prior ordering by construction; this is a software invariant, not a separate empirical replication.

## 5. Main mathematical finding: a transfer boundary

Let Z denote whether the next task belongs to a related latent family. The benefit of a cluster-conditioned search is context-dependent:

\[
\Delta(x)=E[Y_{\mathrm{cluster}}-Y_{\mathrm{baseline}}\mid x].
\]

The synthetic benchmark demonstrates a positive delta in the related regime and a negative delta in the unrelated regime. Therefore a policy that *always* reuses a cluster can be worse than no memory.

A possible future rule is to reuse only when

\[
E[\Delta(x)\mid \text{training-visible evidence}] > \text{reuse cost}+\text{risk margin}.
\]

The expectation and gate must be learned and evaluated on separate data. No threshold was calibrated in this version.

## 6. What this does not prove

The first validated procedure is given without charging the cost of its discovery. The second search is a fixed ordering that does not update after negative observations. Latent families are planted, exact-match oracles are simplistic, and the unrelated groups are disjoint. Thus this study does not establish full H3, autonomous candidate discovery, robust transfer across gradual drift, or self-organized procedural clustering. It also does not test H2 criticality, finite-size scaling collapse, hysteresis, or susceptibility peaks. No real language model or Pegasus execution is involved.

## 7. Next experiment

Version 1.3 should charge for discovery of the first validated cluster; vary relatedness continuously; learn a context-sensitive reuse/abstain gate on training data; update posterior beliefs after failed queries; and report accepted utility per total learning+inference cost on untouched seeds. Retain additive, cache, sham, and unrelated negative controls. Do not select the gate using the final holdout.

## 8. Reproduction and sources

Run `PYTHONPATH=src OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v` and `PYTHONPATH=src python -m agentic_crystallization.stage_d --out experiments/reproduced --seeds 200 --budget 40`. For validation seeds 200–399, call `run(Path('experiments/reproduced_validation'),seeds=range(200,400))` from `agentic_crystallization.stage_d`.

[Stage A code](../src/agentic_crystallization/stage_a.py) · [Stage B code](../src/agentic_crystallization/stage_b.py) · [Stage D code](../src/agentic_crystallization/stage_d.py) · [Stage D tests](../tests/test_stage_d.py) · [Validation manifest](../experiments/stage_d_validation/manifest.json) · [Raw validation CSV](../experiments/stage_d_validation/runs.csv) · [Full prior whitepaper](archive/WHITE_PAPER_1.1.md).

Related established fields include combinatorial interaction decomposition, transfer learning, censored event-time analysis, network percolation and classical nucleation (structural analogy only). No mathematical priority is claimed.
