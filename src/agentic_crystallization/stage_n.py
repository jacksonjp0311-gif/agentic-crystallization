"""Stage N: matched synthetic risk-adaptive verification experiment.

True gains never enter the policy; warnings and audit samples may be misleading.
"""
import argparse,csv,hashlib,json,random
from pathlib import Path
from statistics import mean
from .risk_verification import Config,State,POLICIES,choose

REGIMES=('stationary','abrupt','unannounced_abrupt','gradual','recurrent',
         'missing_cue','misleading_cue','deceptive_audit','unlearnable')

def rng(*parts):
    seed=int.from_bytes(hashlib.sha256('|'.join(map(str,parts)).encode()).digest()[:8],'big')
    return random.Random(seed)

def truth_at(regime,t):
    if regime=='unlearnable':return {'A':0.,'B':0.}
    if regime=='gradual':
        mix=max(0.,min(1.,(t-6)/12))
        a=.35*(1-2*mix)
    elif regime=='recurrent':a=.35 if (t//6)%2==0 else -.35
    elif regime in ('abrupt','unannounced_abrupt','missing_cue','misleading_cue','deceptive_audit'):
        a=.35 if t<8 else -.35
    else:a=.35
    return {'A':a,'B':-a}

def warning(seed,regime,t,cfg):
    if regime=='missing_cue':return None
    current=truth_at(regime,t)['A'];previous=truth_at(regime,t-1)['A'] if t else current
    changed=current*previous<0 or (regime=='gradual' and abs(current-previous)>.05)
    sens=.05 if regime in ('unannounced_abrupt','misleading_cue') else cfg.sensitivity
    spec=.05 if regime=='misleading_cue' else cfg.specificity
    return rng('cue',seed,regime,t).random()<(sens if changed else 1-spec)

def audit_means(seed,regime,t,cfg):
    truth=truth_at(regime,t)
    means={}
    for action in ('A','B'):
        mu=truth[action]
        if regime=='deceptive_audit' and t>=8:mu=-mu
        gen=rng('audit',seed,regime,t,action)
        hits=sum(gen.random()<(1+mu)/2 for _ in range(cfg.samples))
        means[action]=2*hits/cfg.samples-1
    return means

def run_world(seed,regime,cfg):
    if regime not in REGIMES:raise ValueError('invalid regime')
    states={p:State() for p in POLICIES};rows=[]
    for t in range(cfg.epochs):
        truth=truth_at(regime,t);cue=warning(seed,regime,t,cfg)
        means=audit_means(seed,regime,t,cfg)
        for policy in POLICIES:
            event,states[policy]=choose(policy,t,states[policy],cue,means,cfg)
            gain=truth.get(event['selected'],0.)
            rows.append({'seed':seed,'regime':regime,**event,'gain':round(gain,8),
                         'harmful':int(gain<0),'utility':round(cfg.tasks_per_epoch*gain-event['audit_cost'],8)})
    return rows

def summarize(rows):
    out={}
    for regime in REGIMES:
        out[regime]={}
        for policy in POLICIES:
            rr=[r for r in rows if r['regime']==regime and r['policy']==policy]
            if not rr:continue
            out[regime][policy]={'worlds':len({r['seed'] for r in rr}),'epochs':len(rr),
              'mean_utility':round(mean(r['utility'] for r in rr),5),
              'audits':sum(r['audit'] for r in rr),'fresh_certifications':sum(r['fresh_cert'] for r in rr),
              'stale_deployments':sum(r['stale_deployment'] for r in rr),
              'harmful_deployments':sum(r['harmful'] for r in rr),
              'holds':sum(r['held'] for r in rr),
              'total_audit_cost':round(sum(r['audit_cost'] for r in rr),4)}
    return out

def run(out,start_seed=5000,count=60,cfg=None):
    cfg=cfg or Config();out=Path(out)
    if out.exists() and any(out.iterdir()):raise FileExistsError('Refuse experiment overwrite')
    out.mkdir(parents=True,exist_ok=True)
    rows=[r for regime in REGIMES for seed in range(start_seed,start_seed+count)
          for r in run_world(seed,regime,cfg)]
    with (out/'runs.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    summary=summarize(rows)
    (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    src=Path(__file__).resolve().parent
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (src/'stage_n.py',src/'risk_verification.py')}
    protocol={'stage':'N','version':'2.2','start_seed':start_seed,'count':count,
              'worlds':count*len(REGIMES),'rows':len(rows),'epochs':cfg.epochs,
              'policies':POLICIES,'regimes':REGIMES,'config':vars(cfg),'source_hashes':hashes,
              'guarantee':'Simultaneous current-epoch certification only under honest iid audit samples; stale reuse has no guarantee',
              'warning_model':'Fixed hazard/sensitivity/specificity assumed; not calibrated on these worlds',
              'oracle':'Hidden true gains used only for scoring, never for decision'}
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2,sort_keys=True)+'\n')
    checks={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    (out/'SHA256SUMS.json').write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--start-seed',type=int,default=5000)
    p.add_argument('--count',type=int,default=60);args=p.parse_args()
    result=run(Path(args.out),args.start_seed,args.count)
    print(json.dumps({r:{p:result[r][p]['mean_utility'] for p in POLICIES} for r in REGIMES},indent=2))
if __name__=='__main__':main()
