# M001 V2.1 — Mutation Regression Report

**Mission:** M001-TEAM-006  
**Evidence:** `tests/mutation/mutation_harness_v21.py`, `tests/mutation/canary_v21.py`, `tests/results/mutation_results.json`, `reports/logs/canary.txt`, `reports/logs/mutation.txt`

## Independence and safety

A V2.1-specific harness and canary were written; V2's mutation harness was not reused. Mutations
are applied only to disposable copies under `tests/mutation/mutants/` containing `engine/`,
`policy/`, `schemas/` and `tests/fixtures/`. V2, the re-audit, V1, the prior audit and the repo
were never mutated.

## Results

| Metric | Value |
|---|---|
| Baseline canary (unmodified V2.1) | `CANARY_PASS 8/8`, exit 0 |
| Introduced mutations | 4 (one per HIGH remediation area) |
| Detected | **4** |
| Survived | **0** |
| Excluded | 0 |

Exact output: `BASELINE_EXIT 0`, `DETECTED 4/4`.

| Mutation | Controlled defect | Detected |
|---|---|---|
| M1_basis_check_removed | disable `meaningful_text()` on approval basis | YES — canary B01/B02 fail, exit 1 |
| M2_rationale_check_removed | disable `meaningful_text()` on combination rationale | YES — canary B03 fails, exit 1 |
| M3_acceptance_role_binding_removed | replace role-bound subject with bare candidate ref | YES — canary B04 fails, exit 1 |
| M4_schema_terminal_return_removed | replace terminal schema return with `pass` | YES — canary B06/B07 fail, exit 1 |

## Canary properties

- B00 valid synthetic state passes
- B01 ASCII whitespace basis blocked
- B02 Unicode whitespace basis blocked
- B03 whitespace rationale blocked
- B04 wrong-role acceptance blocked
- B05 revoked acceptance evidence blocked
- B06 schema failure controlled and terminal (all dimensions FAIL)
- B07 unresolvable schema reference controlled

## Interpretation

Every introduced defect in the four remediation areas is detected. This demonstrates that the
new controls are covered by executable tests, not merely documented. The result is limited to the
four HIGH areas; it does not re-open or re-test the broader independent mutation suite from
M001-TEAM-005.
