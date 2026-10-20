import tempfile,unittest
from pathlib import Path
from agentic_crystallization import stage_e as e
class StageETests(unittest.TestCase):
 def test_determinism(self):self.assertEqual(e.make_world(15,2001,.25),e.make_world(15,2001,.25))
 def test_hidden_target(self):
  w=e.make_world(12,2001,.75);self.assertNotEqual(w['first'],w['target']);self.assertIn(w['target'],w['candidates'])
 def test_equal_first_cost(self):
  row=e.trial(15,2001,.25,e.train(seeds=range(3)))
  for p in e.POLICIES:self.assertEqual(row[p+'_total_attempts']-row[p+'_restricted_attempts'],row['first_discovery_attempts'])
 def test_gate_training_independent(self):
  gate=e.train(seeds=range(4));self.assertEqual(set(gate),{'True','False'})
  for c in gate:self.assertIs(type(gate[c]['reuse']),bool)
 def test_repeatable_files(self):
  gate=e.train(seeds=range(5))
  with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
   e.run(a,seeds=range(2000,2004),gate=gate);e.run(b,seeds=range(2000,2004),gate=gate)
   for name in ('runs.csv','summary.json','manifest.json','SHA256SUMS.json'):
    self.assertEqual((Path(a)/name).read_bytes(),(Path(b)/name).read_bytes())
 def test_budget_censor(self):
  row=e.trial(18,2010,.25,e.train(seeds=range(4)),budget=1)
  for p in e.POLICIES:self.assertEqual(row[p+'_restricted_attempts'],1)
if __name__=='__main__':unittest.main()
