# Current Assignment Validation — M001 Team Assignment Engine V2

**Date:** 2026-11-27  
**Input:** `state/current_assignment_state.json` (real state — no synthetic candidates)  
**Command:** `python cli/validate.py --state state/current_assignment_state.json`  
**Exit code:** `1` (validation completed; Stage B role readiness NO)  
**Machine-readable evidence:** `reports/current_assignment_validation.json`, `reports/logs/cli_current.txt`

## Preserved real state

| Role | State | Candidate | Formal appointment? |
|---|---|---|---|
| RESEARCH_OWNER | `ACCEPTED_IN_CONVERSATION` | none (no legal name or ID invented) | **NO** |
| MODERATOR | `UNASSIGNED` | none | NO |
| NOTE_TAKER | `UNASSIGNED` | none | NO |
| DATA_CUSTODIAN | `UNASSIGNED` | none | NO |
| ANALYST | `UNASSIGNED` | none | NO |
| CONTINUE_STOP_OWNER | `UNASSIGNED` | none | NO |

The Research Owner record preserves the 2026-11-26 explicit written confirmation in
conversation, marks `formal=false`, and states that a formal signature was NOT PROVIDED
and an official register update is NOT AUTHORIZED. Acceptance in conversation is not
promoted to `FORMALLY_APPOINTED` and does not imply the Continue/Stop Decision Owner
appointment. Topology remains `PROPOSED` (`FOUR_PERSON`). Candidate registry and evidence
registry are empty. There are no appointments and no combination approvals.

## Separate dimension outcomes

| Dimension | Outcome |
|---|---|
| structural_topology_validity | **FAIL** (`E-TOPOLOGY-UNAPPROVED`) |
| role_assignment_completeness | **FAIL** (6 × `E-APPOINTMENT-MISSING`) |
| human_candidate_acceptance | PASS |
| formal_appointment_validity | PASS |
| product_owner_combination_approval | PASS |
| evidence_integrity | PASS |
| role_compatibility | PASS |
| onboarding_readiness | PASS |

**Stage B role readiness: NO**  
**Recruitment authorized: NO**  
**Field validation authorized: NO**  
**Blocking errors: 7 — Warnings: 0**

The six `E-APPOINTMENT-MISSING` errors cover all six roles, including the Research Owner:
`ACCEPTED_IN_CONVERSATION` is deliberately classified as a missing formal appointment.
The seventh error blocks Stage B because the topology is `PROPOSED`. Dimensions that are
PASS do so vacuously (no formal appointment exists to evaluate); none of them grants an
appointment or authorization.

## Authorization confirmation

The CLI output was checked for any positive authorization grant: none exists. The real
state keeps `m001_status=OPEN`, `m002_status=UNAUTHORIZED`, `recruitment=UNAUTHORIZED`,
`field_validation=NOT_STARTED`. A deliberately altered fixture with
`recruitment=AUTHORIZED` is rejected with `E-AUTHORIZATION-STATE` and `E-SCHEMA` and
still reports both authorizations as NO (`reports/logs/cli_recruit.txt`).

## Reproduce

```powershell
python cli/validate.py --state state/current_assignment_state.json --json-out reports/current_assignment_validation.json
# expected exit 1, Stage B role readiness: NO, 7 blocking errors, no traceback
```
