"""Agentic Crystallization v2.1: evidence-driven renewal and retirement.

Scientific scope: bounded synthetic XOR procedures, externally supplied tasks and
paired outcome feedback. Every epoch's promotion uses a fresh, independently
selected validation batch. Monitoring is retrospective: it cannot stop harm
before the feedback is observed, and it requires a trustworthy feedback channel.

All probability guarantees are conditional on bounded, independent rows *within*
the compared validation/feedback batches, and on the observed batch being
representative of the named epoch/block. None establishes stability of future
or unobservable distributions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from statistics import mean
import json
import math
import os
from typing import Any

from .crystal_core import (Configuration, Example, candidates, canonical, digest,
                           valid_procedure, predict, paired_difference, certify)

GENESIS = '0' * 64
POLICIES = ('crystal', 'monitor_hold', 'memoryless', 'periodic', 'fixed_reuse', 'baseline')
RECORD_STATES = ('RETAINED', 'NEEDS_RENEWAL', 'RETIRED')


@dataclass(frozen=True)
class RenewalConfig:
    """Immutable, predeclared controls; source of all costs and error spending."""
    base: Configuration = field(default_factory=lambda: Configuration(initial_credits=150.0))
    alpha_promotion: float = 0.025
    alpha_monitor: float = 0.025
    monitor_drop: float = 0.0
    monitor_threshold: float = 0.025
    max_alarms_before_retire: int = 2
    live_observation_cost: float = 0.0
    monitor_processing_cost: float = 0.0005

    def __post_init__(self) -> None:
        if not (0 < self.alpha_promotion < 1 and 0 < self.alpha_monitor < 1):
            raise ValueError('Invalid alpha allocation')
        if self.alpha_promotion + self.alpha_monitor > self.base.alpha_total + 1e-10:
            raise ValueError('Allocated alpha exceeds total')
        if not (0 <= self.monitor_drop <= 1 and -1 <= self.monitor_threshold <= 1):
            raise ValueError('Invalid drift thresholds')
        if self.max_alarms_before_retire < 1 or self.monitor_processing_cost < 0:
            raise ValueError('Invalid monitoring controls')


@dataclass(frozen=True)
class Segment:
    """Only observationally available data. No generator labels or phase names."""
    scout: tuple[Example, ...]
    discovery: tuple[Example, ...]
    validation: tuple[Example, ...]
    live: tuple[Example, ...]
    reported_feedback: tuple[Example, ...] | None
    discovery_ranked: tuple[str, ...] = ()
    discovery_gain: float | None = None


@dataclass(frozen=True)
class Packet:
    epoch: int
    segments: tuple[Segment, Segment, Segment]


@dataclass
class RenewalState:
    epoch: int = 0
    memory: dict[str, dict[str, int | str]] = field(default_factory=dict)
    anchor: str | None = None
    credits: float = 150.0

    def to_dict(self) -> dict:
        return {'epoch':self.epoch, 'memory':self.memory,'anchor':self.anchor,
                'credits':round(self.credits,8)}

    @classmethod
    def from_dict(cls, value:dict) -> 'RenewalState':
        return cls(int(value['epoch']),{k:dict(v) for k,v in value['memory'].items()},
                   value['anchor'],float(value['credits']))


def canonical_paired_mean(procedure:str, data:tuple[Example,...])->float:
    if not data:
        raise ValueError('No observations')
    return sum(paired_difference(procedure,row) for row in data)/len(data)


def one_sided_radius(n:int, alpha:float)->float:
    """Hoeffding for D in [-1,1], P(hat_mu-mu > r) <= alpha."""
    if n<1 or not (0<alpha<1):raise ValueError('Invalid sample size/alpha')
    return math.sqrt(2*math.log(1/alpha)/n)


def spending(alpha:float, index:int)->float:
    """alpha_t = alpha/(t(t+1)); sum_{t>=1} alpha_t = alpha."""
    if index<1 or not (0<alpha<1):raise ValueError('Invalid spending index/alpha')
    return alpha/(index*(index+1))


def drift_monitor(procedure:str, reference:tuple[Example,...],
                  feedback:tuple[Example,...] | None, index:int,
                  config:RenewalConfig)->dict:
    """One-sided two-batch drift test (reference batch independent of feedback).

    Rejects H0: mu_feedback >= mu_reference - monitor_drop when
      (hat_mu_feedback - hat_mu_reference) + r_ref + r_feedback < -drop.
    Each of the two marginal bounds spends alpha_index/2. An upper bound
    U_feedback < minimum positive gain separately certifies loss of margin.
    Outputs are retrospective, not predictions of a future block.
    """
    if not valid_procedure(procedure,config.base.width) or procedure=='baseline:0':
        raise ValueError('Monitoring only permits nonbaseline whitelist procedures')
    if feedback is None:
        return {'status':'HOLD','reason':'FEEDBACK_MISSING','n':0,
                'drop_upper':None,'mean_reference':None,'mean_feedback':None,
                'reference_digest':digest([(r.bits,r.label) for r in reference]),
                'feedback_digest':None,'alpha':spending(config.alpha_monitor,index)}
    if not reference or not feedback:raise ValueError('Monitoring requires two nonempty batches')
    ar=spending(config.alpha_monitor,index)
    mref=canonical_paired_mean(procedure,reference)
    mcur=canonical_paired_mean(procedure,feedback)
    rr=one_sided_radius(len(reference),ar/2)
    rc=one_sided_radius(len(feedback),ar/2)
    upper_drop=mcur-mref+rr+rc
    # The same upper bound for the current mean can certify insufficiency
    # separately (no inference of future harm). Allocate an extra alpha / 2
    # if this alternative is used; at present only the drop test gates action.
    alarm=upper_drop < -config.monitor_drop
    return {'status':'ALARM' if alarm else 'CLEAR',
            'reason':'CERTIFIED_DETERIORATION' if alarm else 'NOT_DETECTED',
            'n':len(feedback),'n_reference':len(reference),
            'alpha':ar,'r_reference':round(rr,12),'r_current':round(rc,12),
            'mean_reference':round(mref,12),'mean_feedback':round(mcur,12),
            'drop_upper':round(upper_drop,12),
            'reference_digest':digest([(r.bits,r.label) for r in reference]),
            'feedback_digest':digest([(r.bits,r.label) for r in feedback])}


def fast_mask(name:str)->int:
    if name=='baseline:0':return 0
    return sum(1<<int(n) for n in name[4:].split(','))


def masked_accuracy(mask:int, observations:tuple[Example,...])->float:
    return sum(((((sum(bit<<i for i,bit in enumerate(row.bits)) & mask).bit_count()&1)^row.label)==0)
               for row in observations)/len(observations)


def rank_discovery(discovery:tuple[Example,...], width:int)->tuple[tuple[str,...],float]:
    """Ranks exactly the allowed candidate family; no oracle target access."""
    if not discovery:raise ValueError('Missing discovery observations')
    names=candidates(width)
    packed=[(sum(bit<<i for i,bit in enumerate(row.bits)),row.label) for row in discovery]
    scored=[]
    for name in names:
        mask=fast_mask(name)
        correct=sum(((bits&mask).bit_count()&1)==label for bits,label in packed)
        scored.append((name,correct/len(discovery)))
    scored.sort(key=lambda x:(-x[1],x[0]))
    baseline=sum(label==0 for bits,label in packed)/len(discovery)
    return tuple(name for name,score in scored),scored[0][1]-baseline


def propose(state:RenewalState,segment:Segment,mode:str,config:RenewalConfig,
            excluded:set[str]|None=None)->tuple[str|None,str,int,int]:
    """Exploration/retention uses prevalidation data only."""
    excluded = excluded or set()
    base=config.base
    if mode=='baseline':return None,'baseline',0,0
    if mode=='fixed_reuse' and state.anchor:
        return state.anchor,'fixed_anchor',0,0
    if mode in ('crystal','monitor_hold'):
        remembered=[name for name,rec in state.memory.items()
                    if name not in excluded and rec['status']!='RETIRED'
                    and valid_procedure(name,base.width)]
        if remembered:
            scout=segment.scout[:base.scout_size]
            if scout:
                ordered=sorted(remembered,key=lambda p:(-masked_accuracy(fast_mask(p),scout),p))
                score=masked_accuracy(fast_mask(ordered[0]),scout)
                if score>=base.scout_accuracy_gate:
                    return ordered[0],'memory',len(scout),len(scout)*len(remembered)
    if len(segment.discovery)<base.discovery_size:
        return None,'insufficient_discovery',0,0
    if segment.discovery_ranked:
        rank=segment.discovery_ranked
        gain=segment.discovery_gain
    else:
        rank,gain=rank_discovery(segment.discovery[:base.discovery_size],base.width)
    available=[n for n in rank if n not in excluded]
    ops=len(candidates(base.width))*base.discovery_size
    if not available:return None,'no_candidates',base.discovery_size,ops
    # Avoid misleadingly using the precomputed gain of a different winner.
    if available[0]!=rank[0]:
        best=available[0]
        gain=masked_accuracy(fast_mask(best),segment.discovery[:base.discovery_size])-masked_accuracy(0,segment.discovery[:base.discovery_size])
    if gain is None or gain<=base.discovery_gain_gate:
        return None,'low_gain',base.discovery_size,ops
    return available[0],'search',base.discovery_size,ops


def fresh_certificate(procedure:str|None,segment:Segment, index:int,
                      config:RenewalConfig)->dict:
    if procedure is None:
        return {'status':'HOLD','reason':'NO_PROPOSAL','n':0,'lower':None}
    # Reuse v2.0's prespecified-look certificate, but spend *separately*
    # over EACH certification attempt. This prevents unsound extra testing.
    from dataclasses import replace
    base=replace(config.base, alpha_total=config.alpha_promotion)
    return certify(procedure,segment.validation,index,0.0,base)


def initial_mem(state:RenewalState, config:RenewalConfig)->dict:
    result={k:dict(v) for k,v in state.memory.items()}
    for name,rec in result.items():
        if rec['status']=='RETAINED':rec['status']='NEEDS_RENEWAL'
        if (state.epoch+1)-rec['last_certified']>config.base.stale_after:
            rec['status']='RETIRED'
    return result


def transition(state:RenewalState,event:dict,config:RenewalConfig)->RenewalState:
    """Independent receipt replay checks transition, governance, credits."""
    if event['epoch']!=state.epoch+1:raise ValueError('Out-of-order epoch')
    if event['policy'] not in POLICIES:raise ValueError('Unapproved policy')
    if event['state_before']!=digest(state.to_dict()):raise ValueError('Stale state')
    if len(event['active'])!=3 or len(event['origins'])!=3 or any(
            not valid_procedure(p,config.base.width) for p in event['active']):
        raise ValueError('Invalid deployment procedure vector')
    if event['policy']=='baseline' and any(p!='baseline:0' for p in event['active']):
        raise ValueError('Baseline control cannot deploy procedures')
    for i in (0,1,2):
        permits=[p['procedure'] for p in event['promotions'] if p['block']==i]
        if permits and event['active'][i]!=permits[0]:
            raise ValueError('Certificate and deployed procedure differ')
    if event['policy'] not in ('fixed_reuse','baseline') and event['active'][0]!='baseline:0' and not any(
            p['block']==0 and p['procedure']==event['active'][0] for p in event['promotions']):
        raise ValueError('Initial deployment without fresh certification')
    if event['policy']=='crystal' and event['monitor']['status'] in ('ALARM','HOLD'):
        renewed=[p['procedure'] for p in event['promotions'] if p['block']==2]
        if event['active'][2]!='baseline:0' and event['active'][2] not in renewed:
            raise ValueError('Unsafe continuation after monitoring HOLD/ALARM')
    if event['policy']=='monitor_hold' and event['monitor']['status'] in ('ALARM','HOLD') and event['active'][2]!='baseline:0':
        raise ValueError('Monitor-HOLD cannot continue without new certificate')
    projected=round(float(event['queries'])*config.base.sample_cost +
                   float(event['prediction_ops'])*config.base.prediction_cost +
                   len(state.memory)*config.base.maintenance_cost +
                   float(event['monitor_labels'])*config.monitor_processing_cost,8)
    if event['status']=='BUDGET_HOLD':
        if event['queries'] or event['prediction_ops'] or float(event['cost'])!=0:
            raise ValueError('Budget HOLD cannot charge unperformed work')
    elif abs(projected-float(event['cost']))>1e-6:
        raise ValueError('Cost ledger does not balance')
    memory=initial_mem(state,config)
    anchor=state.anchor
    for item in event['promotions']:
        name=item['procedure']
        cert=item['certificate']
        if not valid_procedure(name,config.base.width) or name=='baseline:0':
            raise ValueError('Unpermitted procedure')
        if item['block'] not in (0,1,2) or cert['status']!='CERTIFIED' or cert['lower']<=config.base.minimum_gain:
            raise ValueError('Forged promotion claim')
        if cert['n'] not in config.base.validation_looks or cert['diff_digest'] is None:
            raise ValueError('Missing validation receipt')
        if event['policy'] in ('crystal','monitor_hold'):
            old=memory.get(name,{'certifications':0,'alarms':0,'last_certified':0,'status':'RETIRED'})
            memory[name]={'status':'RETAINED','certifications':int(old['certifications'])+1,
                          'alarms':int(old['alarms']), 'last_certified':event['epoch']}
            if len(memory)>config.base.capacity:
                victim=min(memory,key=lambda k:(memory[k]['status']!='RETIRED',
                           memory[k]['last_certified'],memory[k]['certifications'],k))
                if victim==name and len(memory)>1:
                    others=[k for k in memory if k!=name]
                    victim=min(others,key=lambda k:(memory[k]['status']!='RETIRED',
                                  memory[k]['last_certified'],memory[k]['certifications'],k))
                del memory[victim]
        if event['policy']=='fixed_reuse' and anchor is None:
            anchor=name
    for alarm in event['alarms']:
        if alarm['block'] not in (1,):raise ValueError('Monitoring only after middle block')
        result=alarm['monitor']
        name=alarm['procedure']
        if result['status'] not in ('ALARM','HOLD'):raise ValueError('Unjustified alarm')
        if result['status']=='ALARM' and not result['drop_upper'] < -config.monitor_drop:
            raise ValueError('Forged drift alarm')
        if result['status']=='HOLD' and result['reason']!='FEEDBACK_MISSING':
            raise ValueError('Invalid monitor HOLD')
        if name in memory and event['policy'] in ('crystal','monitor_hold'):
            record=memory[name]
            record['alarms']+=1
            record['status']=('RETIRED' if record['alarms']>=config.max_alarms_before_retire
                             else 'NEEDS_RENEWAL')
    if event['policy'] not in ('crystal','monitor_hold'):
        memory={}
    cost=float(event['cost']); revenue=float(event['revenue'])
    if any(not math.isfinite(v) for v in (cost,revenue)) or cost<0 or revenue<0:
        raise ValueError('Invalid financial transaction')
    if cost>state.credits+1e-7:raise ValueError('Overdraft transaction')
    next_state=RenewalState(epoch=event['epoch'],memory=memory,anchor=anchor,
                            credits=round(state.credits-cost+revenue,8))
    if event['state_after']!=digest(next_state.to_dict()):
        raise ValueError('Poststate commitment mismatch')
    return next_state


def renewal_step(state:RenewalState,packet:Packet,policy:str,
                 config:RenewalConfig)->tuple[dict,RenewalState]:
    """Execute a single 3-block epoch; monitoring evidence arrives AFTER block 1.

    The caller may know hidden experiment truth, but this function's signature
    forbids passing it. Neither source concept nor oracle true gain is used.
    """
    if packet.epoch!=state.epoch+1:raise ValueError('Wrong epoch')
    if policy not in POLICIES:raise ValueError('Unknown policy')
    if len(packet.segments)!=3:raise ValueError('Requires exactly three blocks')
    base=config.base
    for segment in packet.segments:
        if len(segment.validation)<base.validation_looks[-1]:
            raise ValueError('Insufficient fresh validation data')
        if not segment.live:raise ValueError('Empty deployment block')
    # Worst-case reservation guards all possible 3-block decisions *before*
    # sampling. Task revenues are added only AFTER the epoch, never prepaid.
    maxqueries=3*(base.scout_size+base.discovery_size+base.validation_looks[-1])
    maxops=3*(base.scout_size*base.capacity + base.discovery_size*len(candidates(base.width))
               +base.validation_looks[-1]) + len(packet.segments[1].live)
    reserve=round(maxqueries*base.sample_cost+maxops*base.prediction_cost+
                  base.capacity*base.maintenance_cost+
                  len(packet.segments[1].live)*config.monitor_processing_cost,8)
    budget_hold=state.credits+1e-8<reserve
    memory=initial_mem(state,config)
    # Only carry externally visible historical procedures, never their old certificates.
    working=RenewalState(epoch=state.epoch,memory=memory,anchor=state.anchor,
                         credits=state.credits)
    origins=[]; active=[]; promotions=[]; alarms=[]
    monitor={'status':'SKIPPED','reason':'POLICY_NO_MONITOR','n':0}
    total_queries=0; total_ops=0; source_reference=None; promoted=None
    reference_used=0

    def obtain(segment_idx:int,mode:str,exclude:set[str]|None=None)->tuple[str,str]:
        nonlocal total_queries,total_ops,source_reference,promoted,reference_used
        segment=packet.segments[segment_idx]
        cand,origin,queries,ops=propose(working,segment,mode,config,exclude)
        total_queries+=queries; total_ops+=ops
        index=(packet.epoch-1)*3+segment_idx+1
        certificate=fresh_certificate(cand,segment,index,config)
        total_queries+=certificate['n'];total_ops+=certificate['n']
        if certificate['status']!='CERTIFIED':
            return 'baseline:0','hold:'+origin
        promotions.append({'block':segment_idx,'procedure':cand,'source':origin,
                           'certificate':certificate})
        promoted=cand
        if working.anchor is None and policy=='fixed_reuse':working.anchor=cand
        if mode in ('crystal','monitor_hold'):
            old=working.memory.get(cand,{'certifications':0,'alarms':0,'last_certified':0})
            working.memory[cand]={'status':'RETAINED','certifications':int(old['certifications'])+1,
                                  'alarms':int(old['alarms']),'last_certified':packet.epoch}
        if segment_idx==0:
            # Full reference costs even if early stopping used fewer validation rows.
            reference_used=len(segment.validation)
            total_queries+=max(0,reference_used-certificate['n'])
            source_reference=segment.validation
        return cand,origin

    if budget_hold:
        active=['baseline:0']*3; origins=['budget_hold']*3
        monitor={'status':'HOLD','reason':'BUDGET_HOLD','n':0}
    elif policy=='baseline':
        active=['baseline:0']*3;origins=['baseline']*3
    else:
        initial,origin=obtain(0, policy)
        active.append(initial);origins.append(origin)
        if policy=='periodic':
            for part in (1,2):
                selected,origin=obtain(part,'memoryless')
                active.append(selected);origins.append(origin)
        elif policy=='fixed_reuse':
            # Uncertified reuse after the first epoch: deliberate unsafe control.
            hold=initial if initial!='baseline:0' else state.anchor
            if state.anchor:
                hold=state.anchor
            active.extend([hold or 'baseline:0']*2)
            origins.extend(['fixed_unsafe']*2)
        elif policy=='memoryless':
            active.extend([initial]*2)
            origins.extend(['static_until_epoch_end']*2)
        else:
            active.append(initial);origins.append('continue_unverified_future')
            if initial!='baseline:0' and source_reference is not None:
                feedback=packet.segments[1].reported_feedback
                index=(packet.epoch-1)*3+2
                monitor=drift_monitor(initial,source_reference,feedback,index,config)
                total_ops+=monitor['n']
                if monitor['status'] in ('ALARM','HOLD'):
                    alarms.append({'block':1,'procedure':initial,'monitor':monitor})
                    if initial in working.memory:
                        rec=working.memory[initial]
                        rec['alarms']+=1
                        rec['status']='RETIRED' if rec['alarms']>=config.max_alarms_before_retire else 'NEEDS_RENEWAL'
                    if monitor['status']=='HOLD' or policy=='monitor_hold':
                        last='baseline:0'; last_origin='monitor_hold'
                    else:
                        # Candidate is excluded for one immediate recovery attempt.
                        last,last_origin=obtain(2,'crystal',{initial})
                else:
                    last=initial;last_origin='monitor_clear_continuation'
            else:
                last='baseline:0' if initial=='baseline:0' else initial
                last_origin='no_active_candidate' if initial=='baseline:0' else 'unmonitored'
            active.append(last);origins.append(last_origin)

    if len(active)!=3:raise AssertionError('Invalid action vector')
    monitor_cost=config.monitor_processing_cost*monitor.get('n',0)
    cost=round(total_queries*base.sample_cost+total_ops*base.prediction_cost+
               len(state.memory)*base.maintenance_cost+monitor_cost,8)
    if budget_hold:cost=0.0
    if cost>state.credits+1e-8:
        raise AssertionError('Insufficient preflight reserve')
    block_gains=[];block_accuracies=[];revenues=[]
    for procedure,segment in zip(active,packet.segments):
        acc=sum(predict(procedure,r)==r.label for r in segment.live)/len(segment.live)
        baseacc=sum(r.label==0 for r in segment.live)/len(segment.live)
        block_gains.append(round(acc-baseacc,10))
        block_accuracies.append(round(acc,10))
        revenues.append(acc*len(segment.live)*base.revenue_per_correct)
    revenue=round(sum(revenues),8)
    surplus=round(sum(gain*len(segment.live) for gain,segment in zip(block_gains,packet.segments))-cost,8)
    event={'epoch':packet.epoch,'policy':policy,'status':'BUDGET_HOLD' if budget_hold else
           ('MONITOR_HOLD' if monitor['status']=='HOLD' else 'COMPLETED'),
           'active':active,'origins':origins,'promotions':promotions,'alarms':alarms,
           'monitor':monitor,'monitor_labels':monitor.get('n',0),
           'queries':total_queries,'prediction_ops':total_ops,'cost':cost,
           'revenue':revenue,'net_surplus':surplus,
           'block_gains':block_gains,'block_accuracies':block_accuracies,
           'evidence_digest':digest({'epoch':packet.epoch,
                'validation':[(r.bits,r.label) for p in packet.segments for r in p.validation],
                'scout':[(r.bits,r.label) for p in packet.segments for r in p.scout],
                'discovery':[(r.bits,r.label) for p in packet.segments for r in p.discovery],
                'feedback':[(r.bits,r.label) for r in packet.segments[1].reported_feedback] if
                          packet.segments[1].reported_feedback is not None else None}),
           'state_before':digest(state.to_dict())}
    # State digest must be constructed from exactly the trusted replay function.
    memory_final=initial_mem(state,config)
    for item in promotions:
        name=item['procedure']
        if policy in ('crystal','monitor_hold'):
            old=memory_final.get(name,{'certifications':0,'alarms':0,'last_certified':0})
            memory_final[name]={'status':'RETAINED','certifications':int(old['certifications'])+1,
                                'alarms':int(old['alarms']),'last_certified':packet.epoch}
            if len(memory_final)>base.capacity:
                victim=min(memory_final,key=lambda k:(memory_final[k]['status']!='RETIRED',
                           memory_final[k]['last_certified'],memory_final[k]['certifications'],k))
                if victim==name and len(memory_final)>1:
                    others=[k for k in memory_final if k!=name]
                    victim=min(others,key=lambda k:(memory_final[k]['status']!='RETIRED',
                                  memory_final[k]['last_certified'],memory_final[k]['certifications'],k))
                del memory_final[victim]
    for alarm in alarms:
        name=alarm['procedure']
        if name in memory_final and policy in ('crystal','monitor_hold'):
            memory_final[name]['alarms']+=1
            memory_final[name]['status']=('RETIRED' if memory_final[name]['alarms']>=config.max_alarms_before_retire
                                          else 'NEEDS_RENEWAL')
    if policy not in ('crystal','monitor_hold'):memory_final={}
    anchor=state.anchor
    if policy=='fixed_reuse' and anchor is None and promotions:
        anchor=promotions[0]['procedure']
    expected=RenewalState(epoch=packet.epoch,memory=memory_final,anchor=anchor,
                          credits=round(state.credits-cost+revenue,8))
    event['state_after']=digest(expected.to_dict())
    recovered=transition(state,event,config)
    if recovered.to_dict()!=expected.to_dict():raise AssertionError('Receipt/state mismatch')
    return event,recovered


class RenewalLedger:
    """Hash-chained JSONL ledger; checksums detect accidents, not malicious rewrite."""
    def __init__(self,path:str|Path, config:RenewalConfig) -> None:
        self.path=Path(path);self.config=config
        self.path.parent.mkdir(parents=True,exist_ok=True)

    def replay(self)->RenewalState:
        state=RenewalState(credits=self.config.base.initial_credits)
        prior=GENESIS
        if not self.path.exists():return state
        with self.path.open('r',encoding='utf-8') as stream:
            for index,line in enumerate(stream,1):
                if not line.endswith('\n'):raise ValueError('Incomplete transaction')
                receipt=json.loads(line)
                if receipt.get('seq')!=index or receipt.get('parent')!=prior:
                    raise ValueError('Broken receipt chain')
                checked={k:v for k,v in receipt.items() if k!='hash'}
                if receipt.get('hash')!=digest(checked):raise ValueError('Tampered receipt')
                state=transition(state,receipt['event'],self.config)
                prior=receipt['hash']
        return state

    def append(self,event:dict)->RenewalState:
        prior_state=self.replay()
        after=transition(prior_state,event,self.config)
        prior=GENESIS
        if self.path.exists():
            with self.path.open('r',encoding='utf-8') as fd:
                for line in fd:prior=json.loads(line)['hash']
        receipt={'seq':prior_state.epoch+1,'parent':prior,'event':event}
        receipt['hash']=digest(receipt)
        with self.path.open('a',encoding='utf-8') as fd:
            fd.write(canonical(receipt)+'\n');fd.flush();os.fsync(fd.fileno())
        return after
