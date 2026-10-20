"""v2.0 deterministic unit and integration tests.

The statistical theorem is conditional and cannot be proved by Monte Carlo.
These tests verify the implementation, information boundaries and fail closed.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import unittest
from dataclasses import replace

from agentic_crystallization.crystal_core import (
    Configuration, CrystalState, DurableLedger, Evidence, Example,
    candidates, certify, compute_next_state, digest, empirical_accuracy,
    lifetime_alpha, lower_radius, paired_difference, predict,
    select_proposal, step, valid_procedure)
from agentic_crystallization.stage_l import (
    REGIMES, POLICIES, EPOCHS, draw_rows, epoch_packet, latent_concepts,
    run_one, seed_from, true_deployment_gain, demonstration)


class TestCrystallineMathematics(unittest.TestCase):
    def setUp(self):
        self.c=Configuration()

    def test_catalog_only_allowed_compositions(self):
        self.assertEqual(len(candidates(8)), 8+28+56)
        self.assertTrue(valid_procedure('xor:0,1,2',8))
        for text in ('xor:1,0','xor:1,1','xor:999','xor:0,1,2,3',
                     'exec:code', 'xor:0,-1', 'xor:00', 'xor:', 'baseline:1'):
            self.assertFalse(valid_procedure(text,8),text)

    def test_parity_XOR(self):
        row=Example((1,1,0,0,1,0,0,0),0)
        self.assertEqual(predict('xor:0,1,2',row),0)
        self.assertEqual(predict('xor:0,4',row),0)
        self.assertEqual(predict('baseline:0',row),0)
        with self.assertRaises(ValueError): predict('xor:7,8',row)

    def test_triple_synergy_exact_enumeration(self):
        import itertools
        truth=(0,1,2)
        for subset_size in (0,1,2,3):
            for chosen in itertools.combinations(truth,subset_size):
                inputs=[tuple(bits)+(0,0,0,0,0) for bits in itertools.product((0,1),repeat=3)]
                outcomes=[b[0]^b[1]^b[2] for b in inputs]
                correct=sum(int((sum(b[i] for i in chosen)%2)==y) for b,y in zip(inputs,outcomes))
                self.assertEqual(correct/8,1.0 if subset_size==3 else 0.5)

    def test_error_budget_telescopes(self):
        self.assertLess(sum(lifetime_alpha(0.05,i) for i in range(1,100000)),0.05)
        self.assertAlmostEqual(sum(lifetime_alpha(0.05,i) for i in range(1,100000)),0.05,places=5)

    def test_valid_one_sided_radius(self):
        self.assertGreater(lower_radius(64,1,4,0.05),lower_radius(512,1,4,0.05))
        self.assertGreater(lower_radius(64,20,4,0.05),lower_radius(64,1,4,0.05))

    def test_certifies_true_triple_independent_data(self):
        evidence, _, _ =epoch_packet(1234,1,'stationary',self.c)
        true_name='xor:'+','.join(map(str,latent_concepts(1234,self.c.width)['A']))
        result=certify(true_name,evidence.validation,1,0.0,self.c)
        self.assertEqual(result['status'],'CERTIFIED')
        self.assertGreater(result['lower'],self.c.minimum_gain)
        self.assertIn(result['n'],self.c.validation_looks)

    def test_wrong_candidate_held(self):
        evidence,_,_=epoch_packet(1234,1,'stationary',self.c)
        name='xor:'+','.join(map(str,latent_concepts(1234,self.c.width)['B']))
        result=certify(name,evidence.validation,1,0.0,self.c)
        self.assertEqual(result['status'],'HOLD')
        self.assertEqual(result['n'],512)

    def test_certification_requires_declared_shift(self):
        evidence,_,_=epoch_packet(1234,1,'stationary',self.c)
        self.assertEqual(certify('xor:0,1,2',evidence.validation,1,None,self.c)['reason'],'SHIFT_UNJUSTIFIED')
        with self.assertRaises(ValueError):certify('xor:0,1,2',evidence.validation,1,-0.01,self.c)

    def test_evidence_does_not_expose_latent_target(self):
        fields=set(Evidence.__dataclass_fields__)
        self.assertFalse({'source','hidden_target','true_gain','actual_shift_bound'}&fields)

    def test_split_independence_reproducible(self):
        a,live,_=epoch_packet(120,1,'recurrent',self.c)
        b,other,_=epoch_packet(120,1,'recurrent',self.c)
        self.assertEqual(a,b)
        self.assertEqual(live,other)
        self.assertNotEqual(a.scout,a.validation[:len(a.scout)])
        self.assertNotEqual(a.discovery,a.validation[:len(a.discovery)])

    def test_early_certification_uses_only_seen_validation(self):
        packet, live,_=epoch_packet(132,1,'stationary',self.c)
        name='xor:'+','.join(map(str,latent_concepts(132,self.c.width)['A']))
        r=certify(name,packet.validation,1,0,self.c)
        changed=list(packet.validation)
        for k in range(r['n'],len(changed)):
            changed[k]=Example(changed[k].bits,1-changed[k].label)
        self.assertEqual(r,certify(name,tuple(changed),1,0,self.c))

    def test_no_promotion_from_discovery_only(self):
        packet,live,_=epoch_packet(444,1,'stationary',self.c)
        tampered=replace(packet,validation=tuple(Example(x.bits,1-x.label) for x in packet.validation))
        event,_=step(CrystalState(),tampered,live,self.c,'crystal')
        self.assertEqual(event['status'],'HOLD')
        self.assertEqual(event['active'],'baseline:0')

    def test_bounded_shift_gain_direct_not_tv(self):
        evidence,live,audit=epoch_packet(333,1,'bounded_shift',self.c)
        self.assertEqual(evidence.shift_allowance,.06)
        target='xor:'+','.join(map(str,audit['source']))
        self.assertLessEqual(abs(true_deployment_gain(target,audit)-.5),.06)

    def test_shift_unavailable_forces_no_cost_hold(self):
        evidence,live,_=epoch_packet(132,1,'unknown_shift',self.c)
        event,state=step(CrystalState(),evidence,live,self.c,'crystal')
        self.assertEqual(event['certificate']['reason'],'SHIFT_UNJUSTIFIED')
        self.assertEqual(event['queries'],0)
        self.assertEqual(state.memory,{})

    def test_budget_hold_is_nonnegative(self):
        packet,live,_=epoch_packet(10,1,'stationary',self.c)
        event,state=step(CrystalState(credits=0.0),packet,live,self.c,'crystal')
        self.assertEqual(event['certificate']['reason'],'BUDGET_HOLD')
        self.assertEqual(state.credits,round(event['revenue'],8))

    def test_unsupported_catalog_width_rejected(self):
        with self.assertRaises(ValueError):Configuration(width=2)
        with self.assertRaises(ValueError):Configuration(validation_looks=(128,64))


class TestAutonomousLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.c=Configuration()

    def test_crystal_discovers_without_oracle(self):
        p,live,audit=epoch_packet(2020,1,'stationary',self.c)
        event,state=step(CrystalState(),p,live,self.c,'crystal')
        self.assertEqual(event['proposal_source'],'search')
        self.assertEqual(event['status'],'CERTIFIED')
        self.assertEqual(event['candidate'],'xor:'+','.join(map(str,audit['source'])))
        self.assertIn(event['candidate'],state.memory)

    def test_restart_not_trusted_as_current_certificate(self):
        rows=run_one(2020,'recurrent','crystal',self.c)
        self.assertEqual(len(rows),12)
        self.assertEqual(rows[0]['origin'],'search')
        self.assertEqual(rows[1]['origin'],'memory')
        self.assertEqual(rows[2]['origin'],'search')
        self.assertEqual(rows[4]['origin'],'memory')
        self.assertEqual(rows[4]['status'],'CERTIFIED')
        self.assertEqual(len([r for r in rows if r['false_certification']]),0)

    def test_bad_negative_transfer_stops_using_anchor(self):
        rows=run_one(2020,'recurrent','reuse_only',self.c)
        self.assertEqual(rows[0]['status'],'CERTIFIED')
        self.assertEqual(rows[2]['status'],'HOLD')
        self.assertEqual(rows[2]['active'],'baseline:0')

    def test_unlearnable_four_way_parity_never_certifies(self):
        rows=run_one(2020,'noise','crystal',self.c)
        for row in rows:
            if row['phase']=='N':
                self.assertEqual(row['status'],'HOLD')

    def test_missing_shift_forces_twelve_holds(self):
        rows=run_one(2020,'unknown_shift','crystal',self.c)
        self.assertTrue(all(r['status']=='HOLD' and r['queries']==0 for r in rows))

    def test_false_shift_reveals_theorem_limit(self):
        rows=run_one(2020,'false_shift','crystal',self.c)
        wrong=[x for x in rows if x['status']=='CERTIFIED']
        self.assertGreater(len(wrong),5)
        self.assertTrue(all(x['false_certification'] for x in wrong))

    def test_capacity_never_exceeded(self):
        c=replace(self.c,capacity=1)
        rows=run_one(2020,'abrupt','crystal',c)
        self.assertTrue(all(x['memory_size']<=1 for x in rows))

    def test_resource_balance_never_negative(self):
        for regime in REGIMES:
            for mode in POLICIES:
                rows=run_one(2020,regime,mode,self.c)
                self.assertTrue(all(x['credits']>=0 for x in rows), (regime,mode))

    def test_ledger_replay_exact(self):
        with tempfile.TemporaryDirectory() as d:
            log=DurableLedger(Path(d)/'receipts.jsonl',self.c)
            full=run_one(2020,'recurrent','crystal',self.c,log)
            recovered=log.replay()
            self.assertEqual(recovered.epoch,EPOCHS)
            self.assertEqual(len(full),EPOCHS)
            self.assertEqual(len(recovered.memory),3)

    def test_ledger_corruption_detected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'receipts.jsonl'
            log=DurableLedger(path,self.c)
            packet,live,_=epoch_packet(2020,1,'stationary',self.c)
            event,_=step(CrystalState(),packet,live,self.c,'crystal')
            log.append(event)
            raw=path.read_text();path.write_text(raw.replace('CERTIFIED','NOT_CERTIFIED',1))
            with self.assertRaises(ValueError):log.replay()

    def test_ledger_incomplete_line_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'receipts.jsonl';path.write_text('{"seq":1}')
            with self.assertRaises(ValueError):DurableLedger(path,self.c).replay()

    def test_forged_promotion_rejected(self):
        packet,live,_=epoch_packet(2020,1,'stationary',self.c)
        event,_=step(CrystalState(),packet,live,self.c,'crystal')
        event['shift_allowance']=None
        with self.assertRaises(ValueError):compute_next_state(CrystalState(),event,self.c)
        event['shift_allowance']=0.0
        event['certificate']['lower']=-1.0
        with self.assertRaises(ValueError):compute_next_state(CrystalState(),event,self.c)

    def test_restarted_execution_matches_fresh_run(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            ledger=DurableLedger(Path(d)/'receipts.jsonl',self.c)
            seed=2020;regime='recurrent'
            state=CrystalState()
            for ep in range(1,6):
                packet,live,_=epoch_packet(seed,ep,regime,self.c)
                event,state=step(state,packet,live,self.c,'crystal')
                ledger.append(event)
            resumed=run_one(seed,regime,'crystal',self.c,ledger)
            complete=run_one(seed,regime,'crystal',self.c)
            self.assertEqual(resumed,[row for row in complete if row['epoch']>=6])
            self.assertEqual(ledger.replay().epoch,12)

    def test_simulator_actual_target_not_in_receipt(self):
        packet,live,audit=epoch_packet(2020,1,'stationary',self.c)
        event,state=step(CrystalState(),packet,live,self.c,'crystal')
        self.assertNotIn('actual_shift_bound',event)
        self.assertNotIn('phase',event)
        self.assertNotIn('hidden_target',event)


if __name__=='__main__':unittest.main()
