"""Stage L: autonomous bounded procedure discovery, retention, and revalidation.

The generator has hidden synthetic concepts; CrystalKernel receives only labeled
examples and an externally declared shift allowance, never ground-truth keys.
"""
from __future__ import annotations

import argparse
import csv
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
from statistics import mean
from typing import Any

from .crystal_core import (Configuration,CrystalState,DurableLedger,Evidence,
                           Example,candidates,step,canonical,digest)

REGIMES=('stationary','recurrent','abrupt','noise','bounded_shift','unknown_shift','false_shift')
POLICIES=('crystal','memoryless','reuse_only','baseline')
EPOCHS=12
PHASES={
 'stationary':    ('A','A','A','A','A','A','A','A','A','A','A','A'),
 'recurrent':     ('A','A','B','B','A','A','C','C','A','B','A','A'),
 'abrupt':        ('A','B','C','D','A','B','C','D','A','B','C','D'),
 'noise':         ('A','A','N','N','A','A','N','N','A','A','N','N'),
 'bounded_shift':('A','A','B','B','A','A','C','C','A','B','A','A'),
 'unknown_shift':('A','A','B','B','A','A','C','C','A','B','A','A'),
 'false_shift':   ('A','A','A','A','A','A','A','A','A','A','A','A'),
}


def seed_from(*items:object)->int:
    return int(sha256(canonical(items).encode()).hexdigest()[:16],16)


def latent_concepts(world_seed:int,width:int)->dict[str,tuple[int,...]]:
    all_triples=list(combinations(range(width),3))
    rng=random.Random(seed_from(world_seed,'concepts'))
    selected=rng.sample(all_triples,4)
    # The N concept needs four features; beyond the candidate family.
    noise=tuple(sorted(rng.sample(range(width),4)))
    return dict(zip('ABCD',selected)) | {'N':noise}


def parity(bits:tuple[int,...],locations:tuple[int,...])->int:
    v=0
    for k in locations:v^=bits[k]
    return v


def draw_rows(world_seed:int,epoch:int,split:str,n:int,width:int,
              source:tuple[int,...], target:tuple[int,...],mix:float=0.0,
              inverted:bool=False)->tuple[Example,...]:
    rng=random.Random(seed_from(world_seed,epoch,split))
    rows=[]
    for _ in range(n):
        bits=tuple(rng.randrange(2) for _ in range(width))
        y=parity(bits,source)
        if mix and rng.random()<mix:
            y=parity(bits,target)
        if inverted:y^=1
        rows.append(Example(bits,y))
    return tuple(rows)


def epoch_packet(world_seed:int,epoch:int,regime:str,config:Configuration)->tuple[Evidence,tuple[Example,...],dict]:
    if regime not in REGIMES or not 1<=epoch<=EPOCHS:
        raise ValueError('Invalid regime/epoch')
    concepts=latent_concepts(world_seed,config.width)
    phase=PHASES[regime][epoch-1]
    source=concepts[phase]
    alternate=concepts['B'] if phase!='B' else concepts['A']
    mix=0.06 if regime=='bounded_shift' else 0.0
    flip=regime=='false_shift'
    shift=None if regime=='unknown_shift' else mix
    validation=draw_rows(world_seed,epoch,'validation',config.validation_looks[-1],config.width,source,source)
    evidence=Evidence(
        epoch=epoch,
        scout=draw_rows(world_seed,epoch,'scout',config.scout_size,config.width,source,source),
        discovery=draw_rows(world_seed,epoch,'discovery',config.discovery_size,config.width,source,source),
        validation=validation,shift_allowance=shift)
    live=draw_rows(world_seed,epoch,'live',256,config.width,source,alternate,mix=mix,inverted=flip)
    audit={'phase':phase,'source':source,'alternative':alternate,
           'mixture':mix,'invert':flip,'true_shift_bound':1.0 if flip else mix,
           'declared_shift_bound':shift}
    return evidence,live,audit


def true_deployment_gain(active:str,audit:dict)->float:
    """Synthetic oracle metric ONLY for scoring; never passed to controller."""
    if active=='baseline:0':return 0.0
    features=tuple(int(v) for v in active[4:].split(','))
    p=float(audit['mixture'])
    score=(1-p)*(0.5 if features==tuple(audit['source']) else 0.0)
    score+=p*(0.5 if features==tuple(audit['alternative']) else 0.0)
    if audit['invert']:
        score=-0.5 if features==tuple(audit['source']) else 0.0
    return score


def run_one(world_seed:int,regime:str,mode:str,config:Configuration,
            ledger:DurableLedger|None=None)->list[dict[str,Any]]:
    if mode not in POLICIES:raise ValueError('Unknown mode')
    state=ledger.replay() if ledger else CrystalState(credits=config.initial_credits)
    results=[]
    for epoch in range(state.epoch+1,EPOCHS+1):
        evidence,live,audit=epoch_packet(world_seed,epoch,regime,config)
        event,next_state=step(state,evidence,live,config,mode)
        if ledger:
            replayed=ledger.append(event)
            if replayed.to_dict()!=next_state.to_dict():raise AssertionError('Replay mismatch')
        state=next_state
        cert=event['status']=='CERTIFIED'
        gain=true_deployment_gain(event['active'],audit)
        if cert and gain<=config.minimum_gain:
            false_promotion=1
        else:
            false_promotion=0
        results.append({
            'seed':world_seed,'regime':regime,'policy':mode,'epoch':epoch,
            'phase':audit['phase'],'declared_shift':audit['declared_shift_bound'],
            'actual_shift_bound':audit['true_shift_bound'],
            'status':event['status'],'candidate':event['candidate'] or '',
            'active':event['active'],'origin':event['proposal_source'],
            'queries':event['queries'],'prediction_ops':event['prediction_ops'],
            'net_surplus':event['net_surplus'],'score_accuracy':event['score_accuracy'],
            'true_gain':gain,'false_certification':false_promotion,
            'memory_size':len(state.memory), 'credits':state.credits,
            'certificate_lower':event['certificate']['lower'] or '',
            'validation_samples':event['certificate']['n']})
    return results


def summarize(rows:list[dict],config:Configuration)->dict:
    results={}
    for regime in REGIMES:
        results[regime]={}
        for mode in POLICIES:
            r=[x for x in rows if x['regime']==regime and x['policy']==mode]
            if not r:continue
            worlds=len(set(x['seed'] for x in r))
            results[regime][mode]={
                'worlds':worlds,'epochs':len(r),
                'certified':sum(x['status']=='CERTIFIED' for x in r),
                'false_certifications':sum(x['false_certification'] for x in r),
                'memory_activations':sum(x['origin']=='memory' and x['status']=='CERTIFIED' for x in r),
                'total_queries':sum(x['queries'] for x in r),
                'total_prediction_ops':sum(x['prediction_ops'] for x in r),
                'mean_surplus_per_epoch':round(mean(x['net_surplus'] for x in r),4),
                'total_surplus':round(sum(x['net_surplus'] for x in r),4),
                'mean_true_gain':round(mean(x['true_gain'] for x in r),4),
                'mean_memory_size':round(mean(x['memory_size'] for x in r),3),
            }
    return results


def generate(out:Path,first_seed:int,count:int,config:Configuration)->dict:
    out=Path(out)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError('Refuse to overwrite an existing experiment directory')
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for regime in REGIMES:
        for world_seed in range(first_seed,first_seed+count):
            for policy in POLICIES:
                rows.extend(run_one(world_seed,regime,policy,config))
    columns=list(rows[0])
    with (out/'runs.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=columns,lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
    summary=summarize(rows,config)
    (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    source_dir=Path(__file__).resolve().parent
    code_hashes={name:sha256((source_dir/name).read_bytes()).hexdigest()
                 for name in ('crystal_core.py','stage_l.py')}
    protocol={'version':'2.0.0','stage':'L','seed_first':first_seed,'seed_count':count,
              'code_sha256':code_hashes,
              'epochs':EPOCHS,'regimes':REGIMES,'policies':POLICIES,
              'config':config.__dict__,
              'primary_outcome':'mean paired net utility per epoch on a held-out deployment stream',
              'alpha_semantics':'alpha_total is lifetime alpha of one controller run; independent worlds restart alpha spending',
              'known_limitations':['tiny planted parity family','task family source known to simulator only',
                                   'shift bound supplied by experimental protocol not learned',
                                   'rewards replenish credits from EXTERNAL tasks',
                                   'no unconditional perpetual viability guarantee',
                                   'simulation not real Pegasus']}
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2,sort_keys=True)+'\n')
    files={p.name:sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    (out/'SHA256SUMS.json').write_text(json.dumps(files,indent=2,sort_keys=True)+'\n')
    return {'out':str(out),'rows':len(rows),'worlds':count,'summary':summary}


def demonstration(root:Path,seed:int,regime:str,config:Configuration)->dict:
    demo=Path(root)
    demo.mkdir(parents=True,exist_ok=True)
    file=demo/'ledger.jsonl'
    if file.exists():
        raise FileExistsError('Do not overwrite demonstration ledger')
    ledger=DurableLedger(file,config)
    rows=run_one(seed,regime,'crystal',config,ledger)
    replay=ledger.replay()
    if replay.epoch!=EPOCHS:
        raise AssertionError('Durable replay not complete')
    summary={'seed':seed,'regime':regime,'episodes':replay.epoch,
             'credits_after':replay.credits,'memory':replay.memory,
             'state_digest':digest(replay.to_dict()),
             'certified_episodes':sum(r['status']=='CERTIFIED' for r in rows),
             'fresh_reactivation':sum(r['origin']=='memory' and r['status']=='CERTIFIED' for r in rows),
             'false_certifications':sum(r['false_certification'] for r in rows),
             'note':'Credits are rewards from EXTERNAL task deliveries minus evaluation cost; not a closed thermodynamic system.'}
    (demo/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    return summary


def main():
    parser=argparse.ArgumentParser(description='Agentic Crystallization v2.0 Stage L')
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--start-seed',required=True,type=int)
    parser.add_argument('--count',type=int,default=10)
    parser.add_argument('--demo-seed',type=int,default=None)
    args=parser.parse_args()
    if args.count<1:raise ValueError('count must be positive')
    config=Configuration()
    result=generate(args.out,args.start_seed,args.count,config)
    if args.demo_seed is not None:
        result['demo']=demonstration(args.out/'demo',args.demo_seed,'recurrent',config)
    print(json.dumps({'rows':result['rows'],'worlds':result['worlds'],
                      'stationary':result['summary']['stationary'],
                      'recurrent':result['summary']['recurrent'],
                      'false_shift':result['summary']['false_shift']},indent=2))

if __name__=='__main__':main()
