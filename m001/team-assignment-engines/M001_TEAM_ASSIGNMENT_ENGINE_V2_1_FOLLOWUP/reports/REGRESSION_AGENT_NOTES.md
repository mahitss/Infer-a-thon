# Independent regression evidence — M001-TEAM-007

**Role:** independent security auditor, V2.1 regression.
**Date captured:** 2026-11-27.
**Environment:** Python 3.13.5 (`C:\Users\pc\AppData\Local\Programs\Python\Python313\python.exe`).
Every command was run with `PYTHONDONTWRITEBYTECODE=1`, no installs, no network.
Machine-readable capture: `tests/results/independent_regression_results.json`
(raw evidence: `tests/results/_raw_capture.json`).

## Boundary handling

Commands that are read-only were executed **verbatim from the V2.1 root**:
adversarial and regression `unittest discover`, the canary, all CLI checks, and the
two-location determinism check.

Three runners were **not** executed verbatim from the V2.1 root:
`tests/independent/independent_adversarial_v21.py`,
`tests/independent/refined_cases_v21.py`, and
`tests/mutation/mutation_harness_v21.py`. Inspection of their source shows each
writes into its own `ROOT` (`parents[2]` of the script): two write `tests/results/*.json`,
and the mutation harness deletes/recreates `tests/mutation/mutants` and copies four
source trees into it. Running them with `cwd=V2_1` would write into the preserved
V2.1 workspace, which the mission forbids. Byte-identical copies of `engine`, `policy`,
`schemas`, `tests`, `cli` and `state` were placed in
`FOLLOWUP/tests/disposable_v21/` and the scripts were run there. The independent
scripts still hardcode `V2 = C:\...\M001_TEAM_ASSIGNMENT_ENGINE_V2_1`, so the audited
engine and fixtures are the real preserved V2.1 files; only the writes are redirected.
The mutation harness therefore ran in the disposable copy, never in V2.1.

## 1. Adversarial suite — EXECUTED, PASS

```
cwd: C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1
python -m unittest discover -s tests/adversarial -p 'test_*.py' -v
```
Exit `0`; stdout empty; stderr ends with:

```
Ran 24 tests in 1.437s

OK
```
24 checks executed, 24 passed, 0 failed. Matches the claimed 24.

## 2. Regression suite — EXECUTED, PASS

```
cwd: C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1
python -m unittest discover -s tests/regression -p 'test_*.py' -v
```
Exit `0`; stdout empty; stderr ends with:

```
Ran 53 tests in 21.424s

OK
```
53 tests executed, 53 passed, 0 failed. `test_v2_1_high_findings` contributed
`test_01` … `test_22` (22 remediation cases), all `ok`. Matches the claimed 53/22.

## 3. Independent adversarial 50-case corpus — EXECUTED (relocated runner)

```
cwd: C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1_FOLLOWUP\tests\disposable_v21
python tests/independent/independent_adversarial_v21.py
```
Exit `0`; stdout:
`TOTAL 50 SECURE 38 DEFECT 12`, followed by 12 `DEFECT` lines. Full stdout/stderr
are in the JSON. The generated result file is **byte-identical (SHA-256 match)** to
V2.1's own claimed `tests/results/independent_adversarial_results.json`; this is an
executed reproduction, not a copied claim.

Reproduced residual `DEFECT` verdicts (the suite's own evaluator, not harness errors):
`COMB-03, COMB-06, COMB-12, EVID-03, EVID-04, EVID-06, ST-02, ST-03, ST-10, ID-02, ID-03, ID-07`.
These remain weaknesses in the audited engine; passing the other 38 cases does not
establish that these vectors are fixed.

## 4. Refined cases — EXECUTED (relocated runner)

```
cwd: ...\M001_TEAM_ASSIGNMENT_ENGINE_V2_1_FOLLOWUP\tests\disposable_v21
python tests/independent/refined_cases_v21.py
```
Exit `0`; 14 refined cases printed, byte-identical output file to V2.1's claimed
`refined_case_results.json`. Notable observed outcomes: `DIM-02`, `DIM-03`, `COMB-12`,
`EVID-02`, `ID-02` are blocked; but `ST-02_stale_acceptance_order_valid`,
`ID-03_whitespace_ref_consistent`, `ID-07_six_distinct_identities`,
`COMB-03_duplicate_roles_approval`, `EVID-03_hash_mismatch`,
`EVID-04_duplicate_evidence` and `EVID-06_evidence_predates_source` all show
`ready= True` with no codes. These confirm the residual weaknesses rather than their
remediation.

## 5. Canary and mutation — EXECUTED

```
cwd: C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1
python tests/mutation/canary_v21.py --root .
```
Exit `0`; 8 `PASS` checks (`B00`–`B07`), `CANARY_PASS 8/8`, stderr empty.

```
cwd: ...\M001_TEAM_ASSIGNMENT_ENGINE_V2_1_FOLLOWUP\tests\disposable_v21
python tests/mutation/mutation_harness_v21.py
```
Exit `0`; `BASELINE_EXIT 0`, `DETECTED 4/4`; all four mutants detected with exit 1:
`M1_basis_check_removed`, `M2_rationale_check_removed`,
`M3_acceptance_role_binding_removed`, `M4_schema_terminal_return_removed`.
Result file byte-identical to V2.1's claimed `mutation_results.json`.
**Not executed from V2.1 root** by design (writes mutants into its root); see Boundary handling.

## 6. CLI checks — EXECUTED from V2.1 root

All use `python cli/validate.py --state <fixture>`, `cwd=V2_1`. Every stderr was
empty and neither stdout nor stderr contained `Traceback`.

| state | exact `--state` value | expected | observed | verdict |
|---|---|---|---|---|
| current state | `state/current_assignment_state.json` | 1 | 1, `Blocking errors: 7`, `E-APPOINTMENT-MISSING` ×6 + `E-TOPOLOGY-UNAPPROVED` | PASS |
| valid_four_person | `tests/fixtures/valid_four_person.json` | 0 | 0, `Stage B role readiness: YES`, 0 errors | PASS |
| schema_invalid_assignment | `tests/fixtures/schema_invalid_assignment.json` | 1 | 1, `E-SCHEMA` ×8, all eight dimensions FAIL | PASS |
| malformed.json | `tests/fixtures/malformed.json` | 2 | 2, `E-JSON-INVALID` | PASS |
| invalid_utf8.bin | `tests/fixtures/invalid_utf8.bin` | 2 | 2, `E-ENCODING-INVALID` | PASS |
| duplicate_json_key.json | `tests/fixtures/duplicate_json_key.json` | 2 | 2, `E-DUPLICATE-JSON-KEY: schema_version` | PASS |
| does_not_exist | `tests/fixtures/does_not_exist` | 2 | 2, `E-FILE-NOT-FOUND` | PASS |
| does_not_exist.json (extra) | `tests/fixtures/does_not_exist.json` | 2 | 2, `E-FILE-NOT-FOUND` | PASS |

## 7. Determinism — EXECUTED (corrected), PASS

First attempt used `python cli/validate.py --state state/current_assignment_state.json`
from the two cwds `V2_1` and `C:\Users\pc\AppData\Local\Temp`. From the second cwd the
*relative script path* could not be opened, so Python exited 2 with
`can't open file ...\Temp\cli\validate.py`. That is a harness path error, **not** an
engine defect; the attempt is retained in the JSON with verdict `INVALID_HARNESS_PATH`.

Corrected run used absolute paths in both locations:

```
python C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1\cli\validate.py --state C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1\state\current_assignment_state.json
cwd 1 = C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1
cwd 2 = C:\Users\pc\AppData\Local\Temp
```
Both exits `1`, both stderr empty, stdout byte-identical (1300 chars, 7 blocking
errors). `stdout_equal = stderr_equal = exit_equal = true` → PASS. The in-suite
`test_determinism_two_directories` also passed in section 2.

## Hidden-state / preservation verification

- `state/current_assignment_state.json` SHA-256 before **and** after all commands:
  `E6DDC93C94506BA499878D642CBD29E71E1930409F4FBC9498FAE6A3009D094F` — identical.
- V2.1 tree vs `evidence/BASELINE_START.json`: 108 authored files before and after,
  **0 changed**. Pre-vs-post also 0 changed.
- V1 (43), V2 (76), V2_REAUDIT (83): 0 changed vs baseline and pre-vs-post.
- Git repo HEAD unchanged, `git status --porcelain` empty before and after.
- `PYTHONDONTWRITEBYTECODE=1` inherited by subprocesses; no `.pyc` or `__pycache__`
  added to preserved workspaces.

## Tests not executed / limitations

- No assigned test was skipped. The three relocated runners (items 3, 4 and the
  mutation half of 5) were **not** run with `cwd=V2_1` verbatim; the reason is above.
  Their engine under test is still the real V2.1 engine.
- The first determinism attempt is marked invalid; the corrected absolute-path run
  is the evidence of record.
- Results are independent executions, not trust in V2.1's reports; the three result
  files were independently regenerated and then hash-compared to the claimed files
  (all three byte-identical).
