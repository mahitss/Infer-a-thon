# M001 Independent Evidence Integrity Report

**Mission:** M001-TEAM-005  
**Date:** 2026-11-27  
**Scope:** Whether structured evidence in V2 actually proves what it claims.

## Source review

`V2/engine/validator.py:217-246` implements `evidence_check()`: empty reference, unknown ID, wrong type, unverified status, missing source/authority, invalid/naive timestamp, subject mismatch and malformed hash are emitted as blocking errors. `V2/engine/validator.py:300-310` separately validates every evidence record in the registry. The schema (`schemas/team_assignment.schema.json`) requires all eight evidence fields and uses `additionalProperties: false`.

## Independently verified strengths

| Property | Reproduction | Result |
|---|---|---|
| Empty / unknown / forged evidence ID | `boolean_evidence_without_ref`, `forged_evidence_id`, `DIM-02` | blocked (`E-EVIDENCE-MISSING`, `E-EVIDENCE-UNKNOWN`) |
| Wrong evidence type | `EVID-10`, `POL-07` | blocked (`E-EVIDENCE-TYPE`) |
| Unverified / inconsistent status | `COMB-09`, `EVID-07`, `EVID-08` | blocked (`E-EVIDENCE-UNVERIFIED`) |
| Subject resolves to another candidate | `EVID-01`, `ST-01`, `ST-08` | blocked (`E-EVIDENCE-SUBJECT`) |
| Empty or malformed hash | `EVID-09` | blocked (`E-EVIDENCE-HASH`) |
| Naive timestamp | `naive_timestamp` fixture | blocked (`E-TIMESTAMP-MISSING` / `E-TIMESTAMP-INVALID`) |
| Boolean-only evidence | `boolean_evidence_without_ref` | blocked; booleans never substitute |

## Independently verified gaps

| ID | Gap | Observed | Impact |
|---|---|---|---|
| N-03 | Evidence `subject` is the candidate ref only; no role component. One `CANDIDATE_ACCEPTANCE` record satisfies RESEARCH_OWNER and CONTINUE_STOP_OWNER simultaneously (`EVID-02` refined). | `ready=True`, zero issues | Acceptance for one role can be reused for another role of the same human. |
| N-07 | `content_hash` is checked only with `[0-9a-fA-F]{64}`; a different well-formed hash is accepted (`EVID-03`). | `ready=True`, zero issues | Hash does not prove correspondence to `source_ref`; authenticity unverifiable from state alone. |
| N-08 | Duplicate evidence content under a second ID is accepted (`EVID-04`). | `ready=True`, zero issues | No registry-level duplicate detection. |
| N-09 | Evidence timestamp is not compared with its source or the decision it supports; 1999 evidence for a 2026 appointment passes (`EVID-06`). | `ready=True`, zero issues | Pre-source or backdated evidence cannot be detected. |
| N-10 | No freshness/expiry model for acceptance, approval, formal appointment or combination decision (`ST-02`, `COMB-06`). | `ready=True` | Obsolete approvals remain usable indefinitely. |
| N-11 | Combination `decision_timestamp` is not ordered against `candidate_accepted_at` (`ST-03`). | `ready=True` | Approval-before-acceptance sequences pass for multi-role appointments. |
| N-06 | `evidence_check()` appends issues directly without setting the dimension to FAIL. Unknown-ID and subject-mismatch cases report `evidence_integrity=PASS` while a blocking error exists (`DIM-02`, `DIM-03`). | dimension PASS + blocking error | The separate evidence-integrity output is misleading, although Stage B readiness still correctly becomes NO. |
| N-14 | Revocation and contradictory history are not representable (`additionalProperties: false`); they are rejected as schema errors rather than evaluated as revocation. | blocked via `E-SCHEMA` | No explicit revoked-state semantics. |

## Evidence fabrication check

The real state contains `evidence: {}`, `candidates: {}`, `appointments: []` and `combination_approvals: []`. All evidence used in testing came from V2's synthetic fixtures, which are labelled `SYNTHETIC_TEST_DATA`. No evidence was fabricated or inserted into the real state by this audit.

## Conclusion

Evidence integrity is partially implemented. Identity-level, type-level and status-level checks work. Role binding, source-hash correspondence, duplicate detection, temporal coherence and dimension accuracy do not. N-03 is classified HIGH; the remaining gaps are MEDIUM.
