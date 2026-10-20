"""v1.9 mathematical and API contract tests; previous-version tests untouched."""
import math
import unittest

from agentic_crystallization import sequential_certificate as s


class SequentialMathTests(unittest.TestCase):
    def test_finite_single_look_equals_fixed_bound(self):
        self.assertAlmostEqual(s.checkpoint_radius(400,6,1,total_looks=1),s.fixed_radius(400,6))

    def test_more_looks_require_more_caution(self):
        self.assertGreater(s.checkpoint_radius(400,6,1,total_looks=9),s.fixed_radius(400,6))

    def test_more_samples_reduce_radius(self):
        a=s.checkpoint_radius(100,6,4,total_looks=9)
        b=s.checkpoint_radius(1000,6,4,total_looks=9)
        self.assertGreater(a,b)

    def test_infinite_spending_sum_is_one(self):
        self.assertAlmostEqual(sum(1/(j*(j+1)) for j in range(1,100000)),1-1/100000,places=12)

    def test_infinite_radius_conservative_at_same_look(self):
        self.assertGreater(s.checkpoint_radius(800,6,5,total_looks=None),
                           s.checkpoint_radius(800,6,5,total_looks=9))

    def test_alpha_decreases_confidence_radius(self):
        self.assertGreater(s.fixed_radius(100,6,alpha=.01),s.fixed_radius(100,6,alpha=.1))

    def test_reject_invalid_alpha_and_bool_n(self):
        for bad in (-.1,0,1,float('nan'),True):
            with self.assertRaises(ValueError):s.fixed_radius(10,3,alpha=bad)
        with self.assertRaises(ValueError):s.fixed_radius(True,3)

    def test_reject_invalid_look_indices(self):
        with self.assertRaises(ValueError):s.checkpoint_radius(50,6,0,total_looks=9)
        with self.assertRaises(ValueError):s.checkpoint_radius(50,6,10,total_looks=9)

    def test_certifies_clear_winner(self):
        n=1000
        report=s.certificate({'baseline':100,'candidate':950},{'baseline':0,'candidate':0},n,
                             radius=.10,shift_tv_bound=.05)
        self.assertEqual(report['status'],'certified_best')
        self.assertEqual(report['action'],'candidate')
        self.assertGreater(report['margin'],0)

    def test_correctly_refuses_overlap(self):
        report=s.certificate({'baseline':510,'candidate':520},{'baseline':0,'candidate':0},1000,
                             radius=.1,shift_tv_bound=0.)
        self.assertEqual(report['status'],'continue')

    def test_gain_does_not_imply_best(self):
        n=100000
        sums={'baseline':10000,'alpha':70000,'beta':70500}
        costs=dict.fromkeys(sums,0.)
        gain=s.certificate(sums,costs,n,radius=.01,shift_tv_bound=0.,objective='gain')
        best=s.certificate(sums,costs,n,radius=.01,shift_tv_bound=0.,objective='best')
        self.assertEqual(gain['status'],'certified_gain')
        self.assertFalse(gain['certified_best'])
        self.assertEqual(best['status'],'continue')

    def test_missing_shift_refuses_certification(self):
        d=s.certificate({'baseline':0,'a':1000},{'baseline':0,'a':0},1000,
                        radius=.001,shift_tv_bound=None)
        self.assertEqual(d['status'],'hold_unknown_shift')
        self.assertEqual(s.preflight({'baseline':0,'a':0},None),'hold_unknown_shift')

    def test_wide_equal_cost_proves_impossible(self):
        c={'baseline':.05,'a':.05,'b':.05}
        self.assertEqual(s.preflight(c,.5),'hold_impossible_under_bounds')
        self.assertIsNone(s.preflight(c,.499))

    def test_wide_unequal_cost_does_not_prune(self):
        self.assertIsNone(s.preflight({'baseline':.2,'a':0},.9))

    def test_source_cost_units_are_separate(self):
        result=s.certificate({'baseline':50,'a':60},{'baseline':0,'a':.5},100,
                            radius=.001,shift_tv_bound=0.)
        self.assertEqual(result['status'],'certified_best')
        self.assertEqual(result['action'],'baseline')

    def test_reject_mismatched_action_library(self):
        with self.assertRaises(ValueError):
            s.certificate({'baseline':100},{'baseline':0.,'a':0.},100,
                          radius=.01,shift_tv_bound=0.)

    def test_reject_unphysical_shift(self):
        with self.assertRaises(ValueError):
            s.certificate({'baseline':50,'a':60},{'baseline':0,'a':0},100,
                          radius=.01,shift_tv_bound=1.01)

    def test_no_false_claim_when_intervals_cover_truth(self):
        # Deterministic theorem check: if all intervals cover truth, a
        # certified best must truly outrank the alternative.
        truth={'baseline':.2,'a':.8,'b':.3}
        out=s.certificate({'baseline':20,'a':80,'b':30},{a:0 for a in truth},100,
                          radius=.05,shift_tv_bound=.02)
        self.assertTrue(out['certified_best'])
        self.assertTrue(all(out['intervals'][a]['lower']<=truth[a]<=out['intervals'][a]['upper']
                            for a in truth))
        self.assertEqual(out['action'],max(truth,key=truth.get))

    def test_false_shift_invalidates_inference(self):
        # A counterexample showing that coverage assumptions are essential.
        out=s.certificate({'baseline':100,'a':950},{'baseline':0,'a':0},1000,
                          radius=.01,shift_tv_bound=.02)
        target={'baseline':.95,'a':.05}
        self.assertTrue(out['certified_best'])
        self.assertLess(target[out['action']],target['baseline'])


if __name__=='__main__':unittest.main()
