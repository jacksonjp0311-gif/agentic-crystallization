"""Stage J reproducibility, negative controls, shift and resource boundaries."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from agentic_crystallization.stage_j import (one,run,world,true_net,FAMILIES,SCENARIOS,N_LEVELS)

class StageJTests(unittest.TestCase):
    def test_world_determinism(self):
        self.assertEqual(world(10001),world(10001))
        self.assertNotEqual(world(10001),world(10002))

    def test_additive_and_misleading_zero_three_way_interaction(self):
        from agentic_crystallization.stability import finite_difference
        for seed in (10000,10003):
            w=world(seed)
            self.assertIn(w['family'],('additive','misleading_graph'))
            q=true_net(w,.21)
            gamma=finite_difference({s:q[a] for a,s in __import__('agentic_crystallization.stage_j',fromlist=['ACTIONS']).ACTIONS.items() if s<=frozenset('abc')},frozenset('abc'))
            self.assertAlmostEqual(gamma,0.,places=10)

    def test_shift_violation_can_be_detected_against_oracle(self):
        # Failure-mode family: declared TV bound is *not* justified.
        candidate=[one(seed,'violated_shift',6400) for seed in range(10002,10018,4)]
        self.assertTrue(any(x['coverage']==0 for x in candidate))
        self.assertTrue(any(x['certified_best_wrong'] or x['certified_gain_harmful'] for x in candidate))

    def test_unknown_shift_unchanged_baseline(self):
        x=one(10002,'unknown_shift',200)
        self.assertEqual(x['robust_status'],'hold')
        self.assertEqual(x['robust_action'],'baseline')
        self.assertEqual(x['coverage'],'')

    def test_complete_factorial_interaction_sign(self):
        x=one(10002,'iid_related',6400)
        self.assertEqual(x['family'],'triple')
        self.assertEqual(x['interaction_status'],'positive')
        self.assertGreater(x['true_interaction'],0)

    def test_new_output_paths_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'stage_j'
            report=run(out,seeds=range(10000,10004),stage='dev_fixture')
            self.assertEqual(sum(x['worlds'] for x in report),4*len(SCENARIOS)*len(N_LEVELS))
            self.assertTrue((out/'manifest.json').exists())
            manifest=json.loads((out/'manifest.json').read_text())
            self.assertEqual(hashlib.sha256((out/'runs.csv').read_bytes()).hexdigest(),manifest['runs_sha256'])
            with self.assertRaises(ValueError):run(out,seeds=range(10000,10004))

    def test_identical_seed_reproducibility(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'a';b=Path(d)/'b'
            run(a,seeds=range(10000,10003));run(b,seeds=range(10000,10003))
            self.assertEqual((a/'runs.csv').read_bytes(),(b/'runs.csv').read_bytes())
            self.assertEqual((a/'summary.json').read_bytes(),(b/'summary.json').read_bytes())

    def test_output_scope(self):
        x=one(10001,'iid_related',1000)
        self.assertGreaterEqual(x['robust_regret'],-1e-8)
        self.assertIn(x['robust_status'],('certified_best','certified_gain','fallback'))
        self.assertEqual(x['calibration_draws'],1000*9)

if __name__=='__main__':unittest.main()
