"""Stage P: independent audit reference, feedback reliability, tuning and falsification.

True outcomes are used only for final scoring, never in the policy's call.
A direct reference audit is *modeled* as an independent outcome experiment. Its
provenance and correctness cannot be established from agreement alone.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from dataclasses import asdict,replace
from pathlib import Path
from statistics import mean
import numpy as np
from . import stage_n,stage_o
from .adaptive_trust import TrustConfig,TrustState,POLICIES,decide,request_reference

REGIMES = ('stationary','abrupt','gradual','recurrent','deceptive_primary',
           'deceptive_anchor','common_mode','reference_corrupt','all_corrupt',
           'missing_reference','missing_anchor','misleading_cue','unlearnable')


def base_regime(regime):
    if regime not in REGIMES:raise ValueError('Unknown regime')
    if regime=='all_corrupt':return 'common_mode'
    if regime in ('reference_corrupt','missing_reference','missing_anchor'):return 'abrupt'
    return regime


def reference_means(seed:int,regime:str,t:int,cfg:TrustConfig,truth:dict)->dict|None:
    if regime=='missing_reference' and t>=8:return None
    out={}
    for action in ('A','B'):
        mu=truth[action]
        if regime in ('reference_corrupt','all_corrupt') and t>=8:mu=-mu
        rng=np.random.default_rng(stage_o.seed_from('stage_p_reference',seed,regime,t,action))
        hits=int(rng.binomial(cfg.reference_samples,(1+mu)/2))
        out[action]=2*hits/cfg.reference_samples-1
    return out


def world_observations(seed:int,regime:str,t:int,cfg:TrustConfig)->dict:
    old_cfg=stage_o.IntegrityConfig(epochs=cfg.epochs,primary_samples=cfg.primary_samples,
        anchor_samples=cfg.anchor_samples,alpha=cfg.alpha)
    prior=stage_o.world_observations(seed,base_regime(regime),t,old_cfg)
    # Truth is segregated for post-decision scoring only.
    independent=reference_means(seed,regime,t,cfg,prior['truth'])
    if regime=='missing_anchor' and t>=8:prior['anchor']=None
    return {**prior,'reference':independent}


def run_world(seed:int,regime:str,cfg:TrustConfig)->list[dict]:
    if regime not in REGIMES:raise ValueError('Unknown regime')
    states={policy:TrustState() for policy in POLICIES}
    rows=[]
    for t in range(cfg.epochs):
        evidence=world_observations(seed,regime,t,cfg)
        for policy in POLICIES:
            buy_reference,_=request_reference(policy,t,states[policy],evidence['cue'],cfg)
            purchased=evidence['reference'] if buy_reference else None
            event,states[policy]=decide(policy,t,states[policy],evidence['cue'],
               evidence['primary'],evidence['anchor'],purchased,cfg)
            # Hidden truth is accessed *after* decide returns; no policy gets it.
            gain=evidence['truth'].get(event['selected'],0.)
            rows.append({'seed':seed,'regime':regime,'epoch':t,'policy':policy,
                         'cue':evidence['cue'],**event,'true_gain':round(gain,8),
                         'harmful':int(gain<0),
                         'false_fresh_certificate':int(event['fresh'] and gain<=0),
                         'utility':round(cfg.tasks_per_epoch*gain-event['audit_cost'],8)})
    return rows


def summarize(rows:list[dict])->dict:
    out={}
    for regime in REGIMES:
        out[regime]={}
        for policy in POLICIES:
            rr=[r for r in rows if r['regime']==regime and r['policy']==policy]
            if not rr:continue
            out[regime][policy]={'worlds':len({r['seed'] for r in rr}), 'epochs':len(rr),
                'mean_utility':round(mean(r['utility'] for r in rr),5),
                'false_fresh_certificates':sum(r['false_fresh_certificate'] for r in rr),
                'harmful_deployments':sum(r['harmful'] for r in rr),
                'fresh_certificates':sum(r['fresh'] for r in rr),
                'stale_deployments':sum(r['stale'] for r in rr),
                'holds':sum(r['held'] for r in rr),
                'reference_audits':sum(r['reference_audit'] for r in rr),
                'integrity_alarms':sum(r['integrity_alarm'] for r in rr),
                'total_audit_cost':round(sum(r['audit_cost'] for r in rr),4)}
    return out


def code_hashes():
    src=Path(__file__).resolve().parent
    names=('stage_p.py','adaptive_trust.py','stage_o.py','feedback_integrity.py','stage_n.py','risk_verification.py')
    return {name:hashlib.sha256((src/name).read_bytes()).hexdigest() for name in names}


def run(out,start_seed:int=8000,count:int=60,cfg:TrustConfig|None=None)->dict:
    if count<1:raise ValueError('Empty cohort')
    cfg=cfg or TrustConfig()
    out=Path(out)
    if out.exists() and any(out.iterdir()):raise FileExistsError('Refuse to overwrite existing experiment')
    out.mkdir(parents=True,exist_ok=True)
    rows=[row for regime in REGIMES for seed in range(start_seed,start_seed+count)
          for row in run_world(seed,regime,cfg)]
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=sorted({k for r in rows for k in r}),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
    summary=summarize(rows)
    (out/'summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
    protocol={'version':'2.4.0','stage':'P','start_seed':start_seed,'count':count,
              'worlds':count*len(REGIMES),'rows':len(rows),'regimes':REGIMES,'policies':POLICIES,
              'config':asdict(cfg),'source_hashes':code_hashes(),
              'decision_inputs':'Observed primary, anchor, reference means only when purchased; cue, epoch, retained state; never true gains',
              'sample_model':'Independent bounded randomized measurements conditional on the true synthetic world when channels are honest; reference independent draws',
              'honesty_boundary':'A truthful reference is assumed, not proven; all-channel corruption is observationally indistinguishable from some honest world',
              'statistic':'finite-horizon simultaneous Hoeffding interval if channel honest; descriptive Beta(1,1) mismatch mean not calibrated trust',
              'utility':'80*true current gain minus incurred observation costs; hidden oracle is scoring only',
              'task':'Two whitelisted A/B procedures; no real LLM or Pegasus execution'}
    (out/'protocol.json').write_text(json.dumps(protocol,sort_keys=True,indent=2)+'\n')
    sha={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
    (out/'SHA256SUMS.json').write_text(json.dumps(sha,sort_keys=True,indent=2)+'\n')
    return summary


def tune(out,seed_start=4200,count=16):
    """Finite, development-only parameter sweep. Never inspect holdout to tune."""
    if count<1:raise ValueError('Empty development sweep')
    out=Path(out)
    if out.exists():raise FileExistsError('Refuse overwrite of development search')
    out.mkdir(parents=True,exist_ok=False)
    target_regimes=('stationary','abrupt','gradual','recurrent','deceptive_primary',
                    'deceptive_anchor','common_mode','reference_corrupt','misleading_cue')
    scored=[]
    for age in (3,4,6,8):
        for use_cue in (False,True):
            cfg=TrustConfig(max_age=age,use_cue=use_cue)
            rows=[r for regime in target_regimes for seed in range(seed_start,seed_start+count)
                  for r in run_world(seed,regime,cfg) if r['policy']=='triad_adaptive']
            aggregate=mean(r['utility'] for r in rows)
            false=sum(r['false_fresh_certificate'] for r in rows)
            harmed=sum(r['harmful'] for r in rows)
            # All-channel compromise excluded from selection: unsolvable; still in holdout.
            feasible=(false==0)
            score=aggregate-2*harmed/len(rows) if feasible else float('-inf')
            scored.append({'age':age,'use_cue':use_cue,
                           'mean_utility':round(aggregate,6),'harmful':harmed,
                           'false_fresh_certificates':false,'score':round(score,6) if feasible else None})
    feasible=[r for r in scored if r['score'] is not None]
    if not feasible:raise RuntimeError('No feasible policy')
    # Deterministic tie-breaker: simpler/no cue, longer interval.
    best=max(feasible,key=lambda r:(r['score'],int(not r['use_cue']),r['age']))
    manifest={'algorithm':'finite grid search then freeze; no post-hoc retuning',
              'development_seed_range':[seed_start,seed_start+count-1],
              'compared_regimes':target_regimes,'scored':scored,'selected':best,
              'selection_criterion':'max mean utility -2 per-epoch harmed frequency; zero incorrect fresh certs on development valid-reference regimes',
              'source_hashes':code_hashes()}
    (out/'tuning.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    return manifest


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    p.add_argument('--start-seed',type=int,default=8000)
    p.add_argument('--count',type=int,default=60)
    p.add_argument('--max-age',type=int,default=6)
    p.add_argument('--no-cue',action='store_true')
    p.add_argument('--tune',action='store_true')
    args=p.parse_args()
    if args.tune:
        result=tune(args.out,args.start_seed,args.count)
        print(json.dumps(result['selected'],indent=2))
    else:
        result=run(args.out,args.start_seed,args.count,
                   TrustConfig(max_age=args.max_age,use_cue=not args.no_cue))
        print(json.dumps({r:{p:result[r][p]['mean_utility'] for p in POLICIES}
                          for r in REGIMES},indent=2))
if __name__=='__main__':main()
