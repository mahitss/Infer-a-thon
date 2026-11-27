# M001 V2.1 — High-Severity Defect Remediation

**Mission:** M001-TEAM-006  
**Date:** 2026-11-27  
**Workspace:** `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1`  
**Final verdict:** FOUR HIGH DEFECTS REMEDIATED — READY FOR INDEPENDENT FOLLOW-UP

## Scope and preservation

This is a focused security remediation of the four HIGH findings in the independent
`M001_FINAL_DEFECT_REGISTER.json`: **N-01, N-02, N-03, N-15**. It is not a research-package
regeneration and not a repeat of the completed V2 audit.

Before implementation, SHA-256 baselines were recorded (`evidence/PRESERVED_BASELINE.json`) for
V2 (76 authored files), the V2 re-audit (83), V1 (43), the prior audit (465) and repository HEAD
`30db9a1929bbccf73a538f6657cb10f49758688e` (clean). Final check `python verify_preservation.py`
reports all four workspaces unchanged and the repository clean. No governance status, register,
ADR, candidate record, ACL, storage setting or consent record was modified; nobody was contacted.

## Implementation summary

V2.1 is a separate workspace seeded from read-only V2 source. Changes:

1. **Meaningful-text gate** (`meaningful_text()`) requires a string containing at least one
   non-whitespace Unicode character. Applied to approval basis and combination rationale. No
   trimming of meaningful content, no placeholder substitution, no type coercion.
2. **Role-bound acceptance evidence** (`acceptance_evidence_check()`) requires the evidence
   subject to equal `candidate_ref:role` and verifies role, appointment reference, distinct
   decision reference, evidence ID/registry-key consistency, evidence type, verification
   status, timezone-aware timestamp, recording authority and revoked state. Schema and policy
   now document the new evidence fields (`role`, `appointment_ref`, `decision_ref`, `revoked`,
   `revoked_at`); policy version is 2.1.
3. **Terminal schema handling** (`structural_schema_errors()` + early return in
   `validate_state()`): schema/reference failures produce stable `E-SCHEMA*` issues, all
   dimensions FAIL, controlled readiness NO and exit code 1, with no raw traceback. Narrow
   exception classes only; unexpected engine errors are not broadly suppressed.
4. **Rationale reuse guard**: a normalized rationale cannot satisfy a different combination
   decision (`E-COMBINATION-RATIONALE-REUSED`).

## Separate dimensions preserved

The eight role dimensions and Stage B readiness remain distinct. Valid synthetic topology with
all roles formal reports readiness YES; the current real state reports readiness NO. Both
recruitment and field-validation authorization are always emitted NO and are never inferred
from topology, compatibility, acceptance, approval or Stage B readiness.

## Validation evidence

| Command | Result |
|---|---|
| `python -m unittest discover -s tests/adversarial -p 'test_*.py' -v` | 24 tests, exit 0 |
| `python -m unittest discover -s tests/regression -p 'test_*.py' -v` | 53 tests, exit 0 (includes all 22 required new cases) |
| `python tests/independent/independent_adversarial_v21.py` | 50 cases: 38 secure, 12 open MEDIUM/LOW, exit 0 |
| `python tests/independent/refined_cases_v21.py` | 15 refined cases; whitespace basis/rationale and shared acceptance now blocked |
| `python tests/mutation/canary_v21.py --root .` | 8/8 PASS, exit 0 |
| `python tests/mutation/mutation_harness_v21.py` | 4 introduced, 4 detected, 0 survived, exit 0 |
| `python cli/validate.py --state state/current_assignment_state.json` | exit 1, Stage B NO, no traceback |
| `python cli/validate.py --state tests/fixtures/valid_four_person.json` | exit 0, Stage B YES |
| `python verify_all.py` | all 14 captured commands with exact exit codes in `reports/verification_runs.json` |

Full commands, stdout, stderr and exit codes: `reports/logs/*.txt`,
`reports/verification_runs.json`, `reports/adversarial_regression_report.md`.

## Residuals

17 MEDIUM and 7 LOW findings from the independent re-audit remain explicitly tracked and are
not claimed resolved. In particular: evidence hash/source correspondence, stale timestamps,
duplicate approval roles, whitespace candidate references, identity canonicalization, dimension
reporting for non-global evidence errors, and the surrogate-print CLI issue remain open.

## Reproduction

```powershell
cd C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1
python verify_all.py
python verify_preservation.py
python build_manifest.py
```

No synthetic candidate was inserted into real state; all synthetic fixtures are marked
`SYNTHETIC_TEST_DATA`.
