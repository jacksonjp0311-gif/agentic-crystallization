"""Mathematical invariant tests for Agentic Crystallization v1.8."""
import math
import unittest
from agentic_crystallization.robust_calibration import (
    hoeffding_radius, alpha_spending, bounds, select_action, interaction_certificate)

class RobustCalibrationTests(unittest.TestCase):
    def test_radius_declines_with_samples_and_increases_with_actions(self):
        self.assertGreater(hoeffding_radius(100,9),hoeffding_radius(1600,9))
        self.assertGreater(hoeffding_radius(200,19),hoeffding_radius(200,2))

    def test_alpha_spending_sums_to_budget(self):
        self.assertLessEqual(sum(alpha_spending(.05,t) for t in range(1,100000)),.05+1e-12)
        self.assertAlmostEqual(alpha_spending(.05,1),.025)

    def test_unknown_shift_holds_not_zero(self):
        c=bounds({'baseline':.55,'candidate':.9},{'baseline':.05,'candidate':.05},1000)
        self.assertFalse(c['available'])
        self.assertEqual(select_action(c)['status'],'hold')

    def test_explicit_zero_bound_required_for_iid(self):
        c=bounds({'baseline':.1,'candidate':.9},{'baseline':.05,'candidate':.05},6400,shift_tv_bound=0)
        self.assertTrue(c['available'])
        self.assertEqual(select_action(c)['action'],'candidate')
        self.assertEqual(select_action(c)['status'],'certified_best')

    def test_safe_gain_can_be_weaker_than_best_certificate(self):
        c={'available':True,'intervals':{
            'baseline':{'estimate':.15,'lower':.12,'upper':.18},
            'a':{'estimate':.40,'lower':.30,'upper':.53},
            'b':{'estimate':.43,'lower':.32,'upper':.54}}}
        s=select_action(c)
        self.assertEqual(s['status'],'certified_gain')
        self.assertFalse(s['certified_best'])
        self.assertEqual(s['action'],'b')
        self.assertTrue(s['certified_baseline_gain'])

    def test_error_on_bad_inputs(self):
        bad=[(-1,5,.05),(12,0,.05),(12,5,1.0)]
        for n,k,alpha in bad:
            with self.assertRaises(ValueError):hoeffding_radius(n,k,alpha)
        with self.assertRaises(ValueError):bounds({'baseline':.5},{'baseline':.2},10,shift_tv_bound=-.1)
        with self.assertRaises(ValueError):bounds({'baseline':float('nan')},{'baseline':0},10,shift_tv_bound=0)
        with self.assertRaises(ValueError):bounds({'baseline':.5},{},10,shift_tv_bound=0)

    def test_mobius_exact_triple_and_certification(self):
        group=frozenset('abc')
        means={frozenset(x for j,x in enumerate('abc') if mask&(1<<j)): .25+(0.5 if mask==7 else 0.) for mask in range(8)}
        cost={s:0.0 for s in means}
        cert=interaction_certificate(means,cost,10000,group=group,shift_tv_bound=0)
        self.assertEqual(cert['status'],'positive')
        self.assertAlmostEqual(cert['estimated'],.5)
        self.assertLess(cert['error_bound'],.5)
        held=interaction_certificate(means,cost,10000,group=group)
        self.assertEqual(held['status'],'hold')

    def test_factorial_missing_term_refused(self):
        with self.assertRaises(ValueError):
            interaction_certificate({frozenset():.5},{frozenset():0},10,group=frozenset('abc'),shift_tv_bound=0)

    def test_valid_true_value_cannot_be_overruled_when_certified(self):
        # Deterministic proof sanity across every pair of interval endpoints.
        c=bounds({'baseline':.2,'candidate':.83},{'baseline':.05,'candidate':.08},6400,shift_tv_bound=.02)
        out=select_action(c)
        self.assertEqual(out['status'],'certified_best')
        i=c['intervals']
        for b in ('lower','upper'):
            for a in ('lower','upper'):
                self.assertGreater(i['candidate'][a],i['baseline'][b])

if __name__=='__main__':unittest.main()
