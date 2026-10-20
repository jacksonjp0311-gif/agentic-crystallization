"""Verify frozen Stage K data, source linkage and result-file integrity.

A SHA256 manifest detects accidental changes, not fraudulent re-signing.
For scientific replay, rerun the simulation to a new folder and compare hashes.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(experiment:Path, source_root:Path, *, expect_worlds:int|None=None, preseal:bool=False)->dict:
    experiment=Path(experiment);source_root=Path(source_root)
    protocol=json.loads((experiment/'protocol.json').read_text())
    manifest=json.loads((experiment/'manifest.json').read_text())
    summary=json.loads((experiment/'summary.json').read_text())
    with (experiment/'runs.csv').open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    for filename,digest in manifest['sha256'].items():
        if sha(experiment/filename)!=digest:
            raise ValueError(f'Hash mismatch: {filename}')
    stage_file=(source_root/'docs/archive/STAGE_K_PRESEAL_SOURCE.py') if preseal else (source_root/'src/agentic_crystallization/stage_k.py')
    core_file=(source_root/'docs/archive/SEQUENTIAL_CERTIFICATE_PRESEAL_SOURCE.py') if preseal else (source_root/'src/agentic_crystallization/sequential_certificate.py')
    if protocol['stage_k_source_sha256']!=sha(stage_file):
        raise ValueError('Stage K code hash differs from frozen protocol')
    if protocol['sequential_certificate_source_sha256']!=sha(core_file):
        raise ValueError('Certificate code hash differs from frozen protocol')
    expect=protocol['seeds']['count']*len(protocol['regimes'])
    if len(rows)!=manifest['rows'] or len(rows)!=expect:
        raise ValueError('Unexpected number of worlds/results')
    if expect_worlds is not None and protocol['seeds']['count']!=expect_worlds:
        raise ValueError('Unexpected worlds-per-regime count')
    if len(summary)!=len(protocol['regimes']):
        raise ValueError('Summary regime count mismatch')
    seen=set()
    for row in rows:
        key=(int(row['seed']),row['regime'])
        if key in seen:raise ValueError('Duplicate world row')
        seen.add(key)
        if row['regime'] not in protocol['regimes']:raise ValueError('Unexpected regime')
        for p in ('fixed','finite','unbounded'):
            n=int(row[p+'_n_per_action']);observations=int(row[p+'_total_observations'])
            if n<0 or n>protocol['max_samples_per_action'] or observations!=n*len(protocol['actions']):
                raise ValueError('Evidence accounting contradiction')
            if int(row[p+'_certified']) and row[p+'_status']!='certified_best':
                raise ValueError('Certificate status contradiction')
            if int(row[p+'_false_cert']) and not int(row[p+'_certified']):
                raise ValueError('False-certificate flag contradiction')
        if row['declared_shift']=='' and any(row[p+'_status']!='hold_unknown_shift' for p in ('fixed','finite','unbounded')):
            raise ValueError('Unknown-shift fallback violation')
    return {'verified':True,'rows':len(rows),'worlds_per_regime':protocol['seeds']['count'],
            'regimes':len(protocol['regimes']),'source_snapshot':'preseal' if preseal else 'final',
            'source_hashes_match':True,'file_hashes_match':True}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('experiment');p.add_argument('--root',default='.')
    p.add_argument('--preseal',action='store_true',help='Explicitly audit an exploratory run against archived preseal source')
    a=p.parse_args()
    print(json.dumps(verify(Path(a.experiment),Path(a.root),preseal=a.preseal),indent=2))
