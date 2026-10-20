# Agentic Crystallization v2.0 — Mathematical specification

[README](../README.md) · [Whitepaper](WHITE_PAPER.md) · [Algorithm card](ALGORITHM_CARD.md) · [Experimental protocol](PREREGISTRATION_STAGE_L.json) · [Python controller](../src/agentic_crystallization/crystal_core.py) · [v1.9 mathematics](archive/MATHEMATICS_1.9.md)

## 1. Claim boundary and the dynamical object

We define an **operational computational crystal** as a finite-state, externally fueled, closed-loop procedure-learning controller. **Externally fueled** means tasks supply observations and rewards, while a machine supplies computation and power; the word *crystal* is an organizational analogy, not a physical phase transition. Its components are

$$
\mathcal C=(\mathcal P,\mathcal G,M_t,\mathsf E,\mathsf Cert,\mathsf T,B_t,L_t),
$$

where $\mathcal P$ is a *whitelisted primitive procedure family*, $\mathcal G$ constructs bounded candidates, $M_t$ is limited durable procedural memory, $\mathsf E$ is an independent evidence stream, $\mathsf Cert$ is a conditional sequential hypothesis-test certificate, $\mathsf T$ governs admission/retirement, $B_t$ is available evaluation credit, and $L_t$ is a hash-linked audit ledger.

**Operational closure** here means the controller can repeat propose → evaluate → certify/HOLD → retain/prune → restart without a new human instruction *in the sandbox*. It does **not** mean unbounded autonomous intelligence, self-modifying source code, zero external power, or indefinite survival for any task process.

### Nontrivial interaction testbed

There are $d=8$ independently uniform binary feature variables. A latent task has target $Y=X_i\oplus X_j\oplus X_k$, with three distinct indices. The permitted candidate family is all XORs of one, two, or three feature variables; $|\mathcal P\setminus\{\pi_0\}|=8+28+56=92$. The baseline $\pi_0(x)=0$.

If the learner is restricted to only subset $S$ of these true three features, the Bayes-optimal prediction accuracy is

$$
U(S)=\begin{cases}1,&\{i,j,k\}\subseteq S,\\\tfrac12,&\text{otherwise}.\end{cases}
$$

Thus the pure three-way Möbius interaction equals $U(\{i,j,k\})-U(\{i,j\})-U(\{i,k\})-U(\{j,k\})+U(\{i\})+U(\{j\})+U(\{k\})-U(\varnothing)=\tfrac12$. Every empty-baseline pairwise interaction is zero. These are mathematical properties of a **planted** parity target, not measurements of Pegasus or nature.

A negative-control four-way XOR target has no permitted accurate three-feature solution. Under the uniform generator, every admitted candidate has true gain zero relative to the constant-zero baseline.

## 2. Candidate-generation and evidence isolation

At epoch $e$, the controller selects candidate $\pi_e$ using an exploratory scouting sample and, if needed, a discovery sample. This choice can depend on every prior receipt and the current exploration data. It **cannot** access the independent validation sample $Z_{e,1},\ldots,Z_{e,N}$ until selection is frozen. A third, independent deployment split is used for measurement only **after** the decision is frozen.

A remembered candidate must pass an inexpensive contextual scout test, then the **same fresh certificate as a newly generated candidate**. A historical certificate has no authority in a new epoch. If no remembered candidate passes the scout gate, the generator evaluates the 92 permitted XOR combinations against a discovery batch and freezes the highest empirical performer. Source labels are observable task feedback; the hidden target specification is never supplied to this selection function.

The scout gates and proposal-search policy are heuristics. Their mathematical optimality is **not** claimed. Independence of proposal and validation means that multiplicity in exploratory candidate search does not require another factor of 92 in the certificate for the **single preselected candidate**; choosing a different candidate after seeing validation evidence would invalidate this reasoning and is prohibited.

## 3. The lifetime false-promotion theorem

For a fixed, frozen candidate $\pi_e$, define the paired gain on a bounded task observation $Z$ as

$$
D_e(Z)=\mathbf 1\{\pi_e(X)=Y\}-\mathbf 1\{\pi_0(X)=Y\}\in[-1,1].
$$

Let $\mu_{P,e}=\mathbb E_{P_e}D_e$ denote gain on the **validation law** within epoch $e$, and $\mu_{Q,e}=\mathbb E_{Q_e}D_e$ denote gain on the epoch's **deployment law**. A trusted external protocol must justify an allowance

$$
\boxed{|\mu_{P,e}-\mu_{Q,e}|\le \Delta_e.}
$$

Crucial: $\Delta_e$ is a *direct bound on the shift in expected gain*. It is **not** an arbitrary context distance. If all one knows is a total-variation bound $d_{TV}(P_e,Q_e)\le \delta_e$, the generic safe choice is $\Delta_e=2\delta_e$, because the gain spans an interval of length 2. The supplied parity-mixing generator permits a smaller directly proved allowance. Missing $\Delta_e$ forces `HOLD`.

Take an arbitrary (possibly infinite) sequence of episodes $e=1,2,\ldots$, each having a predeclared sequence of $J$ validation checkpoints $1\le n_1<\cdots<n_J$. Fix $\alpha\in(0,1)$, and allocate

$$
\alpha_e=\frac{\alpha}{e(e+1)},\quad
\sum_{e=1}^{\infty}\alpha_e=\alpha.
$$

At the $j$-th checkpoint, let $\widehat\mu_{e,j}=n_j^{-1}\sum_{i\le n_j}D_e(Z_{e,i})$ and

$$
\boxed{r_{e,j}=\sqrt{\frac{2\log(J/\alpha_e)}{n_j}}}\,,\qquad
\boxed{L_{e,j}=\widehat\mu_{e,j}-r_{e,j}-\Delta_e.}
$$

The controller certifies **gain over the named baseline**, not global optimality, only if $L_{e,j}>\varepsilon$, where $\varepsilon=0.025$ in Stage L. It checks only the predeclared checkpoints; after the last unsuccessful checkpoint it returns HOLD and deploys the baseline. The selected action is not changed based on validation outcomes during that episode.

**Theorem (conditional lifetime soundness).** Suppose for *each* epoch $e$, conditional on the past and on exploratory data used to select $\pi_e$:

1. Validation differences $D_e(Z_{e,1}),D_e(Z_{e,2}),\ldots$ are independent, identically distributed and bounded in $[-1,1]$ with fixed conditional mean $\mu_{P,e}$.
2. The declared shift bound $|\mu_{P,e}-\mu_{Q,e}|\le\Delta_e$ holds for that chosen procedure and its deployment distribution.
3. The validation split is not reused to choose the candidate, tune the gate, adjust the error budget, or fit outcome-dependent checkpoints.
4. Only one frozen candidate is certified per episode, and the episode number is never reset within one lifecycle.

Then

$$
\boxed{\Pr\left(\exists e\ge1:\texttt{CERTIFIED}_e\ \land\ \mu_{Q,e}\le\varepsilon\right)\le\alpha.}
$$

**Proof.** Hoeffding's one-sided bound for bounded differences with range length two gives $\Pr(\widehat\mu_{e,j}-\mu_{P,e}>r_{e,j}\mid\mathcal F_{e,0})\le\exp(-n_jr_{e,j}^2/2)=\alpha_e/J$. The union bound across the $J$ checkpoints is at most $\alpha_e$ conditional on the entire history and exploratory selection. When this event does not occur, $\mu_{Q,e}\ge \mu_{P,e}-\Delta_e\ge \widehat\mu_{e,j}-r_{e,j}-\Delta_e=L_{e,j}$ at all checkpoints. Therefore any certification in this episode implies $\mu_{Q,e}>\varepsilon$. A second union bound across epochs gives $\sum_e\alpha_e\le\alpha$. Neither independence across episodes nor independence across candidate scores on a shared discovery task is necessary. $\square$

This is a straightforward application of established Hoeffding concentration plus a telescoping union bound, not a claim of a newly discovered theorem of physics or statistical inference. An empirical zero-error count **cannot** prove the theorem's assumptions.

### Caveat: the certificate is not a free-energy inequality

Certification means a procedure's **expected task-prediction gain** exceeds $\varepsilon$ under the declared target domain. It does not itself prove positive net utility after exploration, validation, deployment costs, or changing execution prices. Resource economics and cross-epoch persistence are separate conditions.

## 4. The resource invariant and finite memory

The controller records nonnegative external task revenue $R_e$ and nonnegative evaluation, proposal-computation and retained-memory cost $C_e$. It spends only with a conservative bound on possible evaluation cost and otherwise deploys the baseline:

$$
B_{e+1}=B_e-C_e+R_e,\qquad 0\le C_e\le B_e,\quad R_e\ge0.
$$

**Invariant.** From $B_0\ge0$, induction yields $B_e\ge0$ for every completed epoch **if the recorded costs/revenues are nonnegative and the transaction guard is enforced**. This is a no-overdraft property; it does **not** establish perpetual positive return, nor that the agent can power itself without external work.

Memory admission occurs only after certification. Each stored entry is `(procedure, last_certified_epoch, count)`. Before the next transition, expired entries are pruned when $e-\text{last\_certified}>\tau$; if capacity $k$ is exceeded, the least recently certified entry is evicted. Consequently

$$
\boxed{|M_e|\le k}\quad\text{for every completed transition.}
$$

**Knowledge is not authority.** Stored procedures are only *shortlisted proposals*. Every episode requires fresh validation. There is no persistent globally valid certificate under arbitrary environmental drift.

### Structural stability versus adaptation

Structural retention is **bounded in size**, **auditable in time**, and **conditional on renewed evidence**. An active set may change as the environment changes. This is better characterized as **metastable adaptive organization**, not a stationary crystal lattice. The system's state dynamics depend on both external task data and governed policy; they are not spontaneous organization of uninterpreted data.

## 5. Procedure and ledger invariants

- **Whitelisted expressions:** only `baseline:0` or canonical XOR expressions over 1–3 distinct, ordered, in-range feature indices.
- **No unauthorized promotion:** CERTIFIED requires a nonempty approved candidate, a nonmissing allowance, an actual positive gain certificate, and a matching active procedure.
- **No stale certificate:** historic entries cannot be activated without certification in the new epoch.
- **Finite memory:** $|M_e|\le k$.
- **Bounded resource expenditure:** actual charged cost cannot exceed available credits.
- **Monotone epochs:** commit at exactly $e+1$, with each receipt hash referencing its predecessor and a state hash verified through deterministic replay.
- **Failure closure:** unknown shift, insufficient budget, and unseparated confidence bounds force baseline HOLD.

The JSONL receipt chain detects accidental modifications, truncation, and out-of-order records **when the verifier trusts its initial ledger and code**. It is **not** an authenticated tamper-proof signature; someone who can rewrite the entire log can generate a fresh chain. Single-writer operation only; concurrent appends require external locking or a transactional database.

## 6. Why the adversarial control is mandatory

Construct a source distribution with $Y=X_i\oplus X_j\oplus X_k$ and a deployment distribution with **inverted** labels $Y'=1-Y$. The procedure with source gain $+1/2$ has deployment gain $-1/2$. Thus a declared allowance $\Delta=0$ is false: the true gain shift is one full unit.

The sequential certificate can then **confidently promote a harmful procedure**. Increasing the sample count narrows sampling uncertainty but cannot repair a false environmental assumption. This is not an implementation failure of Hoeffding's inequality. It directly falsifies any proposed unconditional "always stable" property.

A fully autonomous system would need a separate, empirically justified change-detection or shift-calibration mechanism. Stage L deliberately does **not** pretend to derive $\Delta$ from insufficient data.

## 7. What remains unproved

- Long-run positive drift in resource balance in an adversarial or unconstrained environment.
- Any autonomous discovery beyond the finite 92-combination whitelisted XOR family.
- General structural causal graphs learned from interventions, or graph phase transitions.
- Performance on real language-model agents, real Pegasus tasks, or real-world tools.
- A universally superior procedure-selection policy or optimal search.
- Any literal informational crystal, consciousness, thermodynamic analogy or universal self-organization law.

The operational integration is the new **engineering result**. The mathematical certificates are conditional applications of established probability and invariant reasoning.

## 8. Impossibility of assumption-free deployment certification

**Proposition (observational indistinguishability).** Fix any learning procedure that observes only exploratory and validation data from a source law $P$, plus metadata that does not distinguish two deployment laws. Consider two possible worlds with exactly the **same source observations**: $Q_+=P$ and $Q_-$ obtained by flipping every binary target label in deployment. For a source-perfect nonconstant XOR procedure with a constant-zero baseline, the expected deployment gain is $+\tfrac12$ in $Q_+$ and $-\tfrac12$ in $Q_-$. No decision function of the source data alone can distinguish the worlds.

**Consequence.** Any procedure whose false-certification probability in $Q_-$ must be at most $\alpha$ can certify that candidate in $Q_+$ with probability at most $\alpha$, too, because its observed input distribution is identical in both worlds. Thus **without some restriction on deployment shift or new deployment observations, uniformly reliable nontrivial certification is impossible**.

**Proof.** Let $A$ be the event that the learner issues the relevant positive-gain certificate based on the observed source data. The distribution of its entire information set (including any internal random seed independent of the world) is identical under $Q_+$ and $Q_-$. Hence $\Pr_{Q_+}(A)=\Pr_{Q_-}(A)$. In $Q_-$, event $A$ is an incorrect positive-gain certification. Bounding it by $\alpha$ necessarily bounds the same event in $Q_+$. $\square$

This is an elementary identifiability/no-free-lunch argument, **not a newly discovered general impossibility theorem**. It explains why the external environment contract cannot simply be deleted from the mathematical design. A real self-regulating system must acquire trustworthy **fresh target-domain feedback** or justify a calibrated invariance assumption.
