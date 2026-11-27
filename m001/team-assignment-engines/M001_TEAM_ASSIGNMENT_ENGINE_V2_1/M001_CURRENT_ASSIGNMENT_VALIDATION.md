# M001 V2.1 — Current Assignment Validation

**Mission:** M001-TEAM-006  
**Input:** `state/current_assignment_state.json` (real state; no synthetic records)  
**Command:** `python cli/validate.py --state state/current_assignment_state.json`  
**Exit code:** 1 — Stage B role readiness NO

## Preserved real state

| Role | State |
|---|---|
| RESEARCH_OWNER | `ACCEPTED_IN_CONVERSATION` |
| MODERATOR | `UNASSIGNED` |
| NOTE_TAKER | `UNASSIGNED` |
| DATA_CUSTODIAN | `UNASSIGNED` |
| ANALYST | `UNASSIGNED` |
| CONTINUE_STOP_OWNER | `UNASSIGNED` |

Topology: `PROPOSED` / `FOUR_PERSON`. Governance: M001 OPEN, M002 UNAUTHORIZED,
recruitment UNAUTHORIZED, field validation NOT STARTED. Registry counts: candidates 0,
evidence 0, appointments 0, combination approvals 0.

## Validator result

Six `E-APPOINTMENT-MISSING` errors (all roles, including Research Owner whose conversation
acceptance is not a formal appointment) plus `E-TOPOLOGY-UNAPPROVED`. No synthetic identity,
evidence or appointment was invented. Continue/Stop responsibility was not inferred. No legal
name or candidate identifier was created for any role or the Product Owner.

**Stage B role readiness: NO**  
**Recruitment authorized: NO**  
**Field validation authorized: NO**

The CLI produced no traceback. The same output was obtained from two working directories
(byte-identical stdout/stderr and exit code).

## Authorization separation

A structurally valid synthetic topology (`valid_four_person.json`, topology APPROVED, all roles
FORMALLY_APPOINTED with role-bound evidence) reports Stage B YES and still emits recruitment NO
and field validation NO. Altering governance flags to grant either authorization is rejected at
the schema layer with `E-SCHEMA` under V2.1 terminal handling, and neither authorization is ever
reported as YES. Storage safeguards, consent/withdrawal safeguards, recruitment and field
validation remain outside engine authority.

## Preservation

`python verify_preservation.py` → V2 / re-audit / V1 / prior audit unchanged; repository HEAD
`30db9a1929bbccf73a538f6657cb10f49758688e` unchanged and working tree clean.
