# Mathematical foundations — Agentic Crystallization v1.8

[README](../README.md) · [Full whitepaper](WHITE_PAPER.md) · [Algorithm card](ALGORITHM_CARD.md) · [Empirical methods](EXPERIMENTS.md)

## 1. Non-additive value

For procedure set $S$ and fixed task distribution $D$, define $J(S;D)=E[U(x,S)]$. For disjoint $T$ and $S$, the full finite difference is

$$\Gamma_T(S)=\sum_{B\subseteq T}(-1)^{|T|-|B|}J(S\cup B;D).$$

This is Möbius inversion on a Boolean lattice, not a new identity. A three-way AND benefit can have all pairwise coefficients zero at an empty baseline. An observed nonzero coefficient is a structural utility interaction, not automatically a causal hyperedge.

## 2. Statistical simultaneous error

Let the *fixed* action catalog have size $K$, observed tasks be independent across $i$, and all successes $Y_{ia}$ be in $[0,1]$. For source-domain mean $p_a$,

$$\Pr\{|\widehat p_a-p_a|>\epsilon\}\le 2\exp(-2n\epsilon^2).$$

Union bounding **all** fixed actions at once yields

$$\epsilon_{n,K,\alpha}=\sqrt{\frac{\ln(2K/\alpha)}{2n}},\qquad\Pr\left(\max_a|\widehat p_a-p_a|\le\epsilon_{n,K,\alpha}\right)\ge1-\alpha.$$

No independence across actions is needed. Selecting or inventing extra actions by looking at calibration labels invalidates the library-freezing assumption.

## 3. Target-shift transport

For a bounded function $0\le f\le1$ and total variation TV of joint distributions, $|E_Q f-E_P f|\le \operatorname{TV}(P,Q)$. For covariate shift alone, the same statement requires unchanged $P(Y|x)$ and TV of context marginals. With $\delta\ge\operatorname{TV}(P,Q)$ externally established,

$$L_a=\max(0,\hat p_a-\epsilon-\delta)-c_a,\quad U_a=\min(1,\hat p_a+\epsilon+\delta)-c_a.$$

All true target net utilities lie in their respective intervals with probability at least $1-\alpha$ under the assumptions. *Cost is deterministic and comparable.* If cost varies with environment, new bounds are required.

## 4. Two different certificates

- **Unique best:** $L_{a^*}>\max_{b\ne a^*}U_b$ implies $a^*$ outranks every allowed alternative.
- **Baseline gain:** $L_a>U_{a_0}$ implies $a$ outranks named baseline $a_0$, but not necessarily every rival.

Both proofs use lower-bound > upper-bound on the simultaneous coverage event. Strict inequality matters; equality admits a tie. Selecting the baseline when no gain is certified does **not** certify baseline optimality.

## 5. Higher-order coefficient uncertainty

For a prespecified $k$-procedure group with **all** $2^k$ factorial subsets evaluated,

$$|\widehat\Gamma_T-\Gamma_T|\le\sum_{B\subseteq T}e_B\le2^k(\epsilon_{n,2^k,\alpha}+\delta).$$

The first inequality is the triangle inequality. The second holds if every subset has the same simultaneous statistical/shift radius. Certified positive (or negative) interaction requires the estimated coefficient to exceed the radius (or fall below its negative). Omitting higher-order terms or testing many adaptively chosen interaction groups requires additional statistical accounting. Exact factorial costs can cancel when additive, but the method does not assume they do.

## 6. No universal drift certificate

Construct two contexts $x_0,x_1$ and actions $a,b$. Calibration $P$ puts all mass on $x_0$, where $a$ and $b$ have indistinguishable outcomes. Target $Q_1$ puts mass on $x_1$, where $a$ is superior; target $Q_2$ also puts mass on $x_1$ but has a different conditional outcome kernel where $b$ is superior. Source data cannot distinguish these target worlds, even as $n\to\infty$. Without a constraint on joint distribution shift or stable outcome kernels, certifying one unique best action uniformly across both targets is impossible.

**Implication:** additional source samples reduce statistical uncertainty but do not generally reduce target-domain uncertainty or model misspecification. The simulation includes a deliberately false drift bound to expose this failure mode.

## 7. Algorithmic complexity and scope

Calibration of a fixed action library needs $O(nK)$ bounded outcome observations. Ranking and baseline-gain selection take $O(K)$ (plus optional sorting for deterministic tie-breaks). Full factorial interaction tests for order $k$ need $2^k$ subset outcomes per calibration task; certification gets exponentially more conservative as $k$ grows. These costs have not been justified for actual Pegasus workloads.

The objective is **stability conditional on an operating domain**, not a universally perfect adaptive algorithm. No property in this document constitutes a physical phase-transition proof.
