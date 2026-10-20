import unittest
from agentic_crystallization.stage_a import world,utility,train,coefficients,choose,run_case

class StageATests(unittest.TestCase):
    def test_mobius_triple(self):
        w={'weights':[0,0,0],'pairs':{},'triples':{(0,1,2):1},'groups':[]}
        obs={():0,(0,):0,(1,):0,(2,):0,(0,1):0,(0,2):0,(1,2):0,(0,1,2):1}
        c=coefficients(obs,3)
        self.assertEqual(c[(0,1,2)],1)
        self.assertEqual(c[(0,1)],0)
    def test_additive_no_interaction(self):
        w=world('additive',8,2)
        c=coefficients({s:utility(w,s) for s in __import__('agentic_crystallization.stage_a',fromlist=['subsets']).subsets(range(8))},8)
        self.assertTrue(all(abs(v)<1e-9 for s,v in c.items() if len(s)>1))
    def test_reproducible(self):
        self.assertEqual(run_case('higher_order',8,3),run_case('higher_order',8,3))
    def test_selection_cardinality(self):
        w=world('pairwise',8,1);o=train(w,1);c=coefficients(o,8)
        for p in ('no_memory','cache_only','additive','same_estimates_linear','interaction_aware'):
            self.assertEqual(len(choose(p,tuple(range(7)),o,c)),4)
if __name__=='__main__':unittest.main()
