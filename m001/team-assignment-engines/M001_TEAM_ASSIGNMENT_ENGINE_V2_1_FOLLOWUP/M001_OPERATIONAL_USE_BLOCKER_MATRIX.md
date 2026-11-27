# M001 V2.1 — Operational Use Blocker Matrix

**Mission:** M001-TEAM-007  
**Source:** `analysis/lower_severity_triage.json` plus auditor's new F-007

## Explicit answer

- **Block Stage B readiness:** N-04, N-08, N-11, N-12, F-007 (five findings; four MEDIUM carried forward plus one new MEDIUM residual variant of N-01/N-02).
- **Block recruitment authorization:** no finding directly changes the recruitment flag (hard-coded `NO`); however the five Stage-B blockers indirectly prevent any justified progression from staffing readiness to a recruitment decision.
- **Block field validation:** no finding directly changes the field-validation flag (hard-coded `NOT STARTED` / `NO`); the same indirect dependency applies.
- **Affect participant confidentiality:** none of the carried-forward findings directly exposes participant data; N-08 (evidence duplication) and N-13 (identity canonicalization) weaken attribution integrity, not confidentiality.

## Matrix

| Finding | Severity | Class | Component | Stage B | Recruitment | Field validation | Operational decision |
|---|---|---|---|---|---|---|---|
| N-04 whitespace escalation contact | MEDIUM | A | onboarding `escalation.contact` | **BLOCKS** — role reported ready with no substantive contact | indirect | indirect | Fix before any Stage B claim |
| N-08 duplicate evidence records | MEDIUM | A | evidence registry / role binding | **BLOCKS** — one artifact reused across roles can pass | indirect | indirect | Fix before Stage B |
| N-11 combination timestamp ordering | MEDIUM | A | combination approval chronology | **BLOCKS** — approval-before-acceptance can pass | indirect | indirect | Fix before Stage B |
| N-12 whitespace candidate reference | MEDIUM | A | candidate registry | **BLOCKS** — identity gate satisfiable by whitespace | indirect | indirect | Fix before Stage B |
| F-007 invisible Unicode basis/rationale | MEDIUM | A | `meaningful_text()` | **BLOCKS** — U+200B-only decision text passes | indirect | indirect | Fix before Stage B |
| N-07 source-hash correspondence | MEDIUM | E | evidence `content_hash` | contributes; needs authoritative source | indirect | indirect | Investigate: requires source of truth |
| N-09 evidence timestamp vs source | MEDIUM | E | evidence timestamp | contributes; needs temporal authority | indirect | indirect | Investigate |
| N-10 freshness/expiry | MEDIUM | E | decision timestamps | contributes; needs policy | indirect | indirect | Investigate |
| N-13 identity canonicalization | MEDIUM | E | candidate registry | contributes; needs identity authority | indirect | indirect | Investigate |
| N-14 revocation/history | MEDIUM | E | schema/state model | contributes; needs model design | indirect | indirect | Investigate |
| S-02 hash pattern (overlaps N-07) | MEDIUM | E | schema | contributes | indirect | indirect | Investigate with N-07 |
| N-05 duplicate approval roles | MEDIUM | D | `pair_key()` | no — safe fail-closed via exact key mismatch | no | no | Accept with rationale; cosmetic |
| N-06 dimension misreporting | MEDIUM | D | `evidence_check()` | no — readiness still fails via issues | no | no | Accept with rationale; consumer should read issues, not only dimensions |
| S-01 timestamp format absent | MEDIUM | D | schema | no — engine enforces timestamp validity | no | no | Accept; engine-level gate present |
| S-03 unresolvable `$ref` exception | MEDIUM | D | schema handling | no — **verified closed** by N-15 fix | no | no | Accept; verified closed |
| S-04 fallback subset latent gaps | MEDIUM | D | `validate_schema()` | no — full validator active when jsonschema installed | no | no | Document; treat subset as documentation-only |
| N-16 RecursionError on deep JSON | MEDIUM | D | CLI input handling | no — fails closed, but no structured output | no | no | Accept with rationale; monitor |
| N-17 surrogate print traceback | MEDIUM | D | CLI human report | no — `--json-only` safe | no | no | Accept with rationale; recommend `--json-only` |
| N-21 unused policy fields | LOW | D | policy | no | no | no | Accept; clean up later |
| N-18/N-19/N-20/S-05/S-06/S-07 | LOW | D | CLI/schema/policy | no | no | no | Accept with documented rationale |

## Governance conclusion

The four HIGH remediations are independently closed and do not change human authorization state.
However, five MEDIUM findings must be fixed before V2.1's Stage B role-readiness output can be
trusted operationally. No lower-severity finding authorizes recruitment or field validation; both
remain NOT GRANTED and NOT STARTED. The realistic path is: fix the five A-class blockers, resolve
or formally accept the six E-class investigations, then seek a new independent audit before any
operational governance decision.
