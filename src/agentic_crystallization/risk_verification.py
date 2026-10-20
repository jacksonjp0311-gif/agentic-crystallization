"""Risk-adaptive verification of synthetic, permitted procedures.

Fresh certification is current-epoch only; stale reuse is explicitly counted.
"""
from dataclasses import dataclass
from math import log,sqrt

ACTIONS=('A','B')
POLICIES=('risk','always','periodic','never','cue_switch','monitor_hold','baseline')

@dataclass(frozen=True)
class Config:
    epochs:int=24
    samples:int=384
    alpha:float=.05
    cost_per_observation:float=.002
    tasks_per_epoch:int=80
    hazard:float=.06
    sensitivity:float=.85
    specificity:float=.90
    max_age:int=4
    harm_magnitude:float=.35
    def __post_init__(self):
        if not 0<self.alpha<1 or self.samples<1 or self.epochs<1:raise ValueError('invalid audit allocation')
        if not 0<self.hazard<1 or not 0<self.sensitivity<1 or not 0<self.specificity<1:raise ValueError('invalid cue model')
        if self.max_age<1 or self.cost_per_observation<0 or self.tasks_per_epoch<1:raise ValueError('invalid cost/budget')

@dataclass
class State:
    selected:str|None=None
    last_audit:int=-1
    audits:int=0
    certified:int=0
    held:int=0

def radius(cfg:Config)->float:
    """Two-sided simultaneous Hoeffding radius for [-1,1] samples over 2*epochs tests."""
    return sqrt(2*log(4*cfg.epochs/cfg.alpha)/cfg.samples)

def cue_posterior(age:int,cue:bool|None,cfg:Config)->float|None:
    if cue is None:return None
    # Cue is about the CURRENT adjacent-epoch change, not cumulative changes.
    # Age is controlled separately by mandatory maximum-certificate lifetime.
    p=cfg.hazard
    lc=cfg.sensitivity if cue else 1-cfg.sensitivity
    ls=1-cfg.specificity if cue else cfg.specificity
    return p*lc/(p*lc+(1-p)*ls)

def should_audit(policy:str,t:int,state:State,cue:bool|None,cfg:Config)->bool:
    if policy not in POLICIES:raise ValueError('unsupported policy')
    if policy=='baseline':return False
    if state.last_audit<0:return True
    age=t-state.last_audit
    if policy=='always':return True
    if policy=='periodic':return age>=cfg.max_age
    if policy in ('never','cue_switch'):return False
    if policy=='monitor_hold':return age>=cfg.max_age
    if policy=='risk':
        if cue is None:return age>=2
        risk=cue_posterior(age,cue,cfg)
        return age>=cfg.max_age or risk*cfg.harm_magnitude*cfg.tasks_per_epoch>2*cfg.samples*cfg.cost_per_observation
    raise ValueError('unknown policy')

def certify(means:dict[str,float],cfg:Config)->str|None:
    if set(means)!=set(ACTIONS):raise ValueError('missing candidate')
    if any(not -1<=v<=1 for v in means.values()):raise ValueError('out-of-range audit')
    good=[a for a in ACTIONS if means[a]-radius(cfg)>0]
    return max(good,key=lambda a:(means[a],a)) if good else None

def choose(policy:str,t:int,state:State,cue:bool|None,means:dict[str,float],cfg:Config):
    """Pure decision function; never receives the hidden true utility."""
    audit=should_audit(policy,t,state,cue,cfg)
    nxt=State(state.selected,state.last_audit,state.audits,state.certified,state.held)
    if audit:
        nxt.selected=certify(means,cfg);nxt.last_audit=t
        nxt.audits+=1;nxt.certified+=int(nxt.selected is not None)
    if policy=='baseline':selected=None
    elif policy=='cue_switch' and not audit and cue and state.selected is not None:
        selected='B' if state.selected=='A' else 'A';nxt.selected=selected
    elif policy=='monitor_hold' and not audit and cue:selected=None
    else:selected=nxt.selected
    if selected is None:nxt.held+=1
    return {'policy':policy,'epoch':t,'cue':cue,'audit':int(audit),
            'fresh_cert':int(audit and selected is not None),
            'stale_deployment':int(not audit and selected is not None),
            'selected':selected or 'baseline',
            'held':int(selected is None),'audit_cost':2*cfg.samples*cfg.cost_per_observation if audit else 0.,
            'posterior':cue_posterior(t-state.last_audit,cue,cfg) if state.last_audit>=0 else None},nxt
