# M001-TEAM-005 — Independent V2 Governance Engine Re-Audit

**Date:** 2026-11-27  
**Role:** independent Principal Software Security Engineer / Formal Methods Reviewer / Research Governance Auditor  
**Subject:** `M001_TEAM_ASSIGNMENT_ENGINE_V2`  
**Workspace:** `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT`

## Final verdict

**FAIL — CRITICAL OR HIGH DEFECTS FOUND**

Four independently reproduced HIGH defects remain: whitespace-substantive approval basis,
whitespace-substantive combination rationale, role-unbound acceptance evidence, and a general
schema-error-continues crash class. No CRITICAL defect was found. All 16 original findings
are independently confirmed CLOSED, but that does not make V2 trustworthy as a governance
decision-support control in its present state. No severity was downgraded to obtain this result.

## Independence established

- Source hashes were captured before testing (`evidence/AUDIT_START_BASELINE.json`) for V1 (43
  authored files), V2 (76), the previous audit (465) and the repository HEAD
  `30db9a1929bbccf73a538f6657cb10f49758688e` with a clean working tree.
- V2 `engine/validator.py` SHA-256 `C6EFD2F0CC1AB85DC60A5F4299BE7042A1E76CC5708A611AD03581CCE65E1D66`;
  policy `EB7CCAB5C45A4F14B090E296801393FC2742E1D8159DF97E9C7A5F88068CB5E6`;
  schema `314A7346CEE5FFBBDA799E3B2A1C38708B315EFB535DE5CE94F53CDED80ED7DB`;
  CLI `64D4E179466571A98A206EF53ABB0A6147C8EB790C4A86F4BB03FF6F6F687273`;
  state `E6DDC93C94506BA499878D642CBD29E71E1930409F4FBC9498FAE6A3009D094F`.
- V2's own SHA-256 manifest was independently recomputed: 75 declared files, 0 mismatches.
- No remediation claim was accepted from a passing test or report. Every finding below was
  reproduced by executing auditor-owned harnesses against read-only V2 source, or independently
  re-run by an audit stream.
- Policy-source versions: V1 policy `version 1.0` sourced from the role-assignment decision pack
  and staffing pack; V2 policy `version 2.0` additionally sources the independent audit defect
  register. V2 introduces new interpretations (`formal_appointment_states`,
  `missing_appointment_states`, `NOT_RECOMMENDED`, `review_requirement`,
  `product_owner_combination_review`, `verification_statuses`, topology/combination flags). The
  `NOT_RECOMMENDED` classification is consistent with the mission instruction; hard
  incompatibilities remain unoverridable. No general override mechanism was found.
- Bytecode cache files may have been refreshed by Python imports; all authored source, policy,
  schema, state and report files remain hash-identical to the audit-start baseline.

## Original defect closure

All F-01 through F-16 were independently traced to source and reproduced. Both CRITICAL, all
eight HIGH, all three MEDIUM and all three LOW findings are **CLOSED**. Full detail:
`M001_ORIGINAL_FINDING_CLOSURE_MATRIX.md` and `reports/CLOSURE_AGENT_NOTES.md`.

## Independent adversarial testing

The auditor's own suite ran 50 cases (`tests/independent_adversarial.py`): 35 secure, 15
unexpected. Each ambiguous case was re-constructed in `tests/refined_cases.py` before
classification. Confirmed new findings: N-01 through N-14 (four HIGH/MEDIUM sets described in
`reports/M001_NEW_ADVERSARIAL_TEST_REPORT.md` and `reports/M001_EVIDENCE_INTEGRITY_REPORT.md`).
Hard conflicts, discouraged combinations, exact combination approval, candidate registry,
timestamps, topology blocking and authorization non-inference were independently confirmed secure.

## JSON Schema conformance

`jsonschema` 4.26.0; `Draft202012Validator`; `check_schema` passes; 18-instance parity corpus
shows 0 accept/reject gaps between full and fallback validators on the shipped schema. However,
the schema declares no `format`, `pattern`, `uniqueItems` or conditionals; timestamps and content
hashes are not validated by JSON Schema, and an unresolvable local `$ref` raises an unhandled
exception. See `reports/M001_SCHEMA_CONFORMANCE_REPORT.md`.

## Independent mutation testing

A separate harness and canary produced **30 introduced mutations, 30 detected, 0 survived,
3 excluded with documented reasons**; baseline `CANARY_PASS 44/44`. The first canary run had two
survivors, which were triaged rather than accepted: `M05` (global evidence-verification gate)
was a genuine coverage gap and `M28` (appointment formal-state check) was decision-equivalent
but diagnostic-distinct. Properties A42/A43 were added and both mutants are now detected. V2's
own 16/16 mutation claim is therefore independently reproduced at greater breadth. See
`M001_INDEPENDENT_MUTATION_TEST_REPORT.md`.

## Authorization boundary and current state

`tests/current_state_and_boundary.py`: **36 PASS / 0 FAIL**. The engine emits eight role
dimensions plus Stage B readiness and two always-negative authorization flags. Storage,
consent, recruitment and field validation are outside its authority and are never inferred.
Real state: Research Owner `ACCEPTED_IN_CONVERSATION` (not appointed), other five roles
`UNASSIGNED`, topology `PROPOSED`, zero candidates/evidence/appointments/approvals, Stage B NOT
READY, recruitment and field validation NOT GRANTED, M001 OPEN, M002 UNAUTHORIZED. See
`reports/M001_AUTHORIZATION_BOUNDARY_REAUDIT.md`.

## CLI and parser robustness

Six input-controlled raw traceback cases were independently reproduced: three `AttributeError`
from schema errors continuing into unguarded `.get()` calls (HIGH, N-15), one `RecursionError`
(MEDIUM, N-16), one `UnicodeEncodeError` from a lone surrogate (MEDIUM, N-17). Duplicate keys at
all depths, malformed bytes, unexpected properties, wrong primitive types, a 21 MB input and
determinism all behaved correctly. See `reports/CLI_AGENT_NOTES.md`.

## Findings summary

`M001_FINAL_DEFECT_REGISTER.json`: 28 new findings — 4 HIGH, 17 MEDIUM, 7 LOW, 0 CRITICAL.
Earlier V2 reports described the implementation as ready; this independent audit does not accept
that conclusion because four HIGH defects remain open.

## Recommendations

See `M001_REAUDIT_RECOMMENDATIONS.md`. The required next step is source-level remediation of the
HIGH findings and a fresh independent re-audit. This audit changed no governance status, register,
ADR, candidate record, ACL, storage setting, or participant data, and contacted no one.
