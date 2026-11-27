# M001 V2.2 — Finding Remediation Matrix

**Mission:** M001-TEAM-008  
**Canonical IDs:** N-04, N-08, N-11, N-12 (V2 re-audit register), F-007 (V2.1 follow-up register).

| ID | Severity (unchanged) | Reproduction before fix | Minimal correction | Regression test | Independent result |
|---|---|---|---|---|---|
| N-04 | MEDIUM | `escalation.contact='   '` → Stage B YES | `meaningful_text()` gate on contact | `test_08_escalation_contact` | `E-ESCALATION-CONTACT`, readiness NO |
| N-08 | MEDIUM | identical evidence under a second ID → Stage B YES | semantic-duplicate signature check in evidence registry | `test_09_duplicate_evidence` | `E-EVIDENCE-DUPLICATE`, readiness NO |
| N-11 | MEDIUM | combination decision before acceptance → Stage B YES | order decision timestamp against max acceptance timestamp of held roles | `test_10_combination_before_acceptance`, `test_11_valid_ordering_still_passes` | `E-COMBINATION-APPROVAL-TIMESTAMP-ORDER`, readiness NO; valid ordering still YES |
| N-12 | MEDIUM | fully consistent whitespace-only candidate ref → Stage B YES | `E-CANDIDATE-REF-INVALID` for empty/padded refs | `test_12_whitespace_candidate_reference` | blocked |
| F-007 | MEDIUM | U+200B/U+200E/U+2060-only basis → Stage B YES | Unicode-category meaningful-content predicate | `test_01`–`test_07` | blocked; valid Unicode including ZWJ emoji preserved |

## No unrelated policy change

- Valid four/five/six-person fixtures still pass (53 original V2.1 tests all pass).
- Hard incompatibilities and NOT_RECOMMENDED combinations unchanged.
- Exact combination approval, role-bound acceptance evidence and terminal schema handling remain intact.
- No change to governance flags, state, registers, candidate identities or authorization logic.
- The four HIGH findings from M001-TEAM-005 remain closed; V2.1's 22 remediation tests still pass.

## Corpus improvement

The 50-case auditor-authored corpus moved from **38 secure / 12 defect** on V2.1 to
**43 secure / 7 defect** on V2.2. The four newly secure cases are exactly N-04, N-08, N-11 and
N-12. One stale corpus expectation (COMB-06) was widened to accept the new stable
`E-COMBINATION-APPROVAL-TIMESTAMP-ORDER` code; this is a test-label correction, not a policy change.

## Open findings retained

The seven remaining corpus defects and all unrelated MEDIUM/LOW findings from prior registers
remain OPEN at original severity: duplicate approval roles, approval reuse for unrelated
combinations, source-hash correspondence, evidence timestamp vs source, stale acceptance,
Unicode-equivalent identifiers and split identities. No severity was downgraded and no unrelated
finding was auto-closed.

## Mutation proof

Five introduced mutations (one per remediation area): **5 detected, 0 survived**; canary 8/8.
