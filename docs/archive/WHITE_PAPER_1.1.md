# Agentic Crystallization v1.1
## Observation-Limited Hypergraph Interactions and Critical-Regime Controls

**Research status:** Executed synthetic study. **No actual crystallization threshold, autonomous learning, or real-agent self-improvement has been demonstrated.**

## Abstract
Agentic Crystallization hypothesizes that validated, reusable procedures can form useful functional combinations and might, under additional conditions, exhibit collective adaptive thresholds. Version 1.0 demonstrated recovery of planted interactions under generous full-factorial synthetic training. Version 1.1 adds a limited-observation experiment: randomized training subsets, fixed candidate hyperedge vocabulary, sparse ridge estimation, an intervention sweep in planted triple-interaction density, additive and misleading-connectivity controls, and a disjoint-seed validation cohort. The interaction-aware policy improves synthetic held-out utility over the strongest matched simple policy by **+0.1775** in the exploratory cohort and **+0.1655** in the validation cohort. Controls are near zero or slightly negative. These findings support exploiting planted interactions, not a critical phase transition.

## 1. Hypotheses and definitions
Let $P$ be a finite procedure catalog, $S\subseteq P$ a selected subset, and $J(S;\mathcal D)$ expected independently graded utility. **H0:** additive benefit, caching, increased compute, or smooth improvement suffices. **H1:** nonadditive procedure combinations provide extra utility. **H2:** a reproducible nonlinear adaptive transition occurs as *functional* dependencies change, beyond smooth null models. **H3:** a previously learned validated cluster reduces cost/time to the next independently validated improvement. H1 does not imply H2, and H2 does not imply H3.

## 2. Interaction mathematics
Pairwise finite differences are

$$\Gamma_{ij}(S)=J(S\cup\{i,j\})-J(S\cup\{i\})-J(S\cup\{j\})+J(S).$$

For disjoint $S,T$, higher-order Möbius coefficients are

$$\Gamma_T(S)=\sum_{A\subseteq T}(-1)^{|T|-|A|}J(S\cup A).$$

If success requires the full triple $\{a,b,c\}$, all pairwise interactions at the empty baseline can be zero while $\Gamma_{abc}(\varnothing)=1$. This is a mathematical identity for a specified set function, not a novel law. Coefficients are baseline-dependent.

## 3. Graph structure versus utility
The old nucleation toy $F(n)=\alpha n^{2/3}-\beta n$ assumes three-dimensional geometry without justification for procedure graphs. A graph-dependent *engineering* cost potential is proposed:

$$F(S)=\alpha B(S)+\kappa V(S)-\beta U(S),$$

where $B$ is boundary coordination cost, $V$ is validation/maintenance cost, and $U$ is measured future utility. It is **not thermodynamic free energy**. Define separately structural connectedness $C_G=|V_{\max}|/|V|$ and adaptive advantage $\Delta_A=J_{\rm interaction}-J_{\rm strongest\ simple}$. A large connected component does not imply useful learning. Retention, validated reuse, graph stability, and time-to-next-improvement remain unmeasured in v1.1.

## 4. Preserved Stage A
The v1.0 package evaluated 180 synthetic worlds, five policies, and fully enumerated training subsets up to order three. It showed advantages for interaction-aware selection in planted pairwise/triple families, but not additive/misleading families. It did not evolve a graph or demonstrate learning-to-learn. Its original code, raw data, and manifest remain in this release.

## 5. New Stage B/C protocol
The synthetic oracle is

$$Y(S)=\sum_{i\in S}w_i+\sum_{T\subseteq S,|T|=3}\eta_T.$$

For $n\in\{12,18,24\}$ procedures, choose a fixed candidate vocabulary of $2n$ triples. Plant $\operatorname{round}(dn)$ active triples at density $d\in\{0,.15,.30,.45,.60,.75,.90\}$ with positive weights. Additive worlds have no active triples; misleading worlds contain equally dense *metadata* triples but no functional utility interactions. All policies see the same **160** random training subsets of sizes four to six. Ridge regression (penalty 1, unpenalized intercept) estimates singleton and candidate-triple coefficients. On **30** fresh availability masks per world, policies select four procedures from eight available. Five policies are compared: no-memory lexicographic, cache-only (exact matches with additive fallback), additive, same-estimates-linear (redistributed interaction coefficients), and interaction-aware. None sees planted active edges or oracle test scores during selection.

Two cohorts of four disjoint seeds each, three sizes, seven densities, and three families yield **252 worlds per cohort**, **504 total worlds**, **15,120 held-out contexts**, and **75,600 policy evaluations**. The sweep changes *functional* interactions for the synergy family and only metadata for the misleading family. This is a planted synthetic causal intervention, not real-agent causal discovery.

## 6. Executed results

| Family | Exploratory advantage | Disjoint-seed validation advantage |
|---|---:|---:|
| Planted triple synergy | **+0.1775** | **+0.1655** |
| Additive | -0.0018 | -0.0020 |
| Misleading connectivity | -0.0013 | -0.0014 |

The advantage is a world-level difference from the **maximum** of the cache-only, additive, and same-estimates-linear policy scores, then averaged over 84 worlds per family per cohort. This descriptive maximum is deliberately stringent but not a preregistered significance test. Exploratory synergy connected-component fraction rises from about 0.06 at density zero to about 0.93 at density .90, while the advantage rises from approximately zero to +0.327. Misleading connectivity rises to about 0.92 with no utility advantage. The observed benefit varies with the number of planted useful interactions, with no demonstrated discontinuity, finite-size scaling collapse, or hysteresis.

## 7. Boundaries and falsification
The model class contains the planted triple interaction order and a restricted candidate vocabulary. The experiment has no changing procedure library, no second learning cycle, no real language model, no Pegasus integration, and no longitudinal retention. No confirmatory p-value or threshold fit is claimed. Noise-free oracle test scores and particular budgets favor this synthetic construction. The disjoint validation seeds are independent of the exploratory seeds but the overall protocol was developed iteratively, so this is not a sealed preregistered study. Falsification requires comparing to smooth nulls, degree-preserving rewiring, metadata permutations, controlled ablations, larger and heterogeneous graphs, and ultimately measuring the cost of a *subsequent* validated improvement.

## 8. Next study
Freeze a new protocol before drawing new seeds. Add degree-preserving hypergraph rewiring and ablation/restoration, a stronger edge-agnostic baseline, finite-size sensitivity, out-of-sample smooth versus change-point model comparisons, and an actual longitudinal second-improvement experiment. Keep synthetic research isolated from active Pegasus memory and promotion authority.

## Conclusion
The v1.1 experiment reproduces a **limited advantage from exploiting planted higher-order interactions** and rejects descriptive graph density alone as sufficient in these controls. It does **not** show Agentic Crystallization as a critical phenomenon or autonomous self-improvement. The important next quantity is whether a retained validated cluster lowers the cost of learning the next one.

## Prior mathematical and engineering context
Möbius inversion, factorial experimental designs, network percolation, compositional skills, meta-learning, and adaptive data analysis predate this proposal. Related research: [GEPA](https://arxiv.org/abs/2507.19457), [ACE](https://arxiv.org/abs/2510.04618), [MAML](https://arxiv.org/abs/1703.03400). No priority claim is made for these foundations.
