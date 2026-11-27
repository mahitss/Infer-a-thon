# M001 Independent V2 Adversarial Test Report

**Mission:** M001-TEAM-005  
**Date:** 2026-11-27  
**Method:** Direct import of V2 `engine/validator.py` from its read-only path; all states are in-memory deep copies of V2's synthetic `valid_four_person.json`. No V2 file was written.

## Reproduction commands

```powershell
cd C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT
python tests/independent_adversarial.py
python tests/refined_cases.py
python tests/current_state_and_boundary.py
```

Output artifacts: `tests/results/independent_adversarial_results.json`, `tests/results/refined_case_results.json`, `tests/results/current_state_boundary_results.json`.

## First pass — 50 cases

`TOTAL 50 SECURE 35 DEFECT 15`. Fifteen cases exhibited unexpected acceptance. I re-constructed each ambiguous case with a corrected state before classifying it; the corrections are in `refined_case_results.json`. Cases whose first construction was a no-op orused the wrong expectation are not counted as findings.

## Confirmed independently reproduced defects

| ID | Case | Observed result | Source line(s) | Severity |
|---|---|---|---|---|
| N-01 | Approval basis is whitespace only (`ST-09`) | `ready=True`, `codes=[]` | `validator.py:351` (`if not appr.get('basis')`) | **HIGH** |
| N-02 | Combination rationale is whitespace only (`COMB-11`) | `ready=True`, `codes=[]` | `validator.py:414` (`if not ca.get('rationale')`) | **HIGH** |
| N-03 | One acceptance-evidence record satisfies two roles of the same candidate (`EVID-02`) | `ready=True`, `codes=[]` | `validator.py:341-345` (subject is candidate ref only) | **HIGH** |
| N-04 | Escalation contact is whitespace only (`ST-10`) | `ready=True`, `codes=[]` | `validator.py:374` | MEDIUM |
| N-05 | Duplicate roles inside a combination approval (`COMB-03`) | `ready=True`, `codes=[]` | `validator.py:213` (`sorted(set(roles))`), `:408` | MEDIUM |
| N-06 | `evidence_integrity=PASS` while `E-EVIDENCE-UNKNOWN` or `E-EVIDENCE-SUBJECT` is present (`DIM-02`, `DIM-03`) | dimension PASS, blocking error present | `validator.py:217-246` appends issues without updating `dims`; contrast `:301-310` | MEDIUM |
| N-07 | Content hash changed to a different valid 64-hex value (`EVID-03`) | `ready=True`, `codes=[]` | `validator.py:242-245` (format-only check) | MEDIUM |
| N-08 | Identical evidence record duplicated under a second ID (`EVID-04`) | `ready=True`, `codes=[]` | `validator.py:300-310` (no duplicate-content check) | MEDIUM |
| N-09 | Evidence timestamp set to 1999 while appointment is 2026 (`EVID-06`) | `ready=True`, `codes=[]` | `validator.py:236-238` (no cross-check to source/decision) | MEDIUM |
| N-10 | Stale acceptance or approval timestamp with valid ordering (`ST-02`, `COMB-06`) | `ready=True`, `codes=[]` | `validator.py:355-363`, `:418` (no freshness model) | MEDIUM |
| N-11 | Combination decision timestamp predates candidate acceptance (`ST-03`) | `ready=True`, `codes=[]` | `validator.py:418` (no ordering against role timestamps) | MEDIUM |
| N-12 | Whitespace-only candidate reference used consistently (`ID-03`) | `ready=True`, `codes=[]` | `validator.py:256` (`not ref` only checks empty string) | MEDIUM |
| N-13 | Six distinct candidate identities, zero combination approvals (`ID-07`) | `ready=True`, `codes=[]` | `validator.py:249-263` (no canonical identity/alias linkage) | MEDIUM limitation |
| N-14 | Revocation/history properties (`COMB-07`, `EVID-05`, `ST-06`, `ST-07`) | blocked by `E-SCHEMA`, not by revocation semantics | schema `additionalProperties: false`; no revocation model | MEDIUM limitation |

## Secure behaviours independently confirmed

- Hard incompatibilities blocked even with a complete approval record (`POL-01`, `POL-02`).
- Approval with extra roles, another candidate's approval, or another decision's evidence blocked (`COMB-01`, `COMB-04`, `COMB-05`); approval reused for an unrelated candidate is blocked by exact key matching (`COMB-12` refined).
- Outcome contradiction, unknown/unverified evidence, wrong evidence type, empty hash, wrong subject, and unknown candidate all blocked (`COMB-08`, `COMB-09`, `EVID-01`, `EVID-07`, `EVID-09`, `EVID-10`, `ST-01`, `ST-08`).
- Rejected/deferred states, formal-state contradictions, invalid states, inactive candidates and duplicate identities blocked (`ST-04`, `ST-05`, `ID-04`, `ID-05`, `ID-06`).
- Topology cannot appoint or grant Stage B by itself (`POL-05`, `POL-06`); governance flags cannot be altered to grant recruitment or field validation (`AUTH-01`–`AUTH-03`).
- `NOT_RECOMMENDED` classification remains in policy; explicit review does not modify policy (policy file hash verified unchanged before/after validation).

## Current state and authorization boundary

`python tests/current_state_and_boundary.py` → **36 PASS / 0 FAIL**. Research Owner remains `ACCEPTED_IN_CONVERSATION`, the other five roles `UNASSIGNED`, topology `PROPOSED`, zero candidates/evidence/appointments/approvals, Stage B NO, recruitment and field validation not granted, CLI exit 1 with no traceback. The engine emits eight role dimensions plus Stage B readiness; it emits no storage, consent, recruitment or field-validation authorization dimension, and no code path grants them.

## Interpretation

The three HIGH findings mean a formally appointed role can be reported Stage B-ready with an approval basis containing only whitespace, with an unrelated combination rationale, or with acceptance evidence that is not bound to the role being accepted. These are the same class of defect as original F-10 and F-03 and are **not** downgraded.
