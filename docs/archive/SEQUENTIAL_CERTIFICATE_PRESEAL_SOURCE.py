"""CrystalGuard v1.9: optional-stopping-safe sequential decision certificates.

Guarantee (conditional): frozen finite K action library; independent tasks,
within-action iid outcomes in [0,1] from a *fixed source law*; known fixed
costs; and a justified TV shift bound for the target law. Dependence between
arms for the same task is allowed. Checkpoints must be specified before data.

Finite schedule: a Bonferroni union bound across K actions and J looks.
Unbounded schedule: alpha spending alpha/[j(j+1)] across all j >= 1.
Never claim validity when shift_tv_bound is unavailable or unjustified.
"""
from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Literal

VERSION = '1.9.0'


def _probability(alpha: float) -> float:
    if type(alpha) not in (int,float) or not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError('alpha must be a finite probability in (0,1)')
    return float(alpha)


def _integer(v, name):
    if type(v) is not int or v < 1:
        raise ValueError(f'{name} must be a positive integer')
    return v


def checkpoint_radius(n: int, action_count: int, look_index: int,
                      *, alpha: float=.05, total_looks: int|None=None) -> float:
    """Two-sided simultaneous Hoeffding radius, valid at selected checkpoints.

    For finite predeclared J looks, 2 K J exp(-2 n r_j^2) = alpha.
    For unlimited predeclared looks, allocate alpha_j=alpha/(j(j+1)).
    Do not examine intermediate data and use this guarantee for those looks.
    """
    n=_integer(n,'n');action_count=_integer(action_count,'action_count')
    look_index=_integer(look_index,'look_index');alpha=_probability(alpha)
    if total_looks is not None:
        total_looks=_integer(total_looks,'total_looks')
        if look_index > total_looks:
            raise ValueError('Look index exceeds predeclared schedule')
        multiplier=total_looks
    else:
        multiplier=look_index*(look_index+1)
    return math.sqrt(math.log(2*action_count*multiplier/alpha)/(2*n))


def fixed_radius(n: int, action_count: int, *, alpha: float=.05) -> float:
    n=_integer(n,'n');action_count=_integer(action_count,'action_count')
    return math.sqrt(math.log(2*action_count/_probability(alpha))/(2*n))


def _validate_inputs(sums, costs, n, shift, *, max_n: int|None=None):
    _integer(n,'n')
    if not isinstance(sums,Mapping) or not sums or 'baseline' not in sums or set(sums)!=set(costs):
        raise ValueError('Frozen action sums and costs, including baseline, are required')
    if max_n is not None and n>max_n:
        raise ValueError('Sample count exceeds the frozen maximum')
    for a in sums:
        s=sums[a];c=costs[a]
        if not isinstance(a,str) or not a:
            raise ValueError('Action names must be nonempty strings')
        if type(s) not in (int,float) or not math.isfinite(s) or not 0<=s<=n:
            raise ValueError('Sums must be finite and in [0,n]')
        if type(c) not in (int,float) or not math.isfinite(c) or not 0<=c<=1:
            raise ValueError('Costs must be finite in [0,1]')
    if shift is not None and (type(shift) not in (int,float) or not math.isfinite(shift) or not 0<=shift<=1):
        raise ValueError('Shift bound must be None or finite in [0,1]')


def certificate(sums: Mapping[str,float], costs:Mapping[str,float], n:int,
                *, radius:float, shift_tv_bound:float|None, baseline:str='baseline',
                objective:Literal['best','gain']='best') -> dict:
    """Certify robust-best, gain over baseline, or decline unsupported claim.

    Condition is simultaneous target mean coverage: |hat_p_a - p_target_a|
    <= radius + shift. Strict interval separation is required. A declared
    distribution bound is an assumption, NOT something inferred here.
    """
    _validate_inputs(sums,costs,n,shift_tv_bound)
    if baseline not in sums:
        raise ValueError('Named baseline not in action family')
    if type(radius) not in (float,int) or not math.isfinite(radius) or radius<0:
        raise ValueError('radius must be finite and nonnegative')
    if objective not in ('best','gain'):
        raise ValueError('Unsupported certificate objective')
    if shift_tv_bound is None:
        return {'status':'hold_unknown_shift','action':baseline,'certified_best':False,
                'certified_gain':False,'intervals':{},'margin':None}
    r=radius+shift_tv_bound
    intervals={}
    for a in sorted(sums):
        p=sums[a]/n;c=costs[a]
        intervals[a]={'lower':max(0.,p-r)-c,'upper':min(1.,p+r)-c,
                      'estimate':p-c}
    estimated=sorted(intervals,key=lambda a:(-intervals[a]['estimate'],a))[0]
    other_upper=max((v['upper'] for a,v in intervals.items() if a!=estimated),default=-math.inf)
    best_margin=intervals[estimated]['lower']-other_upper
    if best_margin>0:
        return {'status':'certified_best','action':estimated,'certified_best':True,
                'certified_gain':estimated!=baseline,'intervals':intervals,'margin':best_margin}
    if objective=='gain':
        winners=[a for a in intervals if a!=baseline and intervals[a]['lower']>intervals[baseline]['upper']]
        if winners:
            a=sorted(winners,key=lambda x:(-intervals[x]['lower'],x))[0]
            return {'status':'certified_gain','action':a,'certified_best':False,
                    'certified_gain':True,'intervals':intervals,
                    'margin':intervals[a]['lower']-intervals[baseline]['upper']}
    return {'status':'continue','action':baseline,'certified_best':False,
            'certified_gain':False,'intervals':intervals,'margin':None}


def impossible_without_data(costs:Mapping[str,float], shift_tv_bound:float|None,
                            *, baseline='baseline') -> bool:
    """Sound simple HOLD shortcut for BEST with identical action costs.

    With delta>=1/2, even perfect sample means have maximum possible lower
    bound 1-delta-c and rival upper delta-c. Strict separation impossible.
    Unequal costs can change the conclusion; do NOT prune in that case.
    """
    if not costs or baseline not in costs:
        raise ValueError('Costs require a frozen baseline')
    if shift_tv_bound is None:return False
    if type(shift_tv_bound) not in (int,float) or not math.isfinite(shift_tv_bound) or not 0<=shift_tv_bound<=1:
        raise ValueError('Invalid shift bound')
    for c in costs.values():
        if type(c) not in (float,int) or not math.isfinite(c) or not 0<=c<=1:
            raise ValueError('Invalid cost')
    return len(costs)>1 and len(set(float(c) for c in costs.values()))==1 and shift_tv_bound>=.5


def preflight(costs:Mapping[str,float], shift_tv_bound:float|None, *, objective='best') -> str|None:
    """Return reason for immediate HOLD, else None. Caller spends 0 samples."""
    if not costs or 'baseline' not in costs:
        raise ValueError('Frozen baseline and action costs required')
    if shift_tv_bound is None:return 'hold_unknown_shift'
    if objective=='best' and impossible_without_data(costs,shift_tv_bound):
        return 'hold_impossible_under_bounds'
    return None


def select_at_checkpoint(sums,costs,n,look_index,*,alpha=.05,shift_tv_bound,
                        total_looks:int|None=None,objective='best') -> dict:
    r=checkpoint_radius(n,len(sums),look_index,alpha=alpha,total_looks=total_looks)
    out=certificate(sums,costs,n,radius=r,shift_tv_bound=shift_tv_bound,objective=objective)
    return {**out,'radius':r,'look':look_index,'sample_count_per_action':n}
