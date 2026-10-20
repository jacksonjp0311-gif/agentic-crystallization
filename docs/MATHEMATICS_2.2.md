# Agentic Crystallization v2.2 — Mathematics

[Whitepaper](WHITE_PAPER.md) · [Algorithm card](ALGORITHM_CARD_2.2.md) · [Source](../src/agentic_crystallization/risk_verification.py)

## Simultaneous finite-horizon certification

For $n$ independent observations of each bounded paired gain $D\in[-1,1]$, Hoeffding gives

$$P(|\hat\mu-\mu|\ge r)\le 2e^{-nr^2/2}.$$

Across $K=2$ actions and $T=24$ prespecified epochs, a union bound gives $2KT e^{-nr^2/2}\le\alpha$ for $r=\sqrt{2\log(2KT/\alpha)/n}$. Under honest representative audit sampling, any action with $\hat\mu-r>0$ has positive current-epoch expected gain except on a joint event of probability at most $\alpha$.

This does not certify stale actions, future shifts, or systematically false observations. The proof holds even if audit times are selected using **prior information**, provided each fresh audit batch is conditionally independent and representative, and all possible epochs/actions are included in the union bound.

## Warning posterior

Let $H_t$ indicate a change between epochs $t-1$ and $t$. The assumed prior is $P(H_t)=h$. With warning sensitivity $s$ and specificity $q$:

$$P(H_t=1\mid Z_t=1)=\frac{hs}{hs+(1-h)(1-q)}.$$

$$P(H_t=1\mid Z_t=0)=\frac{h(1-s)}{h(1-s)+(1-h)q}.$$

This is a posterior **only under the declared cue model**. The synthetic regimes deliberately violate that model in several controls. The maximum certificate age is a separate heuristic safeguard; the one-step warning posterior is not a calibrated probability of cumulative change since the last audit.

## Verification economics

Let $m$ be deployment size, $\ell$ an assumed loss per task if a change is missed, $n$ samples per candidate, $K$ candidates, and $c$ cost per sample. A heuristic audit condition is

$$P(H_t=1\mid Z_t)\,m\ell > Knc.$$

The left side is **not** the exact value of information: it ignores false negatives of the audit, alternative actions, missed positive benefit and other costs. Consequently the heuristic has no general regret or optimality guarantee.

## Impossibility counterexample

Two deployment worlds can produce the same historical data and warnings through time $t$, but one switches the candidate's gain to $+g$ and the other to $-g$ at $t+1$. A controller seeing identical information must choose the same action in both. No algorithm can guarantee profitable deployment in both worlds without new assumptions or informative observations. This is a simple indistinguishability argument, not a novel physical law.
