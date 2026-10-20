"""Stage D: synthetic learning-to-learn transfer, with a declared latent-family prior.

Not an agent/model experiment. An oracle identifies an exact triple when queried.
No procedure graph changes; the experiment tests a prior-induced search advantage.
"""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,random,statistics
from pathlib import Path

SIZES=(12,15,18)
SEEDS=tuple(range(200))
CONDITIONS=('related','unrelated')
POLICIES=('no_prior','cache_only','cluster_prior','sham_prior','ablated_prior','restored_prior')
BUDGET=40
GROUP=6

def world(n,seed,condition):
    if n<2*GROUP:raise ValueError('Need at least 12 procedures')
    rng=random.Random(190001+seed*431+n*991)
    pool=list(range(n));rng.shuffle(pool)
    a=frozenset(pool[:GROUP]);b=frozenset(pool[GROUP:2*GROUP])
    first=tuple(sorted(rng.sample(sorted(a),3)))
    target_pool=sorted(itertools.combinations(sorted(a if condition=='related' else b),3))
    second=rng.choice([t for t in target_pool if t!=first])
    # Same randomized base candidate ordering for every policy.
    candidates=list(itertools.combinations(range(n),3));rng.shuffle(candidates)
    sham=tuple(sorted(rng.sample(range(n),3)))  # unrelated random placebo, no access to target
    return first,second,candidates,sham

def order(policy,first,sham,candidates):
    if policy in ('no_prior','ablated_prior'):return list(candidates)
    if policy=='cache_only':return [first]+[c for c in candidates if c!=first]
    prior=sham if policy=='sham_prior' else first
    return sorted(candidates,key=lambda c:-len(set(c)&set(prior)))

def trial(n,seed,condition,budget=BUDGET):
    first,target,candidates,sham=world(n,seed,condition)
    result={'n':n,'seed':seed,'condition':condition,'budget':budget,
            'first_receipt':hashlib.sha256(str(first).encode()).hexdigest()[:16],
            'target_receipt':hashlib.sha256(str(target).encode()).hexdigest()[:16]}
    for policy in POLICIES:
        rank=order(policy,first,sham,candidates).index(target)+1
        found=rank<=budget
        result[policy+'_found']=int(found)
        result[policy+'_restricted_attempts']=min(rank,budget)
        result[policy+'_uncensored_attempts']=rank if found else ''
    return result

def run(out,sizes=SIZES,seeds=SEEDS,budget=BUDGET):
    if not isinstance(budget,int) or budget<1:raise ValueError('budget must be positive')
    out.mkdir(parents=True,exist_ok=True)
    rows=[trial(n,s,c,budget) for c in CONDITIONS for n in sizes for s in seeds]
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    summary=[]
    for condition in CONDITIONS:
        for n in sizes:
            rr=[r for r in rows if r['condition']==condition and r['n']==n]
            d={'condition':condition,'n':n,'worlds':len(rr),'budget':budget}
            for p in POLICIES:
                d[p+'_success']=statistics.mean(r[p+'_found'] for r in rr)
                d[p+'_restricted_attempts']=statistics.mean(r[p+'_restricted_attempts'] for r in rr)
            d['cluster_minus_no_prior_success']=d['cluster_prior_success']-d['no_prior_success']
            d['cluster_minus_sham_success']=d['cluster_prior_success']-d['sham_prior_success']
            d['restricted_attempts_saved']=d['no_prior_restricted_attempts']-d['cluster_prior_restricted_attempts']
            summary.append(d)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    manifest={'schema':'agentic-crystallization-stage-d/1','version':'1.2.0','sizes':list(sizes),'seeds':list(seeds),'conditions':list(CONDITIONS),'policies':list(POLICIES),'budget':budget,'latent_group_size':GROUP,'oracle':'Exact triple equality; each query consumes one attempt; success validated by deterministic oracle','transfer_mechanism':'First task triple and second task triple sampled from same six-node latent group in related condition; disjoint six-node group in unrelated condition. No family label or second target revealed to policy.','cost':'Number of oracle queries, capped by budget; misses right-censored at budget','analysis':'Success rate and restricted attempts; paired worlds; descriptive exploratory results only','limitations':'Planted latent grouping, deterministic oracle, static candidate catalog, no learning from failed second-task queries, no real agent, no criticality or autonomous procedure invention.'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (out/'SHA256SUMS.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256SUMS.json'},indent=2)+'\n')
    return rows,summary

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path('experiments/stage_d'));parser.add_argument('--seeds',type=int,default=200);parser.add_argument('--budget',type=int,default=BUDGET)
    args=parser.parse_args();_,s=run(args.out,seeds=range(args.seeds),budget=args.budget)
    print(json.dumps(s,indent=2))
if __name__=='__main__':main()
