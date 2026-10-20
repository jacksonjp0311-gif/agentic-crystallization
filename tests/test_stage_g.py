import unittest
from agentic_crystallization import stage_f,stage_g,stage_e

class StageGTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=stage_f.train(range(3000,3020))
        cls.world=stage_e.make_world(12,9101,.75)

    def test_probabilities_normalized(self):
        original,l0,l1,q=stage_g.initial(12,self.world,self.model)
        self.assertAlmostEqual(sum(stage_g.weights(original,l0,l1,q).values()),1.0)

    def test_expected_value_exact(self):
        self.assertAlmostEqual(stage_g.continuation_value(['a','b'],{'a':.25,'b':.75},2),39.825)

    def test_bayes_cue(self):
        self.assertAlmostEqual(stage_g.cue_posterior(.5,True),.8)
        self.assertAlmostEqual(stage_g.cue_posterior(.5,False),.2)

    def test_deterministic(self):
        a=stage_g.trial(12,9101,.75,self.model)
        b=stage_g.trial(12,9101,.75,self.model)
        self.assertEqual(a,b)

    def test_budget_and_probe_charge(self):
        for name in stage_g.POLICIES:
            found,used,probes,decision,voi=stage_g.run_policy(self.world,12,self.model,name,True)
            self.assertLessEqual(used,40)
            self.assertIn(probes,(0,1))
            self.assertTrue(used>=probes)

    def test_probe_not_worse_in_model_expectation(self):
        original,l0,l1,q=stage_g.initial(12,self.world,self.model)
        choose,gain=stage_g.probe_decision(original,l0,l1,q,original,30)
        self.assertEqual(choose,gain>1e-12)

if __name__=='__main__':unittest.main()
