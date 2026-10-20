import tempfile,unittest
from pathlib import Path
from agentic_crystallization.risk_verification import Config,State,radius,certify,choose,should_audit,cue_posterior
from agentic_crystallization.stage_n import run,run_world,truth_at,warning,audit_means,REGIMES,POLICIES

class StageNTests(unittest.TestCase):
 def setUp(self):self.cfg=Config()
 def test_certifier_positive(self):self.assertEqual(certify({'A':.6,'B':-.6},self.cfg),'A')
 def test_certifier_hold(self):self.assertIsNone(certify({'A':0,'B':0},self.cfg))
 def test_radius(self):self.assertGreater(radius(self.cfg),0)
 def test_honest_bound(self):self.assertLess(radius(self.cfg),.3)
 def test_invalid(self):
  with self.assertRaises(ValueError):Config(alpha=0)
  with self.assertRaises(ValueError):certify({'A':2,'B':0},self.cfg)
 def test_hidden_truth_not_in_policy(self):
  event,state=choose('risk',0,State(),False,{'A':.5,'B':-.5},self.cfg)
  self.assertEqual(event['selected'],'A');self.assertTrue(event['audit'])
 def test_no_prior_audit(self):self.assertFalse(should_audit('baseline',0,State(),False,self.cfg))
 def test_posterior(self):self.assertGreater(cue_posterior(1,True,self.cfg),cue_posterior(1,False,self.cfg))
 def test_expiration(self):self.assertTrue(should_audit('risk',5,State('A',0),False,self.cfg))
 def test_missing_cue(self):self.assertTrue(should_audit('risk',2,State('A',0),None,self.cfg))
 def test_unlearnable(self):self.assertEqual(truth_at('unlearnable',8),{'A':0.,'B':0.})
 def test_reproducible(self):self.assertEqual(run_world(123,'abrupt',self.cfg),run_world(123,'abrupt',self.cfg))
 def test_seven_policies(self):self.assertEqual(len(run_world(123,'abrupt',self.cfg)),len(POLICIES)*24)
 def test_all_regimes(self):
  for r in REGIMES:self.assertEqual(len(run_world(9,r,self.cfg)),len(POLICIES)*24)
 def test_nonoverwrite(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'exp';run(path,1,1)
   with self.assertRaises(FileExistsError):run(path,1,1)
if __name__=='__main__':unittest.main()
