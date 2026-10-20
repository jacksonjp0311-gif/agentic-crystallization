"""Agentic Crystallization 2.1: falsification-first renewal and drift tests."""
import copy
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from agentic_crystallization.crystal_core import Configuration, Example
from agentic_crystallization.renewal_core import (
    RenewalConfig, RenewalState, RenewalLedger, Packet, POLICIES,
    spending, one_sided_radius, drift_monitor, renewal_step, transition,
    rank_discovery, masked_accuracy, fast_mask, canonical_paired_mean,
    initial_mem)
from agentic_crystallization.stage_m import (REGIMES, EPOCHS, make_packet,
                                             run_world, analytic_true_gain)


class TestV21Mathematics(unittest.TestCase):
    def setUp(self):self.c=RenewalConfig()

    def test_lifetime_error_spending(self):
        a=sum(spending(self.c.alpha_promotion,n) for n in range(1,10001))
        self.assertLessEqual(a,self.c.alpha_promotion)
        self.assertGreater(a,.99*self.c.alpha_promotion)

    def test_confidence_radius_shrinks(self):
        self.assertGreater(one_sided_radius(128,.001),one_sided_radius(256,.001))
        self.assertGreater(one_sided_radius(256,.001),one_sided_radius(512,.001))

    def test_rejects_alpha_overallocation(self):
        with self.assertRaises(ValueError):RenewalConfig(alpha_promotion=.04,alpha_monitor=.04)

    def test_detect_large_degradation(self):
        # Alternating inputs => reference paired gain .5, current gain -.5.
        reference=tuple(Example((i%2,0,0,0,0,0,0,0),i%2) for i in range(4096))
        feedback=tuple(Example((i%2,0,0,0,0,0,0,0),1-(i%2)) for i in range(4096))
        res=drift_monitor('xor:0',reference,feedback,1,self.c)
        self.assertEqual(res['status'],'ALARM')
        self.assertLess(res['drop_upper'],0)

    def test_no_alarm_under_exact_stationarity(self):
        reference=tuple(Example((i%2,0,0,0,0,0,0,0),i%2) for i in range(512))
        result=drift_monitor('xor:0',reference,reference,1,self.c)
        self.assertEqual(result['status'],'CLEAR')

    def test_missing_feedback_is_hold(self):
        ref=(Example((0,)*8,0),)
        self.assertEqual(drift_monitor('xor:0',ref,None,1,self.c)['reason'],'FEEDBACK_MISSING')

    def test_invalid_candidate_cannot_be_monitored(self):
        with self.assertRaises(ValueError):drift_monitor('python:exec',(),(),1,self.c)

    def test_paired_difference_exact(self):
        ref=(Example((0,)*8,0),Example((1,0,0,0,0,0,0,0),1))
        self.assertEqual(canonical_paired_mean('xor:0',ref),.5)

    def test_fast_mask_agrees_with_canonical_evaluation(self):
        from agentic_crystallization.crystal_core import empirical_accuracy
        p, _=make_packet(2718,1,'stationary',self.c)
        data=p.segments[0].discovery
        for n in ('baseline:0','xor:0','xor:0,1','xor:0,1,2'):
            self.assertAlmostEqual(masked_accuracy(fast_mask(n),data),empirical_accuracy(n,data))


class TestV21Lifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.c=RenewalConfig()

    def test_all_regimes_available(self):
        self.assertEqual(len(REGIMES),8)
        self.assertEqual(len(POLICIES),6)

    def test_recertification_is_fresh(self):
        state=RenewalState(credits=self.c.base.initial_credits)
        packet,_=make_packet(2718,1,'stationary',self.c)
        event,state=renewal_step(state,packet,'crystal',self.c)
        self.assertGreater(len(event['promotions']),0)
        self.assertTrue(state.memory)
        stale=initial_mem(state,self.c)
        self.assertTrue(all(x['status']=='NEEDS_RENEWAL' for x in stale.values()))

    def test_recurrence_reuses_but_recertifies(self):
        rows=run_world(2718,'recurrent',self.c)
        crystal=[r for r in rows if r['policy']=='crystal']
        self.assertGreater(sum(r['memory_recertifications'] for r in crystal),0)
        self.assertTrue(all(r['false_promotions']==0 for r in crystal))

    def test_inversion_causes_monitor_alarm_and_harm_lag(self):
        rows=run_world(2718,'inverted_drift',self.c)
        c=[r for r in rows if r['policy']=='crystal']
        self.assertGreater(sum(r['alarm'] for r in c),0)
        self.assertGreater(sum(r['harmful_deployment_blocks'] for r in c),0)
        self.assertTrue(all(r['action2']=='baseline:0' for r in c if r['alarm']))

    def test_fake_feedback_masks_unsafe_behavior(self):
        honest=run_world(2718,'inverted_drift',self.c)
        fake=run_world(2718,'misleading_feedback',self.c)
        hc=[r for r in honest if r['policy']=='crystal']
        fc=[r for r in fake if r['policy']=='crystal']
        self.assertGreater(sum(r['alarm'] for r in hc),sum(r['alarm'] for r in fc))
        self.assertGreater(sum(r['harmful_deployment_blocks'] for r in fc),
                           sum(r['harmful_deployment_blocks'] for r in hc))

    def test_feedback_unavailable_holds_late_block(self):
        c=[r for r in run_world(2718,'missing_feedback',self.c) if r['policy']=='crystal']
        self.assertTrue(all(r['action2']=='baseline:0' for r in c if r['action0']!='baseline:0'))

    def test_unlearnable_fourway_reduces_promotions(self):
        c=[r for r in run_world(2718,'unlearnable',self.c) if r['policy']=='crystal']
        self.assertTrue(all(r['certifications']==0 for r in c if r['phase0']=='N'))

    def test_zero_capital_fails_closed_before_sampling(self):
        packet,_=make_packet(2718,1,'stationary',self.c)
        event,next_state=renewal_step(RenewalState(credits=0),packet,'crystal',self.c)
        self.assertEqual(event['status'],'BUDGET_HOLD')
        self.assertEqual(event['queries'],0)
        self.assertEqual(event['active'],['baseline:0']*3)
        self.assertGreaterEqual(next_state.credits,0)

    def test_no_hidden_evaluator_oracle_in_event(self):
        packet,audit=make_packet(2718,1,'abrupt',self.c)
        event,_=renewal_step(RenewalState(credits=self.c.base.initial_credits),packet,'crystal',self.c)
        self.assertNotIn('phase0',event)
        self.assertNotIn('true_gain',event)
        self.assertNotIn('hidden_target',event)

    def test_all_controls_nonnegative_credits(self):
        for regime in ('stationary','inverted_drift','unlearnable'):
            rows=run_world(2718,regime,self.c)
            self.assertTrue(all(r['credits']>=0 for r in rows),(regime,))

    def test_replay_matches_online_state(self):
        with tempfile.TemporaryDirectory() as folder:
            led=RenewalLedger(Path(folder)/'receipt.jsonl',self.c)
            state=RenewalState(credits=self.c.base.initial_credits)
            for epoch in range(1,5):
                packet,_=make_packet(2718,epoch,'recurrent',self.c)
                event,state=renewal_step(state,packet,'crystal',self.c)
                self.assertEqual(led.append(event).to_dict(),state.to_dict())
            self.assertEqual(led.replay().to_dict(),state.to_dict())

    def test_resume_matches_uninterrupted_run(self):
        with tempfile.TemporaryDirectory() as folder:
            led=RenewalLedger(Path(folder)/'receipt.jsonl',self.c)
            state=RenewalState(credits=self.c.base.initial_credits)
            for epoch in range(1,6):
                packet,_=make_packet(2718,epoch,'recurrent',self.c)
                event,state=renewal_step(state,packet,'crystal',self.c)
                led.append(event)
            state2=led.replay()
            packet,_=make_packet(2718,6,'recurrent',self.c)
            a,na=renewal_step(state,packet,'crystal',self.c)
            b,nb=renewal_step(state2,packet,'crystal',self.c)
            self.assertEqual(a,b)
            self.assertEqual(na.to_dict(),nb.to_dict())

    def test_tampered_ledger_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'receipt.jsonl';led=RenewalLedger(path,self.c)
            packet,_=make_packet(2718,1,'stationary',self.c)
            event,_=renewal_step(RenewalState(credits=self.c.base.initial_credits),packet,'crystal',self.c)
            led.append(event)
            path.write_text(path.read_text().replace('COMPLETED','FORGED',1))
            with self.assertRaises(ValueError):led.replay()

    def test_forged_promotion_lower_bound_fails_replay(self):
        state=RenewalState(credits=self.c.base.initial_credits)
        packet,_=make_packet(2718,1,'stationary',self.c)
        event,_=renewal_step(state,packet,'crystal',self.c)
        forged=copy.deepcopy(event)
        forged['promotions'][0]['certificate']['lower']=-99
        with self.assertRaises(ValueError):transition(state,forged,self.c)

    def test_retired_memory_not_treated_as_valid(self):
        state=RenewalState(epoch=9,memory={'xor:0,1,2':{'status':'RETAINED','certifications':2,'alarms':0,'last_certified':1}},credits=150.0)
        self.assertEqual(initial_mem(state,self.c)['xor:0,1,2']['status'],'RETIRED')

    def test_repeated_alarm_causes_retirement(self):
        result=[r for r in run_world(2718,'inverted_drift',self.c) if r['policy']=='crystal']
        self.assertTrue(any(r['memory_retired']>0 for r in result))

    def test_monitor_only_can_hold_without_recovery(self):
        result=[r for r in run_world(2718,'abrupt',self.c) if r['policy']=='monitor_hold']
        self.assertTrue(all(r['action2']=='baseline:0' for r in result if r['alarm']))

if __name__=='__main__':unittest.main()
