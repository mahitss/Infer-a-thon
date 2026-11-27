# Defect Remediation Matrix — M001-TEAM-004

**Source specification:** `M001_TEAM_ASSIGNMENT_ENGINE_AUDIT/M001_DEFECT_REGISTER.json` (16 findings; 2 CRITICAL, 8 HIGH, 3 MEDIUM, 3 LOW).  
**Severity policy:** no severity was downgraded. Status is REMEDIATED only where executed evidence exists.  
**Execution evidence index:** `reports/logs/adversarial.txt` (24/24 OK), `reports/logs/regression.txt` (31/31 OK), `reports/logs/canary.txt` (18/18 PASS), `reports/logs/mutation.txt` (16/16 detected), `reports/logs/original_v1_mutation_canary.txt` (10/10 PASS).

## CRITICAL

| ID | Severity | V1 verified defect | V2 control | Reproduction test | Execution evidence | Status |
|---|---|---|---|---|---|---|
| F-05 | CRITICAL | Compatible multi-role assignment with no PO combination approval passed. | Every candidate holding >1 role requires an exact `combination_approvals` record: matching candidate ref, exact sorted role set, `outcome=APPROVED`, `product_owner_approved=true`, non-empty rationale, `COMBINATION_REVIEW` evidence with matching subject, timezone-aware `decision_timestamp`. No implicit approval from topology, compatibility, acceptance or prior assignment. | `test_01_multi_role_without_po_combination_approval`, `test_02_approval_for_different_combination`, `test_adv23_different_combination_approval`; fixtures `multi_role_no_approval.json`, `approval_different_combination.json`; mutations M04, M09. | `E-COMBINATION-APPROVAL-MISSING` observed in adversarial/regression logs; canary C4 PASS; M04 DETECTED. | **REMEDIATED** |
| F-08 | CRITICAL | `PROPOSED` role treated as appointed; unsupported states accepted as complete. | State machine allows only `FORMALLY_APPOINTED` to satisfy appointment readiness. `UNASSIGNED`, `PROPOSED`, `ACCEPTED_IN_CONVERSATION`, `CANDIDATE_ACCEPTED`, `REJECTED`, `DEFERRED` all emit `E-APPOINTMENT-MISSING`. Formal state additionally requires coherent acceptance, PO approval, decision basis, formal record, structured evidence and ordered timezone-aware timestamps; `formal=false` while `FORMALLY_APPOINTED` fails closed. No automatic promotion. | `test_03_proposed_treated_as_appointed`, `test_04_accepted_conversation_not_formal`, `test_adv09`, `test_adv10`, `test_adv11`, `test_09_formally_appointed_with_missing_formal_approval`, `test_15_rejected_candidate_not_active`; mutation M05. | Current-state CLI: 6 × `E-APPOINTMENT-MISSING`, exit 1; canary C5/C6 PASS; M05 DETECTED. | **REMEDIATED** |

## HIGH

| ID | Severity | V1 verified defect | V2 control | Reproduction test | Execution evidence | Status |
|---|---|---|---|---|---|---|
| F-01 | HIGH | Discouraged Research Owner + Moderator passed with warning only. | Preserved `NOT_RECOMMENDED` classification; blocks with `E-DISCOURAGED-RO-MODERATOR` until an exact, PO-approved combination review with structured evidence is recorded. Hard incompatibilities remain unoverridable. | `test_adv03`, `test_13_discouraged_without_po_review`, `test_discouraged_with_exact_approval_passes`; mutation M09. | Canary C2 PASS; M09 DETECTED; exact-approval regression passes without weakening the default block. | **REMEDIATED** |
| F-02 | HIGH | Discouraged Data Custodian + Analyst passed with warning only. | Same `NOT_RECOMMENDED` blocking rule and exact PO review requirement; `E-DISCOURAGED-CUSTODIAN-ANALYST`. | `test_adv04`; mutation M09. | Adversarial log OK; canary C2 PASS. | **REMEDIATED** |
| F-03 | HIGH | Boolean evidence flag accepted without evidence reference. | Boolean flags are never sufficient. `evidence_check()` requires a structured evidence record with verified status, source, authority, timezone-aware timestamp, valid hash and matching subject; empty/unknown/wrong-type/broken references emit `E-EVIDENCE-MISSING`/`E-EVIDENCE-UNKNOWN`/`E-EVIDENCE-TYPE`/`E-EVIDENCE-SUBJECT`. | `test_05_boolean_evidence_without_reference`, `test_adv05`; mutation M11. | Canary C10 PASS; M11 DETECTED. | **REMEDIATED** |
| F-04 | HIGH | Explicit Continue/Stop flag accepted without evidence. | Research Owner + Continue/Stop Owner requires both an exact combination approval and the explicit additional appointment in formal state; `E-COND-EXPLICIT-CS` otherwise. Featured in the 18-check canary. | `test_adv04`-adjacent conditional logic; canary C4 includes `E-COND-EXPLICIT-CS`; canary C3 covers evidence separation. | Canary C4 PASS with `E-COND-EXPLICIT-CS` observed; M04 DETECTED. | **REMEDIATED** |
| F-06 | HIGH | Duplicate candidate identifier across roles accepted. | Candidate registry requires stable unique refs; key/reference mismatch and duplicate refs emit `E-CANDIDATE-DUPLICATE`. One human with multiple roles is one registry entry referenced by multiple appointments, which triggers the exact combination approval rule. | `test_07_duplicate_candidate_identities`, `test_adv07`; mutation M14 (both duplicate guards disabled). | Canary C14 PASS; M14 DETECTED. | **REMEDIATED** |
| F-07 | HIGH | Unknown human reference accepted. | Every appointment and formal role must reference a known, active registry candidate; otherwise `E-CANDIDATE-UNKNOWN` / `E-CANDIDATE-INACTIVE`. No Product Owner identity was invented. | `test_08_unknown_candidate_identity`, `test_adv08`; mutation M10. | Canary C9 PASS; M10 DETECTED. | **REMEDIATED** |
| F-09 | HIGH | `FORMALLY_APPOINTED` with `approval.formal=false` accepted. | `E-FORMAL-APPROVAL-MISMATCH` when formal state contradicts formal approval; also requires `approval.product_owner_approved=true`, `formal.formally_appointed=true`, non-empty basis and formal evidence. | `test_09_formally_appointed_with_missing_formal_approval`, `test_adv11`; mutation M06. | Canary C6/C18 PASS; M06 DETECTED. | **REMEDIATED** |
| F-10 | HIGH | Empty Product Owner decision basis accepted. | `E-DECISION-EVIDENCE-EMPTY` for empty basis; PO approval must be explicit and supported by a `PRODUCT_OWNER_APPROVAL` evidence record. | `test_10_empty_approval_basis`, `test_adv12`; mutation M06. | Canary C13 PASS; M06 DETECTED. | **REMEDIATED** |

## MEDIUM

| ID | Severity | V1 verified defect | V2 control | Reproduction test | Execution evidence | Status |
|---|---|---|---|---|---|---|
| F-11 | MEDIUM | No structured decision timestamps; ordering unverifiable. | Schema and engine require timezone-aware ISO-8601 timestamps for acceptance, PO approval, formal appointment, evidence records and combination decisions; naive/missing/invalid formats and impossible ordering `candidate_accepted <= po_approved <= formal_appointed` fail closed. Machine current time is never substituted. | `test_12_missing_timestamps`, `test_adv14`, `test_naive_timestamp_rejected`; fixture `naive_timestamp.json`; mutation M12. | Canary C11 PASS; M12 DETECTED; regression OK. | **REMEDIATED** |
| F-12 | MEDIUM | Unapproved topology did not block Stage B readiness. | `E-TOPOLOGY-UNAPPROVED`; Stage B readiness requires approved topology plus all eight dimensions PASS and zero issues. Topology and appointment outcomes are reported separately. | `test_14_unapproved_topology_not_stage_b_ready`, `test_adv16`; mutation M13. | Canary C12 PASS; M13 DETECTED; current-state CLI emits the error. | **REMEDIATED** |
| F-13 | MEDIUM | Duplicate JSON keys silently resolved last-wins. | `load_json_strict()` uses `object_pairs_hook` and raises `DuplicateKeyError` with `E-DUPLICATE-JSON-KEY`; CLI maps it to exit 2 with no traceback. | `test_13_duplicate_json_keys`, `test_adv15`, `test_safe_input_errors_no_traceback`; fixture `duplicate_json_key.json`. | `reports/logs/cli_dup_key.txt`: exit 2, `E-DUPLICATE-JSON-KEY`, empty stderr. | **REMEDIATED** |

## LOW

| ID | Severity | V1 verified defect | V2 control | Reproduction test | Execution evidence | Status |
|---|---|---|---|---|---|---|
| F-14 | LOW | Malformed JSON produced unhandled traceback. | `load_json_strict()` catches `JSONDecodeError` and emits `E-JSON-INVALID`; CLI catches and formats it without traceback. | `test_17_malformed_json`, `test_adv19`, `test_safe_input_errors_no_traceback`. | `reports/logs/cli_malformed.txt`: exit 2, no stderr. | **REMEDIATED** |
| F-15 | LOW | Missing input file produced unhandled traceback. | `load_json_strict()` catches `OSError` and emits `E-FILE-NOT-FOUND`; CLI maps to exit 2. | `test_19_missing_state_file`, `test_adv21`. | `reports/logs/cli_no_file.txt`: exit 2, no stderr. | **REMEDIATED** |
| F-16 | LOW | Invalid UTF-8 produced unhandled traceback. | `load_json_strict()` decodes with explicit UTF-8 and catches `UnicodeDecodeError` → `E-ENCODING-INVALID`; CLI maps to exit 2. | `test_18_invalid_utf8`, `test_adv20`. | `reports/logs/cli_bad_utf8.txt`: exit 2, no stderr. | **REMEDIATED** |

## Newly introduced security boundaries (mutation coverage)

| Mutation | Boundary weakened | Detection |
|---|---|---|
| M01 / M02 / M16 | Hard incompatibility `MODERATOR+ANALYST`, `MODERATOR+DATA_CUSTODIAN`, and the hard-check guard | canary C1 / C17 — all DETECTED |
| M03 | Conditional evidence separation | canary C3 — DETECTED |
| M04 | Exact multi-role combination approval | canary C4 — DETECTED |
| M05 | `ACCEPTED_IN_CONVERSATION` promoted to formal | canary C5 — DETECTED |
| M06 | Explicit Product Owner approval | canary C18 — DETECTED |
| M07 | Independent candidate acceptance | canary C7 — DETECTED |
| M08 | Onboarding readiness | canary C8 — DETECTED |
| M09 | Discouraged-combination PO review | canary C2 — DETECTED |
| M10 | Unknown candidate rejection | canary C9 — DETECTED |
| M11 | Structured evidence integrity | canary C10 — DETECTED |
| M12 | Timezone-aware timestamp integrity | canary C11 — DETECTED |
| M13 | Topology approval gate | canary C12 — DETECTED |
| M14 | Candidate identity uniqueness | canary C14 — DETECTED |
| M15 | Recruitment/field-validation authorization boundary | canary C15 — DETECTED |

## Open findings

None. All 16 registered findings are REMEDIATED with executed evidence. The independent
audit verdict is not downgraded in V1; V2 is a separate implementation awaiting
independent re-audit.
