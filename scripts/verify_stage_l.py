"""Verify Stage L outputs and the source provenance they claim.

SHA256 checks are integrity checks, NOT cryptographic signatures.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys


def verify(target:Path,repo:Path)->dict:
    target=Path(target).resolve();repo=Path(repo).resolve()
    manifest=json.loads((target/'SHA256SUMS.json').read_text())
    actual={p.name for p in target.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'}
    if set(manifest)!=actual:
        raise ValueError('Experiment inventory altered: %s != %s' % (set(manifest),actual))
    for name,expected in manifest.items():
        got=hashlib.sha256((target/name).read_bytes()).hexdigest()
        if got!=expected:raise ValueError('Experiment SHA256 mismatch: '+name)
    protocol=json.loads((target/'protocol.json').read_text())
    for name,expected in protocol['code_sha256'].items():
        f=repo/'src'/'agentic_crystallization'/name
        if hashlib.sha256(f.read_bytes()).hexdigest()!=expected:
            raise ValueError('Source no longer matches frozen experiment: '+name)
    with (target/'runs.csv').open(newline='',encoding='utf-8') as f:
        records=list(csv.DictReader(f))
    if not records:raise ValueError('No experiment records')
    expected=protocol['seed_count']*protocol['epochs']*len(protocol['regimes'])*len(protocol['policies'])
    if len(records)!=expected:raise ValueError('Unexpected row count')
    keys=set(); bad=[]
    for row in records:
        key=(row['seed'],row['regime'],row['policy'],row['epoch'])
        if key in keys:raise ValueError('Duplicate world/epoch/policy row')
        keys.add(key)
        if int(row['queries'])<0 or int(row['validation_samples'])<0:
            raise ValueError('Invalid sample count')
        if int(row['false_certification']) and row['regime']!='false_shift':
            bad.append(key)
    if bad:print('NOTE: false certificates in the valid shift regimes!',bad[:3],file=sys.stderr)
    return {'verified':True,'rows':len(records),'source_verified':True,
            'protocol_seed_range':[protocol['seed_first'],protocol['seed_first']+protocol['seed_count']-1],
            'note':'SHA256 verifies integrity, not authorization or statistical validity.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('target',type=Path)
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args();print(json.dumps(verify(args.target,args.repo),indent=2))
