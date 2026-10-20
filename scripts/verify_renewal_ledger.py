"""Verify a v2.1 demonstration's durable JSONL receipt chain."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from agentic_crystallization.renewal_core import RenewalConfig,RenewalLedger
from agentic_crystallization.crystal_core import digest

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('path',type=Path)
    args=p.parse_args()
    state=RenewalLedger(args.path,RenewalConfig()).replay()
    print(json.dumps({'verified':True,'epochs':state.epoch,'credits':state.credits,
                      'retained_procedures':len(state.memory),'state_digest':digest(state.to_dict())},indent=2))
