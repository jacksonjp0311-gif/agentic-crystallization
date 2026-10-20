"""Regenerate complete frozen Stage P cohorts in a separate non-overwriting folder."""
import hashlib
import json
from pathlib import Path
import sys
import argparse

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from agentic_crystallization.stage_p import run
from agentic_crystallization.adaptive_trust import TrustConfig


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--resume",action="store_true",help="Verify existing output and generate missing cohorts without overwriting")
    args=parser.parse_args()
    destination=ROOT/"work/reproduction"
    destination.mkdir(parents=True,exist_ok=args.resume)
    report=[]
    for cohort in ("stage_p_holdout","stage_p_replication"):
        frozen=ROOT/"experiments"/cohort
        protocol=json.loads((frozen/"protocol.json").read_text())
        out=destination/cohort
        if not out.exists():
            run(out,protocol["start_seed"],protocol["count"],TrustConfig(**protocol["config"]))
        matches={name:hashlib.sha256((out/name).read_bytes()).hexdigest()==hashlib.sha256((frozen/name).read_bytes()).hexdigest()
                 for name in ("runs.csv","summary.json","protocol.json","SHA256SUMS.json")}
        semantic={name:json.loads((out/name).read_text())==json.loads((frozen/name).read_text())
                  for name in ("summary.json","protocol.json")}
        generated_hashes=json.loads((out/"SHA256SUMS.json").read_text())
        integrity=all(hashlib.sha256((out/name).read_bytes()).hexdigest()==digest
                      for name,digest in generated_hashes.items())
        report.append({"cohort":cohort,"exact_matches":matches,"semantic_matches":semantic,
                       "generated_hashes_verified":integrity,
                       "boundary":"Windows JSON CRLF differs from historical LF; raw CSV must match exactly."})
        print(json.dumps(report[-1]),flush=True)
        if not matches["runs.csv"] or not all(semantic.values()) or not integrity:
            raise ValueError("Reproduction mismatch; preserve output for investigation")
    (destination/"report.json").write_text(json.dumps(report,indent=2)+"\n")


if __name__=="__main__":
    main()
