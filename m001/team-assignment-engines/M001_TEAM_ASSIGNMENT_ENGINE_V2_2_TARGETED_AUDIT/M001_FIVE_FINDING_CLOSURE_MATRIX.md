# M001 V2.2 — Five-Finding Independent Closure Matrix

**Mission:** M001-TEAM-009  
**Canonical sources:** V2 re-audit register (N-04, N-08, N-11, N-12), V2.1 follow-up register (F-007)  
**V2.2 validator SHA-256:** `BAA3634DF3A82F9ECFF158552F263843F97372DADBC16E0D65D6C6D884BC5B5F`  
**V2.1 validator SHA-256:** `58082F5CC1F0D54809C79A6BDBA34CDBB08750A5EFCC61901F77A6BEF91A1B2F`

## Finding-to-source-to-code-to-test traceability

| ID | Canonical description | Vulnerable V2.1 source | V2.2 correction | Dedicated test | Independent verdict |
|---|---|---|---|---|---|
| N-04 | Whitespace-only escalation contact accepted (`contact='   '` → ready YES) | `validator.py:475-476` bare truthiness | `if not meaningful_text(contact): fail('onboarding_readiness','E-ESCALATION-CONTACT', ...)` | `test_08_escalation_contact` plus auditor cases for empty/ASCII/Unicode/invisible/non-string | **VERIFIED CLOSED** |
| N-08 | Duplicate evidence records under different IDs accepted | evidence registry loop (V2.1 `:423-433`) had no semantic duplicate check | deterministic 9-field signature with `E-EVIDENCE-DUPLICATE` | `test_09_duplicate_evidence` plus auditor duplicate corpus | **VERIFIED CLOSED** |
| N-11 | Combination decision timestamp not ordered against candidate acceptance | V2.1 `:567-568` checked only timestamp validity | `decision_ts < max(accepted)` → `E-COMBINATION-APPROVAL-TIMESTAMP-ORDER` | `test_10`, `test_11` plus auditor boundary corpus | **VERIFIED CLOSED** |
| N-12 | Whitespace-only candidate reference accepted | V2.1 `:344-346` `not ref` only | `E-CANDIDATE-REF-INVALID` for non-substantive/padded refs | `test_12` plus auditor identity corpus | **VERIFIED CLOSED** |
| F-007 | Invisible Unicode format characters satisfy `meaningful_text()` | V2.1 predicate used `str.strip()` | Unicode-category predicate (`Cc/Cf/Zs/Zl/Zp` non-content), applied to basis, rationale, contact and refs | `test_01`–`test_07` plus extended Unicode corpus | **VERIFIED CLOSED** |

## Basis and evidence

Expected secure behaviour was taken from the authoritative `M001_RESEARCH_ROLE_CHARTER.md`
(escalation duties, explicit PO documentation, human accountability) and
`M001_MINIMUM_TEAM_STAFFING_MODELS.md` (minimum team models, explicit appointment, evidence
separation), plus the canonical finding descriptions. No requirement was invented.

Full independent case data: `tests/results/unicode_duplicate_results.json`,
`tests/results/timestamp_candidate_results.json`, `tests/results/regression_results.json`,
`tests/results/governance_state.json`.

## Scope note

These five closures are technical validator fixes. They do not complete formal staffing, do not
configure storage/privacy safeguards, and do not authorize recruitment or field validation.
