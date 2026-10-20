# Agentic Crystallization v2.4 — Formal Mathematics

**Status:** conditional finite-sample guarantees and falsifiable impossibility results; all observed outcomes are synthetic.

## 1. The problem and evidence channels

Let time be indexed by epoch $t\in\{0,\ldots,T-1\}$ with $T=24$, candidate actions $a\in\{A,B\}$, and a fallback $a_0$ with known synthetic gain zero. Let the true current-epoch gain relative to that fallback be $g_t(a)\in[-1,1]$. The algorithm does not observe $g_t(a)$ directly. For each channel $c\in\{P,A,R\}$ (primary, anchor, independently generated audit reference), it can **purchase** a sample mean

$$\widehat\mu_{t,a,c}=\frac{1}{n_c}\sum_{i=1}^{n_c} X_{t,a,c,i}, \quad X_{t,a,c,i}\in[-1,1].$$

*Honest channel assumption*: the observations within an action/epoch/channel are independent and their common expectation is $g_t(a)$. The reference is simulated with independent random draws conditional on the latent truth, but **independent randomization does not itself establish the validity of the measurement**. In corruption experiments the assumption is deliberately false. All inputs to the actual decision are sampled means, a cue, time and retained state; the true gain is reserved for scoring.

## 2. The finite-horizon simultaneous certificate

**Theorem 1 (honest reference, familywise coverage).** Prespecify $T$ epochs, $K$ candidate actions, $C$ candidate measurement channels, and confidence budget $\alpha\in(0,1)$. If each selected reference sample mean is composed of $n_R$ independent bounded observations in $[-1,1]$ whose expectation is the *current* $g_t(a)$, then setting

$$r_c=\sqrt{\frac{2}{n_c}\log\!\left(\frac{2TKC}{\alpha}\right)}$$

ensures simultaneous coverage of all **honest** channel means across this finite catalog and time horizon with probability at least $1-\alpha$. Conditional selection or stopping does not invalidate the result, because the union bound covers all prespecified candidate means.

**Proof.** Hoeffding's inequality for an average of independent variables in $[-1,1]$ implies $P(|\widehat\mu-\mu|>r)\le 2e^{-nr^2/2}$. Set the right-hand side to $\alpha/(TKC)$ and sum over the finite prespecified collection. If only the reference channel is honest, its part of the union bound alone still guarantees simultaneous reference coverage with probability at least $1-\alpha$ (indeed more conservatively). $\square$

Here $T=24$, $K=2$, $C=3$, $\alpha=.05$, $n_P=n_A=384$, $n_R=1024$. Each comparison with the fallback is with a baseline known to be exactly zero **inside the synthetic model**.

**Corollary 1 (honest-reference fresh certification).** Define reference-favored candidate $a^*=\arg\max_a\widehat\mu_{t,a,R}$. If

$$\boxed{\widehat\mu_{t,a^*,R}-r_R > \max\big(0,\max_{b\ne a^*}(\widehat\mu_{t,b,R}+r_R)\big)},$$

then on the simultaneous reference-coverage event $g_t(a^*)>0$ and $g_t(a^*)>g_t(b)$ for all competitors $b$. Requiring corroboration by primary and anchor channels may reject more candidates; it **cannot invalidate this conclusion** while the reference remains honest. A certificate is for the *current epoch only* and is not a warranty of future performance.

## 3. Three-way discrepancy rule

Two channel means are statistically incompatible if

$$D_{cR,t}=\mathbf 1\left\{\exists a:|\widehat\mu_{t,a,c}-\widehat\mu_{t,a,R}|>r_c+r_R\right\}.$$

If both channels are honest measurements of the same current gain, then $D_{cR,t}=0$ on the simultaneous coverage event. A positive alarm rejects their joint-honesty assumptions; it **does not identify which channel is untrustworthy**. When either channel disagrees, v2.4 chooses HOLD and records the event. Mere statistical compatibility does not imply either one's honesty.

An accepted fresh certificate additionally requires matching **separately certified best actions** across all three channels. This requirement lowers false promotions when the reference is honest but can cause false negatives and severe utility loss when one channel is compromised or absent. It is conservative corroboration, not majority voting.

## 4. Learned-looking trust scores are not safety guarantees

After $m$ observed comparisons and $f$ gross discrepancies, the code reports

$$\widetilde p_{\rm mismatch}=\frac{1+f}{2+m}.$$

This is the mean of a Beta$(1+f,1+m-f)$ distribution **only under a Bernoulli exchangeability model**. Here, audits are selected from time-varying regimes, so neither exchangeability nor independent reliability labels are assured. Accordingly this number is an **unverified descriptive diagnostic**, never the premise of a certification claim. The only mathematical certification depends on the externally stated honesty assumption and finite-sample concentration.

## 5. A cost-aware audit decision

Let $C_R$ denote the charged reference+primary+anchor audit cost and let $h$ be declared hazard, $\ell_t$ the last *observed* estimated gain, and $d_t$ the number of epochs since the last audit. The experimental adaptive trigger is

$$\boxed{\min(1,hd_t)\,N\max(0,\ell_t)>C_R,}$$

or expiration at maximum age, or an enabled warning cue. No true outcome or future shift label appears in this trigger. The units are synthetic utility points. This is a heuristic **not** a calibrated posterior predictive value-of-information theorem, since the hazard and future harm model are not proven.

v2.4 tuned $d_{\max}\in\{3,4,6,8\}$ and cue enablement on disjoint development worlds. The selected combination was **four epochs, no cue**. On the final holdout, its actions and outcomes coincided with simple four-epoch periodic three-way verification. **The extra scheduling complexity did not demonstrate value and should not be promoted as necessary.**

## 6. Indistinguishability: more agreeing sensors cannot prove truth

**Proposition 2 (common-mode observational equivalence).** Consider two worlds with exactly the same joint distribution over all observed channel outputs, warning cues and retained histories, but opposite true gains for the two candidate actions. No policy measurable with respect to the observed history can guarantee a non-baseline optimal choice in both worlds.

**Proof.** Under equal observation laws, any deterministic or randomized policy has the same conditional distribution over actions in both worlds. Since the optimal actions differ by construction, a non-baseline choice that succeeds in one must fail in the other. Randomization cannot eliminate this contradiction. Abstention can avoid falsely asserting which unobserved world is real, but provides no universal improvement guarantee. $\square$

An externally audited reference can separate the worlds **only if it adds a valid observation whose outcome law differs across them**. If every channel is compromised in the same way, adding their agreements changes nothing about identifiability.

## 7. Safety, costs, and temporal limits

All deployments after the audit epoch and before renewed evidence are flagged **stale**, even if recently certified. Fresh-certification validity does not extend across unknown shift, interference, nonstationarity, delayed feedback or adversarial adaptation. The fallback is known zero-gain *in this specific toy environment*. Audit cost and task reward are measured in the same synthetic units:

$$J(\pi)=\frac{1}{MT}\sum_{w,t}\big(Ng_{w,t}(a_{\pi,t})-C_{\pi,t}^{\rm audit}\big).$$

The controller also reports negative deployments, incorrect fresh certifications, refusal/HOLD counts, and alarms. A policy that rejects everything avoids incorrect fresh certifications but may be economically useless; therefore the utility and coverage metrics must always be shown alongside false-cert counts.

## 8. Claim ladder and falsification

1. **Exact mathematics:** conditional simultaneous finite-horizon Hoeffding certificates, discrepancy implications, and the indistinguishability proposition.
2. **Synthetic empirical observation:** three-way periodic verification catches shared corruption of the first two channels under an honest reference but is expensive and not universally superior.
3. **Negative result:** an added adaptive scheduling heuristic tied simple periodic verification in all 1,040 holdout worlds; it is **not** an established improvement.
4. **Open:** how to validate independent audit provenance, diagnose shared corruption without trusted interventions, and optimize verification economics under real-world tasks.
5. **Not demonstrated:** general self-sustaining improvement, novel physics, critical phase transition, Pegasus or Hermes performance gains.

[Whitepaper](WHITE_PAPER.md) · [Algorithm card](ALGORITHM_CARD_2.4.md) · [Held-out protocol](../experiments/stage_p_holdout/protocol.json) · [Complete source](../src/agentic_crystallization/adaptive_trust.py)
