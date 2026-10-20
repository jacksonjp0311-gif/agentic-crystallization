"""v1.8 Stage J: finite-sample simultaneous calibration under declared TV shift.

This is a deterministic synthetic diagnostic, NOT a Pegasus learning run. The
secret test-domain parameters and planted interactions are used only for grading.
No candidate instructions, models, permissions, or memories are updated.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from pathlib import Path

import numpy as np

from .robust_calibration import bounds,select_action,interaction_certificate
from .stability import finite_difference

VERSION='1.8.0'
ACTIONS={
    'baseline':frozenset(), 'a':frozenset('a'), 'b':frozenset('b'),
    'c':frozenset('c'), 'ab':frozenset('ab'), 'ac':frozenset('ac'),
    'bc':frozenset('bc'), 'abc':frozenset('abc'), 'd':frozenset('d')}
FAMILIES=('additive','pairwise','triple','misleading_graph')
N_LEVELS=(200,1000,6400)
SCENARIOS={
    'iid_related':{'p':.10,'q':.10,'declared_tv':.0,'valid':True},
    'iid_unrelated':{'p':.85,'q':.85,'declared_tv':.0,'valid':True},
    'bounded_shift':{'p':.10,'q':.18,'declared_tv':.08,'valid':True},
    'wide_valid_shift':{'p':.10,'q':.45,'declared_tv':.35,'valid':True},
    'violated_shift':{'p':.10,'q':.92,'declared_tv':.05,'valid':False},
    'unknown_shift':{'p':.10,'q':.18,'declared_tv':None,'valid':None}}
ALPHA=.05
TRIPLE=frozenset('abc')


def deterministic_seed(*parts):
    digest=hashlib.sha256('|'.join(map(str,parts)).encode('utf-8')).digest()
    return int.from_bytes(digest[:8],'big')


def world(seed:int):
    """Plant utility mechanisms without revealing latent parameters to policies."""
    rng=random.Random(deterministic_seed('world',seed))
    family=FAMILIES[seed%len(FAMILIES)]
    base0=.36+rng.uniform(-.023,.023)
    base1=.40+rng.uniform(-.023,.023)
    weights0={'a':.054+rng.uniform(-.012,.012),'b':.059+rng.uniform(-.012,.012),
              'c':.053+rng.uniform(-.012,.012),'d':.018+rng.uniform(-.009,.009)}
    weights1={'a':.012+rng.uniform(-.006,.006),'b':.012+rng.uniform(-.006,.006),
              'c':.010+rng.uniform(-.006,.006),'d':.206+rng.uniform(-.020,.020)}
    pair0=(.15+rng.uniform(-.025,.025)) if family=='pairwise' else 0.
    triple0=(.30+rng.uniform(-.035,.035)) if family=='triple' else 0.
    triple1=(-.09+rng.uniform(-.015,.015)) if family=='triple' else 0.
    def p(s,z):
        base=base1 if z else base0
        weights=weights1 if z else weights0
        value=base+sum(weights[i] for i in s)
        if {'a','b'}<=s and family=='pairwise':value+=(0. if z else pair0)
        if {'a','b','c'}<=s and family=='triple':value+=(triple1 if z else triple0)
        return min(.99,max(.01,value))
    probs={name:(p(s,0),p(s,1)) for name,s in ACTIONS.items()}
    costs={name:(.025+.035*len(s)) for name,s in ACTIONS.items()}
    # Dense but functionally irrelevant edges, used only as a negative control.
    declared_density=.92 if family=='misleading_graph' else (.3 if family in ('pairwise','triple') else .0)
    return {'seed':seed,'family':family,'probs':probs,'costs':costs,'reported_graph_density':declared_density}


def true_net(w, q):
    """Oracle-only target expected net reward; does not enter policy selection."""
    return {a:(1-q)*p[0]+q*p[1]-w['costs'][a] for a,p in w['probs'].items()}


def calibration_means(w,p,n,scenario):
    """Paired task contexts, i.i.d. across tasks. Independent arm coins within a task."""
    rng=np.random.default_rng(deterministic_seed('calibration',w['seed'],scenario,n))
    order=tuple(sorted(ACTIONS))
    contexts=(rng.random(n)<p).astype(np.int8)
    conditional=np.array([w['probs'][a] for a in order],dtype=float).T
    successes=(rng.random((n,len(order)))<conditional[contexts])
    means=successes.mean(axis=0)
    return dict(zip(order,(float(v) for v in means)))


def _conditioned_interaction(data,w,n,shift):
    factorial={s:data[name] for name,s in ACTIONS.items() if s<=TRIPLE}
    costs={s:w['costs'][name] for name,s in ACTIONS.items() if s<=TRIPLE}
    return interaction_certificate(factorial,costs,n,group=TRIPLE,alpha=ALPHA,shift_tv_bound=shift)


def one(seed,scenario,n):
    spec=SCENARIOS[scenario]
    w=world(seed)
    means=calibration_means(w,spec['p'],n,scenario)
    exact=true_net(w,spec['q'])
    cal=bounds(means,w['costs'],n,alpha=ALPHA,shift_tv_bound=spec['declared_tv'])
    decision=select_action(cal)
    best=sorted(exact,key=lambda a:(-exact[a],a))[0]
    greedy=sorted(means,key=lambda a:(-(means[a]-w['costs'][a]),a))[0]
    selected=decision['action']
    coverage=int(cal['available'] and all(cal['intervals'][a]['lower']-1e-12 <=v <=cal['intervals'][a]['upper']+1e-12 for a,v in exact.items()))
    safe_gain=int(decision['certified_baseline_gain'])
    certified=int(decision['certified_best'])
    harmful=int(safe_gain and exact[selected]<exact['baseline']-1e-12)
    cert_error=int(certified and selected!=best)
    ints=_conditioned_interaction(means,w,n,spec['declared_tv'])
    true_interaction=finite_difference({s:exact[a] for a,s in ACTIONS.items() if s<=TRIPLE},TRIPLE)
    sign=ints['status']
    sign_wrong=int(sign in ('positive','negative') and (true_interaction<=0 if sign=='positive' else true_interaction>=0))
    return {
        'seed':seed,'family':w['family'],'scenario':scenario,'n':n,
        'p_source_unrelated':spec['p'],'p_target_unrelated':spec['q'],
        'true_tv_shift':abs(spec['q']-spec['p']),
        'declared_tv':spec['declared_tv'] if spec['declared_tv'] is not None else '',
        'shift_valid':str(spec['valid']),'coverage':coverage if cal['available'] else '',
        'uncertainty_available':int(cal['available']),
        'epsilon_hoeffding':round(cal['sampling_radius'],9),
        'robust_action':selected,'robust_status':decision['status'],
        'certified_best':certified,'certified_baseline_gain':safe_gain,
        'certified_best_wrong':cert_error,'certified_gain_harmful':harmful,
        'greedy_action':greedy,'oracle_action':best,
        'greedy_harmful':int(exact[greedy]<exact['baseline']-1e-12),
        'baseline_utility':round(exact['baseline'],9),
        'greedy_utility':round(exact[greedy],9),
        'robust_utility':round(exact[selected],9),
        'oracle_utility':round(exact[best],9),
        'robust_regret':round(exact[best]-exact[selected],9),
        'greedy_regret':round(exact[best]-exact[greedy],9),
        'interaction_status':sign,'true_interaction':round(true_interaction,9),
        'interaction_wrong_sign':sign_wrong,'interaction_estimate':round(ints['estimated'],9) if ints['estimated'] is not None else '',
        'reported_graph_density':w['reported_graph_density'],
        'calibration_draws':n*len(ACTIONS),
        'statement':'Synthetic oracle grades; not a live-agent outcome.'}


def _ci(values,seed):
    if not values:return [None,None]
    rng=np.random.default_rng(seed)
    arr=np.array(values,dtype=float)
    indices=rng.integers(0,len(values),size=(1500,len(values)))
    return np.percentile(arr[indices].mean(axis=1),[2.5,97.5]).round(6).tolist()


def summarize(rows):
    result=[]
    for scenario in SCENARIOS:
        for n in N_LEVELS:
            group=[x for x in rows if x['scenario']==scenario and x['n']==n]
            if not group:continue
            mean=lambda field:statistics.mean(float(x[field]) for x in group)
            diff=[x['robust_utility']-x['greedy_utility'] for x in group]
            entries={'scenario':scenario,'n':n,'worlds':len(group),
                'joint_coverage':None if not group[0]['uncertainty_available'] else mean('coverage'),
                'certified_best_rate':mean('certified_best'),
                'certified_gain_rate':mean('certified_baseline_gain'),
                'certified_best_wrong_count':sum(x['certified_best_wrong'] for x in group),
                'certified_harm_count':sum(x['certified_gain_harmful'] for x in group),
                'greedy_harm_rate':mean('greedy_harmful'),
                'mean_robust_regret':mean('robust_regret'),
                'mean_greedy_regret':mean('greedy_regret'),
                'mean_robust_minus_greedy_utility':statistics.mean(diff),
                'robust_minus_greedy_bootstrap_95pct':_ci(diff,deterministic_seed('ci',scenario,n)),
                'certified_positive_interactions':sum(x['interaction_status']=='positive' for x in group),
                'false_interaction_signs':sum(x['interaction_wrong_sign'] for x in group),
                'meaning':'World-level descriptive means; certified guarantees conditional on joint coverage and valid TV bound.'}
            result.append(entries)
    return result


def run(out:Path, *, seeds=range(10000,10160), stage='holdout'):
    out=Path(out)
    if out.exists() and any(out.iterdir()):raise ValueError('Output directory must be new/empty: preserve historical experiments.')
    out.mkdir(parents=True,exist_ok=True)
    seeds=list(seeds)
    if not seeds or len(set(seeds))!=len(seeds):raise ValueError('Unique nonempty seeds required.')
    # Binding the protocol and current code before drawing any result is the
    # user-visible preregistration discipline for this *deterministic* generator.
    source=Path(__file__).read_bytes()
    robust_source=Path(__file__).with_name('robust_calibration.py').read_bytes()
    protocol={'schema':'agentic-crystallization-stage-j/1','version':VERSION,'stage':stage,
              'seeds':{'min':min(seeds),'max':max(seeds),'count':len(seeds)},
              'alpha_per_decision':ALPHA,
              'action_library':{k:sorted(v) for k,v in ACTIONS.items()},
              'families':list(FAMILIES),'sample_sizes':list(N_LEVELS),'scenarios':SCENARIOS,
              'per_world_seed_generator':'SHA256 seeded; world parameters frozen per seed; calibration seed additionally scenario and n',
              'data_split':'Independent calibration tasks per world; oracle target values only in grader; different world IDs in development and holdout',
              'costs':'Deterministic per action, all actions measured on same calibration tasks',
              'claim_scope':'Finite frozen action library; iid source samples; TV bound supplied or HOLD; no phase transition inference.',
              'stage_j_source_sha256':hashlib.sha256(source).hexdigest(),
              'calibration_source_sha256':hashlib.sha256(robust_source).hexdigest()}
    protocol_bytes=json.dumps(protocol,indent=2,sort_keys=True).encode('utf-8')+b'\n'
    (out/'protocol.json').write_bytes(protocol_bytes)
    results=[]
    for scenario in SCENARIOS:
        for n in N_LEVELS:
            for seed in seeds:results.append(one(seed,scenario,n))
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
    summaries=summarize(results)
    with (out/'summary.json').open('w',encoding='utf-8') as f:json.dump(summaries,f,indent=2);f.write('\n')
    readme={'schema':'agentic-crystallization-stage-j-manifest/1','version':VERSION,'stage':stage,
            'world_rows':len(results),'worlds_per_regime':len(seeds),'regimes':len(SCENARIOS),'sample_sizes':list(N_LEVELS),
            'protocol_sha256':hashlib.sha256(protocol_bytes).hexdigest(),
            'runs_sha256':hashlib.sha256((out/'runs.csv').read_bytes()).hexdigest(),
            'summary_sha256':hashlib.sha256((out/'summary.json').read_bytes()).hexdigest(),
            'synthetic':True,'model_execution':False,
            'interpretation':'Statistical calibration under stated assumptions; deliberate shift violation demonstrates invalid certificates.'}
    (out/'manifest.json').write_text(json.dumps(readme,indent=2)+'\n')
    return summaries


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--start-seed',type=int,default=10000)
    ap.add_argument('--count',type=int,default=160)
    ap.add_argument('--stage',choices=['development','holdout'],default='holdout')
    a=ap.parse_args()
    res=run(a.out,seeds=range(a.start_seed,a.start_seed+a.count),stage=a.stage)
    print(json.dumps({'rows':a.count*len(SCENARIOS)*len(N_LEVELS),'stage':a.stage,'summary':res},indent=2))
