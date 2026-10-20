"""Read-only verifier for Stage O protocol, data, source freeze and checksums."""
from __future__ import annotations
import csv,hashlib,json,argparse
from collections import defaultdict
from pathlib import Path


def verify(root:Path,cohort:str='stage_o_holdout')->dict:
    root=Path(root).resolve()
    folder=root/'experiments'/cohort
    protocol=json.loads((folder/'protocol.json').read_text())
    summary=json.loads((folder/'summary.json').read_text())
    checks=json.loads((folder/'SHA256SUMS.json').read_text())
    for name,expected in checks.items():
        if not (folder/name).is_file() or hashlib.sha256((folder/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('experiment checksum mismatch: '+name)
    frozen=json.loads((root/'experiments/stage_o_frozen_source.json').read_text())
    src=root/'src/agentic_crystallization'
    for name,expected in frozen['source_sha256'].items():
        if hashlib.sha256((src/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('frozen source changed: '+name)
    if protocol['source_hashes']!=frozen['source_sha256']:
        raise ValueError('protocol does not match frozen source')
    unique=set();counts=defaultdict(int);utilities=defaultdict(float)
    alarms=defaultdict(int);false=defaultdict(int)
    with (folder/'runs.csv').open(newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        for row in reader:
            key=(row['regime'],int(row['seed']),int(row['epoch']),row['policy'])
            if key in unique:raise ValueError('duplicate policy-epoch receipt')
            unique.add(key)
            if row['regime'] not in protocol['regimes'] or row['policy'] not in protocol['policies']:
                raise ValueError('unknown policy or regime')
            if not 0<=key[2]<protocol['epochs']:
                raise ValueError('invalid epoch')
            g=(row['regime'],row['policy'])
            counts[g]+=1;utilities[g]+=float(row['utility'])
            alarms[g]+=int(row['disagreement_alarm']);false[g]+=int(row['false_certificate'])
    if len(unique)!=protocol['rows'] or len(unique)!=protocol['count']*len(protocol['regimes'])*len(protocol['policies'])*protocol['epochs']:
        raise ValueError('missing or extra policy-epoch records')
    for regime in protocol['regimes']:
        for policy in protocol['policies']:
            key=(regime,policy)
            if counts[key]!=protocol['count']*protocol['epochs']:
                raise ValueError('incomplete group')
            ref=summary[regime][policy]
            if abs(utilities[key]/counts[key]-ref['mean_utility'])>0.000006:
                raise ValueError('summary utility mismatch')
            if alarms[key]!=ref['disagreement_alarms'] or false[key]!=ref['false_certificates']:
                raise ValueError('summary alarm/certification mismatch')
    return {'verified':True,'cohort':cohort,'rows':len(unique),'worlds':protocol['count']*len(protocol['regimes']),
            'policies':len(protocol['policies']),'source_frozen':True,
            'scope':'Data and source integrity only; not proof of channel honesty or scientific claim.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('root',nargs='?',default='.')
    parser.add_argument('--cohort',default='stage_o_holdout')
    args=parser.parse_args();print(json.dumps(verify(Path(args.root),args.cohort),indent=2))
