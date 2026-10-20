"""Stage O: feedback-integrity experiments, fresh anchors, and common-mode failure.

All policies share the same synthetic world and independently seeded observations.
Hidden true gains are used exclusively after policy decisions to score results.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,random
from dataclasses import asdict,replace
from pathlib import Path
from statistics import mean
import numpy as np
from .feedback_integrity import (IntegrityConfig,IntegrityState,POLICIES,decide,
                                 cue_calibration)
from . import stage_n

REGIMES=('stationary','abrupt','gradual','recurrent','deceptive_primary',
         'misleading_cue','missing_anchor','deceptive_anchor','common_mode','unlearnable')


def seed_from(*parts)->int:
    return int.from_bytes(hashlib.sha256('|'.join(map(str,parts)).encode()).digest()[:8],'big')


def base_regime(regime:str)->str:
    if regime not in REGIMES:raise ValueError('unknown environment')
    if regime in ('deceptive_primary','deceptive_anchor','common_mode','missing_anchor'):
        return 'abrupt'
    if regime=='misleading_cue':return 'misleading_cue'
    return regime


def calibrate(start_seed:int=1000,n_per_class:int=3000)->dict:
    """Independent balanced labeled cue calibration, frozen before evaluation.

    The generated changed/stable labels are for training only; deployed policy
    receives a cue, never the hidden change label.
    """
    if n_per_class<1:raise ValueError('empty calibration')
    rows=[]
    for changed in (False,True):
        for s in range(start_seed,start_seed+n_per_class):
            u=random.Random(seed_from('calibration',s,changed)).random()
            cue=u<(.85 if changed else .10)
            rows.append((changed,cue))
    result=cue_calibration(rows)
    result.update({'start_seed':start_seed,'n_per_class':n_per_class,
                   'training_mechanism':'0.85 sensitivity, 0.90 specificity; balanced labeled independent samples',
                   'not_estimated':'deployment hazard and post-calibration channel drift'})
    return result


def world_observations(seed:int,regime:str,t:int,cfg:IntegrityConfig)->dict:
    base=base_regime(regime)
    true=stage_n.truth_at(base,t)
    if regime=='misleading_cue':cue=stage_n.warning(seed,'misleading_cue',t,
        stage_n.Config(epochs=cfg.epochs,sensitivity=.85,specificity=.90))
    else:cue=stage_n.warning(seed,base,t,
        stage_n.Config(epochs=cfg.epochs,sensitivity=.85,specificity=.90))
    means={}
    for channel,n in (('primary',cfg.primary_samples),('anchor',cfg.anchor_samples)):
        if channel=='anchor' and regime=='missing_anchor' and t>=8:
            means[channel]=None;continue
        estimates={}
        for action in ('A','B'):
            mu=true[action]
            if t>=8 and ((channel=='primary' and regime in ('deceptive_primary','common_mode')) or
                         (channel=='anchor' and regime in ('deceptive_anchor','common_mode'))):
                mu=-mu
            generator=np.random.default_rng(seed_from('stage_o',seed,regime,t,channel,action))
            count=int(generator.binomial(n,(1+mu)/2))
            estimates[action]=2*count/n-1
        means[channel]=estimates
    return {'truth':true,'cue':cue,**means}


def run_world(seed:int,regime:str,cfg:IntegrityConfig)->list[dict]:
    if regime not in REGIMES:raise ValueError('invalid regime')
    states={p:IntegrityState() for p in POLICIES}
    rows=[]
    for t in range(cfg.epochs):
        observed=world_observations(seed,regime,t,cfg)
        # The oracle truth is NOT an input to decide.
        for policy in POLICIES:
            event,states[policy]=decide(policy,t,states[policy],observed['cue'],
                                         observed['primary'],observed['anchor'],cfg)
            actual_gain=observed['truth'].get(event['selected'],0.)
            rows.append({'seed':seed,'regime':regime,'epoch':t,'policy':policy,
                         'cue':observed['cue'],**event,
                         'true_gain':round(actual_gain,8),
                         'harmful':int(actual_gain<0),
                         'false_certificate':int(event['fresh_certificate'] and actual_gain<=0),
                         'utility':round(cfg.tasks_per_epoch*actual_gain-event['audit_cost'],8)})
    return rows


def summarize(rows:list[dict])->dict:
    out={}
    for regime in REGIMES:
        out[regime]={}
        for policy in POLICIES:
            subset=[r for r in rows if r['regime']==regime and r['policy']==policy]
            if not subset:continue
            out[regime][policy]={
                'worlds':len({r['seed'] for r in subset}),
                'epochs':len(subset),
                'mean_utility':round(mean(r['utility'] for r in subset),5),
                'mean_gain':round(mean(r['true_gain'] for r in subset),5),
                'primary_audits':sum(r['primary_audit'] for r in subset),
                'anchor_audits':sum(r['anchor_audit'] for r in subset),
                'disagreement_alarms':sum(r['disagreement_alarm'] for r in subset),
                'false_certificates':sum(r['false_certificate'] for r in subset),
                'harmful_deployments':sum(r['harmful'] for r in subset),
                'holds':sum(r['held'] for r in subset),
                'stale_deployments':sum(r['stale_deployment'] for r in subset),
                'total_audit_cost':round(sum(r['audit_cost'] for r in subset),4)}
    return out


def run(out,start_seed=5000,count=100,cfg:IntegrityConfig|None=None)->dict:
    if count<1:raise ValueError('empty cohort')
    calibration=calibrate()
    cfg=cfg or replace(IntegrityConfig(),
        sensitivity=calibration['bounds']['sensitivity']['estimate'],
        specificity=calibration['bounds']['specificity']['estimate'])
    out=Path(out)
    if out.exists() and any(out.iterdir()):raise FileExistsError('Refuse to overwrite an existing experiment')
    out.mkdir(parents=True,exist_ok=True)
    rows=[row for regime in REGIMES for seed in range(start_seed,start_seed+count)
          for row in run_world(seed,regime,cfg)]
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
    summary=summarize(rows)
    (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    (out/'calibration.json').write_text(json.dumps(calibration,indent=2,sort_keys=True)+'\n')
    src=Path(__file__).resolve().parent
    names=('stage_o.py','feedback_integrity.py','stage_n.py','risk_verification.py')
    hashes={name:hashlib.sha256((src/name).read_bytes()).hexdigest() for name in names}
    protocol={'stage':'O','version':'2.3.0','start_seed':start_seed,'count':count,
              'worlds':count*len(REGIMES),'rows':len(rows),'epochs':cfg.epochs,
              'regimes':REGIMES,'policies':POLICIES,'config':asdict(cfg),
              'source_hashes':hashes,'calibration':'balanced labeled independent training seeds 1000-3999',
              'decision_inputs':'cue, observed primary/anchor sample means, anchor availability, time and policy state',
              'oracle':'hidden true gain used for scoring only after policy decision',
              'bound':'Simultaneous current-epoch Hoeffding only if relevant channel is honest iid; no future-environment guarantee',
              'costs':'primary and anchor sample costs charged only on actual audit'}
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2,sort_keys=True)+'\n')
    checks={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
    (out/'SHA256SUMS.json').write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',required=True)
    p.add_argument('--start-seed',type=int,default=5000)
    p.add_argument('--count',type=int,default=100)
    args=p.parse_args()
    results=run(args.out,args.start_seed,args.count)
    print(json.dumps({regime:{policy:results[regime][policy]['mean_utility'] for policy in POLICIES}
                      for regime in REGIMES},indent=2))

if __name__=='__main__':main()
