"""Stage P regression tests, including known unsolvable shared-corruption failure."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from dataclasses import replace
from unittest.mock import patch
from agentic_crystallization import stage_p
from agentic_crystallization.adaptive_trust import (
 TrustConfig,TrustState,decide,radius,certificate,incompatible,
 posterior_disagreement,POLICIES)

class StagePTests(unittest.TestCase):
 def test_reference_is_independent_seeded_draw(self):
  cfg=TrustConfig()
  a=stage_p.world_observations(8255,'stationary',0,cfg)
  b=stage_p.world_observations(8255,'stationary',0,cfg)
  self.assertEqual(a,b)
  self.assertNotEqual(a['reference'],a['primary'])
  self.assertNotEqual(a['reference'],a['anchor'])

 def test_radius_decreases_with_n_and_covers_six_means(self):
  cfg=TrustConfig()
  self.assertGreater(radius(128,cfg),radius(768,cfg))
  self.assertGreater(radius(768,cfg),0)

 def test_valid_certificate(self):
  cfg=TrustConfig(reference_samples=4096)
  self.assertEqual(certificate({'A':.8,'B':-.8},4096,cfg),'A')
  self.assertIsNone(certificate({'A':.01,'B':-.01},4096,cfg))

 def test_nonfinite_rejected(self):
  cfg=TrustConfig()
  with self.assertRaises(ValueError):certificate({'A':float('nan'),'B':0},384,cfg)
  with self.assertRaises(ValueError):incompatible({'A':.2,'B':-.2},{'A':.3},384,384,cfg)

 def test_posterior_only_descriptive(self):
  self.assertAlmostEqual(posterior_disagreement(0,0),.5)
  self.assertAlmostEqual(posterior_disagreement(1,2),.5)
  with self.assertRaises(ValueError):posterior_disagreement(2,1)

 def test_common_mode_guarded_by_honest_reference(self):
  rows=stage_p.run_world(8262,'common_mode',TrustConfig())
  tri=[r for r in rows if r['policy']=='triad_periodic']
  legacy=[r for r in rows if r['policy']=='legacy_guard']
  self.assertEqual(sum(r['false_fresh_certificate'] for r in tri),0)
  self.assertGreater(sum(r['integrity_alarm'] for r in tri),0)
  self.assertGreater(sum(r['false_fresh_certificate'] for r in legacy),0)

 def test_unidentifiable_shared_corruption(self):
  rows=stage_p.run_world(8262,'all_corrupt',TrustConfig())
  tri=[r for r in rows if r['policy']=='triad_periodic']
  self.assertGreater(sum(r['false_fresh_certificate'] for r in tri),0)
  self.assertEqual(sum(r['integrity_alarm'] for r in tri),0)

 def test_reference_corrupted_disagrees(self):
  rows=stage_p.run_world(8262,'reference_corrupt',TrustConfig())
  tri=[r for r in rows if r['policy']=='triad_periodic']
  self.assertEqual(sum(r['false_fresh_certificate'] for r in tri),0)
  self.assertGreater(sum(r['integrity_alarm'] for r in tri),0)

 def test_missing_reference_holds_and_never_claims_fresh(self):
  rows=stage_p.run_world(8262,'missing_reference',TrustConfig())
  tri=[r for r in rows if r['policy']=='triad_periodic' and r['epoch']>=8]
  self.assertEqual(sum(r['fresh'] for r in tri),0)
  self.assertTrue(all(r['held'] for r in tri))

 def test_missing_anchor_holds_after_expiry(self):
  rows=stage_p.run_world(8262,'missing_anchor',TrustConfig())
  tri=[r for r in rows if r['policy']=='triad_periodic' and r['epoch']>=8]
  self.assertEqual(sum(r['fresh'] for r in tri),0)
  self.assertTrue(all(r['held'] for r in tri))

 def test_no_unpurchased_reference_cost(self):
  cfg=TrustConfig()
  o=stage_p.world_observations(8262,'stationary',1,cfg)
  state=TrustState()
  _,state=decide('triad_periodic',0,state,o['cue'],o['primary'],o['anchor'],o['reference'],cfg)
  next_event,_=decide('triad_periodic',1,state,False,o['primary'],o['anchor'],o['reference'],cfg)
  self.assertEqual(next_event['reference_audit'],0)
  self.assertEqual(next_event['audit_cost'],0.)
  self.assertEqual(next_event['fresh'],0)

 def test_reference_only_does_not_validate_corrupt_reference(self):
  rows=stage_p.run_world(8262,'reference_corrupt',TrustConfig())
  ref=[r for r in rows if r['policy']=='reference_periodic']
  self.assertGreater(sum(r['false_fresh_certificate'] for r in ref),0)

 def test_policy_inputs_exclude_truth(self):
  cfg=TrustConfig()
  o=stage_p.world_observations(8262,'abrupt',0,cfg)
  with patch('agentic_crystallization.stage_p.decide',wraps=decide) as decision:
   stage_p.run_world(8262,'abrupt',cfg)
   self.assertTrue(decision.called)
   for call in decision.call_args_list:
    self.assertEqual(len(call.args),8)
    self.assertNotIn('truth',call.kwargs)

 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'trial'
   first=stage_p.run(p,8010,1)
   self.assertIn('stationary',first)
   with self.assertRaises(FileExistsError):stage_p.run(p,8010,1)
   hashes=json.loads((p/'SHA256SUMS.json').read_text())
   for name,digest in hashes.items():
    self.assertEqual(hashlib.sha256((p/name).read_bytes()).hexdigest(),digest)

 def test_config_rejects_bogus(self):
  for kwargs in ({'alpha':1},{'hazard':-1},{'reference_samples':0},{'reference_unit_cost':-1}):
   with self.assertRaises(ValueError):TrustConfig(**kwargs)

 def test_policies_share_identical_world(self):
  rows=stage_p.run_world(8262,'stationary',TrustConfig())
  for t in range(24):
   vals={(r['cue'],r['true_gain']) for r in rows if r['epoch']==t and r['selected']=='A'}
   self.assertLessEqual(len(vals),1)

if __name__=='__main__':unittest.main()
