"""Fresh Stage K generation/selection regression tests."""
import tempfile
from pathlib import Path
import json
import csv
import unittest
import numpy as np
from agentic_crystallization import stage_k as k


class StageKTests(unittest.TestCase):
    def test_actions_include_baseline(self):
        self.assertIn('baseline',k.ACTIONS)
        self.assertEqual(len(set(k.ACTIONS)),len(k.ACTIONS))

    def test_checkpoint_schedule_is_predeclared(self):
        self.assertEqual(list(k.LOOKS),sorted(set(k.LOOKS)))
        self.assertEqual(k.LOOKS[-1],k.MAX_N)

    def test_target_shift_contract(self):
        for name in k.REGIMES:
            w=k.make_world(10001,name)
            self.assertEqual(w['target_means'].shape,w['source_means'].shape)
            if w['assumption_valid']:
                self.assertLessEqual(w['eta'],w['declared_shift']+1e-12)
                self.assertTrue(np.all(np.abs(w['target_means']-w['source_means'])<=w['declared_shift']+1e-12))

    def test_same_seed_is_replayable(self):
        for condition in ('stationary_easy','bounded_shift','violated_shift','unknown_shift'):
            self.assertEqual(k.one(61000,condition),k.one(61000,condition))

    def test_no_data_on_unknown_shift(self):
        row=k.one(61000,'unknown_shift')
        for p in ('fixed','finite','unbounded'):
            self.assertEqual(row[p+'_status'],'hold_unknown_shift')
            self.assertEqual(row[p+'_total_observations'],0)

    def test_zero_data_when_bounds_cannot_separate(self):
        row=k.one(61000,'wide_valid_shift')
        for p in ('fixed','finite','unbounded'):
            self.assertEqual(row[p+'_status'],'hold_impossible_under_bounds')
            self.assertEqual(row[p+'_n_per_action'],0)

    def test_sample_limit_for_all_policies(self):
        for regime in k.REGIMES:
            row=k.one(61001,regime)
            for policy in ('fixed','finite','unbounded'):
                self.assertLessEqual(row[policy+'_n_per_action'],k.MAX_N)
                self.assertEqual(row[policy+'_total_observations'],len(k.ACTIONS)*row[policy+'_n_per_action'])

    def test_invalid_shift_is_visible_not_hidden(self):
        row=k.one(61001,'violated_shift')
        self.assertEqual(row['assumption_valid'],'False')
        self.assertGreater(row['true_mixture_eta'],float(row['declared_shift']))
        self.assertEqual(row['finite_false_cert'],1)

    def test_correct_shift_easy_certified(self):
        row=k.one(61001,'stationary_easy')
        self.assertTrue(row['finite_certified'])
        self.assertEqual(row['finite_false_cert'],0)
        self.assertLess(row['finite_n_per_action'],k.MAX_N)

    def test_near_tie_does_not_invent_certainty(self):
        row=k.one(61001,'stationary_near_tie')
        self.assertFalse(row['finite_certified'])

    def test_fresh_reproducible_output_and_sealed_sources(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)/'first'
            summary=k.run(folder,start_seed=61002,count=2,stage='development')
            with (folder/'runs.csv').open(newline='',encoding='utf-8') as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),len(k.REGIMES)*2)
            self.assertEqual(len(summary),len(k.REGIMES))
            manifest=json.loads((folder/'manifest.json').read_text())
            self.assertEqual(manifest['rows'],len(rows))
            with self.assertRaises(ValueError):
                k.run(folder,start_seed=61002,count=2,stage='development')


if __name__=='__main__':unittest.main()

class StageKIsolationTests(unittest.TestCase):
    def test_decision_policy_has_no_oracle_world_argument(self):
        import inspect
        from agentic_crystallization import stage_k as k
        args=list(inspect.signature(k._policy).parameters)
        self.assertEqual(args,['shift','prefix','kind'])
