"""v2.4: independent-audit corroboration, conservative trust, and bounded renewal.

Research sandbox. Agreement of all streams cannot detect shared corruption.
Nothing here certifies that the reference stream is honest.
"""
from __future__ import annotations
from dataclasses import dataclass, replace, field
from math import sqrt, log, isfinite
from typing import Optional
from .feedback_integrity import (IntegrityConfig, IntegrityState, decide as old_decide)

ACTIONS = ('A','B')
POLICIES = ('triad_adaptive','triad_periodic','triad_always',
            'reference_periodic','reference_always','legacy_guard',
            'primary_periodic','baseline')

@dataclass(frozen=True)
class TrustConfig:
    epochs: int = 24
    primary_samples: int = 384
    anchor_samples: int = 384
    reference_samples: int = 1024
    alpha: float = .05
    primary_unit_cost: float = .002
    anchor_unit_cost: float = .006
    reference_unit_cost: float = .006
    tasks_per_epoch: int = 80
    max_age: int = 6
    periodic_age: int = 4
    hazard: float = .06
    use_cue: bool = True
    alarm_backoff_cap: int = 4
    def __post_init__(self):
        if min(self.epochs,self.primary_samples,self.anchor_samples,self.reference_samples,
               self.tasks_per_epoch,self.max_age,self.periodic_age,self.alarm_backoff_cap)<1:
            raise ValueError('Invalid positive configuration')
        if not 0 < self.alpha < 1 or not 0<=self.hazard<1:
            raise ValueError('Invalid alpha/hazard')
        if any(not isfinite(c) or c<0 for c in (self.primary_unit_cost,self.anchor_unit_cost,self.reference_unit_cost)):
            raise ValueError('Invalid cost')
        if not isinstance(self.use_cue,bool):raise ValueError('Invalid cue toggle')

@dataclass
class TrustState:
    selected: str = 'baseline'
    last_audit: int = -1
    suspect: bool = False
    alarm_streak: int = 0
    next_retry: int = 0
    last_estimated_gain: float = 0.
    reference_audits: int = 0
    primary_disagreements: int = 0
    anchor_disagreements: int = 0
    old_state: IntegrityState = field(default_factory=IntegrityState)


def radius(n:int,cfg:TrustConfig)->float:
    """Simultaneous +/- Hoeffding radius over 24*3*2 fixed means in [-1,1].

    Under independent honest bounded observations, per-event means are covered
    jointly with probability >= 1-alpha. No guarantee of channel honesty.
    """
    if n<1:raise ValueError('positive sample count required')
    m=3*len(ACTIONS)*cfg.epochs
    return sqrt(2*log(2*m/cfg.alpha)/n)


def validate(means:Optional[dict]):
    if means is None:return
    if not isinstance(means,dict) or set(means)!=set(ACTIONS):
        raise ValueError('Expected exact two-action dictionary')
    if any(not isinstance(x,(float,int)) or not isfinite(x) or not -1<=x<=1 for x in means.values()):
        raise ValueError('Non-finite/out-of-range evidence')


def certificate(means:dict,n:int,cfg:TrustConfig)->str|None:
    validate(means)
    r=radius(n,cfg)
    winner=max(ACTIONS,key=lambda a:(means[a],a))
    other=next(a for a in ACTIONS if a!=winner)
    if means[winner]-r>max(0.,means[other]+r):return winner
    return None


def incompatible(left:dict,right:dict,n_left:int,n_right:int,cfg:TrustConfig)->bool:
    validate(left);validate(right)
    max_gap=radius(n_left,cfg)+radius(n_right,cfg)
    return any(abs(left[a]-right[a])>max_gap for a in ACTIONS)


def posterior_disagreement(failures:int,checks:int)->float:
    """Descriptive Beta(1,1) posterior mean, NOT a safety certificate.

    The adaptive audit sampling may be informative, nonstationary or attacked.
    Do not interpret this as a calibrated error probability.
    """
    if checks<0 or not 0<=failures<=checks:raise ValueError('Invalid counters')
    return (1+failures)/(2+checks)


def _old_config(cfg:TrustConfig)->IntegrityConfig:
    return IntegrityConfig(epochs=cfg.epochs,primary_samples=cfg.primary_samples,
        anchor_samples=cfg.anchor_samples,alpha=cfg.alpha,
        primary_unit_cost=cfg.primary_unit_cost,anchor_unit_cost=cfg.anchor_unit_cost,
        tasks_per_epoch=cfg.tasks_per_epoch,max_anchor_age=cfg.periodic_age)


def _wrap_legacy(policy:str,t:int,s:TrustState,cue,primary,anchor,cfg):
    mapping={'legacy_guard':'guard','primary_periodic':'primary_periodic','baseline':'baseline'}
    event,old=old_decide(mapping[policy],t,s.old_state,cue,primary,anchor,_old_config(cfg))
    s.old_state=old
    s.selected=event['selected']
    event.update({'reference_audit':0,'reference_unavailable':0,
                  'integrity_alarm':event.get('disagreement_alarm',0),
                  'fresh':event.pop('fresh_certificate'),
                  'stale':event.pop('stale_deployment'),
                  'trust_primary':None,'trust_anchor':None,
                  'reason':'legacy','audit_mode':mapping[policy]})
    return event,s


def request_reference(policy:str,t:int,state:TrustState,cue:bool|None,
                      cfg:TrustConfig)->tuple[bool,str]:
    """Commit to a reference audit BEFORE its observation is delivered.

    For legacy policies, the reference is never available. For new policies,
    this uses only epoch, cue, retained state, and declared economics.
    """
    if policy not in POLICIES or not 0<=t<cfg.epochs:
        raise ValueError('Invalid policy/epoch')
    if policy in ('legacy_guard','primary_periodic','baseline'):
        return False,'legacy'
    s=state
    if s.suspect:
        audit=t>=s.next_retry
        return audit, 'quarantine_retry' if audit else 'quarantine_hold'
    if s.last_audit<0:return True,'initial'
    if policy in ('triad_always','reference_always'):return True,'every_epoch'
    if policy in ('triad_periodic','reference_periodic'):
        audit=t-s.last_audit>=cfg.periodic_age
        return audit,'periodic' if audit else 'defer'
    age=t-s.last_audit
    risk=min(1.,cfg.hazard*age)*cfg.tasks_per_epoch*max(0.,s.last_estimated_gain)
    cost=2*(cfg.primary_samples*cfg.primary_unit_cost+
            cfg.anchor_samples*cfg.anchor_unit_cost+
            cfg.reference_samples*cfg.reference_unit_cost)
    if age>=cfg.max_age:return True,'expiry'
    if risk>cost:return True,'risk'
    if cfg.use_cue and cue is True:return True,'cue'
    return False,'defer'


def decide(policy:str,t:int,state:TrustState,cue:bool|None,primary:dict,
           anchor:dict|None,reference:dict|None,cfg:TrustConfig):
    """Decision sees observed streams only if paid; never receives true gain.

    Simulator precomputes potential observations for common-random-number
    comparisons but they enter decision logic only after the audit gate.
    """
    if policy not in POLICIES or not 0<=t<cfg.epochs:raise ValueError('Invalid policy/epoch')
    validate(primary);validate(anchor);validate(reference)
    s=replace(state,old_state=replace(state.old_state))
    if policy in ('legacy_guard','primary_periodic','baseline'):
        return _wrap_legacy(policy,t,s,cue,primary,anchor,cfg)

    ref_only=policy.startswith('reference_')
    audit,reason=request_reference(policy,t,s,cue,cfg)

    fresh=0;alarm=0;p_mismatch=0;a_mismatch=0;ref_missing=0;ref_audit=0;p_audit=0;a_audit=0
    if audit:
        s.last_audit=t
        if reference is None:
            ref_missing=1
            s.selected='baseline';s.suspect=True
            s.next_retry=min(cfg.epochs,t+cfg.alarm_backoff_cap)
            reason='reference_unavailable'
        else:
            s.reference_audits+=1
            ref_audit=1
            if ref_only:
                accepted=certificate(reference,cfg.reference_samples,cfg)
            else:
                # Both channel observations are purchased at audit; no hidden means.
                p_audit=1;a_audit=int(anchor is not None)
                ref_cert=certificate(reference,cfg.reference_samples,cfg)
                p_cert=certificate(primary,cfg.primary_samples,cfg)
                a_cert=(certificate(anchor,cfg.anchor_samples,cfg) if anchor is not None else None)
                p_mismatch=int(incompatible(primary,reference,cfg.primary_samples,cfg.reference_samples,cfg))
                a_mismatch=int(anchor is not None and incompatible(anchor,reference,cfg.anchor_samples,cfg.reference_samples,cfg))
                s.primary_disagreements+=p_mismatch
                s.anchor_disagreements+=a_mismatch
                alarm=int(bool(p_mismatch or a_mismatch))
                accepted=(ref_cert if ref_cert is not None and ref_cert==p_cert==a_cert and
                          not alarm else None)
            if accepted is not None:
                s.selected=accepted
                s.last_estimated_gain=max(0.,reference[accepted])
                s.suspect=False;s.alarm_streak=0
                fresh=1
            else:
                s.selected='baseline';s.suspect=True
                s.alarm_streak+=1
                cooldown=min(cfg.alarm_backoff_cap,2**min(2,s.alarm_streak-1))
                s.next_retry=min(cfg.epochs,t+cooldown)
    else:
        if s.suspect or s.last_audit<0 or t-s.last_audit>=cfg.max_age:
            s.selected='baseline'
    selection=s.selected
    p_cost=2*cfg.primary_samples*cfg.primary_unit_cost*p_audit
    a_cost=2*cfg.anchor_samples*cfg.anchor_unit_cost*a_audit
    ref_cost=2*cfg.reference_samples*cfg.reference_unit_cost*ref_audit
    event={'epoch':t,'selected':selection,'fresh':fresh,
           'stale':int(selection!='baseline' and not fresh),
           'held':int(selection=='baseline'),'integrity_alarm':alarm,
           'primary_mismatch':p_mismatch,'anchor_mismatch':a_mismatch,
           'primary_audit':p_audit,'anchor_audit':a_audit,'reference_audit':ref_audit,
           'reference_unavailable':ref_missing,'audit_cost':round(p_cost+a_cost+ref_cost,8),
           'trust_primary':round(posterior_disagreement(s.primary_disagreements,s.reference_audits),6) if not ref_only else None,
           'trust_anchor':round(posterior_disagreement(s.anchor_disagreements,s.reference_audits),6) if not ref_only else None,
           'reason':reason,'audit_mode':policy}
    return event,s
