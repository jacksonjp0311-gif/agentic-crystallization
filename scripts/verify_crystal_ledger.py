"""Verify and reconstruct the default CrystalKernel demonstration receipt chain."""
import argparse
import json
from pathlib import Path
from agentic_crystallization.crystal_core import Configuration,DurableLedger,digest

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('ledger',type=Path)
    args=ap.parse_args()
    state=DurableLedger(args.ledger,Configuration()).replay()
    print(json.dumps({'verified':True,'epochs':state.epoch,
                      'state_commitment':digest(state.to_dict()),
                      'memory':state.memory,'credits':state.credits},indent=2,sort_keys=True))
