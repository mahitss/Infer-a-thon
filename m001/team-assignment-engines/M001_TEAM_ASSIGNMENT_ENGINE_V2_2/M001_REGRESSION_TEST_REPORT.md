# M001 V2.2 — Regression Test Report

**Mission:** M001-TEAM-008  
**Evidence:** `reports/verification_runs.json`, `reports/logs/*.txt`, `tests/results/*.json`

## Executed commands and results

| Command | Exit | Result |
|---|---|---|
| `python -m unittest discover -s tests/adversarial -p 'test_*.py' -v` | 0 | 24/24 OK |
| `python -m unittest discover -s tests/regression -p 'test_*.py' -v` | 0 | 66/66 OK (53 V2.1 + 13 new blocker tests) |
| `python tests/independent/independent_adversarial_v21.py` | 0 | 50 cases: 43 secure / 7 open |
| `python tests/independent/refined_cases_v21.py` | 0 | 14 refined cases reproduced |
| `python tests/mutation/canary_v22.py --root .` | 0 | 8/8 PASS |
| `python tests/mutation/mutation_harness_v22.py` | 0 | 5 introduced, 5 detected, 0 survived |
| `python cli/validate.py --state state/current_assignment_state.json` | 1 | Stage B NO, 7 blocking errors, no traceback |
| `python cli/validate.py --state tests/fixtures/valid_four_person.json` | 0 | Stage B YES |
| `python cli/validate.py --state tests/fixtures/schema_invalid_assignment.json` | 1 | `E-SCHEMA`, empty stderr |
| CLI malformed / invalid UTF-8 / duplicate keys / missing file | 2 each | stable codes, empty stderr |
| Determinism (two cwds) | — | byte-identical stdout/stderr/exit |

Full stdout, stderr and exit codes: `reports/verification_runs.json` and `reports/logs/`.

## New blocker tests (13)

`tests/regression/test_v2_2_blockers.py` covers: four individual invisible characters in basis and
rationale; mixed whitespace/invisible combinations; ASCII and Unicode whitespace; five meaningful
Unicode content forms (English, accented, Indic, RTL, ZWJ emoji) for both basis and rationale; null
and non-string inputs; no fabrication; N-04 whitespace and invisible contact; N-08 duplicate
evidence; N-11 ordering and valid-ordering control; N-12 whitespace candidate ref; deterministic
repeated execution.

## Targeted Unicode adversarial results

- U+200B, U+200E, U+2060 and U+FEFF alone or in any combination with whitespace: rejected.
- Meaningful text containing those characters (ZWJ emoji, RTL marks) still passes.
- Non-string/null inputs fail closed via schema or predicate.
- Repeated execution produces identical results.

## Adaptation notes

The copied 50-case corpus had one stale expectation for stale approvals; it was widened to accept
the new stable `E-COMBINATION-APPROVAL-TIMESTAMP-ORDER` code. All other expectations unchanged.
No test was skipped; all requested suites executed.
