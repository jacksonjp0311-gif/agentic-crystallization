"""Paired world-level descriptive analyses of the frozen Stage L holdout."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import random
from statistics import mean


def bootstrap_paired(values:list[float],seed:int=2020,replicates:int=6000)->dict:
    if len(values)<2:raise ValueError('Need multiple independent worlds')
    rng=random.Random(seed)
    n=len(values)
    res=sorted(sum(values[rng.randrange(n)] for _ in range(n))/n for _ in range(replicates))
    return {'mean':round(mean(values),6),
            'ci_95_descriptive':[round(res[int(.025*replicates)],6),
                                 round(res[int(.975*replicates)],6)],
            'units':'independently seeded world' }


def analyze(path:Path)->dict:
    with (path/'runs.csv').open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    worlds=sorted(set(int(x['seed']) for x in rows))
    regimes=sorted(set(x['regime'] for x in rows))
    by={(int(row['seed']),row['regime'],row['policy']):[] for row in rows}
    for row in rows:
        by[(int(row['seed']),row['regime'],row['policy'])].append(row)
    comparisons={}
    for regime in regimes:
        comparisons[regime]={}
        for base in ('memoryless','reuse_only','baseline'):
            util=[];pred_ops=[];samples=[]
            for world in worlds:
                a=by[(world,regime,'crystal')]
                b=by[(world,regime,base)]
                util.append(mean(float(x['net_surplus']) for x in a) - mean(float(x['net_surplus']) for x in b))
                pred_ops.append(sum(int(x['prediction_ops']) for x in a)-sum(int(x['prediction_ops']) for x in b))
                samples.append(sum(int(x['queries']) for x in a)-sum(int(x['queries']) for x in b))
            comparisons[regime]['crystal_minus_'+base]={
                'utility_per_epoch':bootstrap_paired(util,seed=2020),
                'prediction_ops_per_world':bootstrap_paired(pred_ops,seed=2021),
                'task_observations_per_world':bootstrap_paired(samples,seed=2022)}
    false_counts={}
    for regime in regimes:
        r=[x for x in rows if x['regime']==regime and x['policy']=='crystal']
        false_counts[regime]={'certificates':sum(x['status']=='CERTIFIED' for x in r),
                              'false_certificates':sum(int(x['false_certification']) for x in r),
                              'mean_final_credits':round(mean(float(x['credits']) for x in r if int(x['epoch'])==12),6)}
    return {'n_worlds':len(worlds),'n_rows':len(rows),'method':'Paired bootstrap with 6000 replicates on independently seeded world means. Descriptive, not preregistered confirmatory confidence intervals.',
            'comparisons':comparisons,'failure_controls':false_counts}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('experiment',type=Path)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    obj=analyze(args.experiment)
    if args.out.exists():raise FileExistsError('Do not overwrite existing analysis')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'worlds':obj['n_worlds'],'rows':obj['n_rows'],
      'recurrent':obj['comparisons']['recurrent'],
      'false_shifts':obj['failure_controls']['false_shift']},indent=2))

if __name__=='__main__':main()
