# M001 Mutation Test Report

**Governance:** M001 OPEN; M002 UNAUTHORIZED; recruitment UNAUTHORIZED; field validation NOT STARTED; Research Owner ACCEPTED IN CONVERSATION; other five roles UNASSIGNED. Independent audit only: original implementation untouched, no repository/register/ADR change, no appointment, contact, storage configuration or implementation authorization.

Mutation harness: `mutation_harness.py`; canary: `mutation_canary.py`; results: `mutation_results.json`.

Baseline canary against original engine: **exit 0**, all 10 checks pass.

| Mutation | Detection | Canary exit |
|---|---|---|
| M01_remove_moderator_analyst | DETECTED | 1 |
| M02_remove_moderator_custodian | DETECTED | 1 |
| M03_ignore_evidence_separation | DETECTED | 1 |
| M04_ignore_explicit_cs | DETECTED | 1 |
| M05_promote_conversation_to_formal | DETECTED | 1 |
| M06_ignore_po_approval | DETECTED | 1 |
| M07_ignore_candidate_acceptance | DETECTED | 1 |
| M08_ignore_onboarding | DETECTED | 1 |
| M09_allow_discouraged_without_review | DETECTED | 1 |
| M10_infer_appointments_from_topology | DETECTED | 1 |

Detection rate: **10/10 (100%)**; surviving mutations: **none**.

Limitation: canaries verify the behavior the engine currently claims. They do not prove the governance defects F-01–F-16 are corrected. In particular, the original already treats discouraged combinations as warnings, so mutation M09 detects removal of that warning but not the governance defect.

