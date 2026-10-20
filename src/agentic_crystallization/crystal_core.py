"""CrystalKernel v2.0: a bounded, receipt-driven adaptive procedure loop.

No code synthesis, permissions, automatic self-modification, or real-world effect.
Only explicitly permitted XOR feature procedures can be proposed or promoted.
Statistical statements are CONDITIONAL on fresh IID validation within an epoch,
known bounded observations, and a defensible shift allowance.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from itertools import combinations
import json
import math
from pathlib import Path
import os
from typing import Iterable

GENESIS = '0' * 64


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value: object) -> str:
    return sha256(canonical(value).encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class Example:
    bits: tuple[int, ...]
    label: int

    def __post_init__(self) -> None:
        if any(x not in (0, 1) for x in self.bits) or self.label not in (0, 1):
            raise ValueError('Example must be a binary feature vector and a binary outcome')


def candidates(width: int, max_order: int = 3) -> tuple[str, ...]:
    if not (3 <= width <= 20 and 1 <= max_order <= min(width, 3)):
        raise ValueError('Catalog must have 3..20 features and order <= 3')
    return tuple('xor:' + ','.join(map(str, group))
                 for k in range(1, max_order + 1)
                 for group in combinations(range(width), k))


def valid_procedure(procedure: str, width: int) -> bool:
    if procedure == 'baseline:0':
        return True
    if not procedure.startswith('xor:'):
        return False
    try:
        features = tuple(int(v) for v in procedure[4:].split(','))
    except ValueError:
        return False
    return bool(1 <= len(features) <= 3 and tuple(sorted(set(features))) == features
                and features[0] >= 0 and features[-1] < width
                and procedure == 'xor:' + ','.join(map(str, features)))


def predict(procedure: str, example: Example) -> int:
    if procedure == 'baseline:0':
        return 0
    if not valid_procedure(procedure, len(example.bits)):
        raise ValueError('Unapproved procedure')
    value = 0
    for k in (int(v) for v in procedure[4:].split(',')):
        value ^= example.bits[k]
    return value


def empirical_accuracy(procedure: str, data: tuple[Example, ...]) -> float:
    if not data:
        raise ValueError('No observations')
    return sum(int(predict(procedure, row) == row.label) for row in data) / len(data)


def paired_difference(procedure: str, row: Example) -> int:
    return int(predict(procedure, row) == row.label) - int(row.label == 0)


def lifetime_alpha(alpha_total: float, epoch: int) -> float:
    """Spends <= alpha_total across every positive integer epoch."""
    if not (0.0 < alpha_total < 1.0 and epoch >= 1):
        raise ValueError('Invalid significance budget or episode')
    return alpha_total / (epoch * (epoch + 1))


def lower_radius(n: int, epoch: int, looks: int, alpha_total: float) -> float:
    """One-sided Hoeffding radius for differences in [-1,1].

    Across L predeclared looks and unlimited episodes, false-positive
    certification probability <= alpha_total (given conditional iid samples).
    """
    if n <= 0 or looks <= 0:
        raise ValueError('Positive sample size / count of looks required')
    alpha_e = lifetime_alpha(alpha_total, epoch)
    return math.sqrt(2.0 * math.log(looks / alpha_e) / n)


@dataclass(frozen=True)
class Configuration:
    width: int = 8
    capacity: int = 4
    stale_after: int = 5
    validation_looks: tuple[int, ...] = (64, 128, 256, 512)
    scout_size: int = 24
    discovery_size: int = 96
    alpha_total: float = 0.05
    minimum_gain: float = 0.025
    scout_accuracy_gate: float = 0.83
    discovery_gain_gate: float = 0.08
    initial_credits: float = 50.0
    sample_cost: float = 0.025
    prediction_cost: float = 0.00002
    maintenance_cost: float = 0.1
    revenue_per_correct: float = 0.2
    deployment_scale: float = 2048.0

    def __post_init__(self) -> None:
        candidates(self.width)
        looks = self.validation_looks
        if not looks or any(n <= 0 for n in looks) or sorted(set(looks)) != list(looks):
            raise ValueError('Validation checkpoints must be increasing positive integers')
        if self.capacity < 1 or self.stale_after < 0 or self.scout_size < 1 or self.discovery_size < 1:
            raise ValueError('Invalid capacity or sample sizes')
        if not (0 < self.alpha_total < 1) or self.initial_credits < 0:
            raise ValueError('Invalid error budget or capital')


@dataclass
class CrystalState:
    epoch: int = 0
    memory: dict[str, dict[str, int]] = field(default_factory=dict)
    anchor: str | None = None
    credits: float = 50.0

    def to_dict(self) -> dict:
        return {'epoch': self.epoch, 'memory': self.memory, 'anchor': self.anchor,
                'credits': round(self.credits, 8)}

    @classmethod
    def from_dict(cls, obj: dict) -> CrystalState:
        return cls(epoch=int(obj['epoch']),
                   memory={str(k): dict(v) for k, v in obj['memory'].items()},
                   anchor=obj['anchor'], credits=float(obj['credits']))


@dataclass(frozen=True)
class Evidence:
    """The deployed policy receives only these observations, not target truth."""
    epoch: int
    scout: tuple[Example, ...]
    discovery: tuple[Example, ...]
    validation: tuple[Example, ...]
    shift_allowance: float | None  # None => HOLD; external justification mandatory


def select_proposal(state: CrystalState, evidence: Evidence, config: Configuration,
                    mode: str) -> tuple[str | None, str, int, int, list[str]]:
    """Returns (candidate, source, observations, prediction operations, shortlist).

    Selection is based EXCLUSIVELY on preliminary examples; validation held out.
    """
    if mode not in ('crystal', 'memoryless', 'reuse_only', 'baseline'):
        raise ValueError('Unknown policy')
    if mode == 'baseline':
        return None, 'baseline', 0, 0, []
    if mode == 'reuse_only' and state.anchor is not None:
        return state.anchor, 'anchor', 0, 0, [state.anchor]

    n_scout = min(config.scout_size, len(evidence.scout))
    remembered = [name for name in sorted(state.memory) if valid_procedure(name, config.width)]
    if mode == 'crystal' and remembered and n_scout:
        scout = evidence.scout[:n_scout]
        ranked = sorted(remembered, key=lambda p: (-empirical_accuracy(p, scout), p))
        if empirical_accuracy(ranked[0], scout) >= config.scout_accuracy_gate:
            return ranked[0], 'memory', n_scout, n_scout * len(remembered), ranked

    source = evidence.discovery[:config.discovery_size]
    if len(source) != config.discovery_size:
        return None, 'insufficient_discovery', n_scout if remembered and mode == 'crystal' else 0, 0, []
    library = candidates(config.width)
    ranked = sorted(library, key=lambda p: (-empirical_accuracy(p, source), p))
    best = ranked[0]
    baseline = empirical_accuracy('baseline:0', source)
    discovery_queries = len(source)
    pred_ops = len(library) * len(source)
    if mode == 'crystal' and remembered:
        discovery_queries += n_scout
        pred_ops += n_scout * len(remembered)
    if empirical_accuracy(best, source) - baseline <= config.discovery_gain_gate:
        return None, 'low_evidence', discovery_queries, pred_ops, ranked[:4]
    return best, 'search', discovery_queries, pred_ops, ranked[:4]


def certify(procedure: str, validation: tuple[Example, ...], epoch: int,
            shift_allowance: float | None, config: Configuration) -> dict:
    """Anytime-valid at predeclared looks, for one preselected candidate.

    Selection must be independent of this validation data. Certificates last
    for this source/target epoch ONLY and certify GAIN over baseline, not best.
    """
    if shift_allowance is None:
        return {'status':'HOLD', 'reason':'SHIFT_UNJUSTIFIED', 'n':0, 'look':0,
                'lower':None, 'radius':None, 'estimated_gain':None, 'diff_digest':None}
    if not (0 <= shift_allowance <= 1):
        raise ValueError('Shift allowance must be [0,1] or None')
    if not valid_procedure(procedure, config.width) or procedure == 'baseline:0':
        raise ValueError('Candidate outside permitted family')
    checkpoints = config.validation_looks
    max_available = len(validation)
    total = 0
    start = 0
    history = []
    for i, end in enumerate(checkpoints, 1):
        if end > max_available:
            break
        diffs = [paired_difference(procedure, row) for row in validation[start:end]]
        total += sum(diffs)
        start = end
        radius = lower_radius(end, epoch, len(checkpoints), config.alpha_total)
        estimate = total/end
        lower = estimate - radius - shift_allowance
        history.append({'n':end, 'sum':total, 'radius':round(radius, 12),
                        'lower':round(lower, 12)})
        if lower > config.minimum_gain:
            return {'status':'CERTIFIED', 'reason':'POSITIVE_GAIN', 'n':end,
                    'look':i,'lower':round(lower,12), 'radius':round(radius,12),
                    'estimated_gain':round(estimate,12),
                    'diff_digest': digest([paired_difference(procedure,r) for r in validation[:end]]),
                    'checkpoints':history}
    if not history:
        return {'status':'HOLD','reason':'INSUFFICIENT_VALIDATION', 'n':0, 'look':0,
                'lower':None,'radius':None,'estimated_gain':None,'diff_digest':None,
                'checkpoints':[]}
    last=history[-1]
    return {'status':'HOLD','reason':'NOT_CERTIFIED', 'n':last['n'],
            'look':len(history), 'lower':last['lower'], 'radius':last['radius'],
            'estimated_gain':round(last['sum']/last['n'],12),
            'diff_digest':digest([paired_difference(procedure,r) for r in validation[:last['n']]]),
            'checkpoints':history}


def compute_next_state(previous: CrystalState, payload: dict, config: Configuration) -> CrystalState:
    """Deterministic ledger transition; validates every promotion on replay.

    Historical memory is NOT a certification in a new epoch.
    """
    ep = previous.epoch + 1
    if payload['epoch'] != ep:
        raise ValueError('Unexpected sequence or epoch')
    mode = payload['mode']
    if mode not in ('crystal','memoryless','reuse_only','baseline'):
        raise ValueError('Policy not permitted')
    status = payload['status']
    if status not in ('CERTIFIED','HOLD'):
        raise ValueError('Unknown certification status')
    chosen = payload['candidate']
    if chosen is not None and not valid_procedure(chosen, config.width):
        raise ValueError('Unapproved candidate')
    shift = payload['shift_allowance']
    if status == 'CERTIFIED':
        if chosen is None or shift is None or not (0 <= shift <= 1):
            raise ValueError('Invalid certified candidate or shift premise')
        if payload['certificate']['lower'] <= config.minimum_gain:
            raise ValueError('Insufficient certificate for promotion')
        if payload['certificate']['status'] != 'CERTIFIED':
            raise ValueError('Forged certificate status')
    if status == 'HOLD' and payload['active'] != 'baseline:0':
        raise ValueError('HOLD must fall back to baseline')
    if status == 'CERTIFIED' and payload['active'] != chosen:
        raise ValueError('Certified action must match candidate')
    if shift is None and status == 'CERTIFIED':
        raise ValueError('Cannot certify without shift premise')

    memory = {k:dict(v) for k,v in previous.memory.items()
              if ep-v['last_certified'] <= config.stale_after}
    anchor=previous.anchor
    if status == 'CERTIFIED' and mode == 'reuse_only' and anchor is None:
        anchor=chosen
    if status == 'CERTIFIED' and mode == 'crystal':
        former=memory.get(chosen, {'count':0})
        memory[chosen]={'last_certified':ep, 'count':former['count']+1}
        if len(memory)>config.capacity:
            victim=min(memory,key=lambda k:(memory[k]['last_certified'],memory[k]['count'],k))
            del memory[victim]
    if mode == 'memoryless':
        memory={}

    cost=float(payload['cost'])
    revenue=float(payload['revenue'])
    if not (math.isfinite(cost) and math.isfinite(revenue) and cost>=0 and revenue>=0):
        raise ValueError('Invalid cost/revenue')
    if cost>previous.credits + 1e-7:
        raise ValueError('Insufficient credits: transaction cannot be committed')
    credits=round(previous.credits-cost+revenue,8)
    new_state=CrystalState(epoch=ep,memory=memory,anchor=anchor,credits=credits)
    if digest(new_state.to_dict()) != payload['state_hash_after']:
        raise ValueError('State transition commitment does not match receipt')
    return new_state


class DurableLedger:
    """Hash-chained append-only receipt log; no automatic repair of corruption.

    This is an integrity *checksum chain*, not a secret-key signature or an
    anti-tamper scheme against actors able to rewrite the entire ledger.
    """
    def __init__(self, path: str|Path, config: Configuration) -> None:
        self.path=Path(path)
        self.config=config
        self.path.parent.mkdir(parents=True,exist_ok=True)

    def replay(self)->CrystalState:
        state=CrystalState(credits=self.config.initial_credits)
        prev=GENESIS
        if not self.path.exists():
            return state
        with self.path.open('r',encoding='utf-8') as stream:
            for seq,line in enumerate(stream,1):
                if not line.endswith('\n'):
                    raise ValueError('Incomplete receipt record; fail closed')
                obj=json.loads(line)
                if obj.get('seq')!=seq or obj.get('previous')!=prev:
                    raise ValueError('Receipt order/parent-chain mismatch')
                checked={k:v for k,v in obj.items() if k!='hash'}
                if obj.get('hash')!=digest(checked):
                    raise ValueError('Receipt content hash mismatch')
                if obj['payload']['state_hash_before'] != digest(state.to_dict()):
                    raise ValueError('Receipt starting state mismatch')
                state=compute_next_state(state,obj['payload'],self.config)
                prev=obj['hash']
        return state

    def append(self, payload:dict)->CrystalState:
        before=self.replay()
        if payload['state_hash_before'] != digest(before.to_dict()):
            raise ValueError('Concurrent or stale state')
        after=compute_next_state(before,payload,self.config)
        previous=GENESIS
        if self.path.exists():
            with self.path.open('r',encoding='utf-8') as src:
                for line in src:
                    previous=json.loads(line)['hash']
        obj={'seq':before.epoch+1,'previous':previous,'payload':payload}
        obj['hash']=digest(obj)
        with self.path.open('a',encoding='utf-8') as dest:
            dest.write(canonical(obj)+'\n')
            dest.flush()
            os.fsync(dest.fileno())
        return after


def step(state:CrystalState,evidence:Evidence,live:tuple[Example,...],
         config:Configuration,mode:str)->tuple[dict,CrystalState]:
    """One independent epoch. Deployed score never influences proposal/certification.

    This orchestrator is a simulation adapter; an external host must validate
    shift allowances and authorize all real-world effects.
    """
    if evidence.epoch != state.epoch+1:
        raise ValueError('Epoch order mismatch')
    if len(evidence.validation)<config.validation_looks[-1]:
        raise ValueError('Need full maximum fresh validation pool')
    if not live:
        raise ValueError('Need independent deployment evaluation')
    if evidence.shift_allowance is not None and not (0<=evidence.shift_allowance<=1):
        raise ValueError('Invalid shift allowance')

    # Shift qualification is external. Missing qualification => zero-cost HOLD.
    no_shift = evidence.shift_allowance is None
    reserved_max_queries = config.scout_size + config.discovery_size + config.validation_looks[-1]
    reserved_max_ops = (config.scout_size * len(state.memory)
                        + config.discovery_size * len(candidates(config.width))
                        + config.validation_looks[-1])
    reserved_cost = (config.sample_cost * reserved_max_queries
                     + config.prediction_cost * reserved_max_ops
                     + config.maintenance_cost * len(state.memory))
    no_budget = state.credits + 1e-9 < reserved_cost

    candidate=None
    source='none'
    scout_count=0
    ops=0
    shortlist=[]
    certificate={'status':'HOLD','reason':'NOT_EVALUATED','n':0,
                 'lower':None,'radius':None,'estimated_gain':None,'diff_digest':None}
    if not no_shift and not no_budget:
        candidate,source,scout_count,ops,shortlist=select_proposal(state,evidence,config,mode)
        if candidate is not None:
            certificate=certify(candidate,evidence.validation,evidence.epoch,evidence.shift_allowance,config)
            ops+=certificate['n']
    if no_shift:
        certificate['reason']='SHIFT_UNJUSTIFIED'
    if no_budget:
        certificate['reason']='BUDGET_HOLD'
    if candidate is None and not no_shift and not no_budget:
        certificate['reason']='NO_ELIGIBLE_PROPOSAL'

    status=certificate['status']
    active=candidate if status=='CERTIFIED' else 'baseline:0'
    queries=scout_count+certificate['n']
    cost=round(queries*config.sample_cost+ops*config.prediction_cost
               +len(state.memory)*config.maintenance_cost,8)
    if no_budget:
        cost=0.0  # No new work or storage charges on resource-depleted HOLD.
    # Deployment evaluation is kept OUT of the selection/certification path.
    accuracy=sum(predict(active,row)==row.label for row in live)/len(live)
    base_accuracy=sum(row.label==0 for row in live)/len(live)
    revenue=round(accuracy*len(live)*config.revenue_per_correct,8)
    surplus=round(config.deployment_scale*(accuracy-base_accuracy)-cost,8)

    payload={'epoch':evidence.epoch,'mode':mode,'status':status,'candidate':candidate,
             'active':active,'proposal_source':source,'shortlist':shortlist,
             'shift_allowance':evidence.shift_allowance,'certificate':certificate,
             'queries':queries,'prediction_ops':ops,'cost':cost,'revenue':revenue,
             'score_accuracy':round(accuracy,10), 'baseline_accuracy':round(base_accuracy,10),
             'net_surplus':surplus, 'evidence_digest':digest({
                 'scout':[(r.bits,r.label) for r in evidence.scout[:config.scout_size]],
                 'discovery':[(r.bits,r.label) for r in evidence.discovery[:config.discovery_size]],
                 'validation_used':[(r.bits,r.label) for r in evidence.validation[:certificate['n']]]}),
             'state_hash_before':digest(state.to_dict())}

    # Compute state commitment before appending any receipt.
    memory={k:dict(v) for k,v in state.memory.items()
            if evidence.epoch-v['last_certified']<=config.stale_after}
    anchor=state.anchor
    if status=='CERTIFIED' and mode=='reuse_only' and anchor is None:
        anchor=candidate
    if status=='CERTIFIED' and mode=='crystal':
        old=memory.get(candidate,{'count':0})
        memory[candidate]={'last_certified':evidence.epoch,'count':old['count']+1}
        if len(memory)>config.capacity:
            victim=min(memory,key=lambda k:(memory[k]['last_certified'],memory[k]['count'],k))
            del memory[victim]
    if mode=='memoryless':
        memory={}
    credits=round(state.credits-cost+revenue,8)
    new=CrystalState(epoch=evidence.epoch,memory=memory,anchor=anchor,credits=credits)
    payload['state_hash_after']=digest(new.to_dict())
    # No hidden labels or generator internals enter the controller.
    verified=compute_next_state(state,payload,config)
    if verified.to_dict()!=new.to_dict():
        raise AssertionError('State transition mismatch')
    return payload,verified
