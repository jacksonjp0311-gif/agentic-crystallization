"""Stage H: train-only robust probe margin, frozen synthetic validation.

No hidden target or relatedness available to policies. Explicit counterexample
under distribution shift; no claims of physical criticality.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,statistics,random
from pathlib import Path
from . import stage_e,stage_f,stage_g

VERSION='1.6.0'
MARGINS=(0.0,0.1,0.5,1.0,2.0,4.0)
POLICIES=('static','always_probe','voi','margin','no_prior')

def margin_policy(world,n,model,cue,margin,budget=40):
    original,l0,l1,q=stage_g.initial(n,world,model)
    initial=stage_g.ordered(original,stage_g.weights(original,l0,l1,q),original)
    first=initial[:min(8,budget)]
    for i,t in enumerate(first):
        if t==world['target']:return 1,i+1,0,0.0
    remaining=[t for t in original if t not in set(first)]
    if not remaining:return 0,len(first),0,0.0
    mass0=sum(l0[t] for t in remaining);mass1=sum(l1[t] for t in remaining)
    q=q*mass1/(q*mass1+(1-q)*mass0)
    _,voi=stage_g.probe_decision(remaining,l0,l1,q,original,budget-len(first))
    probe=int(voi>margin+1e-12)
    if probe:q=stage_g.cue_posterior(q,bool(cue))
    rank=stage_g.ordered(remaining,stage_g.weights(remaining,l0,l1,q),original)
    left=max(0,budget-len(first)-probe)
    for i,t in enumerate(rank[:left]):
        if t==world['target']:return 1,len(first)+probe+i+1,probe,voi
    return 0,len(first)+probe+min(left,len(rank)),probe,voi

def utility(world,result):
    found,attempts=result[:2]
    return 40*found-.1*(world['first_cost']+attempts)

def tune(model,seeds=range(9000,9060)):
    # Pool both mixtures. The deployment policy does not know the test mixture.
    totals={m:[] for m in MARGINS}
    for mix in stage_f.MIXES:
        for n in stage_f.SIZES:
            for seed in seeds:
                world=stage_e.make_world(n,seed,mix)
                cue=stage_f.second_cue(world,n,seed,mix)
                for margin in MARGINS:
                    totals[margin].append(utility(world,margin_policy(world,n,model,cue,margin)))
    scores={str(m):statistics.mean(v) for m,v in totals.items()}
    # Conservative tie-break: choose larger margin, meaning fewer speculative probes.
    winner=max(MARGINS,key=lambda m:(scores[str(m)],m))
    return winner,scores

def trial(n,seed,mix,model,margin):
    world=stage_e.make_world(n,seed,mix)
    cue=stage_f.second_cue(world,n,seed,mix)
    row={'n':n,'seed':seed,'mix':mix,'related':int(world['related']),
         'world_sha256':hashlib.sha256(repr((n,seed,mix,world['first'],world['target'])).encode()).hexdigest(),
         'first_cost':world['first_cost']}
    for p in POLICIES:
        if p=='margin':found,attempts,probes,voi=margin_policy(world,n,model,cue,margin)
        else:
            found,attempts,probes,decision,voi=stage_g.run_policy(world,n,model,p,cue)
        row[p+'_found']=found;row[p+'_attempts']=attempts;row[p+'_probes']=probes
        row[p+'_utility']=round(40*found-.1*(world['first_cost']+attempts),6)
    return row

def run(out,seeds=range(10000,10120),train_seeds=range(9000,9060),model=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if model is None:model=stage_f.train()
    margin,scores=tune(model,train_seeds)
    rows=[trial(n,seed,mix,model,margin) for mix in stage_f.MIXES for n in stage_f.SIZES for seed in seeds]
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary=[]
    for mix in stage_f.MIXES:
        sub=[r for r in rows if r['mix']==mix]
        record={'mix':mix,'worlds':len(sub),'selected_margin':margin}
        for p in POLICIES:
            record[p+'_utility']=statistics.mean(r[p+'_utility'] for r in sub)
            record[p+'_success']=statistics.mean(r[p+'_found'] for r in sub)
            record[p+'_probe_rate']=statistics.mean(r[p+'_probes'] for r in sub)
        for p in ('static','always_probe','voi','no_prior'):
            record['margin_minus_'+p]=record['margin_utility']-record[p+'_utility']
        summary.append(record)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'manifest.json').write_text(json.dumps({'schema':'agentic-crystallization-stage-h/1','version':VERSION,
       'training_seeds':list(train_seeds),'holdout_seeds':list(seeds),'sizes':stage_f.SIZES,
       'mixes':stage_f.MIXES,'margins':MARGINS,'selected_margin':margin,'training_scores':scores,
       'model_train_seeds':model['train_seeds'],'budget':40,'probe_after':8,
       'utility':'40*found - 0.1*(first discovery cost + second attempts including probe)',
       'limitation':'synthetic latent families; one trained scalar margin; no physical criticality or real agent learning'},indent=2)+'\n')
    (out/'SHA256SUMS.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256SUMS.json'},indent=2)+'\n')
    return rows,summary

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path('experiments/stage_h_holdout'))
    parser.add_argument('--start-seed',type=int,default=10000);parser.add_argument('--count',type=int,default=120)
    args=parser.parse_args();_,summary=run(args.out,range(args.start_seed,args.start_seed+args.count));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
