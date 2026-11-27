# M001 V2.1 — Independent Attack Reproduction (V2 vs V2.1)

**Mission:** M001-TEAM-007  
**Evidence:** `tests/results/quick_comparison_results.json`, `tests/results/independent_followup_results.json`

## Method

Both validators were imported from their preserved paths with `importlib.util.spec_from_file_location`
(no writes). States were in-memory deep copies of each version's own synthetic
`valid_four_person.json`. No V2 or V2.1 file was modified.

Command: `python tests/quick_v2_v21_compare.py`

## Reproduced attacks and V2.1 results

| Finding | Mutation | V2 (original vulnerability) | V2.1 (remediated) |
|---|---|---|---|
| N-01 | `approval.basis = ' \t\n '` | `ready=True`, zero issues | `ready=False`, `E-DECISION-EVIDENCE-EMPTY` |
| N-02 | `combination_approvals[0].rationale = ' \t\n '` | `ready=True`, zero issues | `ready=False`, `E-COMBINATION-RATIONALE` |
| N-03 | both roles of one candidate reference one acceptance-evidence record | `ready=True`, zero issues | `ready=False`, `E-ACCEPTANCE-APPOINTMENT`, `E-ACCEPTANCE-DECISION-REUSED`, `E-ACCEPTANCE-ROLE`, `E-EVIDENCE-SUBJECT` |
| N-15 | `governance = None` | unhandled `AttributeError: 'NoneType' object has no attribute 'get'` | `ready=False`, `E-SCHEMA`, no exception |
| N-15 | schema with `$ref: '#/$defs/NOPE'` | unhandled `_WrappedReferencingError` (PointerToNowhere) | `ready=False`, `E-SCHEMA-REFERENCE`, bounded message, no exception |

## Additional auditor cases (V2.1 only)

27 atomic cases were executed: all passed. They include Unicode whitespace (`\u00a0\u2003\u3000`),
null and non-string basis/rationale, meaningful Unicode basis still accepted, exact combination
roles still enforced, rationale reuse across unrelated decisions, wrong-role/wrong-candidate/
other-appointment/reused/missing/unverified/revoked/wrong-type/key-id-mismatch acceptance evidence,
and all six schema-failure shapes. A deliberately injected `RuntimeError` propagated, confirming
unexpected programming errors are not suppressed.

## New unrelated defects found in this comparison

None in the four remediation areas. Lower-severity findings carried forward are triaged separately
in `M001_LOWER_SEVERITY_RISK_TRIAGE.md`.

## Tests not reproduced

All requested attack reproductions were executed. No test was skipped.
