"""Verify frozen Stage M experiment receipts, source version and aggregates.

This is a reproducibility/integrity test, not an authenticity signature.
"""
from __future__ import annotations

import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import sys


def checked(directory:Path,root:Path) -> dict:
    if not directory.is_dir():raise FileNotFoundError(directory)
    manifest=json.loads((directory/'SHA256SUMS.json').read_text())
    actual={p.name for p in directory.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'}
    if set(manifest)!=actual:raise ValueError('Experiment inventory mismatch')
    for f,expected in manifest.items():
        if sha256((directory/f).read_bytes()).hexdigest()!=expected:
            raise ValueError('Experiment SHA mismatch: '+f)
    protocol=json.loads((directory/'protocol.json').read_text())
    if protocol['version']!='2.1.0' or protocol['stage']!='M':
        raise ValueError('Unexpected protocol')
    for name,expected in protocol['source_hashes_sha256'].items():
        path=root/'src'/'agentic_crystallization'/name
        if not path.is_file() or sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError('Frozen source mismatch: '+name)
    sys.path.insert(0,str(root/'src'))
    from agentic_crystallization.stage_m import summarize
    with (directory/'runs.csv').open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    numeric=('seed','epoch','certifications','memory_recertifications','alarm','monitor_n',
             'actual_large_drop','missed_drift','false_alarm','inappropriate_deployment_blocks',
             'harmful_deployment_blocks','false_promotions','task_count','total_queries',
             'total_prediction_ops','memory_size','memory_retired','memory_needs_renewal')
    floats=('true_gain0','true_gain1','true_gain2','observed_gain0','observed_gain1',
            'observed_gain2','net_surplus','credits')
    for r in rows:
        for key in numeric:r[key]=int(r[key])
        for key in floats:r[key]=float(r[key])
        for name in ('feedback_trustworthy','feedback_available'):
            if r[name] not in ('True','False'):raise ValueError('Invalid bool field')
        if r['credits']<0:raise ValueError('Overdraft')
        if r['certifications'] and r['false_promotions']>r['certifications']:
            raise ValueError('False-promotion count inconsistent')
    regimes=tuple(protocol['regimes']);policies=tuple(protocol['policies']);epochs=protocol['epochs_per_world']
    expected_rows=protocol['worlds']*len(regimes)*len(policies)*epochs
    if len(rows)!=expected_rows:raise ValueError('Wrong number of rows')
    expected={(seed,regime,pol,epoch) for seed in range(protocol['start_seed'],protocol['start_seed']+protocol['worlds'])
             for regime in regimes for pol in policies for epoch in range(1,epochs+1)}
    found={(r['seed'],r['regime'],r['policy'],r['epoch']) for r in rows}
    if found!=expected or len(found)!=len(rows):raise ValueError('Missing/duplicate/unexpected evaluation')
    recomputed=summarize(rows)
    stored=json.loads((directory/'summary.json').read_text())
    if recomputed!=stored:raise ValueError('Aggregate summary differs from raw data')
    return {'stage':'M','valid':True,'rows':len(rows),'worlds':protocol['worlds'],
            'source_hash_verified':True,'all_rows_reconciled':True,
            'experiment_files_verified':len(manifest)}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('experiment',type=Path)
    p.add_argument('--repo',type=Path,default=Path('.'))
    args=p.parse_args()
    print(json.dumps(checked(args.experiment.resolve(),args.repo.resolve()),indent=2))
