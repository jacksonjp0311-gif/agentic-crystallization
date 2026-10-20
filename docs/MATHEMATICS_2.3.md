# Agentic Crystallization 2.3 — Feedback Integrity Mathematics

**Scope:** A synthetic, finite-horizon, two-procedure decision system. All probability guarantees are **conditional** on stated sampling assumptions. No new physical force, phase transition, or real Pegasus performance claim is made.

## 1. Observables, latent outcomes, and trust

At epoch \(t\), the true deployment gain of action \(a\in\{A,B\}\) relative to the zero-gain baseline is \(g_t(a)\in[-1,1]\). The policy **cannot observe** \(g_t\). It receives a warning cue \(Z_t\), a primary audit sample \(X^{P}_{t,a,i}\), and optionally a separately generated anchor sample \(X^{A}_{t,a,i}\). In honest conditions,

\[
\mathbb E[X^{P}_{t,a,i}\mid t,a]=\mathbb E[X^{A}_{t,a,i}\mid t,a]=g_t(a),\qquad X\in\{-1,+1\}.
\]

The anchor is an *independently simulated measurement channel*, not a guaranteed source of ground truth. The policy cannot deduce its honesty from agreement alone. Both channels can share systematic bias.

## 2. Simultaneous concentration theorem

Let \(T\) be the prespecified number of epochs, \(K\) the number of candidate actions, \(C\) the number of channels, and \(M=T K C\). Suppose every inspected channel/action/epoch sample mean consists of \(n_c\) independent bounded observations in \([-1,1]\) with the declared current-epoch expectation. Hoeffding gives

\[
\Pr\big(|\widehat\mu_{t,a,c}-\mu_{t,a,c}|>r_c\big)\le 2\exp(-n_c r_c^2/2).
\]

By a union bound, choosing

\[
\boxed{r_c=\sqrt{\frac{2\log(2M/\alpha)}{n_c}}}
\]

ensures simultaneous coverage for all prespecified sample means with probability at least \(1-\alpha\). Here \(T=24\), \(K=2\), \(C=2\), \(M=96\), \(\alpha=.05\), and \(n_P=n_A=384\), giving \(r\approx0.20733\).

This bound is finite-horizon, **per independently generated world**, and only concerns the means of *honest* channels. It does not validate the channel's relationship to true deployment reward, nor future epochs. A corrupted channel violates the theorem's premises.

## 3. A channel-disagreement alarm

Under the null hypothesis that both channels are honest and estimate the same \(g_t(a)\), simultaneous coverage implies

\[
|\widehat\mu^P_{t,a}-\widehat\mu^A_{t,a}|\le r_P+r_A.
\]

Therefore an alarm

\[
\boxed{D_t=\mathbf1\{\exists a:\ |\widehat\mu^P_{t,a}-\widehat\mu^A_{t,a}|>r_P+r_A\}}
\]

has familywise false-alarm probability at most \(\alpha\) over the prespecified finite horizon if *both* channels are honest, independent within each sample, and share the same current-epoch expectation. Independence **between** the channels is not required for this union-bound statement, although it is relevant to their interpretation as separate evidence sources.

An alarm means *incompatibility with the joint honesty model*. It does **not** identify which channel is wrong. The conservative action is HOLD.

## 4. A fresh best-action certificate

Let \(a^*=\arg\max_a\widehat\mu^A_{t,a}\) be the candidate favored by the anchor and \(b\ne a^*\) the other candidate. Under an honest anchor, the condition

\[
\boxed{\widehat\mu^A_{t,a^*}-r_A>\max(0,\widehat\mu^A_{t,b}+r_A)}
\]

certifies that \(a^*\) is strictly better than both the baseline and the other action **for that epoch**, on the simultaneous coverage event. The integrity guard additionally requires primary-anchor agreement before issuing a fresh certificate.

Old certificates may be reused as a *stale* policy decision within a maximum age, but that reuse has no current-epoch statistical guarantee. All stale deployments are counted separately.

## 5. Calibration of warning likelihoods

The cue \(Z\) is intended to indicate whether a change occurred. Independent balanced, labeled training observations estimate sensitivity \(s=P(Z=1\mid H=1)\) and specificity \(q=P(Z=0\mid H=0)\). With \(n_h\) independent Bernoulli samples per class, a two-rate simultaneous interval is

\[
\widehat p_h\pm\sqrt{\frac{\log(4/\alpha)}{2n_h}},\quad h\in\{0,1\},
\]

clipped to \([0,1]\). This is a standard Hoeffding interval; it is not a shift-robust guarantee. v2.3 uses 3,000 training samples per class and freezes the resulting point estimates for the synthetic policy. The change hazard remains a declared prior, **not** a learned quantity.

The calibration data and held-out worlds use disjoint seeds. The misleading-warning regime deliberately changes cue quality after training, so its calibration guarantee no longer applies.

## 6. Impossibility of identifying common-mode deception

**Proposition (observational equivalence).** Consider two environments with identical distributions over the entire observed history \(H=(Z,X^P,X^A)\) but opposite true deployment gains. No algorithm whose decisions are functions only of \(H\) can guarantee the correct non-baseline action in both environments.

**Proof.** The algorithm's conditional action distribution given \(H\) is identical in both environments, because the law of \(H\) is identical. The optimal non-baseline action differs by construction. Hence any action that is correct in one environment is incorrect in the other, unless the algorithm always abstains. \(\square\)

The common-mode experiment realizes this by flipping both observed channels together after a hidden environmental change. Cross-channel agreement does not detect the deception. Additional samples from the same jointly biased channels cannot resolve the ambiguity. A separately justified trustworthy measurement or new intervention is required.

## 7. Cost and risk

For policy \(\pi\), synthetic per-epoch utility is

\[
U_t(\pi)=80\,g_t(a_t)-0.002\,N_{P,t}-0.006\,N_{A,t},
\]

where \(N_{P,t}\) and \(N_{A,t}\) are the actual primary/anchor observations purchased, including both actions. An unavailable anchor incurs no sample cost but causes HOLD when required. The safe baseline has zero gain and no audit cost.

The guard is not an optimal solution to this objective. It sacrifices utility by checking two channels and by abstaining when they disagree. A simpler periodic policy may outperform it when the channel it trusts is genuinely honest. The experiment measures this tradeoff instead of claiming universal dominance.

## 8. Claim boundaries

- H1 (nonadditive procedure utility): supported only in earlier planted synthetic tasks.
- H2 (critical adaptive phase transition): unestablished.
- H3 (general learning-to-learn): unestablished.
- v2.3: two-channel discrepancy can detect certain single-channel failures; common-mode deception remains unidentifiable from the two channels alone.
- No real Pegasus, local model, or live deployment was evaluated.

[Whitepaper](WHITE_PAPER.md) · [Algorithm card](ALGORITHM_CARD_2.3.md) · [Source](../src/agentic_crystallization/feedback_integrity.py) · [Holdout](../experiments/stage_o_holdout/summary.json)
