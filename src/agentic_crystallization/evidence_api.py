"""Preview external-evidence contract. No sampling, agent control or truth inference.

Fixed two-candidate, three-channel finite-horizon bounds. Producer assertions
must be independently justified; this module cannot authenticate their truth.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from contextlib import closing
import hashlib
import json
import math
from pathlib import Path
import sqlite3
from typing import Literal
from .api_version import API_SCHEMA, IMPLEMENTATION_VERSION, RESEARCH_VERSION

Status = Literal["CERTIFY_CURRENT", "HOLD", "STALE", "ALARM"]
CHANNELS = ("primary", "anchor", "reference")
MAX_SAMPLES = 16384
MAX_TOTAL_SAMPLES = 6 * MAX_SAMPLES
MAX_TEXT = 4096
MAX_TEXT_BYTES = 65536
MAX_EPOCHS = 1000000
MAX_INTEGER = 2**53 - 1


@dataclass(frozen=True)
class Protocol:
    identity: str
    candidates: tuple[str, str]
    baseline: str
    task: str
    context: str
    epochs: int
    alpha: float
    sample_counts: tuple[int, int, int]
    committed_at: float
    sampling_design: str
    reference_assumption: str
    independent_within_stream: bool
    fixed_before_observation: bool
    evaluator_revision: str = ""
    gain_semantics: str = "reward_gain"


@dataclass(frozen=True)
class Measurement:
    receipt_id: str
    candidate: str
    baseline: str
    channel: str
    provenance: str
    samples: tuple[float, ...]
    lower: float
    upper: float
    started_at: float
    ended_at: float
    verification_cost: float


@dataclass(frozen=True)
class Evidence:
    protocol: Protocol
    epoch: int
    audit_requested_at: float
    reference_revealed_at: float
    expires_at: float
    measurements: tuple[Measurement, ...]


@dataclass(frozen=True)
class Receipt:
    schema: str
    status: Status
    reason: str
    selected: str | None
    evidence_digest: str
    protocol_digest: str
    epoch: int | None
    context: str | None
    verification_cost: float | None
    evaluated_at: float
    bounds: dict
    assumptions: tuple[str, ...]
    implementation_version: str = IMPLEMENTATION_VERSION
    research_version: str = RESEARCH_VERSION

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, allow_nan=False)


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False,
                                    separators=(",", ":")).encode()).hexdigest()


def _number(x) -> bool:
    return ((type(x) is int and x.bit_length() <= 53 and abs(x) <= MAX_INTEGER)
            or (type(x) is float and math.isfinite(x)))


def _text(x) -> bool:
    return type(x) is str and len(x) <= MAX_TEXT and bool(x.strip())


def _structure(e) -> bool:
    """Fixed-depth shape walk: no user-controlled recursive traversal or methods.

    Reject containers at primitive leaves. Cycles/nesting cannot enter this shape.
    Length limits precede iteration; exact classes exclude behavioral subclasses.
    At most 98,304 numeric leaves and 65,536 UTF-8 text bytes are visited.
    """
    if type(e) is not Evidence:
        return False
    text_bytes = 0

    def texts(obj, names):
        nonlocal text_bytes
        for name in names:
            value = getattr(obj, name)
            if not _text(value):
                return False
            text_bytes += len(value.encode("utf-8"))
            if text_bytes > MAX_TEXT_BYTES:
                return False
        return True

    def numbers(obj, names):
        return all(_number(getattr(obj, name)) for name in names)

    try:
        p = e.protocol
        if type(p) is not Protocol:
            return False
        if not texts(p, ("identity", "baseline", "task", "context", "sampling_design",
                         "reference_assumption", "evaluator_revision", "gain_semantics")):
            return False
        if type(p.candidates) is not tuple or len(p.candidates) != 2:
            return False
        for value in p.candidates:
            if not _text(value):
                return False
            text_bytes += len(value.encode("utf-8"))
        if (type(p.sample_counts) is not tuple or len(p.sample_counts) != 3
                or any(type(n) is not int or not 1 <= n <= MAX_SAMPLES for n in p.sample_counts)
                or type(p.epochs) is not int or not 1 <= p.epochs <= MAX_EPOCHS
                or type(e.epoch) is not int or not 0 <= e.epoch < p.epochs
                or type(p.independent_within_stream) is not bool
                or type(p.fixed_before_observation) is not bool
                or p.gain_semantics not in ("reward_gain", "net_task_utility_gain")):
            return False
        if not numbers(p, ("alpha", "committed_at")) or not numbers(
                e, ("audit_requested_at", "reference_revealed_at", "expires_at")):
            return False
        if type(e.measurements) is not tuple or len(e.measurements) != 6:
            return False
        total = 0
        for m in e.measurements:
            if type(m) is not Measurement:
                return False
            if not texts(m, ("receipt_id", "candidate", "baseline", "channel", "provenance")):
                return False
            if not numbers(m, ("lower", "upper", "started_at", "ended_at", "verification_cost")):
                return False
            if type(m.samples) is not tuple or not 1 <= len(m.samples) <= MAX_SAMPLES:
                return False
            total += len(m.samples)
            if total > MAX_TOTAL_SAMPLES or any(not _number(x) or not -1 <= x <= 1 for x in m.samples):
                return False
        return text_bytes <= MAX_TEXT_BYTES
    except (AttributeError, UnicodeError):
        return False


def _matches(expected, actual):
    """Compare only the bounded shape of a locally computed receipt."""
    if type(expected) is not type(actual):
        return False
    if type(expected) is dict:
        return (len(expected) == len(actual) and all(type(k) is str for k in actual) and all(
            k in actual and _matches(v, actual[k]) for k, v in expected.items()))
    if type(expected) in (list, tuple):
        return len(expected) == len(actual) and all(_matches(a, b) for a, b in zip(expected, actual))
    if type(expected) is str:
        return len(expected) == len(actual) and expected == actual
    return expected == actual


def evaluate(evidence: Evidence, *, now: float, current_epoch: int,
             current_context: str) -> Receipt:
    """Return a recommendation receipt; invalid evidence produces HOLD.

    `now`, current epoch and context are supplied by a trusted caller. This is
    not an anytime-valid test. A caller must not recycle protocols/budgets.
    """
    if not _number(now) or now < 0:
        raise ValueError("A finite nonnegative trusted evaluation time is required")
    if not _structure(evidence):
        return Receipt(API_SCHEMA, "HOLD", "invalid_bounded_structure", None,
                       "not_computed", "not_computed", None, None, None, now, {},
                       ("Evidence rejected before serialization; no certification.",))
    digest = "unserializable"
    protocol_digest = "unserializable"
    cost = None
    bounds = {}
    p = evidence.protocol if isinstance(evidence, Evidence) else None

    def result(status, reason, selected=None):
        accounted = reason in (
            "conditional_current_certificate", "channel_disagreement_quarantine",
            "insufficient_separation", "uncorroborated_winner",
            "epoch_context_or_expiry_changed", "invalid_current_context")
        return Receipt(API_SCHEMA, status, reason, selected,
                       digest, protocol_digest,
                       evidence.epoch if isinstance(evidence, Evidence) and type(evidence.epoch) is int else None,
                       p.context if isinstance(p, Protocol) and _text(p.context) else None,
                       cost if accounted else None, now, bounds,
                       ("External provenance and honesty are assumed, not verified.",
                        "Fixed catalog/counts; independent bounded within-stream observations.",
                        "Agreement cannot exclude shared corruption.",
                        "No future validity or actual agent-performance claim."))

    try:
        if not isinstance(evidence, Evidence) or not isinstance(p, Protocol):
            return result("HOLD", "invalid_schema")
        digest = _digest(asdict(evidence))
        protocol_digest = _digest(asdict(p))
        if (not isinstance(p.candidates, tuple) or len(p.candidates) != 2
                or not all(_text(x) for x in p.candidates)
                or len(set(p.candidates)) != 2 or p.baseline in p.candidates
                or not all(_text(x) for x in (p.identity, p.baseline, p.task, p.context))):
            return result("HOLD", "invalid_identity")
        if (type(p.epochs) is not int or p.epochs < 1
                or type(evidence.epoch) is not int or not 0 <= evidence.epoch < p.epochs
                or not _number(p.alpha) or not 0 < p.alpha < 1
                or not isinstance(p.sample_counts, tuple) or len(p.sample_counts) != 3
                or any(type(n) is not int or n < 1 for n in p.sample_counts)):
            return result("HOLD", "invalid_confidence_allocation")
        if (p.independent_within_stream is not True or p.fixed_before_observation is not True
                or not _text(p.sampling_design) or not _text(p.reference_assumption)):
            return result("HOLD", "missing_measurement_assumptions")
        times = (p.committed_at, evidence.audit_requested_at,
                 evidence.reference_revealed_at, evidence.expires_at)
        if (not all(_number(t) and t >= 0 for t in times)
                or not p.committed_at <= evidence.audit_requested_at <= evidence.reference_revealed_at <= now
                or evidence.expires_at <= evidence.reference_revealed_at):
            return result("HOLD", "invalid_audit_order")
        if not isinstance(evidence.measurements, tuple) or len(evidence.measurements) != 6:
            return result("HOLD", "missing_or_extra_measurement")
        seen_ids = set()
        indexed = {}
        cost = 0.0
        for m in evidence.measurements:
            if not isinstance(m, Measurement):
                return result("HOLD", "invalid_measurement")
            if (m.candidate not in p.candidates or m.baseline != p.baseline
                    or m.channel not in CHANNELS):
                return result("HOLD", "measurement_identity_mismatch")
            key = (m.channel, m.candidate)
            if not _text(m.receipt_id) or m.receipt_id in seen_ids or key in indexed:
                return result("HOLD", "duplicate_receipt")
            if not _text(m.provenance):
                return result("HOLD", "missing_provenance")
            if (not _number(m.lower) or not _number(m.upper)
                    or (m.lower, m.upper) != (-1, 1)
                    or not isinstance(m.samples, tuple)
                    or len(m.samples) != p.sample_counts[CHANNELS.index(m.channel)]
                    or any(not _number(x) or not -1 <= x <= 1 for x in m.samples)):
                return result("HOLD", "unsupported_range_or_sampling")
            if (not _number(m.started_at) or not _number(m.ended_at)
                    or not evidence.audit_requested_at <= m.started_at <= m.ended_at <= evidence.reference_revealed_at):
                return result("HOLD", "invalid_measurement_window")
            if not _number(m.verification_cost) or m.verification_cost < 0:
                cost = None
                return result("HOLD", "invalid_verification_cost")
            cost += m.verification_cost
            if not math.isfinite(cost):
                cost = None
                return result("HOLD", "invalid_verification_cost")
            seen_ids.add(m.receipt_id)
            indexed[key] = m
        if type(current_epoch) is not int or not _text(current_context):
            return result("HOLD", "invalid_current_context")
        if current_epoch != evidence.epoch or current_context != p.context or now >= evidence.expires_at:
            return result("STALE", "epoch_context_or_expiry_changed")
        radii = {}
        means = {}
        for (channel, candidate), m in indexed.items():
            n = len(m.samples)
            radius = math.sqrt(2 * (math.log(12) + math.log(p.epochs) - math.log(p.alpha)) / n)
            mu = math.fsum(m.samples) / n
            means[channel, candidate] = mu
            radii[channel] = radius
            bounds.setdefault(channel, {})[candidate] = {"mean": mu, "lower": mu-radius, "upper": mu+radius, "n": n}
        for channel in ("primary", "anchor"):
            if any(abs(means[channel, a]-means["reference", a]) >
                   radii[channel]+radii["reference"] for a in p.candidates):
                return result("ALARM", "channel_disagreement_quarantine")
        winners = []
        for channel in CHANNELS:
            a = max(p.candidates, key=lambda a: means[channel, a])
            b = next(b for b in p.candidates if b != a)
            if bounds[channel][a]["lower"] <= max(0, bounds[channel][b]["upper"]):
                return result("HOLD", "insufficient_separation")
            winners.append(a)
        if len(set(winners)) != 1:
            return result("HOLD", "uncorroborated_winner")
        return result("CERTIFY_CURRENT", "conditional_current_certificate", winners[0])
    except (TypeError, ValueError, OverflowError, AttributeError):
        return result("HOLD", "invalid_evidence")


class ReceiptLedger:
    """Caller-owned SQLite store. Atomic uniqueness; no execution authority.

    Rejects repeated protocol/epoch decisions and sample receipt IDs, even if a
    caller changes protocol IDs. This is local replay protection, not a signature.
    All evidence paths must share one ledger; deleting it loses replay protection.
    """
    def __init__(self, path: str | Path):
        self.path = Path(path)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS receipts (digest TEXT PRIMARY KEY, protocol TEXT, epoch INTEGER, body TEXT, UNIQUE(protocol, epoch))")
            db.execute("CREATE TABLE IF NOT EXISTS samples (identity TEXT PRIMARY KEY, digest TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS protocols (identity TEXT PRIMARY KEY, digest TEXT)")

    def evaluate_and_record(self, evidence: Evidence, *, now: float,
                            current_epoch: int, current_context: str) -> Receipt:
        """Preferred trusted entry point. A stored result grants no authority."""
        receipt = evaluate(evidence, now=now, current_epoch=current_epoch,
                           current_context=current_context)
        self._insert(evidence, receipt)
        return receipt

    def record(self, evidence: Evidence, receipt: Receipt, *, now: float,
               current_epoch: int, current_context: str) -> None:
        """Compatibility path: require trusted context and compare every decision field."""
        expected = evaluate(evidence, now=now, current_epoch=current_epoch,
                            current_context=current_context)
        if type(receipt) is not Receipt or not _matches(asdict(expected), vars(receipt)):
            raise ValueError("Receipt differs from trusted recomputation")
        self._insert(evidence, expected)

    def _insert(self, evidence: Evidence, receipt: Receipt) -> None:
        # Store only validated complete evaluations, not malformed attempts.
        if receipt.reason not in ("conditional_current_certificate", "channel_disagreement_quarantine",
                                  "insufficient_separation", "uncorroborated_winner",
                                  "epoch_context_or_expiry_changed"):
            raise ValueError("Invalid evidence is not admissible to the ledger")
        try:
            with closing(sqlite3.connect(self.path)) as db, db:
                db.execute("BEGIN IMMEDIATE")
                previous = db.execute("SELECT digest FROM protocols WHERE identity=?", (evidence.protocol.identity,)).fetchone()
                if previous and previous[0] != receipt.protocol_digest:
                    raise ValueError("Protocol identity changed")
                db.execute("INSERT OR IGNORE INTO protocols VALUES (?,?)", (evidence.protocol.identity,receipt.protocol_digest))
                db.execute("INSERT INTO receipts VALUES (?,?,?,?)",
                           (receipt.evidence_digest,evidence.protocol.identity,evidence.epoch,receipt.to_json()))
                db.executemany("INSERT INTO samples VALUES (?,?)",
                               [(m.receipt_id,receipt.evidence_digest) for m in evidence.measurements])
        except sqlite3.IntegrityError as exc:
            raise ValueError("Repeated evidence, epoch, or sample receipt") from exc

    def replay(self) -> list[dict]:
        with closing(sqlite3.connect(self.path)) as db, db:
            return [json.loads(row[0]) for row in db.execute("SELECT body FROM receipts ORDER BY rowid")]
