"""Stage M: environmental self-regulation under fresh paired feedback.

No hidden concept, true gain, or shift magnitude is passed to renewal_step.
Scored deployment outcomes are external tasks with their own labels. The
'misleading_feedback' regime explicitly violates trustworthy feedback.

Reproducibility: standard-library only; all pseudo-random draws have labeled
SHA-256-derived independent seeds. Validation and reported feedback are distinct.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import random
from statistics import mean
from typing import Any

from .crystal_core import Configuration, Example, candidates, canonical, digest
from .renewal_core import (RenewalConfig, RenewalState, RenewalLedger, Packet, Segment,
                           POLICIES, renewal_step, rank_discovery)
from .stage_l import seed_from, latent_concepts, parity

REGIMES=('stationary','gradual','abrupt','recurrent','inverted_drift',
         'unlearnable','missing_feedback','misleading_feedback')
EPOCHS=12


def latent_schedule(epoch:int,regime:str)->tuple[str,str,str]:
    if not 1<=epoch<=EPOCHS:raise ValueError('Epoch out of range')
    if regime=='stationary':return 'A','A','A'
    if regime=='gradual':return 'A','A','A'
    if regime=='abrupt':
        cycle='ABCD'
        first=cycle[(epoch-1)%4]
        next_one=cycle[epoch%4]
        return first,next_one,next_one
    if regime=='recurrent':
        phases=('A','A','B','B','A','A','C','C','A','B','A','A')
        first=phases[epoch-1]
        nxt=phases[epoch] if epoch in (3,7,10) else first
        return first,nxt,nxt
    if regime=='unlearnable':
        first='N' if epoch in (3,4,7,8,11,12) else 'A'
        middle='N' if epoch in (2,6,10) else first
        return first,middle,middle
    if regime in ('inverted_drift','missing_feedback','misleading_feedback'):
        return 'A','B' if regime=='missing_feedback' else 'A', 'B' if regime=='missing_feedback' else 'A'
    raise ValueError('Unknown regime')


def observations(seed:int,epoch:int,block:int,split:str,count:int,width:int,
                 current:tuple[int,...],alternate:tuple[int,...],
                 mixture:float=0.0, inverted:bool=False)->tuple[Example,...]:
    """Each split is disjoint in RNG-state; no target oracle exposed."""
    rng=random.Random(seed_from('stage_m_v2.1',seed,epoch,block,split))
    rows=[]
    for _ in range(count):
        bits=tuple(rng.randrange(2) for _ in range(width))
        source=alternate if mixture and rng.random()<mixture else current
        label=parity(bits,source)
        if inverted:label^=1
        rows.append(Example(bits,label))
    return tuple(rows)


def make_packet(seed:int,epoch:int,regime:str,config:RenewalConfig)->tuple[Packet,tuple[dict,...]]:
    """Generator returns separate controller packet and evaluator-only audit."""
    if regime not in REGIMES:raise ValueError('Unknown regime')
    base=config.base
    concepts=latent_concepts(seed,base.width)
    schedule=latent_schedule(epoch,regime)
    blocks=[];audits=[]
    for block,phase in enumerate(schedule):
        source=concepts[phase]
        alt=concepts['B' if phase!='B' else 'A']
        mix=(0.0,.30,.50)[block] if regime=='gradual' else 0.0
        flip=(regime in ('inverted_drift','misleading_feedback') and block>0)
        def draw(split:str,size:int):
            return observations(seed,epoch,block,split,size,base.width,source,alt,mix,flip)
        scout=draw('scout',base.scout_size)
        discovery=draw('discovery',base.discovery_size)
        validation=draw('validation',base.validation_looks[-1])
        live=draw('live',(256,768,512)[block])
        if block==1:
            if regime=='missing_feedback':
                feedback=None
            elif regime=='misleading_feedback':
                # Observable channel is deceptively unchanged while truth flips.
                feedback=observations(seed,epoch,block,'live',768,base.width,source,alt,mix,False)
            else:
                feedback=live
        else:
            feedback=live
        rank,gain=rank_discovery(discovery,base.width)
        blocks.append(Segment(scout,discovery,validation,live,feedback,rank,gain))
        audits.append({'phase':phase,'source':source,'alternate':alt,
                       'mixture':mix,'inverted':flip,
                       'feedback_trustworthy':not(regime=='misleading_feedback' and block==1),
                       'feedback_available':feedback is not None})
    return Packet(epoch,tuple(blocks)),tuple(audits)


def analytic_true_gain(procedure:str,audit:dict)->float:
    """Hidden evaluator only. Never used by controllers or receipts."""
    if procedure=='baseline:0':return 0.0
    features=tuple(map(int,procedure[4:].split(',')))
    p=audit['mixture']
    source=audit['source'];alternate=audit['alternate']
    gain=((1-p)*0.5 if features==source else 0.0)+ (p*0.5 if features==alternate else 0.0)
    return -gain if audit['inverted'] else gain


def run_world(seed:int,regime:str,config:RenewalConfig,
              ledger_root:Path|None=None)->list[dict]:
    """One world and regime. Generate each epoch ONCE; share observed tasks across arms."""
    packets=[make_packet(seed,epoch,regime,config) for epoch in range(1,EPOCHS+1)]
    states={p:RenewalState(credits=config.base.initial_credits) for p in POLICIES}
    ledgers={p:RenewalLedger(ledger_root/(regime+'_'+p+'.jsonl'),config)
             for p in POLICIES} if ledger_root else {}
    rows=[]
    for packet,audits in packets:
        for policy in POLICIES:
            event,state=renewal_step(states[policy],packet,policy,config)
            if policy in ledgers:
                replayed=ledgers[policy].append(event)
                if replayed.to_dict()!=state.to_dict():raise AssertionError('Replay disagreement')
            states[policy]=state
            truth=[analytic_true_gain(action,audit) for action,audit in zip(event['active'],audits)]
            bad_blocks=sum(action!='baseline:0' and gain<=config.base.minimum_gain
                           for action,gain in zip(event['active'],truth))
            wrong_promotions=sum(analytic_true_gain(item['procedure'],audits[item['block']])
                                 <=config.base.minimum_gain for item in event['promotions'])
            source_ref_gain=analytic_true_gain(event['active'][0],audits[0])
            mid_gain=analytic_true_gain(event['active'][1],audits[1])
            real_drop=(mid_gain-source_ref_gain)
            real_change=real_drop < -config.monitor_drop - .10
            monitored=event['monitor']['status'] in ('ALARM','CLEAR')
            alarm=event['monitor']['status']=='ALARM'
            labels_common=sum(len(seg.live) for seg in packet.segments)
            row={
                'seed':seed,'regime':regime,'policy':policy,'epoch':packet.epoch,
                'phase0':audits[0]['phase'],'phase1':audits[1]['phase'],'phase2':audits[2]['phase'],
                'feedback_trustworthy':audits[1]['feedback_trustworthy'],
                'feedback_available':audits[1]['feedback_available'],
                'certifications':len(event['promotions']),
                'memory_recertifications':sum(item['source']=='memory' for item in event['promotions']),
                'origin0':event['origins'][0], 'origin2':event['origins'][2],
                'action0':event['active'][0], 'action1':event['active'][1], 'action2':event['active'][2],
                'alarm':int(alarm),'monitor_status':event['monitor']['status'],
                'monitor_n':event['monitor_labels'],'actual_large_drop':int(real_change),
                'missed_drift':int(real_change and monitored and not alarm),
                'false_alarm':int(not real_change and alarm),
                'inappropriate_deployment_blocks':bad_blocks,
                'harmful_deployment_blocks':sum(p!='baseline:0' and g < -.025
                                                for p,g in zip(event['active'],truth)),
                'false_promotions':wrong_promotions,
                'true_gain0':round(truth[0],6),'true_gain1':round(truth[1],6),
                'true_gain2':round(truth[2],6),
                'observed_gain0':event['block_gains'][0],
                'observed_gain1':event['block_gains'][1],
                'observed_gain2':event['block_gains'][2],
                'task_count':labels_common,
                'total_queries':event['queries'],
                'total_prediction_ops':event['prediction_ops'],
                'net_surplus':event['net_surplus'],
                'credits':state.credits,'memory_size':len(state.memory),
                'memory_retired':sum(rec['status']=='RETIRED' for rec in state.memory.values()),
                'memory_needs_renewal':sum(rec['status']=='NEEDS_RENEWAL' for rec in state.memory.values()),
            }
            rows.append(row)
    return rows


def summarize(rows:list[dict])->dict:
    summary={}
    for regime in REGIMES:
        summary[regime]={}
        for mode in POLICIES:
            r=[x for x in rows if x['regime']==regime and x['policy']==mode]
            if not r:continue
            summary[regime][mode]={
                'worlds':len(set(x['seed'] for x in r)),'epochs':len(r),
                'certified_promotions':sum(x['certifications'] for x in r),
                'false_promotions':sum(x['false_promotions'] for x in r),
                'alarms':sum(x['alarm'] for x in r),
                'false_alarms':sum(x['false_alarm'] for x in r),
                'missed_drift':sum(x['missed_drift'] for x in r),
                'harmful_blocks':sum(x['harmful_deployment_blocks'] for x in r),
                'inappropriate_blocks':sum(x['inappropriate_deployment_blocks'] for x in r),
                'memory_recertifications':sum(x['memory_recertifications'] for x in r),
                'total_queries':sum(x['total_queries'] for x in r),
                'total_prediction_ops':sum(x['total_prediction_ops'] for x in r),
                'total_surplus':round(sum(x['net_surplus'] for x in r),5),
                'mean_surplus_per_epoch':round(mean(x['net_surplus'] for x in r),5),
                'mean_memory':round(mean(x['memory_size'] for x in r),4),
                'min_credits':round(min(x['credits'] for x in r),6),
            }
    return summary


def generate(out:Path,start_seed:int,count:int,config:RenewalConfig)->dict:
    out=Path(out)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError('Existing experiment directory; refuse overwrite')
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for regime in REGIMES:
        for seed in range(start_seed,start_seed+count):
            rows.extend(run_world(seed,regime,config))
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
    result=summarize(rows)
    (out/'summary.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    directory=Path(__file__).parent
    files=('renewal_core.py','stage_m.py','crystal_core.py','stage_l.py')
    protocol={
        'version':'2.1.0','stage':'M','status':'synthetic comparative experiment',
        'start_seed':start_seed,'worlds':count,'epochs_per_world':EPOCHS,
        'regimes':REGIMES,'policies':POLICIES,
        'config': {'base':asdict(config.base),
                    'alpha_promotion':config.alpha_promotion,
                    'alpha_monitor':config.alpha_monitor,
                    'monitor_drop':config.monitor_drop,
                    'monitor_processing_cost':config.monitor_processing_cost},
        'source_hashes_sha256':{n:sha256((directory/n).read_bytes()).hexdigest() for n in files},
        'metrics':{'primary':'mean net surplus per epoch, relative to baselines',
                   'safety':'false promotions on validation period, inappropriate and harmful deployment blocks',
                   'reactivity':'monitor alarms and missed true deterioration',
                   'efficiency':'selection/validation samples, prediction operations, reactivations'},
        'warning':'feedback is delayed; no guarantee against future shift, absent labels, or adversarially misleading labels',
        'caveats':[
           'synthetic planted XOR concepts, not Pegasus or real-world agents',
           'source/validation/live distribution only justified within each simulated block',
           'monitoring feedback observed only after middle block; one-block detection lag',
           'lifetime error budget is per policy run; no global guarantee across independent simulation worlds',
           'false feedback may invalidate drift detection',
           'economic credits depend on external task reward and finite simulation horizon',
           'new procedures restricted to prespecified finite XOR family',
        ]}
    (out/'protocol.json').write_text(json.dumps(protocol,sort_keys=True,indent=2)+'\n')
    checks={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
    (out/'SHA256SUMS.json').write_text(json.dumps(checks,sort_keys=True,indent=2)+'\n')
    return {'out':str(out),'worlds':count,'rows':len(rows),'summary':result}


def demonstrate(out:Path, seed:int, regime:str, config:RenewalConfig)->dict:
    root=Path(out);root.mkdir(parents=True,exist_ok=True)
    rows=run_world(seed,regime,config,root)
    recovered=RenewalLedger(root/(regime+'_crystal.jsonl'),config).replay()
    report={'seed':seed,'regime':regime,'rows':len(rows),'epochs':recovered.epoch,
            'credits':recovered.credits,'retained':recovered.memory,
            'state_hash':digest(recovered.to_dict()),
            'monitor_alarms':sum(r['alarm'] for r in rows if r['policy']=='crystal'),
            'false_promotions':sum(r['false_promotions'] for r in rows if r['policy']=='crystal'),
            'warning':'This is a finite synthetic task stream with external rewards.'}
    (root/'summary.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report


def main():
    parser=argparse.ArgumentParser(description='Agentic Crystallization v2.1 Stage M')
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--start-seed',type=int,required=True)
    parser.add_argument('--count',type=int,default=3)
    parser.add_argument('--demo-seed',type=int,default=None)
    parser.add_argument('--demo-regime',choices=REGIMES,default='recurrent')
    args=parser.parse_args()
    if args.count<1:raise ValueError('count must be positive')
    config=RenewalConfig()
    result=generate(args.out,args.start_seed,args.count,config)
    if args.demo_seed is not None:
        result['demo']=demonstrate(args.out/'demo',args.demo_seed,args.demo_regime,config)
    print(json.dumps({'out':result['out'],'rows':result['rows'],
                      'worlds':result['worlds'],
                      'abrupt':result['summary']['abrupt'],
                      'misleading_feedback':result['summary']['misleading_feedback']},indent=2))

if __name__=='__main__':main()
