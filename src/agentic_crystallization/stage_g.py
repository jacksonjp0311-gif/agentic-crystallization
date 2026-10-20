"""Stage G: exact one-step value-of-information decision on a synthetic triple oracle.

The controller is evaluated against the static and always-probe controls. It does
not see the target, latent family, or second cue until it pays for the probe.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,random,statistics
from pathlib import Path
from . import stage_e,stage_f

VERSION='1.5.0'
SIZES=stage_f.SIZES
MIXES=stage_f.MIXES
BUDGET=40
PROBE_AFTER=8
PROBE_ACCURACY=stage_f.PROBE_ACCURACY
POLICIES=('static','always_probe','voi','no_prior','always_reuse')


def initial(n,world,model):
    first=set(world['first']); candidates=list(world['candidates'])
    raw={r:[model['likelihood'][f'{n}:{r}:{len(set(t)&first)}'] for t in candidates] for r in (0,1)}
    sums={r:sum(raw[r]) for r in (0,1)}
    l0={t:raw[0][i]/sums[0] for i,t in enumerate(candidates)}
    l1={t:raw[1][i]/sums[1] for i,t in enumerate(candidates)}
    q=model['prior_related'];a=model['cue_accuracy'];cue=bool(world['cue'])
    p1=a if cue else 1-a;p0=1-a if cue else a
    q=q*p1/(q*p1+(1-q)*p0)
    return candidates,l0,l1,q


def weights(candidates,l0,l1,q):
    m0=sum(l0[t] for t in candidates);m1=sum(l1[t] for t in candidates)
    if m0<=0 or m1<=0:raise ValueError('Zero conditional candidate mass')
    return {t:(1-q)*l0[t]/m0+q*l1[t]/m1 for t in candidates}


def ordered(candidates,probs,original):
    tie={t:i for i,t in enumerate(original)}
    return sorted(candidates,key=lambda t:(-probs[t],tie[t]))


def continuation_value(order,probs,budget):
    """Exact expected utility of remaining search (not including first-cluster cost).
    Failures consume all available attempts; a successful query ends search.
    """
    if budget<=0:return 0.0
    k=min(budget,len(order));p=sum(probs[t] for t in order[:k])
    expected_calls=sum((i+1)*probs[t] for i,t in enumerate(order[:k]))+k*(1-p)
    return 40*p-.1*expected_calls


def cue_posterior(q,cue,accuracy=PROBE_ACCURACY):
    a=accuracy if cue else 1-accuracy;b=1-accuracy if cue else accuracy
    return q*a/(q*a+(1-q)*b)


def probe_decision(remaining,l0,l1,q,original,budget,probe_cost=1):
    """Compute one-step Bayes VOI; cue outcomes are marginalized before decision."""
    p=weights(remaining,l0,l1,q)
    static_order=ordered(remaining,p,original)
    no=continuation_value(static_order,p,budget)
    if budget<=probe_cost:return False,0.0
    expected=0.0
    for cue in (False,True):
        cue_probability=q*(PROBE_ACCURACY if cue else 1-PROBE_ACCURACY)+(1-q)*(1-PROBE_ACCURACY if cue else PROBE_ACCURACY)
        qc=cue_posterior(q,cue)
        pc=weights(remaining,l0,l1,qc)
        order=ordered(remaining,pc,original)
        expected+=cue_probability*continuation_value(order,pc,budget-probe_cost)
    expected-=.1*probe_cost
    return expected>no+1e-12,expected-no


def run_policy(world,n,model,policy,probe_cue,budget=BUDGET):
    if policy in ('no_prior','always_reuse'):
        found,attempts=stage_e.result(world,policy,budget)
        return int(found),int(attempts),0,False,0.0
    original,l0,l1,q0=initial(n,world,model)
    first_order=ordered(original,weights(original,l0,l1,q0),original)
    first=first_order[:min(PROBE_AFTER,budget)]
    for i,t in enumerate(first):
        if t==world['target']:return 1,i+1,0,False,0.0
    remaining=[t for t in original if t not in set(first)]
    if not remaining:return 0,len(first),0,False,0.0
    mass0=sum(l0[t] for t in remaining);mass1=sum(l1[t] for t in remaining)
    q=q0*mass1/(q0*mass1+(1-q0)*mass0)
    decision=False;voi=0.0;probes=0
    if policy in ('always_probe','voi') and budget>len(first):
        decision,voi=probe_decision(remaining,l0,l1,q,original,budget-len(first))
        if policy=='always_probe':decision=True
        if decision:
            q=cue_posterior(q,bool(probe_cue));probes=1
    remaining_order=ordered(remaining,weights(remaining,l0,l1,q),original)
    available=max(0,budget-len(first)-probes)
    for i,t in enumerate(remaining_order[:available]):
        if t==world['target']:return 1,len(first)+probes+i+1,probes,decision,voi
    return 0,len(first)+probes+min(available,len(remaining_order)),probes,decision,voi


def trial(n,seed,mix,model):
    w=stage_e.make_world(n,seed,mix);cue2=stage_f.second_cue(w,n,seed,mix)
    row={'n':n,'seed':seed,'mix':mix,'related':int(w['related']),'first_cost':w['first_cost'],
         'world_sha256':hashlib.sha256(repr((n,seed,mix,w['first'],w['target'])).encode()).hexdigest()}
    for policy in POLICIES:
        found,attempts,probes,decision,voi=run_policy(w,n,model,policy,cue2)
        row.update({policy+'_found':found,policy+'_attempts':attempts,policy+'_probes':probes,
                    policy+'_utility':round(40*found-.1*(w['first_cost']+attempts),6)})
        if policy=='voi':row['voi_estimate']=round(voi,8);row['voi_decision']=int(decision)
    return row


def run(out,seeds=range(8000,8200),model=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if model is None:model=stage_f.train()
    rows=[trial(n,s,m,model) for m in MIXES for n in SIZES for s in seeds]
    with (out/'runs.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    summary=[]
    for mix in MIXES:
        rr=[r for r in rows if r['mix']==mix]
        entry={'mix':mix,'worlds':len(rr),'probe_rate':statistics.mean(r['voi_probes'] for r in rr)}
        for policy in POLICIES:
            entry[policy+'_success']=statistics.mean(r[policy+'_found'] for r in rr)
            entry[policy+'_utility']=statistics.mean(r[policy+'_utility'] for r in rr)
            entry[policy+'_attempts']=statistics.mean(r[policy+'_attempts'] for r in rr)
        for policy in ('static','always_probe','no_prior','always_reuse'):
            entry['voi_minus_'+policy]=entry['voi_utility']-entry[policy+'_utility']
        summary.append(entry)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    manifest={'schema':'agentic-crystallization-stage-g/1','version':VERSION,'sizes':SIZES,'mixes':MIXES,'seeds':list(seeds),
              'budget':BUDGET,'probe_after':PROBE_AFTER,'probe_accuracy':PROBE_ACCURACY,'model':model,
              'policy':'one-step conditional expected net utility of a paid cue; no hidden relatedness or target input',
              'utility':'40*found - 0.1*(first discovery cost + second attempts including paid cue)',
              'limits':'synthetic planted families; no real model, autonomous procedure creation, or phase transition'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'SHA256SUMS.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256SUMS.json'},indent=2)+'\n')
    return rows,summary


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path('experiments/stage_g_holdout'));p.add_argument('--start-seed',type=int,default=8000);p.add_argument('--count',type=int,default=200)
    a=p.parse_args();_,summary=run(a.out,range(a.start_seed,a.start_seed+a.count));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
