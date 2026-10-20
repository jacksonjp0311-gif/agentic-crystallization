# v2.4 rc2 API hardening audit

Reference: b5641b86e7d657d19225396fe1d70af1e63e8509. No reset was performed.
Reproduced: cyclic context caused RecursionError before validation; altered selected=B
was stored with unchanged evidence hashes. The second was a documented trusted-caller
limitation, not a previously undisclosed authorization exploit.

Corrections: fixed-depth validation before recursive work; strict primitive/class limits;
trusted evaluate-and-record and full receipt recomputation; evaluator revision and explicit
gain semantics; schema/version identity; unprivileged fixture-containing research bundle.
All statistical formulas, frozen controllers, protected tests and results remain unchanged.
The new limits restrict admissible external inputs; they do not improve the theorem.

The conditional Hoeffding/union proof in SOURCE_AUDIT.md remains applicable to the declared
finite protocol. Within-stream independence is different from cross-channel dependence.
Superiority of measured gains requires honest measurement to imply superiority of true gains.
Current certification says nothing about future shifts. Disagreement rejects joint consistency,
not one identified channel. Shared corruption remains the permanent negative control.

The ledger is local replay protection, not identity verification or a campaign accountant.
Changing all labels does not create data. Confidence allocation across protocols and proof
of preregistration remain external host responsibilities. No lifetime guarantee is claimed.
Audit costs are recorded separately; they are not added as arbitrary statistical penalties.

Publication remains HOLD: license unresolved, public assets not anonymously verified while
private, archived-material disclosure review and owner publication approval pending.
Historical SOURCE_AUDIT.md and RELEASE_AUDIT.md remain prior audit records; this document
and API.md describe rc2 behavior.
