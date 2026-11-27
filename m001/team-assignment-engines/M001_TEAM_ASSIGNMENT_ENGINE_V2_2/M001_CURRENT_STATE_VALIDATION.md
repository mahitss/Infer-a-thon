# M001 V2.2 — Current Assignment Validation

**Mission:** M001-TEAM-008  
**Input:** `state/current_assignment_state.json` (real state; no synthetic content)  
**Command:** `python cli/validate.py --state state/current_assignment_state.json`  
**Exit:** 1 — Stage B role readiness NO

## State preserved exactly

| Role | State |
|---|---|
| RESEARCH_OWNER | `ACCEPTED_IN_CONVERSATION` |
| MODERATOR | `UNASSIGNED` |
| NOTE_TAKER | `UNASSIGNED` |
| DATA_CUSTODIAN | `UNASSIGNED` |
| ANALYST | `UNASSIGNED` |
| CONTINUE_STOP_OWNER | `UNASSIGNED` |

Topology `PROPOSED` / `FOUR_PERSON`. Candidates `{}`, evidence `{}`, appointments `[]`,
combination approvals `[]`. Research Owner `formal.formally_appointed = false`, no candidate
reference, no legal name invented. Continue/Stop responsibility not inferred.

Governance: M001 OPEN, M002 UNAUTHORIZED, recruitment UNAUTHORIZED, field validation NOT STARTED.

## Validation result

Six `E-APPOINTMENT-MISSING` errors (all roles) plus `E-TOPOLOGY-UNAPPROVED`.

**Stage B role readiness: NO**  
**Recruitment authorized: NO**  
**Field validation authorized: NO**

CLI stderr empty, no traceback. Output identical from two working directories. State hash unchanged
before and after validation (no hidden mutation).

## Separation preserved

Role completeness, formal appointment, candidate acceptance, Product Owner approval, combination
approval, evidence integrity, availability, conflict disclosure, confidentiality, onboarding and
Stage B readiness remain separate dimensions. A passing topology or technical validation does not
authorize operational configuration, recruitment or field validation. No lower-severity finding was
auto-closed by this remediation; all unrelated open findings remain tracked.
