# M001 V2.1 — Focused Independent Security Follow-Up

**Mission:** M001-TEAM-007  
**Date:** 2026-11-27  
**Workspace:** `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1_FOLLOWUP`  
**Verdict:** CONDITIONAL PASS — HIGH FINDINGS CLOSED, RESIDUAL BLOCKERS REMAIN

## Independence

All prior workspaces were hashed before testing (`evidence/BASELINE_START.json`) and verified
unchanged after: V1 43 authored files, V2 76, prior audit 83, V2.1 108; repository HEAD
`30db9a1929bbccf73a538f6657cb10f49758688e` with a clean tree. Exact source hashes:

| Artifact | SHA-256 |
|---|---|
| V2 `engine/validator.py` | `C6EFD2F0CC1AB85DC60A5F4299BE7042A1E76CC5708A611AD03581CCE65E1D66` |
| V2.1 `engine/validator.py` | `58082F5CC1F0D54809C79A6BDBA34CDBB08750A5EFCC61901F77A6BEF91A1B2F` |

V2.1's own tests and reports were not accepted as proof. Auditor-authored tests imported each
validator from its preserved path with `importlib.util.spec_from_file_location` and built states
by deep-copying fixtures in memory. Scripts that write results were run from disposable mirrors in
this follow-up workspace.

## Four HIGH findings — independently verified closed

| ID | Auditor evidence | Result |
|---|---|---|
| N-01 | 7 atomic cases plus V2/V2.1 comparison | V2 accepted whitespace basis (ready=True); V2.1 emits `E-DECISION-EVIDENCE-EMPTY`. Empty, ASCII/Unicode whitespace, null and non-string rejected; meaningful Unicode still passes; no substituted text. |
| N-02 | 7 atomic cases plus comparison | V2 accepted whitespace and verbatim rationale; V2.1 emits `E-COMBINATION-RATIONALE` / `E-COMBINATION-RATIONALE-REUSED`. Exact role set still enforced. |
| N-03 | 13 atomic cases plus comparison | V2 accepted one acceptance record for two roles; V2.1 emits role/appointment/decision/subject/type/status/authority/timestamp/revocation/key-id errors; valid role-bound evidence passes. |
| N-15 | 6 schema cases plus comparison and suppression probe | V2 raised `AttributeError` and `_WrappedReferencingError`; V2.1 returns controlled `E-SCHEMA`/`E-SCHEMA-REFERENCE` with all dimensions FAIL. An injected `RuntimeError` propagated, proving no broad suppression. |

Details: `M001_HIGH_FINDINGS_INDEPENDENT_CLOSURE_MATRIX.md`,
`M001_REMEDIATION_ATTACK_REPRODUCTION.md`.

## Regression evidence (executed)

- 24 original adversarial checks: 24/24 OK
- V2.1 regression suite: 53/53 OK (22 remediation-focused cases included)
- 50-case independent corpus: 38 secure / 12 carried-forward MEDIUM-LOW residuals
- Auditor's own 27 cases + 6 schema-failure cases: all as expected
- Canary 8/8; mutation harness 4 introduced / 4 detected / 0 survived
- CLI exit codes 1/0/1/2/2/2/2/2 with empty stderr and no traceback; deterministic output
- State and authorization boundary: 38/38 PASS

Exact commands, stdout/stderr and exit codes: `tests/results/independent_regression_results.json`,
`reports/REGRESSION_AGENT_NOTES.md`, `M001_V2_1_REGRESSION_RESULTS.md`.

## New findings and residuals

- **F-007 (MEDIUM, class A):** `meaningful_text()` relies on `str.strip()`, so basis or rationale
  composed only of invisible Unicode format characters (U+200B, U+200E, U+2060) still yields
  Stage B YES. Independently reproduced. Residual variant of the N-01/N-02 control intent.
- **F-008 (LOW, class D):** invalid schema structure is labelled `E-SCHEMA-REFERENCE` rather than
  `E-SCHEMA-INVALID`; controlled and fail-closed.
- **F-009 (LOW, class E):** rationale-reuse guard rejects identical legitimate boilerplate across
  unrelated decisions; a deliberate strictness change needing a downstream compatibility decision.
- 24 carried-forward findings: 4 class A, 0 B, 0 C, 14 D, 6 E. Only S-03 was independently
  verified closed (incidentally by N-15). No severity was downgraded.

Explicit blocker answer: five findings (N-04, N-08, N-11, N-12, F-007) block trusting Stage B
readiness. None directly changes recruitment or field-validation authorization — both flags are
hard-coded NO — but they indirectly prevent any justified operational progression. See
`M001_LOWER_SEVERITY_RISK_TRIAGE.md` and `M001_OPERATIONAL_USE_BLOCKER_MATRIX.md`.

## Governance state

Research Owner remains `ACCEPTED_IN_CONVERSATION` and not formally appointed; five roles
UNASSIGNED; topology PROPOSED; no synthetic identity, evidence, appointment or approval in real
state; Stage B NOT READY; recruitment UNAUTHORIZED; field validation NOT STARTED; M001 OPEN;
M002 UNAUTHORIZED. State hash unchanged before/after validation.

## Final verdict

**CONDITIONAL PASS — HIGH FINDINGS CLOSED, RESIDUAL BLOCKERS REMAIN**
