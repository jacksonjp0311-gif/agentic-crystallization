"""Stage F: frozen conditional candidate probabilities and optional new observation.

No hidden target or relatedness label is available to policies.  Synthetic only.
"""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,math,random,statistics
from pathlib import Path
from . import stage_e

SIZES=stage_e.SIZES
MIXES=stage_e.MIXES
BUDGET=40
TRAIN_SEEDS=range(3000,3400)
VALID_SEEDS=range(5000,5300)
PROBE_AFTER=8
PROBE_ACCURACY=0.80
POLICIES=('no_prior','always_reuse','learned_gate','bayes_static','bayes_online','bayes_no_probe','oracle_context')


def train(seeds=TRAIN_SEEDS):
    """Fit candidate likelihood per overlap stratum, conditional on relatedness.
    All training targets are labeled; evaluation targets remain hidden.
    """
    totals={}; examples={}; related_counts={}
    for n in SIZES:
        for mix in MIXES:
            for seed in seeds:
                w=stage_e.make_world(n,seed,mix)
                k=(n,int(w['related']))
                counts={j:0 for j in range(4)}
                for candidate in w['candidates']:
                    counts[len(set(candidate)&set(w['first']))]+=1
                overlap=len(set(w['target'])&set(w['first']))
                for j,num in counts.items():totals[(n,int(w['related']),j)]=totals.get((n,int(w['related']),j),0)+num
                examples[(n,int(w['related']),overlap)]=examples.get((n,int(w['related']),overlap),0)+1
                related_counts[mix]=related_counts.get(mix,0)+int(w['related'])
    # Conditional probability of a particular candidate, smoothed across overlap strata.
    model={}
    for n in SIZES:
        for rel in (0,1):
            n_worlds=len(seeds)*len(MIXES)
            for k in range(4):
                model[f'{n}:{rel}:{k}']=(examples.get((n,rel,k),0)+0.1)/(totals.get((n,rel,k),0)+0.1*math.comb(n,3))
            # Renormalize over one world's candidate counts at evaluation time.
    return {'likelihood':model,'cue_accuracy':stage_e.CUE_ACCURACY,
            'prior_related':sum(related_counts.values())/(len(seeds)*len(SIZES)*len(MIXES)),
            'train_seeds':[min(seeds),max(seeds)],'probe_accuracy':PROBE_ACCURACY}


def second_cue(world,n,seed,mix):
    rng=random.Random(173909+n*193+seed*1297+int(mix*1000)*97)
    return world['related'] if rng.random()<PROBE_ACCURACY else not world['related']


def search(world,n,policy,model,budget=BUDGET,probe_cue=None,gate=None):
    if policy in ('no_prior','always_reuse','learned_gate','oracle_context'):
        if policy=='learned_gate':
            chosen='always_reuse' if gate[str(world['cue'])]['reuse'] else 'no_prior'
        else:chosen=policy
        found,attempts=stage_e.result(world,chosen,budget)
        return found,attempts,0,chosen
    remaining=list(world['candidates'])
    first=set(world['first'])
    # Training-visible prior, with observed cue likelihood.
    q=model['prior_related']; accuracy=model['cue_accuracy']
    cue=bool(world['cue'])
    q=q*(accuracy if cue else 1-accuracy)/(q*(accuracy if cue else 1-accuracy)+(1-q)*(1-accuracy if cue else accuracy))
    tested=0; probes=0
    # Normalized conditional likelihoods of candidate given R or not R.
    raw={rel:[model['likelihood'][f'{n}:{rel}:{len(set(t)&first)}'] for t in remaining] for rel in (0,1)}
    mass={rel:sum(raw[rel]) for rel in (0,1)}
    like={t:(raw[0][i]/mass[0],raw[1][i]/mass[1]) for i,t in enumerate(remaining)}
    denom0=1.0;denom1=1.0
    tie={t:-i for i,t in enumerate(world['candidates'])}
    while tested+probes<budget and remaining:
        if policy=='bayes_online' and tested==PROBE_AFTER and probes==0 and probe_cue is not None:
            # One new noisy observation costs one unit; no access to ground truth.
            acc=model['probe_accuracy']; likelihood=acc if probe_cue else 1-acc
            q=q*likelihood/(q*likelihood+(1-q)*(1-likelihood));probes=1
        # Failed exact-match tests remove candidates; this updates P(R|failures).
        best=max(remaining,key=lambda t:(q*like[t][1]/denom1+(1-q)*like[t][0]/denom0,tie[t]))
        p0,p1=like[best]
        evidence0=p0/denom0;evidence1=p1/denom1
        remaining.remove(best);tested+=1
        denom0-=p0;denom1-=p1
        if best==world['target']:return 1,tested+probes,probes,'bayes'
        # Bayes update on negative exact-match observation.
        q=q*(1-evidence1)/(q*(1-evidence1)+(1-q)*(1-evidence0))
    return 0,tested+probes,probes,'bayes'


def trial(n,seed,mix,model,gate,budget=BUDGET):
    w=stage_e.make_world(n,seed,mix)
    cue2=second_cue(w,n,seed,mix)
    row={'n':n,'seed':seed,'mix':mix,'related':int(w['related']),'cue':int(w['cue']),
         'probe_cue':int(cue2),'first_cost':w['first_cost'],
         'world_receipt':hashlib.sha256(repr((n,seed,mix,w['first'],w['target'])).encode()).hexdigest()[:24]}
    for policy in POLICIES:
        found,attempts,probes,_=search(w,n,policy,model,budget,cue2,gate)
        row[policy+'_found']=found
        row[policy+'_attempts']=attempts
        row[policy+'_probes']=probes
        row[policy+'_utility']=round(40*found-0.1*(w['first_cost']+attempts),5)
    return row


def run(out,seeds=VALID_SEEDS,model=None,gate=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if model is None:model=train()
    if gate is None:gate=stage_e.train()
    rows=[trial(n,seed,mix,model,gate) for mix in MIXES for n in SIZES for seed in seeds]
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary=[]
    for mix in MIXES:
        rr=[r for r in rows if r['mix']==mix]
        entry={'mix':mix,'worlds':len(rr),'related_fraction':statistics.mean(r['related'] for r in rr)}
        for p in POLICIES:
            entry[p+'_success']=statistics.mean(r[p+'_found'] for r in rr)
            entry[p+'_utility']=statistics.mean(r[p+'_utility'] for r in rr)
            entry[p+'_attempts']=statistics.mean(r[p+'_attempts'] for r in rr)
        for p in ('no_prior','always_reuse','learned_gate','bayes_static','bayes_no_probe'):
            entry['online_minus_'+p]=entry['bayes_online_utility']-entry[p+'_utility']
        summary.append(entry)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'manifest.json').write_text(json.dumps({'schema':'agentic-crystallization-stage-f/1','version':'1.4.0',
        'sizes':SIZES,'mixes':MIXES,'seeds':list(seeds),'train_model':model,'trained_gate':gate,
        'budget':BUDGET,'probe_after':PROBE_AFTER,'probe_accuracy':PROBE_ACCURACY,
        'oracle':'exact triple equality','utility':'40*success - 0.1*(first discovery rank + second search calls + probes)',
        'claim_limit':'planted latent groups; fixed synthetic oracle; no phase transition; no autonomous agent learning'},indent=2)+'\n')
    (out/'SHA256SUMS.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256SUMS.json'},indent=2)+'\n')
    return rows,summary

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path('experiments/stage_f_holdout'));parser.add_argument('--start-seed',type=int,default=5000);parser.add_argument('--count',type=int,default=300)
    args=parser.parse_args();_,summary=run(args.out,seeds=range(args.start_seed,args.start_seed+args.count));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
