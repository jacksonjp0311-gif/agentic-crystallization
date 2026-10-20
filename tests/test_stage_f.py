import tempfile,unittest
from pathlib import Path
from agentic_crystallization import stage_f,stage_e

class StageFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=stage_f.train(seeds=range(3000,3020))
        cls.gate=stage_e.train(seeds=range(1000,1020))
    def test_hidden_target_not_in_model(self):
        self.assertNotIn('target',self.model)
        self.assertTrue(all(':' in k for k in self.model['likelihood']))
    def test_no_probe_bayesian_equivalence(self):
        for n in stage_f.SIZES:
            w=stage_e.make_world(n,5001,0.75)
            a=stage_f.search(w,n,'bayes_static',self.model,20,True,self.gate)
            b=stage_f.search(w,n,'bayes_no_probe',self.model,20,False,self.gate)
            self.assertEqual(a,b)
    def test_online_probe_budget(self):
        w=stage_e.make_world(12,5001,0.25)
        found,used,probes,_=stage_f.search(w,12,'bayes_online',self.model,12,True,self.gate)
        self.assertLessEqual(used,12)
        self.assertLessEqual(probes,1)
    def test_deterministic_run(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            x,_=stage_f.run(a,seeds=range(5000,5003),model=self.model,gate=self.gate)
            y,_=stage_f.run(b,seeds=range(5000,5003),model=self.model,gate=self.gate)
            self.assertEqual(x,y)
    def test_negative_transfer_not_forced(self):
        self.assertEqual(stage_f.POLICIES.count('no_prior'),1)
        self.assertIn('oracle_context',stage_f.POLICIES)
if __name__=='__main__':unittest.main()
