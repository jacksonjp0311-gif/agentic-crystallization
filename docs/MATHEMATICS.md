# Agentic Crystallization 2.1 — Mathematics and Claim Boundaries

**Mathematical status:** Established concentration inequalities combined into a restricted, reproducible engineering protocol. This is not a new physical theory and does not prove spontaneous self-organization, a phase transition, or indefinite self-sufficiency.

[Whitepaper](WHITE_PAPER.md) · [Algorithm card](ALGORITHM_CARD.md) · [Frozen protocol](PREREGISTRATION_STAGE_M.json) · [Executable code](../src/agentic_crystallization/renewal_core.py) · [Historical mathematics v2.0](archive/MATHEMATICS_2.0.md)

## 1. Formal object

Let $\mathcal P$ be a finite, permission-bounded family of computational procedures, including baseline $a_0$. The crystal state is

$$
\mathcal C_e=(M_e,\,A_e,\,B_e,\,L_e),
$$

where $M_e$ is a bounded record of formerly useful procedures and their renewal/retirement statuses; $A_e$ is the current epoch's *conditional* deployment authority; $B_e\ge0$ is the synthetic computation-credit ledger, and $L_e$ is an append-only hash-linked record of observations and transitions. The environment supplies externally generated tasks, outcomes, and task rewards; the state cannot operate from data alone.

We separate four distinct concepts:

1. **Combinatorial structure:** a higher-order procedure can encode interacting primitives.
2. **Historical retention:** a previously useful procedure is available to propose again.
3. **Statistical certification:** a new, independently observed test justifies current-period expected benefit.
4. **Environmental regulation:** later task feedback may establish that the earlier relationship has degraded.

None logically entails the next without stated conditions. In particular, a stored procedure is **not** an active certificate.

### Research lineage

The v2.0 finite family contains the $92$ XOR expressions over one, two, or three of eight Boolean features. For a planted triple parity target, the higher-order Möbius coefficient of Bayes accuracy is $+\frac12$ (baseline accuracy $\frac12$, complete triple accuracy $1$), while all empty-baseline pairwise coefficients are zero. This is a constructed example of **nonadditive information utility**; its algebra is standard and it does not establish a natural critical crystallization threshold. Prior work also established the usefulness of cautious procedure reuse and the necessity of explicitly justified domain-shift bounds.

Version 2.1 investigates *feedback-mediated renewal*, not the discovery of a new high-order interaction identity.

## 2. Time and observable feedback contract

Each epoch $e$ has three sequential deployment blocks $b=0,1,2$. The simulator may change the law between blocks. For any fixed block $b$, let $P_{e,b}$ denote the law of a task $Z=(X,Y)$. The validation observations used for a certification of block $b$ are independent of the proposal-selection observations, and are independent and identically distributed from **the same $P_{e,b}$**. This within-block representativeness assumption is **explicit** and cannot be deduced merely from having a dataset.

For a selected procedure $a$, define paired outcome gain

$$
D_a(Z)=\mathbf1\{a(X)=Y\}-\mathbf1\{a_0(X)=Y\}\in[-1,1],
\qquad \mu_{e,b}(a)=\mathbb E_{P_{e,b}}D_a(Z).
$$

The selector freezes $a$ using only separate scout/discovery observations and previous receipts. Certification observes fresh independent validation; monitoring observes **middle-block outcomes after that block's actions have already been taken**. In real applications, paired baseline/candidate scores must actually be observable on the same tasks. A delayed, missing, biased, or falsified feedback stream invalidates some or all of the conclusions.

This chronology matters: the algorithm may detect a mid-epoch change after block $1$ and prevent continued reuse in block $2$, but cannot in general prevent damage already incurred during block $1$.

## 3. The new split lifetime budget

Fix total declared probability-of-error allowance $\alpha=0.05$. Allocate disjoint budgets

$$
\alpha^{\mathrm{prom}}=0.025,
\qquad \alpha^{\mathrm{monitor}}=0.025,
\qquad \alpha^{\mathrm{prom}}+\alpha^{\mathrm{monitor}}=\alpha.
$$

For each possible certification slot $(e,b)$, $b\in\{0,1,2\}$, assign index

$$
 t(e,b)=3(e-1)+b+1,
 \qquad \alpha^{\mathrm{prom}}_t=\frac{\alpha^{\mathrm{prom}}}{t(t+1)}.
$$

The sequence telescopes: $\sum_{t=1}^{\infty}[t(t+1)]^{-1}=1$. Thus certification slots not used by a policy merely leave some of the allowance unspent; adaptive stopping does not create additional unbudgeted tests.

For each certification attempt, predeclare exactly four observation checkpoints $N=(64,128,256,512)$, set $J=4$, and compute

$$
\widehat\mu_{t,j}=\frac1{n_j}\sum_{i=1}^{n_j}D_a(Z_i),
\qquad r_{t,j}=\sqrt{\frac{2\log(J/\alpha^{\mathrm{prom}}_t)}{n_j}}.
$$

The candidate is certified for the **observed current block only** when

$$
\boxed{\widehat\mu_{t,j}-r_{t,j}>\tau},\qquad\tau=0.025.
$$

When the inequality is not met by $n=512$, use baseline HOLD. Exactly one preselected proposal is validated per slot; alternate candidates cannot be selected after peeking at validation outcomes in that slot. The permitted search algorithm can be arbitrary and adaptive on separate discovery data without adding a multiple-candidate factor to the **single frozen candidate's** certificate.

### Theorem 1 — Lifetime promotion soundness (conditional)

Condition on the past and on proposal-selection data. Suppose each certified slot's fresh validation differences are independent, identically distributed from its block's target distribution, bounded in $[-1,1]$, and not used to select the candidate. Then for one perpetual controller run,

$$
\boxed{\Pr\!\left(\exists(e,b)\text{ certified despite }\mu_{e,b}(a)\le\tau\right)\le\alpha^{\mathrm{prom}}.}
$$

**Proof.** Hoeffding's one-sided inequality yields

$$
\Pr(\widehat\mu_{t,j}-\mu_{e,b}(a)>r_{t,j}\mid\mathrm{history})
\le \exp(-n_jr_{t,j}^2/2)=\alpha^{\mathrm{prom}}_t/J.
$$

Union across the $J$ checkpoints is at most $\alpha^{\mathrm{prom}}_t$. Outside this exceptional event, certification entails $\mu_{e,b}(a)\ge\widehat\mu_{t,j}-r_{t,j}>\tau$. Union across every possible slot gives $\sum_t\alpha^{\mathrm{prom}}_t\le\alpha^{\mathrm{prom}}$. $\square$

**Critical scope:** This does **not** guarantee performance in blocks $b+1$, next week, a new deployment population, or under nonrepresentative validation. The monitor is a separate, delayed test, not a missing magical premise that makes the certificate timeless.

## 4. Two-sample degradation detection

Suppose $a$ was chosen independently of the current epoch's validation. Take an independently sampled reference batch $V$ of $n_r=512$ outcomes from $P_{e,0}$. The selected action executes on the middle block $b=1$ and subsequently receives $n_c=768$ appropriately labeled feedback outcomes from $P_{e,1}$.

Define

$$
\Delta_e(a)=\mu_{e,1}(a)-\mu_{e,0}(a),
\qquad \widehat\Delta_e(a)=\overline D_{c}-\overline D_r.
$$

Assign a unique monitor index $s(e)=3(e-1)+2$ and spend

$$
\beta_s=\frac{\alpha^{\mathrm{monitor}}}{s(s+1)},\qquad
u_r=\sqrt{\frac{2\log(2/\beta_s)}{n_r}},\qquad
\nu_c=\sqrt{\frac{2\log(2/\beta_s)}{n_c}}.
$$

Each one-sided Hoeffding statement is allocated $\beta_s/2$. A union bound gives an upper bound on the **change** in mean paired gain:

$$
\boxed{U_e^{\mathrm{drop}}=\overline D_c-\overline D_r+\nu_r+\nu_c.}
$$

For a predetermined tolerated deterioration $d\ge0$, raise an alarm only when

$$
\boxed{U_e^{\mathrm{drop}}<-d.}
$$

The Stage M setting is $d=0$; it tests for any substantial detectable deterioration, not only for provable net harm. A retained procedure with $U_e^{\mathrm{drop}}<0$ may still beat baseline; the alarm says its estimated benefit has **declined**, not that it necessarily became harmful.

### Theorem 2 — Lifetime false-deterioration control (conditional)

Under independent reference/monitoring batches from their respective well-defined distributions, honest paired labels, and fixed selection of the monitored procedure before both batches, for any history-adaptive series of monitor checks with the preallocated indices,

$$
\boxed{\Pr\bigl(\exists e:\mathrm{ALARM}_e\text{ while }\Delta_e(a)\ge-d\bigr)
\le\alpha^{\mathrm{monitor}}.}
$$

**Proof.** With probability at least $1-\beta_s$, both one-sided deviations are simultaneously within $\nu_r$ and $\nu_c$. On this event $\Delta_e(a)\le U_e^{\mathrm{drop}}$; therefore $U_e^{\mathrm{drop}}<-d$ implies $\Delta_e(a)<-d$. Union over the assigned slots gives $\sum_s\beta_s\le\alpha^{\mathrm{monitor}}$. $\square$

The monitored procedure was frozen using scout/discovery data independent of both monitoring batches. Reference data may also be used to certify the **already chosen** procedure, but this does not authorize trying several candidates on the reference and then choosing whichever test yields a desired alarm. For clarity, Stage M checks at most one procedure per epoch.

**False-negative caveat:** Failing to reject deterioration does not show that $\Delta_e\ge-d$. A `CLEAR` result means *not detected*, not *no drift*. Sample size and conservative risk spending can cause missed gradual changes.

## 5. Retirement and the distinction between memory and authority

The state transition policy is deterministic, finite and receipt-backed:

| Condition | State/action | Interpretation |
|---|---|---|
| Current-period independent lower bound exceeds $\tau$ | Admit / `RETAINED` | Eligible for proposals, not future deployment authority |
| New epoch starts | `NEEDS_RENEWAL` | Old certificate cannot authorize current execution |
| After middle-block feedback, $U_e^{\mathrm{drop}}<0$ | `NEEDS_RENEWAL`; fresh block-2 search allowed | Evidence of retrospective deterioration; remove continuation authority |
| Feedback unavailable | HOLD for late block | No inference from silence |
| Repeated deterioration alarms (threshold two) or prolonged staleness | `RETIRED` | Exclude from memory-based nominations; preserve historic receipts |
| A retired structure is independently rediscovered and newly certified | Re-admit | Permitted recovery, never unreviewed resurrection |

The finite list of allowed procedures, four-slot bounded memory, versioned record statuses, and explicit negative-control policies keep the semantics auditable. The controller can still make poor choices before delayed feedback arrives; its operational state transitions are not proofs of external safety or future optimality.

### Unbounded cumulative uncertainty is not erased by fresh renewal

Even with $\Pr(\text{false promotion ever})\le\alpha^{\mathrm{prom}}$ under the source conditions, it is possible for an environment to change abruptly **after** validation. Fresh evidence before a block guards only the target law it actually represents. A block executed under a different law is *uncertified exposure* and must be measured as such, not falsely added to the denominator of “correct certificates.”

## 6. No universal drift predictor: an identifiability result

Consider environments $E_0$ and $E_1$ with *identical* probability laws for all evidence available to the learner through a decision time $t$. In $E_0$ the earlier procedure remains optimal after $t$; in $E_1$ its future paired gain becomes negative. Any policy whose decision is a (possibly randomized) function of the observed history has the **same decision distribution in both environments** at time $t$, because the observed histories are indistinguishable. It cannot almost surely make opposing correct future decisions in both environments without receiving distinguishing future information.

The Stage M misleading-feedback counterexample constructs this limitation directly: actual middle-block labels invert but the reported monitoring labels are synthesized from the old, unchanged rule. The controller sees no statistical evidence of the true deterioration, so the alarm rule cannot be expected to work. This is an information limit, not a parameter-tuning failure.

The corresponding `missing_feedback` regime permits only a conservative HOLD for the late block. Withholding evidence prevents false certainty but also sacrifices useful action; this tradeoff is measured.

## 7. Resources, accounting, and restart

Let $q_e$ be charged independent scout/discovery/validation samples, $k_e$ prediction operations, $m_e$ maintained entries, and $f_e$ processed labeled feedback count. The synthetic cost is

$$
C_e=c_s q_e+c_p k_e+c_m m_e+c_f f_e,
$$

with all coefficients nonnegative and predeclared. A pessimistic evaluation-cost reserve is checked **before** attempting the epoch, against current synthetic credits $B_e$. If unaffordable, it does no certification or monitoring work and deploys the baseline. After deployment, it records externally provided task revenue $R_e\ge0$:

$$
\boxed{B_{e+1}=B_e-C_e+R_e,\qquad 0\le C_e\le B_e.}
$$

Thus $B_e\ge0$ for each committed transaction by induction. This says nothing about perpetual viability if external tasks, feedback, or power disappear. The hash-linked ledger reconstructs control state after restart. It detects accidental corruption but does not authenticate the entire log against an adversary capable of rewriting and recomputing every checksum.

## 8. What the mathematics does *not* establish

- **Not thermodynamics:** These costs are synthetic computing/task scores, not measured free energy or entropy production.
- **Not H2 criticality:** No scale sweep, hysteresis test, divergent susceptibility, or finite-size collapse is demonstrated.
- **Not H3 general learning-to-learn:** All procedures and data-generating relations are predeclared. Memory rediscovery savings are not autonomous invention of a new representation language.
- **Not always optimal:** A periodic independent validator can dominate the reactive monitor under rapid change because its fresh probes come **before** the affected block.
- **Not resilient to false labels:** The monitor test assumes trustworthy, representative outcomes. An adversarial channel can invalidate it without the algorithm being able to infer this from source history alone.
- **Not empirically guaranteed lifetime operation:** The simulations are finite, use seeded synthetic RNG, and provide credits from external tasks.

The scientific gain of v2.1 is an implementable and falsifiable set of **conditional inference and state-transition contracts**. Useful real-world generalization remains an open hypothesis.

## 9. Reproduction

From the repository root:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m agentic_crystallization.stage_m --out experiments/local_new --start-seed 91000 --count 2
python scripts/verify_stage_m.py experiments/stage_m_holdout --repo .
```

The maintained history is archived in `docs/archive/`, and historical source files remain included in the package. Use the v2.0 whitepaper in `docs/archive/WHITE_PAPER_2.0.md` for the preceding lifetime-certification formulation.
