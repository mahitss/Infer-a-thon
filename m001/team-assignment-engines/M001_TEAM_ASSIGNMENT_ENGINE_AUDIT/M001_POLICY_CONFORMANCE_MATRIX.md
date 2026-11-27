# M001 Policy Conformance Matrix

**Governance:** M001 OPEN; M002 UNAUTHORIZED; recruitment UNAUTHORIZED; field validation NOT STARTED; Research Owner ACCEPTED IN CONVERSATION; other five roles UNASSIGNED. Independent audit only: original implementation untouched, no repository/register/ADR change, no appointment, contact, storage configuration or implementation authorization.

| Policy requirement | Source | Implemented? | Independent result |
|---|---|---|---|
| Six role identifiers | role charter | Yes | PASS |
| Seven appointment states | PO decision sheet v2 | Yes, structurally | PARTIAL: PROPOSED treated as appointed (F-08) |
| Hard: Moderator+Analyst | role charter line 21 | Yes | PASS ADV-01 |
| Hard: Moderator+Custodian | role charter line 23 | Yes | PASS ADV-02 |
| Discouraged: RO+Moderator | role charter line 20 | Warning only | FAIL ADV-03 |
| Discouraged: Custodian+Analyst | role charter line 22 | Warning only | FAIL ADV-04 |
| Conditional: Moderator+Note-taker | staffing models line 17 | Boolean flag only | FAIL ADV-05 |
| Conditional: RO+Continue/Stop | charter line 19 | Boolean + state check, no evidence ref | FAIL ADV-06 |
| All multi-role assignments require explicit PO documentation | charter line 25 | Not implemented | FAIL ADV-07 CRITICAL |
| Missing appointments | dependency map v2 B2 | Yes | PASS ADV-17 |
| RO conversation not formal appointment | confirmation changelog | Yes | PASS ADV-18 |
| Candidate acceptance/PO approval/onboarding | decision sheet v2 | Partial | PASS for omitted fields; FAIL for weak evidence/state contradictions |
| Timestamps | governance traceability | Not implemented | FAIL ADV-15 |
| Topology approval | dependency map v2 | Warning only | FAIL ADV-16 |
| Recruitment/field validation authorization separated | governance state | Schema enum only; no positive authorization possible | PASS |
| Full JSON Schema compliance | schema doc | Subset only | Documented limitation |

