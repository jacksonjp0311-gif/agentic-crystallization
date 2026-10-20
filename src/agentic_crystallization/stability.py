"""Agentic Crystallization v1.7: finite-action robust certificates and exact factorial checks.

This is a mathematical auditing instrument, NOT an autonomous learning agent.
All values must be in common utility units. Error bounds are externally supplied.
"""
from __future__ import annotations
from itertools import combinations
import math

def finite_difference(utility: dict[frozenset, float], group: frozenset, base=frozenset()):
    """Mobius interaction with explicit complete subset support."""
    if group & base: raise ValueError('group and base must be disjoint')
    terms=sorted(group)
    value=0.0
    for n in range(len(terms)+1):
        for part in combinations(terms,n):
            key=base | frozenset(part)
            if key not in utility: raise ValueError('missing subset value')
            value+=(-1)**(len(terms)-n)*utility[key]
    return value

def mobius_bound(error: dict[frozenset,float], group:frozenset, base=frozenset()):
    """Triangle bound for arbitrary correlated errors, no independence assumed."""
    if group & base: raise ValueError('overlap')
    terms=sorted(group); total=0.0
    for n in range(len(terms)+1):
        for part in combinations(terms,n):
            key=base | frozenset(part)
            if key not in error: raise ValueError('missing error bound')
            e=error[key]
            if not math.isfinite(e) or e<0: raise ValueError('invalid error')
            total+=e
    return total

def certify_action(qhat:dict[str,float], errors:dict[str,float]):
    """Exact rectangular uncertainty certificate, including ties and nonuniform errors.
    Return robust action only if its worst-case value strictly exceeds every other
    action's best case. Empty or nonfinite inputs are rejected.
    """
    if not qhat or set(qhat)!=set(errors):raise ValueError('missing actions or error bounds')
    for a,v in qhat.items():
        if not math.isfinite(v) or not math.isfinite(errors[a]) or errors[a]<0:raise ValueError('nonfinite value or invalid error')
    ranked=sorted(qhat,key=lambda a:(-qhat[a],a)); winner=ranked[0]
    if len(ranked)==1:return {'action':winner,'certified':True,'gap':math.inf,'margin':math.inf}
    challenger=max((qhat[a]+errors[a],a) for a in ranked[1:])
    gap=qhat[winner]-max(qhat[a] for a in ranked[1:])
    margin=qhat[winner]-errors[winner]-challenger[0]
    return {'action':winner,'certified':margin>0,'gap':gap,'margin':margin}

def choose_with_fallback(qhat,errors,fallback='baseline'):
    result=certify_action(qhat,errors)
    return result['action'] if result['certified'] else fallback

def cluster_error_bound(term_errors:dict[frozenset,float], subset:frozenset):
    """Bound error of additive + interaction decomposition using absolute sums.
    Caller supplies all included term errors; no omitted-interaction guarantee.
    """
    total=0.
    for key,v in term_errors.items():
        if key and key <= subset:
            if not math.isfinite(v) or v<0:raise ValueError('invalid term bound')
            total+=v
    return total

def value_interval(qhat, errors):
    return {a:(qhat[a]-errors[a],qhat[a]+errors[a]) for a in qhat}
