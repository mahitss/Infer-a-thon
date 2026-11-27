# M001 V2.2 — Timestamp Ordering Independent Verification (N-11)

**Mission:** M001-TEAM-009  
**Evidence:** `tests/results/timestamp_candidate_results.json`, `reports/TIMESTAMP_CANDIDATE_AGENT_NOTES.md`, independent auditor reproduction

## Algorithm inspected

`engine/validator.py:540-585`. Predicate: `decision_ts < max(accepted)` where `accepted` contains
`parse_timestamp(role.acceptance.candidate_accepted_at)` for each role in `ca.roles` whose role
record binds the same candidate. Violation emits `E-COMBINATION-APPROVAL-TIMESTAMP-ORDER` in the
`product_owner_combination_approval` dimension. Invalid/naive timestamps emit `E-TIMESTAMP-INVALID`.
No wall-clock call (`now`/`utcnow`) exists in the engine.

## Executed cases (20 N-11 cases)

| Case | Result |
|---|---|
| Decision before first-role acceptance | `E-COMBINATION-APPROVAL-TIMESTAMP-ORDER`, readiness NO |
| Decision before last-role acceptance (two roles, different acceptance times) | same error; `max()` used correctly |
| Valid decision after all acceptances | passes |
| Missing decision timestamp (`null`) | `E-TIMESTAMP-INVALID`, no ordering error |
| Missing key | schema-terminal `E-SCHEMA` |
| Timezone-naive decision | `E-TIMESTAMP-INVALID` |
| Equivalent instants with different offsets | `02:00+00:00` vs `03:00+01:00` at equality passes; `>=` boundary deterministic |
| Cross-offset decision actually earlier | rejected (comparison is timezone-aware, not wall-clock string) |
| Equal timestamps | passes |
| Invalid ISO strings (`not-a-timestamp`, out-of-range, empty, date-only) | `E-TIMESTAMP-INVALID`, no exception |
| Contradictory role chronology | `E-TIMESTAMP-ORDER` in `formal_appointment_validity` |
| Reused approval record with old timestamp | ordering error emitted twice, readiness NO |
| Far-future decision | passes — no current-time substitution |
| `Z`-suffixed UTC timestamp | passes |

All 20 cases reproduced the expected secure behaviour; 0 defects in N-11 scope.

## New adjacent defect D-01 (N-12 scope)

While inspecting all `candidate_ref` consumers, the independent stream found that the appointments
loop (`validator.py:515-538`) never asserts that `appointment.candidate_ref` equals the formal role
record's `candidate_ref`. I independently reproduced:

```text
state = valid_four_person.json + registry entry C-NEW
       + appointment (C-NEW, RESEARCH_OWNER)
result: stage_b_role_ready=True, issues=[], all eight dimensions PASS
role ref = C-P1; appointment refs = [C-P1, C-NEW]
```

Impact: an appointment record naming a candidate with no acceptance, PO approval, formal record or
onboarding can be recorded against a role formally held by someone else. This does NOT fail the
N-12 registry predicate itself; the N-12 fix is verified closed. D-01 is a separate MEDIUM defect
adjacent to N-12 that must be tracked and remediated before Stage B reliance on appointment records.
No severity was downgraded and N-12 is not reclassified.
