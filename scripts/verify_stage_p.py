"""Read-only v2.4 verification: source freeze, raw receipts, manifests and statistics."""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import defaultdict
from pathlib import Path


def verify(root:Path,cohort='stage_p_holdout')->dict:
    root=Path(root).resolve();folder=root/'experiments'/cohort
    protocol=json.loads((folder/'protocol.json').read_text())
    summary=json.loads((folder/'summary.json').read_text())
    hashes=json.loads((folder/'SHA256SUMS.json').read_text())
    frozen=json.loads((root/'experiments/stage_p_frozen_source.json').read_text())
    for name,digest in hashes.items():
        if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Stage P file corrupted: '+name)
    src=root/'src/agentic_crystallization'
    if protocol['source_hashes']!=frozen['frozen_source_hashes']:
        raise ValueError('Experiment source hash differs from frozen source')
    for name,digest in frozen['frozen_source_hashes'].items():
        if hashlib.sha256((src/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Source altered after freeze: '+name)
    if cohort=='stage_p_holdout' and (protocol['start_seed'],protocol['count'])!=(9000,80):
        raise ValueError('Holdout changed')
    if cohort=='stage_p_replication' and (protocol['start_seed'],protocol['count'])!=(11000,40):
        raise ValueError('Replication changed')
    unique=set();sums=defaultdict(float);counts=defaultdict(int)
    faults=defaultdict(int);alarms=defaultdict(int);costs=defaultdict(float)
    with (folder/'runs.csv').open(newline='',encoding='utf-8') as f:
        for row in csv.DictReader(f):
            seed=int(row['seed']);epoch=int(row['epoch']);policy=row['policy'];regime=row['regime']
            if not protocol['start_seed']<=seed<protocol['start_seed']+protocol['count']:
                raise ValueError('Unknown seed')
            if not 0<=epoch<protocol['config']['epochs']:
                raise ValueError('Epoch outside horizon')
            if policy not in protocol['policies'] or regime not in protocol['regimes']:
                raise ValueError('Unrecognized policy or regime')
            key=(seed,epoch,regime,policy)
            if key in unique:raise ValueError('Duplicate receipt')
            unique.add(key)
            group=(regime,policy)
            gain=float(row['true_gain']);cost=float(row['audit_cost'])
            if abs(float(row['utility'])-(80*gain-cost))>1e-5:
                raise ValueError('Utility receipt irreconcilable')
            if int(row['false_fresh_certificate']) != int(int(row['fresh']) and gain<=0):
                raise ValueError('False-cert count altered')
            if int(row['harmful']) != int(gain<0):
                raise ValueError('Harm count altered')
            counts[group]+=1;sums[group]+=float(row['utility']);costs[group]+=cost
            faults[group]+=int(row['false_fresh_certificate']);alarms[group]+=int(row['integrity_alarm'])
    expected=protocol['count']*len(protocol['regimes'])*len(protocol['policies'])*protocol['config']['epochs']
    if len(unique)!=expected or len(unique)!=protocol['rows']:raise ValueError('Missing receipts')
    for regime in protocol['regimes']:
        for policy in protocol['policies']:
            group=(regime,policy);reported=summary[regime][policy]
            if counts[group]!=protocol['count']*protocol['config']['epochs']:
                raise ValueError('Incomplete policy/regime')
            if abs(sums[group]/counts[group]-reported['mean_utility'])>5.1e-6:
                raise ValueError('Utility summary mismatch')
            if faults[group]!=reported['false_fresh_certificates'] or alarms[group]!=reported['integrity_alarms']:
                raise ValueError('Integrity summary mismatch')
            if abs(costs[group]-reported['total_audit_cost'])>5e-3:
                raise ValueError('Audit cost mismatch')
    return {'verified':True,'cohort':cohort,'rows':len(unique),
            'worlds':protocol['count']*len(protocol['regimes']),
            'source_frozen':True,'scoring_reconciled':True,
            'boundary':'Integrity cannot establish audit-channel truth or future stability'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('root',nargs='?',default='.')
    parser.add_argument('--cohort',default='stage_p_holdout');args=parser.parse_args()
    print(json.dumps(verify(Path(args.root),args.cohort),indent=2))
