"""v2.3: independent feedback anchors, simultaneous finite-horizon bounds, and HOLD.

Synthetic research only. Independence and anchor honesty are assumptions, not
properties this code can establish from the observed streams themselves.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from math import log, sqrt, isfinite
from .risk_verification import Config, State, should_audit, certify as primary_certify

ACTIONS = ('A', 'B')
POLICIES = ('guard', 'dual_periodic', 'anchor_periodic', 'anchor_risk',
            'anchor_always', 'primary_risk', 'primary_periodic', 'baseline')

@dataclass(frozen=True)
class IntegrityConfig:
    epochs: int = 24
    primary_samples: int = 384
    anchor_samples: int = 384
    alpha: float = .05
    primary_unit_cost: float = .002
    anchor_unit_cost: float = .006
    tasks_per_epoch: int = 80
    max_anchor_age: int = 4
    hazard: float = .06
    sensitivity: float = .85
    specificity: float = .90
    def __post_init__(self):
        if self.epochs < 1 or self.primary_samples < 1 or self.anchor_samples < 1:
            raise ValueError('invalid sample/epoch count')
        if not 0 < self.alpha < 1 or self.max_anchor_age < 1:
            raise ValueError('invalid confidence or age')
        if min(self.primary_unit_cost,self.anchor_unit_cost) < 0 or self.tasks_per_epoch < 1:
            raise ValueError('invalid costs')
        if not all(0 < x < 1 for x in (self.hazard,self.sensitivity,self.specificity)):
            raise ValueError('invalid cue probabilities')

@dataclass
class IntegrityState:
    selected: str | None = None
    last_primary: int = -1
    last_anchor: int = -1
    suspect: bool = False
    require_anchor: bool = False


def radius(n: int, cfg: IntegrityConfig) -> float:
    """Simultaneous two-sided Hoeffding for 2 channels x 2 actions x epochs.

    Each observation is in [-1,1]. Union bound covers all prespecified
    channel/action/epoch sample means, even if not all are inspected.
    """
    m = 2 * len(ACTIONS) * cfg.epochs
    return sqrt(2 * log(2 * m / cfg.alpha) / n)


def validate_means(means: dict[str,float] | None) -> None:
    if means is None: return
    if not isinstance(means,dict) or set(means) != set(ACTIONS):
        raise ValueError('expected exact action means')
    if any(not isinstance(x,(float,int)) or not isfinite(x) or not -1 <= x <= 1 for x in means.values()):
        raise ValueError('invalid sample means')


def certified_best(means: dict[str,float], n: int, cfg: IntegrityConfig) -> str | None:
    """Best and better than baseline (zero) under simultaneous bounds."""
    validate_means(means)
    r=radius(n,cfg)
    winner=max(ACTIONS,key=lambda a:(means[a],a))
    other=next(a for a in ACTIONS if a != winner)
    if means[winner]-r > max(0.,means[other]+r):
        return winner
    return None


def disagreement(primary: dict[str,float], anchor: dict[str,float],cfg:IntegrityConfig) -> bool:
    """Reject equal channel means when their simultaneous CIs are disjoint.

    False alarm controlled only if both channels are honest iid observations
    with the same underlying expectation for each action.
    """
    validate_means(primary);validate_means(anchor)
    cutoff=radius(cfg.primary_samples,cfg)+radius(cfg.anchor_samples,cfg)
    return any(abs(primary[a]-anchor[a])>cutoff for a in ACTIONS)


def risk_config(cfg:IntegrityConfig) -> Config:
    return Config(epochs=cfg.epochs,samples=cfg.primary_samples,alpha=cfg.alpha,
                  cost_per_observation=cfg.primary_unit_cost,
                  tasks_per_epoch=cfg.tasks_per_epoch,hazard=cfg.hazard,
                  sensitivity=cfg.sensitivity,specificity=cfg.specificity,
                  max_age=cfg.max_anchor_age)


def decide(policy:str,t:int,state:IntegrityState,cue:bool|None,
           primary:dict[str,float],anchor:dict[str,float]|None,
           cfg:IntegrityConfig) -> tuple[dict,IntegrityState]:
    """Only observed means/cue/availability enter; hidden true gain never enters.

    'guard' crosschecks both channels at risk/expiry audits and quarantines on
    disagreement. Other arms isolate the cost of primary vs anchor sampling.
    No old certificate is represented as fresh when reused.
    """
    if policy not in POLICIES or not 0 <= t < cfg.epochs:
        raise ValueError('unsupported policy/epoch')
    validate_means(primary);validate_means(anchor)
    s=replace(state)
    p_audit=False;a_audit=False
    if policy == 'baseline':s.selected=None
    elif policy in ('primary_risk','primary_periodic'):
        if policy=='primary_risk':
            p_audit=should_audit('risk',t,State(s.selected,s.last_primary),cue,risk_config(cfg))
        else:p_audit=s.last_primary < 0 or t-s.last_primary >= cfg.max_anchor_age
    elif policy in ('anchor_periodic','anchor_always','anchor_risk'):
        if policy=='anchor_always':a_audit=True
        elif policy=='anchor_periodic':a_audit=s.last_anchor<0 or t-s.last_anchor>=cfg.max_anchor_age
        else:a_audit=should_audit('risk',t,State(s.selected,s.last_anchor),cue,risk_config(cfg))
    elif policy=='dual_periodic':
        p_audit=a_audit=s.last_anchor<0 or t-s.last_anchor>=cfg.max_anchor_age
    elif policy=='guard':
        p_audit=should_audit('risk',t,State(s.selected,s.last_primary),cue,risk_config(cfg))
        a_audit=(s.last_anchor<0 or t-s.last_anchor>=cfg.max_anchor_age
                 or s.require_anchor or s.suspect
                 or (cue is True and t>s.last_anchor))
        # A changed primary recommendation is not authoritative until anchored.
        if p_audit and s.selected is not None:
            p_winner=certified_best(primary,cfg.primary_samples,cfg)
            if p_winner!=s.selected:a_audit=True
        # Never grant a fresh anchored certificate from only one channel.
        # Otherwise a corrupted anchor could be mistaken for independent truth.
        if a_audit:p_audit=True
    primary_decision=None;anchor_decision=None;alarm=False;fresh=False
    if p_audit:
        s.last_primary=t
        primary_decision=certified_best(primary,cfg.primary_samples,cfg)
    if a_audit:
        if anchor is None:
            s.selected=None;s.suspect=True;s.require_anchor=True
        else:
            s.last_anchor=t
            anchor_decision=certified_best(anchor,cfg.anchor_samples,cfg)
            if p_audit and policy in ('guard','dual_periodic'):
                alarm=disagreement(primary,anchor,cfg)
            if alarm:
                # Cannot infer which channel is honest from disagreement alone.
                s.selected=None;s.suspect=True;s.require_anchor=True
            else:
                s.selected=anchor_decision
                s.suspect=False;s.require_anchor=False
                fresh=anchor_decision is not None
    elif p_audit:
        if policy.startswith('primary_'):
            s.selected=primary_decision
            fresh=primary_decision is not None
        elif policy=='guard':
            # Primary is not an independent anchor. No fresh certificate.
            if primary_decision!=s.selected:
                s.selected=None;s.require_anchor=True
    if policy=='guard' and s.last_anchor>=0 and t-s.last_anchor>=cfg.max_anchor_age and not a_audit:
        s.selected=None;s.require_anchor=True
    if policy in ('anchor_periodic','anchor_always','anchor_risk','dual_periodic') and a_audit and anchor is None:
        s.selected=None
    if s.suspect and policy in ('guard','dual_periodic'):s.selected=None
    chosen=s.selected or 'baseline'
    p_cost=2*cfg.primary_samples*cfg.primary_unit_cost if p_audit else 0.
    a_cost=2*cfg.anchor_samples*cfg.anchor_unit_cost if a_audit and anchor is not None else 0.
    return {'selected':chosen,'primary_audit':int(p_audit),
            'anchor_audit':int(a_audit and anchor is not None),
            'anchor_unavailable':int(a_audit and anchor is None),
            'disagreement_alarm':int(alarm),
            'fresh_certificate':int(fresh),
            'stale_deployment':int(chosen!='baseline' and not fresh),
            'held':int(chosen=='baseline'),
            'suspect':int(s.suspect),
            'audit_cost':round(p_cost+a_cost,8)},s


def cue_calibration(observations:list[tuple[bool,bool]],alpha:float=.05)->dict:
    """Estimate cue sensitivity/specificity on independent labeled examples.

    Fixed balanced design, not a proof of stationarity of future cue quality.
    """
    if not 0<alpha<1:raise ValueError('alpha')
    positive=[cue for changed,cue in observations if changed]
    negative=[cue for changed,cue in observations if not changed]
    if not positive or not negative:raise ValueError('both classes required')
    sensitivity=sum(positive)/len(positive)
    specificity=sum(not cue for cue in negative)/len(negative)
    bounds={}
    for name,rate,n in (('sensitivity',sensitivity,len(positive)),('specificity',specificity,len(negative))):
        # Two rates, two-sided simultaneous Hoeffding, [0,1] observations.
        eps=sqrt(log(4/alpha)/(2*n))
        bounds[name]={'estimate':rate,'lower':max(0.,rate-eps),
                      'upper':min(1.,rate+eps),'n':n}
    return {'alpha':alpha,'bounds':bounds,
            'limitation':'Only under iid labeled calibration samples from the same cue mechanism.'}
