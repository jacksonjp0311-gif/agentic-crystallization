import unittest,math
from agentic_crystallization.stability import finite_difference,mobius_bound,certify_action,choose_with_fallback,cluster_error_bound
from agentic_crystallization.stage_i import run
from pathlib import Path
from tempfile import TemporaryDirectory

class StabilityTests(unittest.TestCase):
 def test_three_way_and(self):
  names='abc'; u={frozenset(c for i,c in enumerate(names) if mask&(1<<i)):float(mask==7) for mask in range(8)}
  self.assertAlmostEqual(finite_difference(u,frozenset(names)),1.)
  self.assertAlmostEqual(finite_difference(u,frozenset('ab')),0.)
 def test_mobius_bound(self):
  d={frozenset():.1,frozenset('a'):.1,frozenset('b'):.1,frozenset('ab'):.1}
  self.assertAlmostEqual(mobius_bound(d,frozenset('ab')),.4)
 def test_certified_gap(self):
  x=certify_action({'a':1.,'b':.6},{'a':.1,'b':.1})
  self.assertTrue(x['certified'])
 def test_uncertain_gap(self):
  x=certify_action({'a':1.,'b':.85},{'a':.1,'b':.1})
  self.assertFalse(x['certified'])
  self.assertEqual(choose_with_fallback({'a':1.,'b':.85},{'a':.1,'b':.1}), 'baseline')
 def test_nonuniform(self):
  self.assertFalse(certify_action({'a':1.,'b':.8},{'a':.19,'b':.02})['certified'])
  self.assertTrue(certify_action({'a':1.,'b':.8},{'a':.1,'b':.02})['certified'])
 def test_tie_not_certified(self):
  self.assertFalse(certify_action({'a':1.,'b':1.},{'a':0.,'b':0.})['certified'])
 def test_invalid(self):
  with self.assertRaises(ValueError):certify_action({'a':math.nan},{'a':.1})
  with self.assertRaises(ValueError):certify_action({'a':1},{'a':-.1})
 def test_cluster_bound(self):
  self.assertEqual(cluster_error_bound({frozenset('a'):.1,frozenset('ab'):.3,frozenset('c'):.5},frozenset('ab')),.4)
 def test_exhaustive_interval_corner(self):
  q={'a':1.,'b':.7};e={'a':.1,'b':.1}
  self.assertTrue(certify_action(q,e)['certified'])
  for a in [-1,1]:
   for b in [-1,1]:
    self.assertGreater(q['a']+a*e['a'],q['b']+b*e['b'])
 def test_deterministic_experiment(self):
  with TemporaryDirectory() as d:
   a=run(Path(d)/'one',range(40));b=run(Path(d)/'two',range(40))
   self.assertEqual(a,b)
   self.assertEqual(a['violations'],0)
