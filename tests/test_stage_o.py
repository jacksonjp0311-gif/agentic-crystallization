import json,tempfile,unittest
from pathlib import Path
from agentic_crystallization.feedback_integrity import (
    IntegrityConfig,IntegrityState,radius,certified_best,disagreement,
    decide,cue_calibration,POLICIES)
from agentic_crystallization.stage_o import (
    calibrate,run_world,run,REGIMES,world_observations)

class FeedbackIntegrityTests(unittest.TestCase):
    def setUp(self):self.cfg=IntegrityConfig()
    def test_simultaneous_radius(self):
        self.assertGreater(radius(384,self.cfg),0)
        self.assertLess(radius(384,self.cfg),.25)
    def test_certificate_and_hold(self):
        self.assertEqual(certified_best({'A':.7,'B':-.7},384,self.cfg),'A')
        self.assertIsNone(certified_best({'A':0.,'B':0.},384,self.cfg))
    def test_strong_disagreement(self):
        self.assertTrue(disagreement({'A':.6,'B':-.6},{'A':-.6,'B':.6},self.cfg))
        self.assertFalse(disagreement({'A':.4,'B':-.4},{'A':.4,'B':-.4},self.cfg))
    def test_reject_malformed(self):
        with self.assertRaises(ValueError):certified_best({'A':float('nan'),'B':0.},384,self.cfg)
        with self.assertRaises(ValueError):IntegrityConfig(alpha=1.)
    def test_guard_requires_both_channels_for_fresh_certificate(self):
        event,state=decide('guard',0,IntegrityState(),False,{'A':.7,'B':-.7},None,self.cfg)
        self.assertTrue(event['held']);self.assertFalse(event['fresh_certificate'])
        self.assertTrue(event['anchor_unavailable'])
    def test_guard_rejects_disagreement(self):
        event,state=decide('guard',0,IntegrityState(),False,
                            {'A':.7,'B':-.7},{'A':-.7,'B':.7},self.cfg)
        self.assertTrue(event['disagreement_alarm']);self.assertTrue(event['held'])
        self.assertFalse(event['fresh_certificate'])
    def test_guard_can_certify_when_agree(self):
        event,state=decide('guard',0,IntegrityState(),False,
                            {'A':.7,'B':-.7},{'A':.7,'B':-.7},self.cfg)
        self.assertEqual(event['selected'],'A');self.assertTrue(event['fresh_certificate'])
    def test_primary_only_can_be_deceived(self):
        event,_=decide('primary_risk',0,IntegrityState(),False,
                       {'A':-.7,'B':.7},{'A':.7,'B':-.7},self.cfg)
        self.assertEqual(event['selected'],'B')
    def test_calibration_interval(self):
        c=cue_calibration([(True,True)]*20+[(False,False)]*20)
        self.assertTrue(c['bounds']['sensitivity']['lower']<1)
        self.assertTrue(c['bounds']['specificity']['upper']==1)
        with self.assertRaises(ValueError):cue_calibration([(True,True)])
    def test_calibration_deterministic(self):self.assertEqual(calibrate(n_per_class=30),calibrate(n_per_class=30))
    def test_shared_observations(self):
        a=world_observations(100,'deceptive_primary',10,self.cfg)
        self.assertEqual(a,world_observations(100,'deceptive_primary',10,self.cfg))
    def test_world_reproducible(self):
        self.assertEqual(run_world(100,'stationary',self.cfg),run_world(100,'stationary',self.cfg))
    def test_all_regimes_and_policies(self):
        for reg in REGIMES:
            rows=run_world(100,reg,self.cfg)
            self.assertEqual(len(rows),len(POLICIES)*self.cfg.epochs)
    def test_single_channel_deception_guard_no_false_cert(self):
        for reg in ('deceptive_primary','deceptive_anchor'):
            rows=[x for x in run_world(100,reg,self.cfg) if x['policy']=='guard']
            self.assertEqual(sum(x['false_certificate'] for x in rows),0)
            self.assertGreater(sum(x['disagreement_alarm'] for x in rows),0)
    def test_common_mode_counterexample(self):
        rows=[x for x in run_world(100,'common_mode',self.cfg) if x['policy']=='guard']
        self.assertGreater(sum(x['false_certificate'] for x in rows),0)
    def test_missing_anchor_holds(self):
        rows=[x for x in run_world(100,'missing_anchor',self.cfg) if x['policy']=='guard']
        self.assertGreater(sum(x['anchor_unavailable'] for x in rows),0)
    def test_unlearnable_does_not_certify(self):
        rows=[x for x in run_world(100,'unlearnable',self.cfg) if x['policy']=='guard']
        self.assertEqual(sum(x['fresh_certificate'] for x in rows),0)
    def test_nonoverwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'run';run(p,12,1)
            with self.assertRaises(FileExistsError):run(p,12,1)
    def test_source_hash_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'run';run(p,13,1)
            protocol=json.loads((p/'protocol.json').read_text())
            self.assertEqual(protocol['rows'],len(REGIMES)*len(POLICIES)*24)
            self.assertEqual(len(protocol['source_hashes']),4)

if __name__=='__main__':unittest.main()
