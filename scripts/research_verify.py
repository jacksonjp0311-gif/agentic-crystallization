"""Verify preserved manifest subset and both frozen Stage P receipt cohorts."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.verify_stage_p import verify


def main():
    manifest=json.loads((ROOT/"docs/provenance/ORIGINAL_PACKAGE_SHA256SUMS.json").read_text())
    checked=0;archives=[];bytecode=[]
    remapped={"README.md":"docs/provenance/original_README.md","run.ps1":"docs/provenance/original_run.ps1"}
    for name, expected in manifest["files"].items():
        if name.endswith(".pyc"):
            bytecode.append(name)
            continue
        if name.endswith(".zip"):
            archives.append({"path":name,"sha256":expected})
            continue
        p=ROOT/remapped.get(name,name)
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise ValueError("Historical content changed: "+name)
        checked+=1
    result={"preserved_files_verified":checked,"generated_bytecode_excluded":bytecode,"archives_excluded_from_git":archives,
            "cohorts":[verify(ROOT,c) for c in ("stage_p_holdout","stage_p_replication")]}
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
