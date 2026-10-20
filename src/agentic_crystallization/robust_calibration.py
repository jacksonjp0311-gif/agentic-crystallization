"""Agentic Crystallization v1.8: distribution-robust, simultaneous action certificates.

The strict proof is valid only for a finite, frozen library of actions;
i.i.d. [0,1] calibration outcomes from one source distribution; fixed known
costs; and a *justified*, predeclared total-variation shift bound for the
same outcomes/conditional task mechanism. No model confidence can create that bound.
"""
from __future__ import annotations
import math
from collections.abc import Mapping

VERSION = '1.8.0'


def hoeffding_radius(n: int, action_count: int, alpha: float = 0.05) -> float:
    """Two-sided simultaneous Hoeffding radius, Bonferroni over fixed actions.

    P(all |hat_mu(a)-mu_P(a)| <= r) >= 1-alpha, with iid calibration
    *across tasks* for every fixed action. Cross-action independence is not needed.
    """
    if type(n) is not int or n <= 0 or type(action_count) is not int or action_count <= 0:
        raise ValueError('Positive integer sample and frozen action counts required.')
    if isinstance(alpha, bool) or not isinstance(alpha,(int,float)) or not math.isfinite(alpha) or not 0<alpha<1:
        raise ValueError('alpha must be a finite number strictly between zero and one.')
    return math.sqrt(math.log(2*action_count/alpha)/(2*n))


def alpha_spending(alpha_total: float, decision_index: int) -> float:
    """A conservative union-bound budget for a prespecified sequence of checks.

    Sum_{t>=1} alpha_t = alpha_total. It does *not* repair data-adaptive
    invention/reuse of uncalibrated candidate actions.
    """
    if type(decision_index) is not int or decision_index < 1:raise ValueError('Decision index starts at one.')
    if type(alpha_total) not in (int,float) or not math.isfinite(alpha_total) or not 0<alpha_total<1:
        raise ValueError('Invalid error budget.')
    return float(alpha_total)/(decision_index*(decision_index+1))


def bounds(means: Mapping[str,float], costs: Mapping[str,float], n:int,
           *, alpha:float=0.05, shift_tv_bound:float|None=None):
    """Statistical P means -> simultaneous Q net-utility intervals.

    Shift budget must cover total variation of relevant *joint* task/outcome
    distributions, or task covariates under unchanged outcome mechanisms.
    None means unavailable. Never silently assume zero shift.
    """
    if not means or set(means)!=set(costs) or 'baseline' not in means:
        raise ValueError('A fixed, named baseline and matching action/cost keys are required.')
    for name in means:
        if not isinstance(name,str) or not name or type(means[name]) not in (int,float) or not math.isfinite(means[name]) or not 0<=means[name]<=1:
            raise ValueError('Observed action mean must be finite and within [0,1].')
        if type(costs[name]) not in (int,float) or not math.isfinite(costs[name]) or not 0<=costs[name]<=1:
            raise ValueError('Known deterministic action cost must be within [0,1].')
    eps=hoeffding_radius(n,len(means),alpha)
    if shift_tv_bound is None:
        return {'available':False,'reason':'No justified target/source distribution-shift bound; certification unavailable.',
                'action_count':len(means),'sample_count':n,'sampling_radius':eps,'alpha':alpha,'intervals':{}}
    if type(shift_tv_bound) not in (int,float) or not math.isfinite(shift_tv_bound) or not 0<=shift_tv_bound<=1:
        raise ValueError('The predeclared total-variation bound must lie in [0,1].')
    interval={}
    for name in sorted(means):
        m=float(means[name]);cost=float(costs[name]);r=eps+float(shift_tv_bound)
        interval[name]={'estimate':m-cost,
                        'lower':max(0.,m-r)-cost,'upper':min(1.,m+r)-cost,
                        'cost':cost}
    return {'available':True,'intervals':interval,'alpha':alpha,
            'action_count':len(means),'sample_count':n,'sampling_radius':eps,
            'shift_tv_bound':float(shift_tv_bound),'radius_before_clipping':eps+shift_tv_bound,
            'interpretation':'Simultaneous target mean bounds conditional on iid data, frozen library, fixed costs, and valid declared TV shift bound.'}


def select_action(calibration, *, baseline='baseline'):
    """Robust-best rank certificate; otherwise safe gain over baseline or fallback.

    A safe gain guarantees superiority to the baseline on the valid joint
    coverage event, *not* global optimality. Baseline fallback has no certificate
    of optimality and is not equivalent to HOLD from the host's point of view.
    """
    if not calibration.get('available'):
        return {'action':baseline,'status':'hold','certified_best':False,
                'certified_baseline_gain':False,'reason':calibration.get('reason','Calibration unavailable.')}
    intervals=calibration['intervals']
    if baseline not in intervals:raise ValueError('Baseline must be one of the frozen actions.')
    names=sorted(intervals)
    estimated=sorted(names,key=lambda a:(-intervals[a]['estimate'],a))[0]
    rival=max((intervals[a]['upper'] for a in names if a!=estimated),default=-math.inf)
    if intervals[estimated]['lower']>rival:
        return {'action':estimated,'status':'certified_best','certified_best':True,
                'certified_baseline_gain':estimated!=baseline,
                'margin':intervals[estimated]['lower']-rival}
    contenders=[a for a in names if a!=baseline and intervals[a]['lower']>intervals[baseline]['upper']]
    if contenders:
        selected=sorted(contenders,key=lambda a:(-intervals[a]['lower'],a))[0]
        return {'action':selected,'status':'certified_gain','certified_best':False,
                'certified_baseline_gain':True,
                'margin':intervals[selected]['lower']-intervals[baseline]['upper']}
    return {'action':baseline,'status':'fallback','certified_best':False,
            'certified_baseline_gain':False,'margin':None,
            'reason':'No candidate is certified better than the named baseline.'}


def interaction_certificate(value_means:Mapping[frozenset,float], costs:Mapping[frozenset,float],
                            n:int,*, group:frozenset,alpha:float=.05,shift_tv_bound:float|None=None):
    """Sign certificate for an explicit full factorial group of bounded outcomes.

    Every subset must have iid calibration observations on fixed task samples.
    Positive sign is only certified when estimate - sum(radii)>0.
    The error sum scales as 2**len(group) and may be extremely conservative.
    """
    from .stability import finite_difference
    if not isinstance(group,frozenset) or not 2 <= len(group) <= 4 or any(not isinstance(x,str) for x in group):
        raise ValueError('Use a frozen group of 2 to 4 named procedures.')
    expected={frozenset(x for i,x in enumerate(sorted(group)) if mask & (1<<i)) for mask in range(1<<len(group))}
    if set(value_means)!=expected or set(costs)!=expected:
        raise ValueError('Complete factorial utility and cost observations are required.')
    for key in expected:
        if type(value_means[key]) not in (int,float) or not math.isfinite(value_means[key]) or not 0<=value_means[key]<=1:
            raise ValueError('Each factorial outcome mean must lie in [0,1].')
        if type(costs[key]) not in (int,float) or not math.isfinite(costs[key]) or not 0<=costs[key]<=1:
            raise ValueError('Each factorial cost must lie in [0,1].')
    # For factorial count m, use the same direct fixed-family guarantee with m
    # actions (no artificial duplicate baseline that increases K).
    eps=hoeffding_radius(n,len(expected),alpha)
    if shift_tv_bound is None:
        return {'status':'hold','reason':'Shift bound unavailable.','estimated':None,'error_bound':None}
    if type(shift_tv_bound) not in (int,float) or not 0<=shift_tv_bound<=1:
        raise ValueError('Invalid shift bound.')
    net={s:float(value_means[s])-float(costs[s]) for s in expected}
    estimate=finite_difference(net,group)
    error=(2**len(group))*(eps+float(shift_tv_bound))
    state='positive' if estimate>error else 'negative' if estimate< -error else 'uncertain'
    return {'status':state,'estimated':estimate,'error_bound':error,
            'interval':[estimate-error,estimate+error], 'sampling_radius':eps,
            'shift_tv_bound':float(shift_tv_bound),'alpha':alpha,
            'meaning':'Higher-order finite difference; sign conditional on simultaneous bounds, not a critical threshold.'}
