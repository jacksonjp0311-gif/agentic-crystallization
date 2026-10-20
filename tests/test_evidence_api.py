import json
from dataclasses import replace
import tempfile
from pathlib import Path
import unittest

from agentic_crystallization.evidence_api import evaluate, ReceiptLedger
from agentic_crystallization.example_evidence import example


class ExternalEvidenceTests(unittest.TestCase):
    def check(self, e=None, **kwargs):
        return evaluate(e or example(), **({"now":10,"current_epoch":0,"current_context":"demo-context"} | kwargs))

    def changed(self, **changes):
        e=example()
        return replace(e, measurements=(replace(e.measurements[0], **changes),)+e.measurements[1:])

    def test_certification(self):
        r=self.check()
        self.assertEqual((r.status,r.selected),("CERTIFY_CURRENT","A"))
        self.assertEqual(json.loads(r.to_json())["reason"],"conditional_current_certificate")

    def test_insufficient(self):
        e=example()
        self.assertEqual(self.check(replace(e,measurements=tuple(replace(m,samples=(0.0,)*1024) for m in e.measurements))).status,"HOLD")

    def test_corrupted_feedback(self):
        e=example()
        e=replace(e,measurements=tuple(replace(m,samples=tuple(-x for x in m.samples)) if m.channel=="primary" else m for m in e.measurements))
        self.assertEqual(self.check(e).status,"ALARM")

    def test_shared_corruption_unidentifiable(self):
        # Same observations can describe opposite latent truths. Honesty is not detectable here.
        self.assertEqual(self.check().status,"CERTIFY_CURRENT")
        e=example()
        bad=replace(e,protocol=replace(e.protocol,reference_assumption=""))
        self.assertEqual(self.check(bad).status,"HOLD")

    def test_missing_reference(self):
        e=example()
        self.assertEqual(self.check(replace(e,measurements=e.measurements[:4])).status,"HOLD")

    def test_stale(self):
        for args in ({"now":20},{"current_epoch":1},{"current_context":"changed"}):
            self.assertEqual(self.check(**args).status,"STALE")

    def test_ranges_and_counts(self):
        for kwargs in ({"lower":0},{"samples":(2.,)*1024},{"samples":(float("nan"),)*1024},{"samples":(.8,)*100},{"samples":(True,)*1024}):
            self.assertEqual(self.check(self.changed(**kwargs)).status,"HOLD")

    def test_identity(self):
        for kw in ({"candidate":"C"},{"baseline":"unknown"},{"channel":"audit"},{"provenance":""}):
            self.assertEqual(self.check(self.changed(**kw)).status,"HOLD")

    def test_duplicate(self):
        self.assertEqual(self.check(self.changed(receipt_id=example().measurements[1].receipt_id)).status,"HOLD")

    def test_audit_cost(self):
        self.assertAlmostEqual(self.check().verification_cost,.6)
        self.assertEqual(self.check(self.changed(verification_cost=-1)).status,"HOLD")
        e=example()
        invalid=replace(e,measurements=e.measurements[:-1]+(replace(e.measurements[-1],candidate="unknown"),))
        self.assertIsNone(self.check(invalid).verification_cost)

    def test_pre_audit_and_fixed_design(self):
        e=example()
        self.assertEqual(self.check(replace(e,audit_requested_at=5)).status,"HOLD")
        for kw in ({"fixed_before_observation":False},{"sample_counts":(True,1024,1024)},{"epochs":True},{"alpha":float("inf")}):
            self.assertEqual(self.check(replace(e,protocol=replace(e.protocol,**kw))).status,"HOLD")

    def test_ledger_reopen_replay_and_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"receipts.sqlite"
            ledger=ReceiptLedger(path);e=example();r=self.check(e)
            ledger.record(e,r)
            self.assertEqual(ReceiptLedger(path).replay(),[json.loads(r.to_json())])
            with self.assertRaises(ValueError):ledger.record(e,r)
            new=replace(e,protocol=replace(e.protocol,identity="new-protocol"))
            with self.assertRaises(ValueError):ledger.record(new,self.check(new))
            self.assertEqual(len(ledger.replay()),1)

    def test_receipt_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            ledger=ReceiptLedger(Path(d)/"r.sqlite")
            with self.assertRaises(ValueError):
                ledger.record(example(),replace(self.check(),evidence_digest="forged"))

    def test_no_host_permissions(self):
        import inspect
        import agentic_crystallization.evidence_api as api
        source=inspect.getsource(api)
        for forbidden in ("subprocess","import requests","import socket","import pegasus","os.system"):
            self.assertNotIn(forbidden,source)


if __name__=="__main__":
    unittest.main()
