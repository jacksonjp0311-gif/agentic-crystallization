"""Read-only verifier for frozen Agentic Crystallization Stage J experiments.

This is a file integrity / design-contract check, not independent certification
of source truth or of the experiment's scientific conclusions.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_json(path):
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 10_000_000:
        raise ValueError('Missing, linked, or oversized experiment record: '+str(path))
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict):raise ValueError('Experiment record is not an object: '+str(path))
    return value


def verify(directory:Path):
    directory=Path(directory).resolve(strict=True)
    manifest=get_json(directory/'manifest.json')
    proto=get_json(directory/'protocol.json')
    if manifest.get('schema')!='agentic-crystallization-stage-j-manifest/1' or proto.get('schema')!='agentic-crystallization-stage-j/1':
        raise ValueError('Unsupported experiment schema.')
    if manifest.get('version')!=proto.get('version') or manifest.get('stage')!=proto.get('stage'):
        raise ValueError('Experiment version or split mismatch.')
    for name,claimed in (('protocol.json',manifest.get('protocol_sha256')),('runs.csv',manifest.get('runs_sha256')),
                         ('summary.json',manifest.get('summary_sha256'))):
        if digest(directory/name)!=claimed:raise ValueError(name+' differs from frozen manifest.')
    for source,hash_field in (('stage_j.py','stage_j_source_sha256'),('robust_calibration.py','calibration_source_sha256')):
        if digest(ROOT/'src/agentic_crystallization'/source)!=proto.get(hash_field):
            raise ValueError('Source code no longer matches frozen protocol: '+source)
    seedinfo=proto.get('seeds')
    if not isinstance(seedinfo,dict) or type(seedinfo.get('count')) is not int or seedinfo['count']<=0:
        raise ValueError('Invalid recorded seed cohort.')
    combos={(sc,n) for sc in proto['scenarios'] for n in proto['sample_sizes']}
    expected=seedinfo['count']*len(combos)
    with (directory/'runs.csv').open('r',encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=expected or len(rows)!=manifest.get('world_rows'):
        raise ValueError('Incorrect row count or incomplete factorial cohort.')
    seen=set()
    for row in rows:
        try:seed=int(row['seed']);n=int(row['n']);sc=row['scenario']
        except (ValueError,KeyError,TypeError) as e:raise ValueError('Malformed CSV experiment identity.') from e
        if seed<seedinfo['min'] or seed>seedinfo['max'] or (sc,n) not in combos:
            raise ValueError('Row is outside frozen seed/condition scope.')
        identity=(seed,sc,n)
        if identity in seen:raise ValueError('Duplicate world-condition row.')
        seen.add(identity)
        if row.get('calibration_draws')!=str(n*len(proto['action_library'])):
            raise ValueError('Calibration effort was not fully recorded.')
        if row.get('scenario')=='unknown_shift' and (row.get('robust_status')!='hold' or row.get('coverage')!=''):
            raise ValueError('Unknown-shift evidence was turned into a false certificate.')
    if {seed for seed,_,_ in seen}!=set(range(seedinfo['min'],seedinfo['max']+1)):
        raise ValueError('Seed series is incomplete or nonconsecutive.')
    sums=json.loads((directory/'summary.json').read_text(encoding='utf-8'))
    if not isinstance(sums,list) or len(sums)!=len(combos) or sum(x.get('worlds',0) for x in sums)!=expected:
        raise ValueError('Summary coverage does not match frozen experiment cohort.')
    return {'status':'verified_file_integrity_and_scope','directory':str(directory),
            'world_parameters':seedinfo['count'],'condition_rows':len(rows),
            'source_identical':True,'manifest_integrity':True,
            'limitation':'These checks do not establish phase transition, scientific causality or real Pegasus adaptation.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory',type=Path,help='Stage J directory with frozen protocol, raw CSV, summary and manifest')
    args=ap.parse_args()
    try:
        print(json.dumps(verify(args.directory),indent=2))
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as error:
        print(json.dumps({'status':'FAIL','error':str(error)},indent=2))
        sys.exit(1)
