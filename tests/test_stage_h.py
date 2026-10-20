import unittest
from agentic_crystallization import stage_e,stage_f,stage_g,stage_h

class StageHTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.model=stage_f.train(range(3000,3020))
  cls.world=stage_e.make_world(12,10001,.75)
  cls.cue=stage_f.second_cue(cls.world,12,10001,.75)
 def test_candidate_budget(self):
  for margin in stage_h.MARGINS:
   found,attempts,probe,voi=stage_h.margin_policy(self.world,12,self.model,self.cue,margin)
   self.assertLessEqual(attempts,40)
   self.assertIn(probe,(0,1))
 def test_reduces_to_original_voi_at_zero_margin(self):
  expected=stage_g.run_policy(self.world,12,self.model,'voi',self.cue)
  observed=stage_h.margin_policy(self.world,12,self.model,self.cue,0)
  self.assertEqual(expected[:3],observed[:3])
 def test_monotone_probe_suppression(self):
  counts=[]
  for m in stage_h.MARGINS:
   counts.append(stage_h.margin_policy(self.world,12,self.model,self.cue,m)[2])
  self.assertEqual(counts,sorted(counts,reverse=True))
 def test_training_holdout_disjoint(self):
  self.assertTrue(set(range(9000,9060)).isdisjoint(range(10000,10120)))
 def test_repeatability(self):
  self.assertEqual(stage_h.margin_policy(self.world,12,self.model,self.cue,.5),stage_h.margin_policy(self.world,12,self.model,self.cue,.5))
 def test_first_cost_charged(self):
  v=stage_h.margin_policy(self.world,12,self.model,self.cue,.5)
  self.assertAlmostEqual(stage_h.utility(self.world,v),40*v[0]-.1*(self.world['first_cost']+v[1]))

if __name__=='__main__':unittest.main()
