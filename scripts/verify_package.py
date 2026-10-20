"""Verify all files in an extracted Agentic Crystallization release.

SHA256 integrity detects accidental changes; it is not a digital signature.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import argparse


def verify(root:Path)->dict:
    root=Path(root).resolve()
    manifest=json.loads((root/'PACKAGE_SHA256SUMS.json').read_text())
    files=manifest['files']
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='PACKAGE_SHA256SUMS.json'}
    if set(files)!=actual:
        raise ValueError(f'Package file inventory differs: missing={sorted(set(files)-actual)}, extra={sorted(actual-set(files))}')
    for relative,expected in files.items():
        path=(root/relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Manifest contains path outside package')
        actual_digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_digest!=expected:
            raise ValueError(f'SHA256 mismatch: {relative}')
    return {'verified':True,'version':manifest.get('version'),'checked_files':len(files),
            'statement':'All files match SHA256 manifest; this is not an external authenticity signature.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('root',nargs='?',default='.')
    args=parser.parse_args()
    print(json.dumps(verify(Path(args.root)),indent=2))
