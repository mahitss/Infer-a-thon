# M001 V2.2 — Targeted Independent Verification

**Mission:** M001-TEAM-009  
**Date:** 2026-11-28  
**Workspace:** `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_2_TARGETED_AUDIT`  
**Verdict:** CONDITIONAL PASS — FIVE REMEDIATIONS VERIFIED, RESIDUAL FINDINGS REMAIN

## Independence and preservation

Baselines were hashed before testing (`evidence/BASELINE_START.json`) for V1, V2, V2.1, V2.2, the
V2.1 follow-up and the repository. Exact hashes:

| Artifact | SHA-256 |
|---|---|
| V2.1 validator | `58082F5CC1F0D54809C79A6BDBA34CDBB08750A5EFCC61901F77A6BEF91A1B2F` |
| V2.2 validator | `BAA3634DF3A82F9ECFF158552F263843F97372DADBC16E0D65D6C6D884BC5B5F` |

Every preserved workspace remained hash-identical and HEAD
`30db9a1929bbccf73a538f6657cb10f49758688e` with a clean tree. All V2.2 tests were executed by this
audit or by auditor-authored harnesses importing the real V2.2 validator from its read-only path.

## Five remediation areas

| ID | Canonical reproduction | Independent result |
|---|---|---|
| N-04 | whitespace escalation contact | rejected with `E-ESCALATION-CONTACT`; missing/empty/ASCII/Unicode/invisible/non-string all fail closed; meaningful contact passes; no fabricated value |
| N-08 | identical evidence under a second ID | `E-EVIDENCE-DUPLICATE`; deterministic signature; distinct evidence not rejected; original evidence unchanged |
| N-11 | combination decision before acceptance | timezone-aware `decision_ts < max(accepted)`; 20/20 cases secure including offsets, equality, naive/invalid/missing, reused records; no wall-clock substitution |
| N-12 | whitespace-only candidate ref | `E-CANDIDATE-REF-INVALID`; case/Unicode variants remain distinct; invalid identities cannot satisfy appointments |
| F-007 | U+200B/U+200E/U+2060-only basis | 104 reject cases and 60 meaningful Unicode cases all as expected; predicate consistent across six sites; no text mutation |

Canonical reproductions are **verified fixed**. The V2.1→V2.2 source diff is limited to the five
areas (114 diff lines), with no unrelated policy change.

## New findings discovered during verification

| ID | Severity | Finding | Impact |
|---|---|---|---|
| D-01 | MEDIUM | appointment `candidate_ref` is not bound to the formal role record's ref (`validator.py:515-538`) | an unbacked identity can be recorded as appointed; Stage B YES with zero issues |
| D-02 | MEDIUM | non-base Unicode characters (Mn/Mc/Me, U+FE0F, Co, Cn, Cs) satisfy `meaningful_text()` | decision text with no visible base passes Stage B |
| D-03 | MEDIUM | duplicate-evidence signature bypass via unchecked `role` on non-acceptance evidence | canonical N-08 harm still achievable for PO approval, formal and onboarding evidence |

These are new residuals, not reopenings of the canonical findings. They require further engine
engineering before Stage B reliance. No severity was downgraded.

## Regression evidence

24/24 adversarial; 66/66 V2.2 regression; 22/22 V2.1 focused; 13/13 V2.2 blockers; canary 8/8;
mutation 5 introduced / 5 detected / 0 survived; 50-case corpus 43 secure / 7 individually
classified (2 expectation artifacts, 3 genuine residuals, 2 inconclusive). CLI exits 1/0/1/2/2/2/2
with empty stderr and no traceback; deterministic output. Exact data: `M001_REGRESSION_RESULTS.md`,
`tests/results/regression_results.json`.

## Governance state

Research Owner `ACCEPTED_IN_CONVERSATION` and not formally appointed; five roles UNASSIGNED; topology
`PROPOSED`; Stage B **NOT READY**; recruitment UNAUTHORIZED; field validation NOT STARTED; M001 OPEN;
M002 UNAUTHORIZED. State unchanged and hash-identical after validation. 30/30 governance checks pass.

Crucially: technical remediation (A) does not complete formal staffing completeness (B), operational
storage/privacy safeguards (C), recruitment authorization (D) or field-validation authorization (E).
No PASS from this audit authorizes any of B–E.

## Remaining findings

34 tracked entries: 5 verified closed (the four V2.2 fixes plus S-03), 29 open, 6 requiring
remediation before Stage B. No silent closure or severity downgrade. See
`M001_REMAINING_FINDING_TRIAGE.md` and `M001_TARGETED_DEFECT_REGISTER.json`.

## Final verdict

**CONDITIONAL PASS — FIVE REMEDIATIONS VERIFIED, RESIDUAL FINDINGS REMAIN**

Further engine engineering is genuinely necessary for D-01, D-02 and D-03 before V2.2 can be relied
on for Stage B readiness. This verdict is not Stage B authorization.
