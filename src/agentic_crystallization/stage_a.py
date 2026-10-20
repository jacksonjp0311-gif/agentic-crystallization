"""Agentic Crystallization 1.0: deterministic, oracle-grounded Stage A.

All methods consume identical observations. The world is synthetic; this does not
establish phase transitions or autonomous learning in a real agent.
"""
from __future__ import annotations
import argparse, csv, hashlib, itertools, json, math, random, statistics
from pathlib import Path

FAMILIES=('additive','pairwise','higher_order','redundancy','misleading')
POLICIES=('no_memory','cache_only','additive','same_estimates_linear','interaction_aware')
SIZES=(8,10,12)
SEEDS=tuple(range(12))
TRAIN_NOISE=0.02
K=4

def subsets(items,max_order=3):
    for order in range(max_order+1):
        yield from itertools.combinations(items,order)

def world(family,n,seed):
    rng=random.Random(1000003*seed+97*n+sum(ord(x) for x in family))
    weights=[rng.uniform(.1,.65) for _ in range(n)]
    pairs={}; triples={}; groups=[]
    if family=='pairwise':
        options=list(itertools.combinations(range(n),2));rng.shuffle(options)
        pairs={p:rng.uniform(.5,1.1) for p in options[:max(2,n//2)]}
    if family=='higher_order':
        options=list(itertools.combinations(range(n),3));rng.shuffle(options)
        triples={t:rng.uniform(.8,1.5) for t in options[:max(2,n//4)]}
    if family=='redundancy':
        groups=[tuple(range(0,min(4,n)))]
    # Deliberately dense metadata unrelated to causal utility.
    metadata=[list(p) for p in itertools.combinations(range(n),2) if rng.random()<.75] if family=='misleading' else []
    return dict(family=family,n=n,weights=weights,pairs=pairs,triples=triples,groups=groups,metadata=metadata)

def utility(w,S):
    chosen=set(S);score=sum(w['weights'][i] for i in chosen)
    score+=sum(v for edge,v in w['pairs'].items() if set(edge)<=chosen)
    score+=sum(v for edge,v in w['triples'].items() if set(edge)<=chosen)
    # Redundant procedures share one capped bonus, never multiple bonuses.
    for group in w['groups']:
        if chosen.intersection(group):score+=.8
    return score

def train(w,seed):
    rng=random.Random(seed*2999+w['n']*13+9)
    return {s:utility(w,s)+rng.uniform(-TRAIN_NOISE,TRAIN_NOISE) for s in subsets(range(w['n']))}

def coefficients(obs,n):
    coeff={}
    for s in subsets(range(n)):
        coeff[s]=sum((-1)**(len(s)-len(a))*obs[a] for a in subsets(s,len(s)))
    return coeff

def predict(coeff,S,mode):
    chosen=set(S)
    if mode=='interaction_aware':
        return sum(v for s,v in coeff.items() if set(s)<=chosen)
    if mode=='additive':
        return coeff[()]+sum(coeff[(i,)] for i in S)
    if mode=='same_estimates_linear':
        # Exact same interaction coefficients, projected to linear procedure scores.
        return coeff[()]+sum(sum(v/len(s) for s,v in coeff.items() if s and i in s) for i in S)
    raise ValueError(mode)

def choose(policy,available,obs,coeff):
    available=tuple(sorted(available))
    if policy=='no_memory':return available[:K]
    if policy=='cache_only':
        # Reuse best previously observed feasible set, then fill remaining slots
        # deterministically by singleton evidence (no unseen combination scoring).
        feasible=[s for s in obs if len(s)<=3 and set(s)<=set(available)]
        seed=max(feasible,key=lambda s:(obs[s],tuple(-i for i in s)))
        fill=sorted((i for i in available if i not in seed),key=lambda i:(-obs[(i,)],i))
        return tuple(sorted(seed+tuple(fill[:K-len(seed)])))
    return max(itertools.combinations(available,K),key=lambda s:(predict(coeff,s,policy),tuple(-i for i in s)))

def run_case(family,n,seed,test_count=80):
    w=world(family,n,seed);obs=train(w,seed);coeff=coefficients(obs,n)
    rng=random.Random(7000003+seed*127+n*31+len(family))
    totals={p:[] for p in POLICIES};optimal=[];sets={p:[] for p in POLICIES}
    for _ in range(test_count):
        avail=tuple(sorted(rng.sample(range(n),min(n,7))))
        optimum=max(utility(w,s) for s in itertools.combinations(avail,K));optimal.append(optimum)
        for p in POLICIES:
            s=choose(p,avail,obs,coeff);sets[p].append(s);totals[p].append(utility(w,s))
    # Exact nonzero coefficients are causal Möbius effects in this synthetic world.
    ground={s:sum((-1)**(len(s)-len(a))*utility(w,a) for a in subsets(s,len(s))) for s in subsets(range(n)) if len(s)>=2}
    predicted={s:coeff[s] for s in ground}
    threshold=.25
    truth={s for s,v in ground.items() if abs(v)>threshold}
    discovered={s for s,v in predicted.items() if abs(v)>threshold}
    tp=len(truth&discovered);fp=len(discovered-truth);fn=len(truth-discovered)
    # Graph topology measured separately from task utility; pairwise positive edges only.
    actual_edges=[s for s,v in ground.items() if len(s)==2 and v>threshold]
    structural=len(actual_edges)/(n*(n-1)/2)
    if family=='misleading':structural=len(w['metadata'])/(n*(n-1)/2)
    return dict(family=family,n=n,seed=seed,train_queries=len(obs),test_cases=test_count,
                scores={p:statistics.mean(v) for p,v in totals.items()},oracle=statistics.mean(optimal),
                precision=tp/(tp+fp) if tp+fp else (1.0 if not truth else 0.0),
                recall=tp/(tp+fn) if tp+fn else 1.0,truth_interactions=len(truth),
                recovered_interactions=tp,false_positives=fp,structural_density=structural,
                reuse_rate={p:sum(s in obs for s in sets[p])/test_count for p in POLICIES},
                # No longitudinal procedure promotion occurs in Stage A.
                retention=None,graph_stability=None,
                adaptation_efficiency={p:(statistics.mean(totals[p])-statistics.mean(totals['no_memory']))/len(obs) for p in POLICIES})

def execute(out:Path,seeds=SEEDS,sizes=SIZES,test_count=80):
    out.mkdir(parents=True,exist_ok=True)
    cases=[run_case(f,n,seed,test_count) for f in FAMILIES for n in sizes for seed in seeds]
    rows=[]
    for c in cases:
        for p in POLICIES:
            rows.append({k:c[k] for k in ('family','n','seed','train_queries','test_cases','precision','recall','truth_interactions','recovered_interactions','false_positives','structural_density','retention','graph_stability')}|{'policy':p,'score':c['scores'][p],'oracle':c['oracle'],'reuse_rate':c['reuse_rate'][p],'adaptation_efficiency':c['adaptation_efficiency'][p]})
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summaries={}
    for family in FAMILIES:
        subset=[c for c in cases if c['family']==family]
        summaries[family]={p:{'mean':statistics.mean(c['scores'][p] for c in subset),
                             'sd_across_worlds':statistics.stdev(c['scores'][p] for c in subset),
                             'mean_regret':statistics.mean(c['oracle']-c['scores'][p] for c in subset)} for p in POLICIES}
        summaries[family]['interaction_recovery']={'precision':statistics.mean(c['precision'] for c in subset),'recall':statistics.mean(c['recall'] for c in subset),'false_positives_mean':statistics.mean(c['false_positives'] for c in subset)}
        summaries[family]['structural_density_mean']=statistics.mean(c['structural_density'] for c in subset)
    manifest={'schema':'agentic-crystallization-stage-a/1','version':'1.0.0','seed_list':list(seeds),'sizes':list(sizes),'families':list(FAMILIES),'policies':list(POLICIES),'train_noise_uniform':TRAIN_NOISE,'test_count_per_world':test_count,'selected_procedures':K,'available_procedures':7,'train_design':'complete factorial subsets of order <=3; identical for all policies','test_design':'fresh held-out availability masks; oracle world fixed; no model inference','interaction_max_order':3,'threshold':.25,'results':'runs.csv','limitation':'Synthetic planted interactions; no causal discovery in real agents; no phase-transition claim; R/D/E proxies only, S and K unmeasured.'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n',encoding='utf-8')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*') if p.is_file()}
    (out/'SHA256SUMS.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    return summaries,len(cases)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path('experiments/results'));parser.add_argument('--seeds',type=int,default=12);parser.add_argument('--tests',type=int,default=80);a=parser.parse_args()
    s,n=execute(a.out,seeds=range(a.seeds),test_count=a.tests)
    print(json.dumps({'worlds':n,'results':str(a.out),'family_means':{f:{p:round(s[f][p]['mean'],4) for p in POLICIES} for f in FAMILIES}},indent=2))
if __name__=='__main__':main()
