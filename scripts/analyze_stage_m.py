"""Stage M paired world bootstrap and falsification analysis.

Intervals are DESCRIPTIVE Monte Carlo quantiles over randomly generated world
seeds. The bootstrap does not prove a distribution-free universal improvement,
nor account for choosing regimes from prior development experiments.
"""
from __future__ import annotations
import argparse,csv,json,random
from pathlib import Path
from statistics import mean
from hashlib import sha256

REGIMES=('stationary','gradual','abrupt','recurrent','inverted_drift','unlearnable','missing_feedback','misleading_feedback')
CONTROLS=('memoryless','periodic','fixed_reuse','monitor_hold','baseline')


def analyze(path:Path,replicates:int=3000)->dict:
    with path.open(newline='',encoding='utf-8') as stream:
        rows=list(csv.DictReader(stream))
    groups={}
    for row in rows:
        key=(row['regime'],row['policy'],int(row['seed']))
        groups.setdefault(key,[]).append(float(row['net_surplus']))
    outcome={}
    for regime in REGIMES:
        worldids=sorted(seed for r,policy,seed in groups if r==regime and policy=='crystal')
        compare={}
        for control in CONTROLS:
            diffs=[]
            for seed in worldids:
                c=groups[(regime,'crystal',seed)]; b=groups[(regime,control,seed)]
                if len(c)!=12 or len(b)!=12:raise ValueError('Incomplete world')
                diffs.append(mean(c)-mean(b))
            rng=random.Random(21001+REGIMES.index(regime)*20+CONTROLS.index(control))
            bmeans=[]
            for _ in range(replicates):
                sampled=[diffs[rng.randrange(len(diffs))] for _ in diffs]
                bmeans.append(mean(sampled))
            bmeans.sort()
            compare[control]={
                'worlds':len(diffs),'mean_paired_utility_per_epoch':round(mean(diffs),6),
                'descriptive_bootstrap_95pct':[
                    round(bmeans[int(.025*replicates)],6),
                    round(bmeans[min(replicates-1,int(.975*replicates))],6)],
                'fraction_worlds_crystal_better':round(sum(d>0 for d in diffs)/len(diffs),6),
            }
        outcome[regime]=compare
    report={'source_csv_sha256':sha256(path.read_bytes()).hexdigest(),
            'replicates':replicates,'unit_of_resampling':'independent synthetic world seed',
            'interventions':'none; policies share seeded episodes and independent proposed actions',
            'status':'descriptive 95% world bootstrap; not preregistered confirmatory intervals',
            'comparison':outcome}
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('csv_file',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--replicates',type=int,default=3000)
    args=parser.parse_args()
    if args.replicates<100:raise ValueError('Too few bootstrap draws')
    result=analyze(args.csv_file,args.replicates)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'report':str(args.out),'regimes':list(result['comparison']),
                      'recurrent_crystal_minus_memoryless':result['comparison']['recurrent']['memoryless'],
                      'abrupt_crystal_minus_periodic':result['comparison']['abrupt']['periodic']},indent=2))
