"""Stage K: fresh, frozen synthetic experiment for sequential certificates.

A source task produces a vector of independent Bernoulli procedure outcomes;
source task vectors are iid. A target task is drawn from a mixture
Q=(1-eta)P+eta B, with B a fixed adversarial vector. Thus TV(Q,P)<=eta.
The latent target law is available only to the evaluator, not to policies.

The project evaluates conditional validity; no real model is executed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

import numpy as np

from . import sequential_certificate as cert

VERSION='1.9.0'
ALPHA=.05
ACTIONS=('baseline','a','b','c','d','e')
COSTS={a:.02 for a in ACTIONS}
MAX_N=6400
LOOKS=(25,50,100,200,400,800,1600,3200,6400)
REGIMES={
    'stationary_easy': {'p':(.25,.86,.30,.28,.23,.19), 'declared_shift':0., 'eta':0.,'assumption_valid':True},
    'stationary_near_tie':{'p':(.50,.56,.55,.53,.49,.48), 'declared_shift':0.,'eta':0.,'assumption_valid':True},
    'bounded_shift':{'p':(.25,.81,.34,.31,.23,.20),'declared_shift':.08,'eta':.08,'assumption_valid':True},
    'gradual_shift':{'p':(.25,.73,.37,.32,.21,.18),'declared_shift':.10,'eta':'uniform_0_.10','assumption_valid':True},
    'wide_valid_shift':{'p':(.25,.82,.34,.30,.22,.19),'declared_shift':.55,'eta':.45,'assumption_valid':True},
    'violated_shift':{'p':(.25,.82,.28,.29,.22,.19),'declared_shift':.02,'eta':.92,'assumption_valid':False},
    'unknown_shift':{'p':(.25,.82,.34,.31,.23,.20),'declared_shift':None,'eta':.08,'assumption_valid':None},
}
ADVERSARY=np.array([.8,0.,1.,.2,.2,.2],dtype=float)


def deterministic_seed(*args):
    return int.from_bytes(hashlib.sha256('|'.join(map(str,args)).encode('utf-8')).digest()[:8], 'big')


def make_world(seed:int,regime:str):
    if type(seed) is not int or seed<0 or regime not in REGIMES:
        raise ValueError('Seed must be nonnegative integer and regime must be frozen')
    spec=REGIMES[regime]
    rng=np.random.default_rng(deterministic_seed('stage-k-world',seed,regime))
    jitter=rng.uniform(-.013,.013,len(ACTIONS))
    p=np.clip(np.array(spec['p'],dtype=float)+jitter,.001,.999)
    eta=rng.uniform(0,.10) if spec['eta']=='uniform_0_.10' else float(spec['eta'])
    q=(1-eta)*p+eta*ADVERSARY
    return {'seed':seed,'regime':regime,'source_means':p,'target_means':q,
            'eta':eta,'declared_shift':spec['declared_shift'],
            'assumption_valid':spec['assumption_valid']}


def source_draws(w):
    rng=np.random.default_rng(deterministic_seed('stage-k-draws',w['seed'],w['regime']))
    draws=(rng.random((MAX_N,len(ACTIONS)))<w['source_means']).astype(np.uint8)
    return draws.cumsum(axis=0,dtype=np.int32)


def _policy(shift,prefix,kind:str):
    # The policy receives ONLY the declared shift and source sample sums.
    # The hidden target distribution remains in the independent grader.
    reason=cert.preflight(COSTS,shift,objective='best')
    if reason:
        return {'status':reason,'action':'baseline','n':0,'looks':0,'margin':None,
                'sampling_radius':None,'intervals':None}
    if kind=='fixed':
        schedule=(MAX_N,)
    else:
        schedule=LOOKS
    last=None
    for j,n in enumerate(schedule,start=1):
        sums=dict(zip(ACTIONS,(int(v) for v in prefix[n-1])))
        if kind=='fixed':
            radius=cert.fixed_radius(n,len(ACTIONS),alpha=ALPHA)
            result=cert.certificate(sums,COSTS,n,radius=radius,shift_tv_bound=shift,objective='best')
        else:
            radius=cert.checkpoint_radius(n,len(ACTIONS),j,alpha=ALPHA,
                   total_looks=len(LOOKS) if kind=='finite' else None)
            result=cert.certificate(sums,COSTS,n,radius=radius,shift_tv_bound=shift,objective='best')
        last={'status':result['status'],'action':result['action'],'n':n,'looks':j,
              'margin':result['margin'],'sampling_radius':radius,'intervals':result['intervals']}
        if result['certified_best']:
            return last
    last['status']='hold_budget'
    last['action']='baseline'
    return last


def one(seed:int,regime:str)->dict:
    w=make_world(seed,regime)
    if w['declared_shift'] is None or cert.preflight(COSTS,w['declared_shift']) is not None:
        prefix=None
    else:
        prefix=source_draws(w)
    truth=dict(zip(ACTIONS,(float(v)-COSTS[a] for a,v in zip(ACTIONS,w['target_means']))))
    best=sorted(truth,key=lambda a:(-truth[a],a))[0]
    row={'seed':seed,'regime':regime,'declared_shift':w['declared_shift'] if w['declared_shift'] is not None else '',
         'true_mixture_eta':round(w['eta'],8),'assumption_valid':str(w['assumption_valid']),
         'target_best':best,'target_best_utility':round(truth[best],8),
         'target_baseline_utility':round(truth['baseline'],8)}
    for policy in ('fixed','finite','unbounded'):
        result=_policy(w['declared_shift'],prefix,policy)
        used=result['n']*len(ACTIONS)
        status=result['status'];action=result['action']
        correct=int(status=='certified_best' and action==best)
        false=int(status=='certified_best' and truth[action] < truth[best]-1e-12)
        fullcover=None
        if result['intervals'] is not None:
            fullcover=int(all(z['lower']-1e-12<=truth[a]<=z['upper']+1e-12
                              for a,z in result['intervals'].items()))
        row.update({f'{policy}_status':status, f'{policy}_action':action,
                    f'{policy}_n_per_action':result['n'],f'{policy}_total_observations':used,
                    f'{policy}_looks':result['looks'],f'{policy}_certified':int(status=='certified_best'),
                    f'{policy}_correct_cert':correct,f'{policy}_false_cert':false,
                    f'{policy}_coverage':fullcover if fullcover is not None else '',
                    f'{policy}_radius':round(result['sampling_radius'],8) if result['sampling_radius'] is not None else '',
                    f'{policy}_regret':round(truth[best]-truth[action],8),
                    f'{policy}_target_utility':round(truth[action],8)})
    return row


def bootstrap_ci(values,seed=2188,iterations=3000):
    if not values:return [None,None]
    rng=np.random.default_rng(seed)
    x=np.asarray(values,dtype=float)
    b=x[rng.integers(0,len(x),(iterations,len(x)))].mean(axis=1)
    return [round(float(v),6) for v in np.quantile(b,[.025,.975])]


def summarize(rows):
    summary=[]
    for regime in REGIMES:
        subset=[row for row in rows if row['regime']==regime]
        if not subset:continue
        n=len(subset)
        rec={'regime':regime,'worlds':n,'assumption_valid':REGIMES[regime]['assumption_valid'],
             'declared_shift':REGIMES[regime]['declared_shift']}
        for policy in ('fixed','finite','unbounded'):
            rec[f'{policy}_cert_rate']=round(statistics.mean(row[f'{policy}_certified'] for row in subset),6)
            rec[f'{policy}_wrong_cert_count']=sum(row[f'{policy}_false_cert'] for row in subset)
            rec[f'{policy}_mean_observations']=round(statistics.mean(row[f'{policy}_total_observations'] for row in subset),4)
            rec[f'{policy}_hold_rate']=round(statistics.mean(not row[f'{policy}_certified'] for row in subset),6)
            rec[f'{policy}_coverage_rate_at_final_look']=None if not [row for row in subset if row[f'{policy}_coverage']!=''] else round(statistics.mean(row[f'{policy}_coverage'] for row in subset if row[f'{policy}_coverage']!=''),6)
            rec[f'{policy}_mean_regret']=round(statistics.mean(row[f'{policy}_regret'] for row in subset),6)
        pairs=[row for row in subset if row['fixed_certified'] and row['finite_certified'] and row['fixed_action']==row['finite_action']]
        rec['paired_cert_count']=len(pairs)
        reductions=[1-row['finite_total_observations']/row['fixed_total_observations'] for row in pairs]
        rec['paired_mean_evidence_reduction']=round(statistics.mean(reductions),6) if reductions else None
        rec['paired_reduction_bootstrap_95pct']=bootstrap_ci(reductions,seed=deterministic_seed('ci',regime))
        summary.append(rec)
    return summary


def _source_hash(name):
    path=Path(__file__).with_name(name)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(out:Path, *, start_seed:int=50000, count:int=360, stage:str='holdout'):
    out=Path(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output directory must not contain prior experiment files')
    if type(start_seed) is not int or start_seed<0 or type(count) is not int or count<=0:
        raise ValueError('Start seed and count must be valid positive integers')
    out.mkdir(parents=True,exist_ok=True)
    proto={
       'schema':'agentic-crystallization-stage-k/1','version':VERSION,'stage':stage,
       'seeds':{'start':start_seed,'count':count,'last':start_seed+count-1},
       'regimes':REGIMES,'actions':list(ACTIONS),'known_action_costs':COSTS,
       'alpha_per_world':ALPHA,'max_samples_per_action':MAX_N,'checkpoints':list(LOOKS),
       'finite_alpha_spend':'alpha/(K*J) two-sided at each checkpoint',
       'unbounded_alpha_spend':'alpha/(K*j*(j+1)) two-sided at checkpoint j',
       'fixed_alpha_spend':'alpha/K two-sided at final n only',
       'target_mechanism':'Q=(1-eta)P+eta B on joint task/outcome vectors; TV(Q,P)<=eta',
       'source_sampling':'iid task outcome vectors with Bernoulli(p_a) each arm; arm dependence not required by theorem',
       'data_split':'Fresh world seed IDs separate from development and earlier v1.8 holdout. Same source draws for all policies, hidden target used for grading only.',
       'counterexamples':'violated_shift intentionally lies about its bound; unknown_shift refuses certification',
       'primary_endpoint':'Mean total evaluated action outcomes among worlds certified by both fixed and finite-grid rules for the same action',
       'secondary_endpoints':'world-level false best certificates, coverage, HOLD rate, regret, unbounded checkpoints, raw evidence count',
       'research_boundary':'Controlled finite library, exact known costs, correct shift bounds required; no phase transition, no autonomous Pegasus run',
       'stage_k_source_sha256':_source_hash('stage_k.py'),
       'sequential_certificate_source_sha256':_source_hash('sequential_certificate.py'),
       'numpy_version':np.__version__,
    }
    (out/'protocol.json').write_text(json.dumps(proto,indent=2,sort_keys=True,allow_nan=False)+'\n')
    results=[]
    for regime in REGIMES:
        for seed in range(start_seed,start_seed+count):
            results.append(one(seed,regime))
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
    summary=summarize(results)
    (out/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    sums={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ('protocol.json','runs.csv','summary.json')}
    (out/'manifest.json').write_text(json.dumps({'schema':'agentic-crystallization-stage-k-manifest/1',
                                                 'version':VERSION,'rows':len(results),'worlds_per_regime':count,
                                                 'stage':stage,'sha256':sums,
                                                 'synthetic':True,'model_execution':False},indent=2)+'\n')
    return summary


def main():
    p=argparse.ArgumentParser(description='Reproduce Stage K cost-aware sequential certification experiments')
    p.add_argument('--out',required=True)
    p.add_argument('--start-seed',type=int,default=50000)
    p.add_argument('--count',type=int,default=360)
    p.add_argument('--stage',choices=['development','holdout'],default='holdout')
    args=p.parse_args()
    print(json.dumps(run(Path(args.out),start_seed=args.start_seed,count=args.count,stage=args.stage),indent=2))

if __name__=='__main__':main()
