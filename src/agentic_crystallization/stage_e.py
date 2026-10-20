"""Stage E: learned conditional reuse under observable noisy task similarity.

Synthetic exact-match oracle, not a model or a demonstrated phase transition.
Train and test worlds are disjoint. First procedure discovery cost is charged.
"""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,random,statistics
from pathlib import Path
from .stage_d import GROUP, order

SIZES=(12,15,18)
MIXES=(0.25,0.75)
BUDGET=40
CUE_ACCURACY=0.8
POLICIES=('no_prior','cache_only','always_reuse','learned_gate','sham_prior','oracle_context')

def make_world(n,seed,mix):
    if n < 2*GROUP: raise ValueError('catalog too small')
    rng=random.Random(812341+n*13007+seed*983+int(mix*1000)*319)
    pool=list(range(n));rng.shuffle(pool)
    a=sorted(pool[:GROUP]);b=sorted(pool[GROUP:2*GROUP])
    first=tuple(sorted(rng.sample(a,3)))
    related=rng.random()<mix
    candidates_a=list(itertools.combinations(a,3))
    candidates_b=list(itertools.combinations(b,3))
    target=rng.choice([t for t in (candidates_a if related else candidates_b) if t!=first])
    cue=related if rng.random()<CUE_ACCURACY else not related
    all_candidates=list(itertools.combinations(range(n),3));rng.shuffle(all_candidates)
    # This is a fully observed prior validation cost, not a free oracle-given prior.
    first_cost=all_candidates.index(first)+1
    sham=tuple(sorted(rng.sample(range(n),3)))
    return {'first':first,'target':target,'related':related,'cue':cue,
            'candidates':all_candidates,'first_cost':first_cost,'sham':sham}

def result(world,policy,budget=BUDGET):
    if policy=='learned_gate':raise ValueError('gate needs frozen decision')
    if policy=='oracle_context': policy='always_reuse' if world['related'] else 'no_prior'
    method={'always_reuse':'cluster_prior','no_prior':'no_prior','cache_only':'cache_only','sham_prior':'sham_prior'}[policy]
    ranking=order(method,world['first'],world['sham'],world['candidates'])
    rank=ranking.index(world['target'])+1
    return int(rank<=budget),min(rank,budget)

def train(seeds=range(1000,1300),sizes=SIZES,mixes=MIXES,budget=BUDGET):
    # Each cue has its own empirical expected *utility* difference, on training only.
    values={str(c):[] for c in (False,True)}
    for mix in mixes:
        for n in sizes:
            for seed in seeds:
                w=make_world(n,seed,mix)
                base=result(w,'no_prior',budget)
                reuse=result(w,'always_reuse',budget)
                # One success is worth 40 query units; every query costs 0.1 unit.
                u=lambda r:40*r[0]-0.1*r[1]
                values[str(w['cue'])].append(u(reuse)-u(base))
    return {key:{'count':len(v),'estimated_delta_utility':statistics.mean(v),
                 'reuse':statistics.mean(v)>0} for key,v in values.items()}

def trial(n,seed,mix,gate,budget=BUDGET):
    w=make_world(n,seed,mix)
    row={'n':n,'seed':seed,'mix':mix,'related':int(w['related']),'cue':int(w['cue']),
         'first_discovery_attempts':w['first_cost'],
         'first_receipt':hashlib.sha256(str(w['first']).encode()).hexdigest()[:16],
         'target_receipt':hashlib.sha256(str(w['target']).encode()).hexdigest()[:16]}
    for p in POLICIES:
        if p=='learned_gate':
            actual='always_reuse' if gate[str(w['cue'])]['reuse'] else 'no_prior'
            row['gate_action']=actual
        else:actual=p
        found,used=result(w,actual,budget)
        row[p+'_found']=found
        row[p+'_restricted_attempts']=used
        row[p+'_total_attempts']=used+w['first_cost']
        row[p+'_utility']=round(40*found-0.1*(used+w['first_cost']),5)
    return row

def run(out,seeds=range(2000,2300),gate=None,sizes=SIZES,mixes=MIXES,budget=BUDGET):
    if gate is None:gate=train()
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[trial(n,seed,mix,gate,budget) for mix in mixes for n in sizes for seed in seeds]
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summaries=[]
    for mix in mixes:
        for n in sizes:
            subset=[r for r in rows if r['mix']==mix and r['n']==n]
            d={'mix':mix,'n':n,'worlds':len(subset),'related_fraction':statistics.mean(r['related'] for r in subset),
               'first_discovery_attempts':statistics.mean(r['first_discovery_attempts'] for r in subset)}
            for p in POLICIES:
                d[p+'_success']=statistics.mean(r[p+'_found'] for r in subset)
                d[p+'_utility']=statistics.mean(r[p+'_utility'] for r in subset)
                d[p+'_restricted_attempts']=statistics.mean(r[p+'_restricted_attempts'] for r in subset)
            d['gate_minus_no_prior_utility']=d['learned_gate_utility']-d['no_prior_utility']
            d['gate_minus_always_reuse_utility']=d['learned_gate_utility']-d['always_reuse_utility']
            summaries.append(d)
    (out/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
    manifest={'schema':'agentic-crystallization-stage-e/1','version':'1.3.0','seeds':list(seeds),'sizes':list(sizes),
        'mixes':list(mixes),'budget':budget,'cue_accuracy':CUE_ACCURACY,'training_seeds':list(range(1000,1300)),
        'gate':gate,'oracle':'exact triple equality','first_cost':'full shuffled rank of first validated triple, included in every arm',
        'evaluation':'40*success - 0.1*(first discovery queries + restricted second discovery queries)',
        'limitations':'no model; planted latent groups and noisy cue; fixed ordering without posterior updates; exact-match oracle; no threshold test; validation not preregistered before model design'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'SHA256SUMS.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256SUMS.json'},indent=2)+'\n')
    return rows,summaries

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path('experiments/stage_e_holdout'));parser.add_argument('--start-seed',type=int,default=2000);parser.add_argument('--count',type=int,default=300)
    args=parser.parse_args();_,summary=run(args.out,seeds=range(args.start_seed,args.start_seed+args.count));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
