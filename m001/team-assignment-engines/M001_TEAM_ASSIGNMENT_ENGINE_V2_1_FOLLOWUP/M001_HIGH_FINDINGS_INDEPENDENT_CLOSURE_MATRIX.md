# M001 V2.1 — Independent High-Finding Closure Matrix

**Mission:** M001-TEAM-007  
**Date:** 2026-11-27  
**Canonical source:** `V2_REAUDIT/M001_FINAL_DEFECT_REGISTER.json` (unchanged)  
**Evidence:** `tests/results/independent_followup_results.json`, `tests/results/state_boundary_results.json`

## Independence

V2.1's own tests and reports were not accepted as proof. The auditor imported V2.1's validator
from its read-only path via `importlib.util.spec_from_file_location`, built states by deep-copying
V2.1 fixtures, and executed 27 atomically scored cases plus six schema-failure cases. Exact
validator hash: `58082F5CC1F0D54809C79A6BDBA34CDBB08750A5EFCC61901F77A6BEF91A1B2F`.

## Closure decisions

| ID | Original severity | Affected source | Auditor's independent reproduction | Result | Decision |
|---|---|---|---|---|---|
| N-01 | HIGH | `meaningful_text()`; approval basis check | AU-01 empty, AU-02 ASCII whitespace, AU-03 Unicode whitespace, AU-04 null, AU-05 integer → all emit `E-DECISION-EVIDENCE-EMPTY`; AU-06 normal basis and AU-07 meaningful Unicode content (`Dokumentierte PO-Entscheidung 日本 ✓`) still pass; no substituted text in issues | 7/7 as expected | **INDEPENDENTLY CLOSED** |
| N-02 | HIGH | `meaningful_text()` on rationale; `used_rationales` | AU-08 empty, AU-09 ASCII whitespace, AU-10 Unicode whitespace, AU-11 null, AU-12 list → all blocked; AU-13 altered role set → `E-COMBINATION-APPROVAL-MISSING` (exact combination still enforced); AU-14 copied rationale to an unrelated decision → `E-COMBINATION-RATIONALE-REUSED` | 7/7 as expected | **INDEPENDENTLY CLOSED** |
| N-03 | HIGH | `acceptance_evidence_check()` + evidence registry | AU-15 wrong role, AU-16 wrong candidate, AU-17 other appointment, AU-18 reused decision, AU-19 missing, AU-20 unverified, AU-21 revoked, AU-22 wrong role field, AU-23 whitespace authority, AU-24 naive timestamp, AU-25 wrong type, AU-26 key/id mismatch → all blocked; AU-27 valid role-bound evidence passes | 13/13 as expected | **INDEPENDENTLY CLOSED** |
| N-15 | HIGH | `structural_schema_errors()` + terminal return | schema_invalid_assignment, invalid_schema, unresolvable_ref_schema, missing required governance, invalid nested roles, invalid evidence structure → all return controlled `E-SCHEMA`/`E-SCHEMA-REFERENCE`, all dimensions FAIL, readiness NO; a deliberately injected `RuntimeError` propagated (no broad suppression) | 6/6 plus suppression probe | **INDEPENDENTLY CLOSED** |

## Totals

- 27 atomic cases: **27 PASS / 0 FAIL**
- 6 schema/assignment failure cases: all controlled, no traceback
- Unexpected programming error propagation: confirmed
- State and authorization boundary: **38 PASS / 0 FAIL**

## Scope limits

This matrix covers only the four HIGH findings. Lower-severity findings remain tracked in
`M001_LOWER_SEVERITY_RISK_TRIAGE.md` and `M001_FOLLOWUP_DEFECT_REGISTER.json`; they are not
closed by this matrix. No test in this matrix was inherited from V2.1.
