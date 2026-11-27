# M001 V2.1 High-Finding Remediation Matrix

**Mission:** M001-TEAM-006  
**Date:** 2026-11-27  
**Canonical source:** `M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT/M001_FINAL_DEFECT_REGISTER.json`  
**Rule:** the original defect register is untouched; each remediation links to its canonical finding ID.

## The four canonical HIGH findings

| Canonical ID | Title (from independent register) | V2.1 remediation | Source location | Verified by |
|---|---|---|---|---|
| N-01 | Whitespace-only Product Owner approval basis satisfies formal appointment | `meaningful_text()` requires a string with at least one non-whitespace Unicode character; approval basis now uses it. Empty, ASCII-whitespace, Unicode-whitespace, null, missing and non-string values all emit blocking `E-DECISION-EVIDENCE-EMPTY`; no coercion and no manufactured rationale. | `engine/validator.py` `meaningful_text()` and formal-appointment approval block | tests 01–06; mutations M1 |
| N-02 | Whitespace-only combination rationale satisfies multi-role combination approval | Same `meaningful_text()` gate applied to combination rationale; additionally a normalized-rationale registry rejects a rationale reused from another combination decision (`E-COMBINATION-RATIONALE-REUSED`). | `engine/validator.py` combination-approval loop | tests 07–10; mutation M2 |
| N-03 | Acceptance evidence is not role-bound; one record satisfies two roles of one candidate | New `acceptance_evidence_check()` binds evidence to exact candidate ref and role via subject `candidate:role`, plus `role`, `appointment_ref`, unique `decision_ref`, `evidence_id` consistency, `CANDIDATE_ACCEPTANCE` type, `VERIFIED` status, timezone-aware timestamp, recording authority and non-revoked state. Errors: `E-EVIDENCE-SUBJECT`, `E-ACCEPTANCE-ROLE`, `E-ACCEPTANCE-APPOINTMENT`, `E-ACCEPTANCE-DECISION`, `E-ACCEPTANCE-DECISION-REUSED`, `E-EVIDENCE-REVOKED`. | `engine/validator.py` `acceptance_evidence_check()`; schema evidence `$defs`; policy v2.1 | tests 11–17, 22; mutation M3 |
| N-15 | Schema type errors non-fatal → `AttributeError` tracebacks | Schema errors are terminal: `validate_state()` returns a controlled result with all dimensions FAIL and the exact `E-SCHEMA` / `E-SCHEMA-REFERENCE` / `E-SCHEMA-INVALID` issues. Reference-resolution and malformed-schema exceptions are caught narrowly and converted to stable messages (no traceback). Unexpected programming errors are not broadly suppressed. | `engine/validator.py` `structural_schema_errors()` and early return in `validate_state()` | tests 18–21; mutation M4 |

## Evidence of closure

| Test ID | Required case | Result |
|---|---|---|
| 01 | Empty approval basis | `E-DECISION-EVIDENCE-EMPTY`, readiness NO |
| 02 | ASCII whitespace-only basis | `E-DECISION-EVIDENCE-EMPTY`, readiness NO |
| 03 | Unicode whitespace-only basis | `E-DECISION-EVIDENCE-EMPTY`, readiness NO |
| 04 | Missing basis | `E-DECISION-EVIDENCE-EMPTY`, readiness NO |
| 05 | Null basis | `E-DECISION-EVIDENCE-EMPTY`, readiness NO |
| 06 | Non-string basis | blocked (`E-SCHEMA` at schema layer; `meaningful_text()` also guards custom-schema paths) |
| 07 | Empty rationale | `E-COMBINATION-RATIONALE`, readiness NO |
| 08 | Whitespace-only rationale | `E-COMBINATION-RATIONALE`, readiness NO |
| 09 | Unicode whitespace-only rationale | `E-COMBINATION-RATIONALE`, readiness NO |
| 10 | Missing rationale | blocked (`E-SCHEMA` at schema layer) |
| 11–17 | Wrong-role / wrong-candidate / other-appointment / reused-subject / unverified / revoked / missing acceptance evidence | each blocked with role-binding or evidence error |
| 18 | Invalid schema structure | `E-SCHEMA-REFERENCE`, all dimensions FAIL, no exception |
| 19 | Unresolvable schema reference | `E-SCHEMA-REFERENCE`, bounded message (<250 chars), no exception |
| 20 | Assignment blocked after schema failure | `E-SCHEMA`, no downstream business issues, all dimensions FAIL |
| 21 | Stable CLI errors | exit 1/2, empty stderr, no traceback for all five invalid inputs |
| 22 | Valid matching evidence | readiness YES, zero errors |

## Mutation proof

`tests/mutation/mutation_harness_v21.py`: baseline 8/8 canary PASS; **4 introduced, 4 detected, 0 survived** — one mutation per remediation area.

## Explicitly not claimed

The 17 MEDIUM and 7 LOW findings from the independent register remain OPEN and tracked. This focused remediation does not claim the whole engine passes its independent audit.
