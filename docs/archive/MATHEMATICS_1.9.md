# Agentic Crystallization v1.9 — Mathematical foundations

[Overview](../README.md) · [Research paper](WHITE_PAPER.md) · [Experiment design](EXPERIMENTS.md) · [Implementation](../src/agentic_crystallization/sequential_certificate.py) · [Historical v1.8 mathematics](archive/MATHEMATICS_1.8.md)

## 1. What is—and is not—being solidified

A *procedure* can be an individual action or a **pre-validated, frozen combination of actions**. In this version the candidate library is fixed **before** sampling. We certify decisions about members of that library; we do **not** generate new combinations, infer causal hyperedges, demonstrate autonomous learning, or establish a critical phase transition. The mathematical advance is reduced evidence cost for conditional decision certification.

Let \(\mathcal A=\{a_1,\ldots,a_K\}\), with named baseline \(a_0\). Each source task \(X_t\sim P\) supplies a bounded evaluation \(f_a(X_t)\in[0,1]\) for every frozen action \(a\). The task vectors \(X_1,X_2,\ldots\) are independent and identically distributed under a **fixed** source law \(P\). Correlation among the action outcomes evaluated on the **same** task is permitted. Known action costs \(c_a\in[0,1]\) do not change between the source and target environments.

Define source and target net value

\[
V_P(a)=\mathbb E_P f_a(X)-c_a,\qquad
V_Q(a)=\mathbb E_Q f_a(X)-c_a.
\]

The critical external assumption is a **justified** upper bound \(d_{\mathrm{TV}}(P,Q)\le\delta\), where \(P,Q\) are the relevant **joint distributions** of tasks and action outcomes. A marginal context-shift bound alone does not suffice when the outcome mechanism also changes. For every \(f_a\in[0,1]\),

\[
|\mathbb E_P f_a-\mathbb E_Q f_a|\le\delta.
\]

The code never learns or derives \(\delta\). If it is unavailable, it returns `HOLD` without certifying any action.

## 2. A finite-checkpoint simultaneous confidence theorem

Fix in advance \(K\), the candidate actions, significance \(0<\alpha<1\), and \(J\) checkpoints \(1\le n_1<\cdots<n_J\). At checkpoint \(j\), for action \(a\), observe the empirical source mean

\[
\widehat\mu_a(n_j)=\frac{1}{n_j}\sum_{t=1}^{n_j}f_a(X_t).
\]

Use the radius

\[
\boxed{r_j=\sqrt{\frac{\log(2KJ/\alpha)}{2n_j}}.}
\]

**Theorem 1 (simultaneous fixed-family confidence).** Under the assumptions in Section 1,

\[
\Pr_P\!\left(\forall a\in\mathcal A,\ \forall j\in\{1,\ldots,J\}:\ |\widehat\mu_a(n_j)-\mathbb E_Pf_a|\le r_j\right)\ge1-\alpha.
\]

**Proof.** Hoeffding's inequality gives \(\Pr(|\widehat\mu_a(n_j)-\mu_a|>r_j)\le 2\exp(-2n_jr_j^2)=\alpha/(KJ)\) for each action and checkpoint. The union bound over \(KJ\) predeclared pairs yields total violation probability at most \(\alpha\). No cross-action independence is required. \(\square\)

> This is a standard finite-horizon group-sequential/union-bound construction. The theorem is not new. The release contributes an audited procedure-decision application and measured evidence-cost tradeoffs.

**Important nuance:** The confidence guarantee applies at the **predeclared checkpoints**, not to arbitrary continuous monitoring between them. The code checks only those checkpoints.

## 3. Target-domain interval and certification theorem

For each \(a,j\), define

\[
L_{a,j}=\max(0,\widehat\mu_a(n_j)-r_j-\delta)-c_a,
\]

\[
U_{a,j}=\min(1,\widehat\mu_a(n_j)+r_j+\delta)-c_a.
\]

On the simultaneous event from Theorem 1, every target-domain value \(V_Q(a)\) is in **every** corresponding interval \([L_{a,j},U_{a,j}]\). The intervals account for both sampling error and the declared domain-shift budget.

**Theorem 2 (certified best at an adaptive stopping checkpoint).** Suppose the algorithm chooses a data-dependent index \(\tau\in\{1,\ldots,J\}\) and an action \(a^*\) only when

\[
\boxed{L_{a^*,\tau}>\max_{b\ne a^*}U_{b,\tau}.}
\]

Then with probability at least \(1-\alpha\), **every** certified action is strictly optimal for the target among the fixed library, for that world and its prescribed assessment sequence.

**Proof.** On the simultaneous event, for every \(b\ne a^*\), \(V_Q(a^*)\ge L_{a^*,\tau}>U_{b,\tau}\ge V_Q(b)\). The event covers all checkpoints before the stopping rule is applied, so the stopping time cannot invalidate it. \(\square\)

The **weaker** statement \(L_{a,\tau}>U_{\mathrm{baseline},\tau}\) certifies improvement over the baseline *only*, not global optimality. The implementation exposes `objective='gain'` separately; Stage K uses the stricter `best` endpoint.

A certified baseline means **no upgrade is justified**, not successful discovery of a new improved procedure. `HOLD` or `CONTINUE` does not mean that the baseline is optimal.

## 4. Checkpoints without a known final horizon

For checkpoint indices \(j=1,2,\ldots\) set a per-look error budget \(\alpha_j=\alpha/[j(j+1)]\). Because \(\sum_{j\ge1}1/[j(j+1)]=1\), the radius

\[
\boxed{r_j^{\infty}=\sqrt{\frac{\log(2Kj(j+1)/\alpha)}{2n_j}}}
\]

provides simultaneous confidence across a **countably infinite predeclared checkpoint schedule**. Its proof is the same union bound across the \(K\) actions and the infinite alpha-spending series. Stage K benchmarks both versions under the same nine actual checkpoints and sample cap. This does **not** justify peeking at arbitrary non-checkpoint samples or recycling the same error budget across indefinitely many newly invented action libraries.

For repeated deployments over many decision episodes, allocate a new episode-level error budget \(\alpha_e\) such that \(\sum_e\alpha_e\le\alpha_{\mathrm{lifetime}}\); source/target assumptions must separately hold in each episode. No continuous, autonomous online application is claimed.

## 5. Sample-efficiency and limits

With equal costs, ignoring interval clipping, the robust best-vs-rival comparison can succeed if the **observed** mean separation satisfies

\[
\widehat\mu_{a^*}(n_j)-\widehat\mu_b(n_j)>2(r_j+\delta).
\]

For a nonrandom observed gap \(g>2\delta\), rearranging the finite-checkpoint inequality gives the **algebraic requirement**

\[
n_j>\frac{2\log(2KJ/\alpha)}{(g-2\delta)^2}.
\]

This is **not** a guaranteed sample-size formula because the observed gap is random. On the simultaneous source-coverage event, a conservative sufficient condition in terms of a *true* source gap \(g_P\) is \(g_P>4r_j+2\delta\). Both formulas reveal a structural limit: when \(g_P\le2\delta\), even infinite data generally cannot establish separation using this symmetric worst-case shift model.

**Theorem 3 (no separation if broad shift dominates, equal costs).** For \(K>1\), identical action costs and \(\delta\ge1/2\), **no** bounded empirical action means and **no** nonnegative statistical radius can yield strict target-interval separation. Indeed, \(L_{a,j}\le 1-\delta-c\le\delta-c\le U_{b,j}\) for every rival \(b\). Therefore the code may return `HOLD_IMPOSSIBLE` **before spending any evidence**. This short-circuit is not applied to unequal-cost libraries, where the proof does not hold.

## 6. What failure looks like

Suppose the source strongly favors action A, but the target almost entirely replaces source tasks with an adversarial task family favoring B. With a **falsely declared** small shift bound, both finite and sequential methods can certify A with narrow intervals while A is badly inferior on the target. No amount of source sampling fixes this. In Stage K, all 400 deliberately false-bound worlds produce incorrect best-action certificates. This falsifies any unconditional interpretation of “stable crystal.”

The correct conclusion is **conditional stability**: uncertainty bounds certify a decision only inside a documented evidence-and-shift contract.

## 7. How this relates to higher-order crystallization

The historical interaction estimand remains

\[
\Gamma_T(S)=\sum_{B\subseteq T}(-1)^{|T|-|B|}J(S\cup B),
\]

where \(J\) is independently evaluated expected procedure utility. If each of its \(2^{|T|}\) involved values has a valid radius \(e_B\), a sufficient deterministic interaction error bound is \(|\widehat\Gamma_T-\Gamma_T|\le\sum_{B\subseteq T}e_B\). Stage K **does not** estimate these interactions anew; that is a separate historical research line. Stable selection **does not imply** cluster emergence, causal synergy, learning-to-learn, or physical criticality.

## 8. Complexity and operational implications

At checkpoint \(n_j\), the controller needs \(K\) running sums and costs, plus \(O(K)\) work to compare intervals; checking all \(J\) checkpoints costs \(O(KJ)\) decision arithmetic. Collecting the evidence costs \(O(Kn_\tau)\) action-outcome evaluations; per-task task-vector outcomes may be correlated without invalidating the union bound. The synthetic generator holds all outcomes in memory for parity of policy comparison, while the reusable controller only needs running sums.

The stopping rule addresses **evidence consumption**, not network latency, wall-clock energy, accuracy of task generators, or real-agent delegation semantics. Those are separate measurable engineering constraints.

## 9. Release gates for a genuine application

A deployment-ready `CERTIFY` must have all of: frozen actions and baseline, independent task sampling or a validated alternative concentration model, bounded stable scoring, declared non-data-invented shift bound, fixed costs or their bounded uncertainty, predeclared checkpoints, non-reused alpha budget, verifiable outcome receipts, and a strict positive lower-versus-upper margin. Otherwise output `HOLD`; do not promote knowledge or override governance.

**Reference implementation:** [`sequential_certificate.py`](../src/agentic_crystallization/sequential_certificate.py). [Protocol](../experiments/stage_k_holdout/protocol.json) · [Raw runs](../experiments/stage_k_holdout/runs.csv).
