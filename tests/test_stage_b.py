import unittest
from agentic_crystallization import stage_b as b
class TestStageB(unittest.TestCase):
    def test_additive_has_no_interaction(self):
        base,c,edges,metadata=b.make_world(12,.75,2,'additive')
        self.assertFalse(edges)
        self.assertAlmostEqual(b.score(base,edges,(0,1,2,3)),sum(base[i] for i in (0,1,2,3)))
    def test_misleading_is_not_causal(self):
        _,_,edges,metadata=b.make_world(12,.9,2,'misleading')
        self.assertFalse(edges);self.assertTrue(metadata)
    def test_component_bounds(self):
        self.assertEqual(b.largest_component(12,[]),1/12)
        self.assertEqual(b.largest_component(3,[(0,1,2)]),1)
    def test_determinism(self):
        self.assertEqual(b.one_world(12,.3,2,'synergy',32,5),b.one_world(12,.3,2,'synergy',32,5))
    def test_finite(self):
        r=b.one_world(12,.45,1,'synergy',48,8)
        self.assertTrue(0<=r['interaction']<=r['oracle']+1e-8)
if __name__=='__main__':unittest.main()
