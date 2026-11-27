# M001 V2.1 — Evidence Role-Binding Report (N-03)

**Mission:** M001-TEAM-006  
**Source:** independent register finding N-03 (acceptance evidence not role-bound)  
**Implementation:** `engine/validator.py` → `evidence_check()`, `acceptance_evidence_check()`

## What changed

V2 used `evidence_check(..., 'CANDIDATE_ACCEPTANCE', ref, ...)` — a subject of the candidate ref
only. One candidate-acceptance record with `subject=C-P1` therefore satisfied both
RESEARCH_OWNER and CONTINUE_STOP_OWNER. V2.1 replaces that call with
`acceptance_evidence_check()`, which enforces all required bindings:

| Binding | Enforcement | Error code |
|---|---|---|
| Exact candidate reference + exact role | `subject == '<candidate_ref>:<role>'` | `E-EVIDENCE-SUBJECT` |
| Exact role | `record.role == role` | `E-ACCEPTANCE-ROLE` |
| Relevant appointment | `record.appointment_ref == '<candidate_ref>:<role>'` | `E-ACCEPTANCE-APPOINTMENT` |
| Relevant decision | non-empty `decision_ref`, unique per appointment | `E-ACCEPTANCE-DECISION`, `E-ACCEPTANCE-DECISION-REUSED` |
| Evidence identifier | non-empty string, registry key equals `evidence_id` field | `E-EVIDENCE-MISSING`, `E-EVIDENCE-ID-MISMATCH` |
| Evidence type | `CANDIDATE_ACCEPTANCE` | `E-EVIDENCE-TYPE` |
| Verification status | `VERIFIED` | `E-EVIDENCE-UNVERIFIED` |
| Timezone-aware timestamp | `valid_timestamp()` | `E-TIMESTAMP-INVALID` |
| Recording authority | non-empty after whitespace check | `E-EVIDENCE-INCOMPLETE` |
| Revocation | `revoked is True` or `revoked_at is not None` rejected | `E-EVIDENCE-REVOKED` |

The schema's evidence definition now declares the five new optional fields; policy 2.1 records
`acceptance_evidence_binding`. A generic candidate acceptance record can no longer authorize
every role.

## Independently reproduced before/after

| Case | V2 (independent re-audit) | V2.1 |
|---|---|---|
| One acceptance record shared by two roles of one candidate | `ready=True`, zero issues | `E-ACCEPTANCE-APPOINTMENT`, `E-ACCEPTANCE-DECISION-REUSED`, `E-ACCEPTANCE-ROLE`, `E-EVIDENCE-SUBJECT`; ready NO |
| Acceptance evidence for the wrong role | accepted | blocked (test 11) |
| Acceptance evidence for another candidate | accepted | blocked (test 12) |
| Evidence for another appointment | accepted | blocked (test 13) |
| Reused evidence with subject mismatch | accepted | blocked (test 14) |
| Unverified evidence | blocked | blocked (test 15) |
| Revoked evidence | not representable | `E-EVIDENCE-REVOKED` (test 16) |
| Missing evidence | blocked | blocked (test 17) |
| Valid role-bound evidence | passed | passed (test 22) |

## Mutation proof

`M3_acceptance_role_binding_removed` changes the evidence-check subject back to the bare
candidate ref; the 8-check canary fails it (exit 1). 4/4 remediation mutations detected, 0 survived.

## Boundary

This does not implement source-content hash verification, freshness/expiry, duplicate-evidence
content detection or evidence timestamp-vs-source ordering. Those remain tracked MEDIUM findings
from the independent re-audit and are not claimed resolved.
