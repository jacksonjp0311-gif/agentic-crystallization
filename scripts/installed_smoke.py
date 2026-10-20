"""Run with an isolated installed interpreter outside the checkout."""
from importlib.metadata import version
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from agentic_crystallization.evidence_api import evaluate, ReceiptLedger
from agentic_crystallization.example_evidence import example
from agentic_crystallization.api_version import IMPLEMENTATION_VERSION, API_SCHEMA

assert version("agentic-crystallization")==IMPLEMENTATION_VERSION
e=example()
context=dict(now=10,current_epoch=0,current_context="demo-context")
r=evaluate(e,**context)
assert r.schema==API_SCHEMA and r.status=="CERTIFY_CURRENT"
cycle=[];cycle.append(cycle)
assert evaluate(replace(e,protocol=replace(e.protocol,context=cycle)),**context).status=="HOLD"
with TemporaryDirectory() as td:
    ledger=ReceiptLedger(Path(td)/"receipt.sqlite")
    ledger.evaluate_and_record(e,**context)
    try:
        ledger.record(e,replace(r,selected="B"),**context)
    except ValueError:
        pass
    else:
        raise AssertionError("Altered receipt accepted")
print(IMPLEMENTATION_VERSION,API_SCHEMA,"isolated wheel smoke PASS")
