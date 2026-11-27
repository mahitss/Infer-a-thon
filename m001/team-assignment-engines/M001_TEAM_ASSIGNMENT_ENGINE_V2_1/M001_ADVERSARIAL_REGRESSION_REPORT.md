# M001 V2.1 — Adversarial Regression Report

**Mission:** M001-TEAM-006  
**Evidence:** `reports/logs/*.txt`, `reports/verification_runs.json`, `tests/results/*.json`

## Exact commands and results

| Command | Exit | Result |
|---|---|---|
| `python -m unittest discover -s tests/adversarial -p 'test_*.py' -v` | 0 | 24 tests OK (original independent adversarial checks) |
| `python -m unittest discover -s tests/regression -p 'test_*.py' -v` | 0 | 53 tests OK |
| `python tests/independent/independent_adversarial_v21.py` | 0 | 50 cases: 38 secure, 12 open MEDIUM/LOW |
| `python tests/independent/refined_cases_v21.py` | 0 | 15 refined cases; see below |
| `python cli/validate.py --state state/current_assignment_state.json` | 1 | Stage B NO, 7 blocking errors, no traceback |
| `python cli/validate.py --state tests/fixtures/valid_four_person.json` | 0 | Stage B YES, zero errors |
| `python cli/validate.py --state tests/fixtures/schema_invalid_assignment.json` | 1 | `E-SCHEMA`, empty stderr |
| `python cli/validate.py --state tests/fixtures/malformed.json` | 2 | `E-JSON-INVALID`, empty stderr |
| `python cli/validate.py --state tests/fixtures/invalid_utf8.bin` | 2 | `E-ENCODING-INVALID`, empty stderr |
| `python cli/validate.py --state tests/fixtures/duplicate_json_key.json` | 2 | `E-DUPLICATE-JSON-KEY`, empty stderr |
| `python cli/validate.py --state tests/fixtures/does_not_exist.json` | 2 | `E-FILE-NOT-FOUND`, empty stderr |
| determinism (workspace root vs system temp cwd) | — | byte-identical stdout/stderr/exit |

The 53 regression tests comprise 5 CLI tests, 20 explicit M001-TEAM-004 scenarios, 6 V2 semantic
regressions and the 22 new M001-TEAM-006 HIGH-finding tests.

## 22 required cases

All 22 are implemented in `tests/regression/test_v2_1_high_findings.py` and pass. Their observed
results are itemised in `M001_HIGH_FINDING_REMEDIATION_MATRIX.md`.

## Independent 50-case suite

The auditor-authored suite from the completed V2 re-audit was copied into V2.1 (the original
audit workspace was not modified) and its path constants and evidence IDs adapted to V2.1's
role-bound fixture names. Result: 38 secure / 12 expected-open. The 12 remaining cases are the
previously tracked MEDIUM/LOW limitations (duplicate approval roles, stale approvals, stale
evidence, hash-source correspondence, duplicate evidence, escalation whitespace, candidate
identity canonicalization and split identities). **None of the four HIGH findings remains
observable**: the whitespace basis/rationale cases and the shared-acceptance case are now blocked.

## Refined cases (before/after)

| Case | V2 re-audit | V2.1 |
|---|---|---|
| whitespace approval basis | `ready=True`, no issues | `E-DECISION-EVIDENCE-EMPTY`, ready NO |
| whitespace combination rationale | `ready=True`, no issues | `E-COMBINATION-RATIONALE`, ready NO |
| one acceptance evidence shared by two roles | `ready=True`, no issues | four role-binding/evidence errors, ready NO |

## Tests that could not be reproduced

All requested suites were reproduced. The only adaptations were: (a) evidence-ID mapping in the
copied 50-case suite to match V2.1 role-bound fixture IDs; (b) four inherited/new assertions
widened to accept the terminal `E-SCHEMA` block introduced by N-15. No test was skipped or removed.

## Synthetic data boundary

Every synthetic fixture is marked `SYNTHETIC_TEST_DATA`. The real state contains zero candidates,
zero evidence, zero appointments and zero combination approvals; no synthetic record was inserted.
