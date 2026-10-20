import tempfile,unittest
from pathlib import Path
from agentic_crystallization import stage_d as m
class StageDTests(unittest.TestCase):
    def test_repeatable(self):self.assertEqual(m.trial(12,9,'related'),m.trial(12,9,'related'))
    def test_independent_ablated(self):
        for c in m.CONDITIONS:
            r=m.trial(15,13,c)
            self.assertEqual(r['no_prior_found'],r['ablated_prior_found'])
            self.assertEqual(r['no_prior_restricted_attempts'],r['ablated_prior_restricted_attempts'])
    def test_restore_exact(self):
        for c in m.CONDITIONS:
            r=m.trial(18,42,c)
            self.assertEqual(r['cluster_prior_found'],r['restored_prior_found'])
            self.assertEqual(r['cluster_prior_restricted_attempts'],r['restored_prior_restricted_attempts'])
    def test_no_target_leak(self):
        first,target,options,sham=m.world(12,5,'related')
        self.assertNotEqual(first,target)
        self.assertIn(target,options)
        self.assertEqual(len(options),220)
    def test_reproducible_files(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            m.run(Path(a),seeds=range(8));m.run(Path(b),seeds=range(8))
            for name in ('runs.csv','summary.json','manifest.json','SHA256SUMS.json'):
                self.assertEqual((Path(a)/name).read_bytes(),(Path(b)/name).read_bytes())
    def test_budget_and_censor(self):
        r=m.trial(18,3,'unrelated',1)
        for p in m.POLICIES:
            self.assertEqual(r[p+'_restricted_attempts'],1)
            self.assertIn(r[p+'_found'],(0,1))
if __name__=='__main__':unittest.main()
