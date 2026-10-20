"""Stage B/C: controlled sparse-hypergraph availability interventions.
Synthetic fixed-oracle study; no real agent learning or phase transition claimed.
"""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,random,statistics
from pathlib import Path
import numpy as np

SIZES=(12,18,24)
DENSITIES=(0.,.15,.3,.45,.6,.75,.9)
SEEDS=tuple(range(8))
POLICIES=('no_memory','cache','additive','same_estimates_linear','interaction')
FAMILIES=('synergy','additive','misleading')
TRAIN=320
TEST=60
RIDGE=1.0

def make_world(n,density,seed,family):
    rng=random.Random(seed*100003+n*997+sum(map(ord,family)))
    base=np.array([rng.uniform(.10,.45) for _ in range(n)])
    all_trip=list(itertools.combinations(range(n),3));rng.shuffle(all_trip)
    # Fixed candidate budget across density: latent hyperedges + decoys.
    candidates=tuple(sorted(all_trip[:2*n]))
    planted=set(rng.sample(candidates[:n],round(density*n))) if family=='synergy' else set()
    # misleading graph has the same density and edge counts, but no utility interactions.
    metadata=set(rng.sample(candidates[:n],round(density*n))) if family=='misleading' else set(planted)
    strengths={edge:rng.uniform(.5,1.1) for edge in planted}
    return base,candidates,strengths,metadata

def score(base,strengths,chosen):
    s=set(chosen)
    return float(sum(base[i] for i in s)+sum(v for edge,v in strengths.items() if set(edge)<=s))

def features(chosen,n,candidates):
    s=set(chosen)
    return np.array([1.]+[float(i in s) for i in range(n)]+[float(set(t)<=s) for t in candidates],dtype=float)

def largest_component(n,hyperedges):
    adj=[set() for _ in range(n)]
    for edge in hyperedges:
        for a,b in itertools.combinations(edge,2):adj[a].add(b);adj[b].add(a)
    unseen=set(range(n));largest=0
    while unseen:
        node=unseen.pop();stack=[node];size=1
        while stack:
            for j in adj[stack.pop()] & unseen:
                unseen.remove(j);stack.append(j);size+=1
        largest=max(largest,size)
    return largest/n

def fit(X,y,n,candidates):
    # Common observations, fixed ridge, no oracle leakage.
    pen=np.eye(X.shape[1])*RIDGE;pen[0,0]=0.
    co=np.linalg.solve(X.T@X+pen,X.T@y)
    return co

def policy_value(policy,chosen,co,n,candidates,cache):
    if policy=='no_memory':return -sum(chosen)*0.000001  # tie chooses lexicographic subset
    if policy=='cache':return cache.get(tuple(chosen),-1e6)
    if policy=='additive':return co[0]+sum(co[1+i] for i in chosen)
    if policy=='same_estimates_linear':
        weights=co[1:n+1].copy()
        for edge,val in zip(candidates,co[n+1:]):
            for i in edge:weights[i]+=val/3
        return co[0]+sum(weights[i] for i in chosen)
    if policy=='interaction':return float(features(chosen,n,candidates)@co)
    raise ValueError(policy)

def one_world(n,density,seed,family,train_count=TRAIN,test_count=TEST):
    base,candidates,strengths,metadata=make_world(n,density,seed,family)
    rng=random.Random(seed*1234567+n*211+int(density*1000)*71+sum(map(ord,family)))
    # Fixed-size subset sampling; every policy receives the same observations.
    train_sets=[tuple(sorted(rng.sample(range(n),rng.choice((4,5,6))))) for _ in range(train_count)]
    X=np.vstack([features(s,n,candidates) for s in train_sets]);y=np.array([score(base,strengths,s) for s in train_sets])
    co=fit(X,y,n,candidates)
    cache={}
    for s,v in zip(train_sets,y):cache[s]=float(v)
    # Held-out availability masks, all policies choose 4 of 8; no direct oracle during choice.
    outcomes={p:[] for p in POLICIES};opt=[]
    for _ in range(test_count):
        avail=tuple(sorted(rng.sample(range(n),8)))
        options=list(itertools.combinations(avail,4))
        best=max(score(base,strengths,s) for s in options);opt.append(best)
        for policy in POLICIES:
            if policy=='cache':
                # Prior exact-size observations only; fallback to additive prediction.
                chosen=max(options,key=lambda s:(cache.get(s,policy_value('additive',s,co,n,candidates,cache)),tuple(-i for i in s)))
            else:chosen=max(options,key=lambda s:(policy_value(policy,s,co,n,candidates,cache),tuple(-i for i in s)))
            outcomes[policy].append(score(base,strengths,chosen))
    # Held-out oracle truth known only to evaluator.
    estimated={t:float(v) for t,v in zip(candidates,co[n+1:])}
    true=set(strengths)
    top=set(sorted(candidates,key=lambda t:abs(estimated[t]),reverse=True)[:len(true)]) if true else set()
    # Note: precision@k is not a confirmatory significance test.
    return dict(family=family,n=n,density=density,seed=seed,train_queries=train_count,test_cases=test_count,
                planted=len(true),metadata=len(metadata),largest_component=largest_component(n,metadata),
                precision_at_k=(len(top&true)/len(top) if top else None),
                oracle=statistics.mean(opt),**{p:statistics.mean(v) for p,v in outcomes.items()})

def run(out:Path,sizes=SIZES,densities=DENSITIES,seeds=SEEDS,train_count=TRAIN,test_count=TEST):
    out.mkdir(parents=True,exist_ok=True)
    rows=[one_world(n,d,s,f,train_count,test_count) for f in FAMILIES for n in sizes for d in densities for s in seeds]
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as fp:
        w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    aggregate=[]
    for family in FAMILIES:
        for n in sizes:
            for density in densities:
                rr=[r for r in rows if r['family']==family and r['n']==n and r['density']==density]
                item={'family':family,'n':n,'density':density,'worlds':len(rr)}
                for k in ('largest_component','oracle',*POLICIES):item[k]=statistics.mean(r[k] for r in rr)
                item['interaction_minus_best_simple']=statistics.mean(r['interaction']-max(r['cache'],r['additive'],r['same_estimates_linear']) for r in rr)
                item['precision_at_k']=statistics.mean(r['precision_at_k'] for r in rr if r['precision_at_k'] is not None) if any(r['precision_at_k'] is not None for r in rr) else None
                aggregate.append(item)
    (out/'summary.json').write_text(json.dumps(aggregate,indent=2)+'\n',encoding='utf-8')
    manifest={'schema':'agentic-crystallization-stage-b/1','version':'1.1.0','sizes':list(sizes),'densities':list(densities),'seeds':list(seeds),'families':list(FAMILIES),'policies':list(POLICIES),'train_per_world':train_count,'test_per_world':test_count,'candidate_hyperedges_per_world':'2*n, fixed independent of density','planted_hyperedges':'round(density*n) among first n candidates','interaction_order':3,'selection':'4 from 8 available','estimator':'ridge on identical fixed-budget random training observations; no oracle graph supplied','ridge':RIDGE,'limitations':'Synthetic planted triples; metadata is not a functional dependency; no time-evolving graph, repeated learning cycle, or criticality inference.'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (out/'SHA256SUMS.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'},indent=2)+'\n')
    return rows,aggregate

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path('experiments/stage_b'));ap.add_argument('--seeds',type=int,default=8);ap.add_argument('--train',type=int,default=320);ap.add_argument('--tests',type=int,default=60)
    a=ap.parse_args();rows,agg=run(a.out,seeds=range(a.seeds),train_count=a.train,test_count=a.tests)
    print(json.dumps({'worlds':len(rows),'family_means':{f:{p:round(statistics.mean(r[p] for r in rows if r['family']==f),5) for p in POLICIES} for f in FAMILIES}},indent=2))
if __name__=='__main__':main()
