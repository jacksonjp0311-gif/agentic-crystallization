# Evidence API schema 2 — packaging preview rc2

Research remains v2.4. Installed distribution/implementation is 2.4.0rc2.
Receipts record `agentic-crystallization/evidence/2`, implementation_version and research_version.
Use `api_version.IMPLEMENTATION_VERSION` or installed distribution metadata; historical
`agentic_crystallization.__version__ == '1.0.0'` is preserved and is not the API version.

## Supported evidence and resource limits
Exact Protocol, Evidence and Measurement dataclasses only; behavioral subclasses and other
objects are rejected. The validator follows only the fixed schema before asdict, hashing or
JSON serialization. Containers at primitive leaves, cycles, extra nesting, nonfinite numbers,
numeric booleans and incomplete objects produce a bounded HOLD with `not_computed` digests.
It never stringifies the rejected input. Invalid trusted time still raises ValueError.
Invalid trusted epoch/context produces HOLD. A malformed-input receipt is diagnostic only.

Exactly two candidates and six measurements (three channels times two candidates).
Each sample tuple contains 1..16,384 paired gains; total at most 98,304 samples.
Each text field has at most 4,096 characters, all text together at most 65,536 UTF-8 bytes.
Integers have magnitude at most 2**53-1; epochs are 1..1,000,000.
Samples must be finite builtin int/float in [-1,1]. These limits bound accepted JSON
below 4 MiB; callers parsing external JSON must also bound bytes and parser nesting.
Limits are operational constraints, not new statistical assumptions.

## Mathematical and campaign boundary
Prespecify candidates, baseline, evaluator revision, task/context, sample counts, finite
horizon and confidence budget before observations. No optional sample-size stopping or
undeclared repeated looks. A protocol ID, timestamp or Boolean does not prove preregistration.
Observations within a stream must satisfy the stated independence/bounded-expectation
assumptions. Channels need not be mutually independent for union coverage.
Agreement cannot prove measurement honesty, exclude shared corruption or identify a liar.
CERTIFY_CURRENT means conditional measured superiority in the supplied current epoch/context,
not future validity, economic value, authorization or demonstrated agent improvement.

The API is stateless: identical calls return identical bounds, never extra samples.
Ledger duplicates are rejected by sample ID and protocol/epoch. Renaming every ID cannot
be distinguished from new data by hashes: hosts must govern real observation identities.
Separate protocols need explicit campaign-level alpha allocation whose total is controlled
externally. No automatic lifetime protection is implemented or claimed.
Integration must use host-owned campaign/protocol identity and a frozen allocation manifest.

## Safe evaluation and recording
Use `ledger.evaluate_and_record(evidence, now=..., current_epoch=..., current_context=...)`.
It computes the exact recommendation internally and atomically inserts it.
`record(evidence, receipt, *, now, current_epoch, current_context)` is a compatibility path:
it recomputes using trusted caller context and compares all receipt fields before insertion.
Altered decisions, bounds, costs, assumptions and version identity are rejected without
recursively serializing caller-supplied receipt content.

Concurrent duplicates permit one insertion. Transaction rollback includes protocol and sample
rows. Replay returns stored historical records; it does not renew certification.
Assess old evidence again with current time/context/epoch for STALE. A renewed certificate
requires newly acquired evidence for a governed protocol epoch. Old schema-1 rows remain
readable but are historical unverified-caller records; new insertion uses schema 2.
The SQLite file is caller-owned, not tamper-proof. Ledger membership never grants authority.
Hashes establish identity, not honesty, producer authentication or cryptographic trust.

## Cost semantics
`gain_semantics` is either `reward_gain` or `net_task_utility_gain`.
The latter may already subtract task execution costs, but MUST exclude the audit costs
reported separately in `verification_cost`. The mathematical test does not subtract that
cost again. Reported cost is accounting, not a prospective acquisition decision.
CERTIFY_CURRENT does not mean obtaining the evidence was economically worthwhile.
A future acquisition scheduler must evaluate expected benefits and prospective audit costs
before acquisition; it is a separate component. Missing/invalid evidence may have unknown cost.
