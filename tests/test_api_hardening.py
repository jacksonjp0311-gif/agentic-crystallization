from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from agentic_crystallization import evidence_api as api
from agentic_crystallization.example_evidence import example

CONTEXT = dict(now=10, current_epoch=0, current_context="demo-context")


class InputBoundaryTests(unittest.TestCase):
    def reject(self, evidence):
        with patch.object(api, "asdict", side_effect=AssertionError("serialization reached")):
            r = api.evaluate(evidence, **CONTEXT)
        self.assertEqual((r.status, r.reason), ("HOLD", "invalid_bounded_structure"))
        self.assertLess(len(r.to_json()), 1000)

    def test_cycle_before_serialization(self):
        cycle=[];cycle.append(cycle)
        self.reject(replace(example(), protocol=replace(example().protocol, context=cycle)))

    def test_deep_nesting_before_serialization(self):
        x=0
        for _ in range(10000):
            x=(x,)
        self.reject(replace(example(), measurements=x))

    def test_uninitialized_and_wrong_dataclasses(self):
        for x in (object.__new__(api.Evidence), object(), {}, example().protocol, None):
            self.reject(x)

    def test_subclasses_and_behavioral_objects(self):
        class Trick:
            def __deepcopy__(self, memo):
                raise AssertionError("untrusted method invoked")
        class Sub(api.Evidence):
            pass
        self.reject(replace(example(), protocol=Trick()))
        self.reject(Sub(**vars(example())))

    def test_nonfinite_boolean_large_integer(self):
        e=example()
        for value in (True, float("nan"), float("inf"), 10**10000, object(), (0,)):
            self.reject(replace(e,measurements=(replace(e.measurements[0],samples=(value,)*1024),)+e.measurements[1:]))

    def test_text_limit_and_total_bytes(self):
        self.reject(replace(example(),protocol=replace(example().protocol,context="x"*(api.MAX_TEXT+1))))
        e=example()
        self.reject(replace(e,measurements=tuple(replace(m,provenance="\U0001f600"*api.MAX_TEXT) for m in e.measurements)))

    def test_sample_limit_before_iteration(self):
        e=example()
        self.reject(replace(e,measurements=(replace(e.measurements[0],samples=(.8,)*(api.MAX_SAMPLES+1)),)+e.measurements[1:]))

    def test_boundary_sample_and_text_valid(self):
        e=example()
        e=replace(e,protocol=replace(e.protocol,sample_counts=(api.MAX_SAMPLES,)*3,
                                    sampling_design="x"*api.MAX_TEXT),
                  measurements=tuple(replace(m,samples=(m.samples[0],)*api.MAX_SAMPLES) for m in e.measurements))
        r=api.evaluate(e,**CONTEXT)
        self.assertEqual(r.status,"CERTIFY_CURRENT")
        self.assertLess(len(json.dumps(asdict(e))), 4*1024*1024)

    def test_missing_evaluator(self):
        self.reject(replace(example(),protocol=replace(example().protocol,evaluator_revision="")))

    def test_invalid_trusted_time_exception(self):
        for x in (True,float("nan"),10**10000,-1,None):
            with self.assertRaises(ValueError):
                api.evaluate(example(),**(CONTEXT|{"now":x}))


class LedgerBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"ledger.sqlite"
        self.ledger=api.ReceiptLedger(self.path)

    def test_trusted_operation_and_restart(self):
        r=self.ledger.evaluate_and_record(example(),**CONTEXT)
        self.assertEqual(api.ReceiptLedger(self.path).replay(),[json.loads(r.to_json())])

    def test_all_receipt_decisions_checked(self):
        e=example();r=api.evaluate(e,**CONTEXT)
        for kw in ({"selected":"B"},{"status":"ALARM"},{"bounds":{}},{"verification_cost":0},
                   {"assumptions":()},{"reason":"forged"},{"implementation_version":"1.0.0"}):
            with self.assertRaises(ValueError):
                self.ledger.record(e,replace(r,**kw),**CONTEXT)
        self.assertEqual(self.ledger.replay(),[])

    def test_cyclic_receipt_is_not_serialized(self):
        d={};d["primary"]=d
        with self.assertRaises(ValueError):
            self.ledger.record(example(),replace(api.evaluate(example(),**CONTEXT),bounds=d),**CONTEXT)

    def test_concurrent_duplicate_atomicity(self):
        def submit(_):
            try:
                self.ledger.evaluate_and_record(example(),**CONTEXT)
                return "stored"
            except ValueError:
                return "duplicate"
        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes=list(pool.map(submit,range(8)))
        self.assertEqual(outcomes.count("stored"),1)
        self.assertEqual(outcomes.count("duplicate"),7)
        self.assertEqual(len(api.ReceiptLedger(self.path).replay()),1)

    def test_late_sample_conflict_rolls_back(self):
        e=example()
        self.ledger.evaluate_and_record(e,**CONTEXT)
        new=replace(e,protocol=replace(e.protocol,identity="new"),
                    measurements=tuple(replace(m,receipt_id="new-"+m.receipt_id) if i<5 else m
                                       for i,m in enumerate(e.measurements)))
        with self.assertRaises(ValueError):
            self.ledger.evaluate_and_record(new,**CONTEXT)
        from contextlib import closing
        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM protocols").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM samples").fetchone()[0],6)
        fixed=replace(new,measurements=tuple(replace(m,receipt_id="all-new-"+m.receipt_id) for m in new.measurements))
        self.ledger.evaluate_and_record(fixed,**CONTEXT)
        self.assertEqual(len(self.ledger.replay()),2)

    def test_replay_not_current_certification(self):
        e=example();r=self.ledger.evaluate_and_record(e,**CONTEXT)
        for kw in ({"now":20},{"current_epoch":1},{"current_context":"new"}):
            self.assertEqual(api.evaluate(e,**(CONTEXT|kw)).status,"STALE")
            with self.assertRaises(ValueError):
                self.ledger.record(e,r,**(CONTEXT|kw))
        self.assertEqual(self.ledger.replay()[0]["status"],"CERTIFY_CURRENT")

    def test_protocol_mutation_rejected(self):
        e=example();self.ledger.evaluate_and_record(e,**CONTEXT)
        for kw in ({"alpha":.1},{"evaluator_revision":"different"},{"epochs":25}):
            altered=replace(e,protocol=replace(e.protocol,**kw))
            with self.assertRaises(ValueError):
                self.ledger.evaluate_and_record(altered,**CONTEXT)

    def test_renaming_does_not_prove_new_observations(self):
        e=example()
        # Pure mathematical evaluation is repeatable, never accumulation.
        self.assertEqual(api.evaluate(e,**CONTEXT),api.evaluate(e,**CONTEXT))
        renamed=replace(e,protocol=replace(e.protocol,identity="new-label"),
                        measurements=tuple(replace(m,receipt_id="new-"+m.receipt_id) for m in e.measurements))
        self.assertEqual(api.evaluate(e,**CONTEXT).bounds,api.evaluate(renamed,**CONTEXT).bounds)
        # The caller must govern campaign allocation; labels do not authenticate data.
