# M001 V2.1 — Independent Regression Results

**Mission:** M001-TEAM-007  
**Evidence:** `tests/results/independent_regression_results.json`, `reports/REGRESSION_AGENT_NOTES.md`, `tests/results/independent_followup_results.json`

## Executed results (not inherited)

| Suite | Command | Exit | Result |
|---|---|---|---|
| Original 24 adversarial checks | `python -m unittest discover -s tests/adversarial -p 'test_*.py' -v` (V2.1 root) | 0 | 24/24 PASS |
| V2.1 regression suite | `python -m unittest discover -s tests/regression -p 'test_*.py' -v` (V2.1 root) | 0 | 53/53 PASS, including all 22 remediation cases |
| 50-case independent corpus | `python tests/independent/independent_adversarial_v21.py` (disposable mirror) | 0 | 38 SECURE / 12 residual MEDIUM-LOW defects |
| Refined cases | `python tests/independent/refined_cases_v21.py` (disposable mirror) | 0 | 14 cases reproduced; residuals confirmed |
| Canary | `python tests/mutation/canary_v21.py --root .` (disposable mirror) | 0 | 8/8 PASS |
| Mutation harness | `python tests/mutation/mutation_harness_v21.py` (disposable mirror) | 0 | 4 introduced, 4 detected, 0 survived |
| CLI cases (8) | real V2.1 CLI | — | exits 1/0/1/2/2/2/2/2, all stderr empty, no traceback |
| Determinism | two working directories | — | PASS (after correcting a harness path bug) |
| Auditor's own cases | `python tests/independent_followup_tests.py` | 0 | 27/27 PASS plus 6 schema-failure cases |
| State/boundary | `python tests/state_and_boundary.py` | 0 | 38/38 PASS |

The independent scripts and mutation harness were run from byte-identical disposable mirrors under
the FOLLOWUP workspace because they write result/mutant files into their own root. V2.1 was never
written to; its state hash and all authored files remained unchanged (verified against
`evidence/BASELINE_START.json`).

## CLI expectation-assertion correction

The regression harness marked CLI_CURRENT and CLI_SCHEMA_INVALID as FAIL because their
`stdout_contains` expectation was a compound literal string (e.g. `"E-APPOINTMENT-MISSING /
E-TOPOLOGY-UNAPPROVED"`). Independent inspection of the captured stdout confirms both satisfy
the real requirements:

- CLI_CURRENT: exit 1, stderr empty, `Stage B role readiness: NO`, both authorizations NO,
  six `E-APPOINTMENT-MISSING` plus `E-TOPOLOGY-UNAPPROVED`.
- CLI_SCHEMA_INVALID: exit 1, stderr empty, all eight dimensions FAIL, `E-SCHEMA` present.

Effective CLI result: **8/8 requirement-satisfying**. No engine defect is associated with the two
harness mislabels.

## Residual verdicts in the 50-case corpus

12 cases remain DEFECT: duplicate approval roles, stale approval/acceptance timestamps, stale
evidence, source-hash mismatch, duplicate evidence, whitespace escalation contact, whitespace
candidate ref, identity canonicalization and split identities. These are the carried-forward
MEDIUM/LOW findings triaged in `M001_LOWER_SEVERITY_RISK_TRIAGE.md`; none is one of the four HIGH
findings.

## Tests not executed

None requested were left unexecuted. The only deviations were the harmless disposable-mirror
relocation and the corrected determinism harness path, both documented in the agent notes.
