# M001 V2.2 — Independent Regression Results

**Mission:** M001-TEAM-009  
**Evidence:** `tests/results/regression_results.json`, `reports/REGRESSION_AGENT_NOTES.md`

## Executed (not inherited)

| Suite | Exit | Result |
|---|---|---|
| `python -m unittest discover -s tests/adversarial -p 'test_*.py' -v` | 0 | 24/24 pass |
| `python -m unittest discover -s tests/regression -p 'test_*.py' -v` | 0 | 66/66 pass |
| 50-case auditor corpus | 0 | 43 secure / 7 defect; each open case classified individually |
| V2.1 focused tests (`test_v2_1_high_findings.py`) | 0 | 22/22 pass |
| V2.2 blocker tests (`test_v2_2_blockers.py`) | 0 | 13/13 pass |
| Canary `canary_v22.py --root .` | 0 | 8/8 pass |
| Mutation harness (disposable copy) | 0 | 5 introduced, 5 detected, 0 survived |
| CLI 7 cases | — | exits 1/0/1/2/2/2/2, empty stderr, no Traceback |
| Determinism (two cwds) | — | byte-identical stdout/stderr/exit |

Writing runners were executed from a byte-identical disposable copy inside this audit workspace so
V2.2 was never written; V2.2 tree (132 files) and state hash unchanged; git HEAD unchanged, clean.
No suite was skipped.

## Seven open corpus cases — individual classification

| Case | Classification | Basis |
|---|---|---|
| COMB-03 | expectation artifact | `pair_key()` uses `sorted(set(roles))`; expected code `E-COMBINATION-APPROVAL-DUPLICATE` does not exist in engine/policy/schema and no documented contract requires it |
| COMB-12 | expectation artifact | appended deepcopy retains `candidate_ref='C-P1'` and C-P5 holds no roles; claimed scenario never constructed; refined variant does block |
| EVID-03 | genuine residual | `content_hash` checked only as 64-hex format, never against source content |
| EVID-06 | genuine residual | no evidence timestamp ↔ decision/source ordering |
| ST-02 | expectation artifact | ordering still valid; no freshness contract exists in policy |
| ID-02 | genuine residual | no Unicode-normalisation collision check |
| ID-07 | inconclusive | blocked only incidentally by role/evidence binding; no explicit alias check exists |

This is why the corpus is reported as 43 secure / 7 defect rather than being auto-marked pass or fail:
two are expectation artifacts, three are genuine residuals and two are inconclusive.

## Passing / failing / open / inconclusive / excluded

- Passing: 24 + 66 + 22 + 13 + 8 + 5 mutation detections + 7 CLI + determinism + 43 corpus cases.
- Failing: none in the executed suites (all exit 0 or expected CLI codes).
- Open residual cases: EVID-03, EVID-06, ID-02; inconclusive: ID-07; expectation artifacts: COMB-03, COMB-12, ST-02.
- Excluded: none; the only relocation was the three writing harnesses into a disposable copy, with the real V2.2 engine under test.
