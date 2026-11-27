# M001-TEAM-007 — Independent lower-severity triage (V2.1 follow-up)

**Agent:** independent research-governance and security auditor
**Date:** 2026-11-27
**Deliverables (only files written):**
- `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1_FOLLOWUP\analysis\lower_severity_triage.json`
- `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1_FOLLOWUP\reports\TRIAGE_AGENT_NOTES.md`

**Boundaries honoured:** V1, V2, V2_REAUDIT, V2_1 and the git repository were read only. All probes used `python -B` (no bytecode written into protected directories), captured stdout/stderr only, and never used `--json-out`. No installs and no network access.

## Scope

Triaged **all 24 carried-forward lower-severity findings** from
`M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT\M001_FINAL_DEFECT_REGISTER.json`:
17 MEDIUM (N-04..N-14, S-01..S-04, N-16, N-17) and 7 LOW (S-05, S-06, S-07, N-18..N-21). The four HIGH findings (N-01, N-02, N-03, N-15) were excluded from triage but their fixes were inspected because they incidentally affect lower findings. No finding was automatically closed and no severity was downgraded. Original severities are preserved verbatim in the JSON.

## Source inspected (read only)

All under `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1`:

| File | Lines used for this triage |
|---|---|
| `engine/validator.py` | 24-40 (schema exception tuple); 51-58 (`meaningful_text`, `identity_subject`); 110-133 (`load_json_strict`); 144-209 (subset fallback); 220-238 (schema error handling); 240-257 (`valid_timestamp`, `parse_timestamp`, `pair_key`); 260-300 (`evidence_check`); 303-335 (`acceptance_evidence_check`); 338-352 (`candidate_registry_check`); 355-389 (`validate_state` setup + terminal schema return); 391-410 (registry loop); 412-477 (role loop, escalation at 475-476); 478-501 (appointments); 503-531 (combination approvals); 533-560 (compatibility); 562-565 (readiness); 568-592 (reports) |
| `schemas/team_assignment.schema.json` | 3 (`$id`); 42-43 (arrays); 55-72 (evidence, `content_hash` L62); 74-121 (roleRecord); 122-129 (appointment); 131-143 (combinationApproval) |
| `policy/role_constraints.json` | 2-7 (version/source/states); 8-19 (combination rules); 20-27 (evidence types, unused fields, dimensions) |
| `cli/validate.py` | 8-9, 26-36 (`ROOT`, relative `--state`); 38-49 (exception tuple); 51-58 (`--json-out`, `print`) |

For comparison, read-only V2 source (`M001_TEAM_ASSIGNMENT_ENGINE_V2\engine\validator.py` L176-315) and the V2 re-audit reports (`CLI_AGENT_NOTES.md`, `SCHEMA_AGENT_NOTES.md`, `M001_EVIDENCE_INTEGRITY_REPORT.md`) were consulted to distinguish genuine V2.1 changes from inherited behaviour.

## Environment

- Python 3.13.5; jsonschema **4.26.0 installed**, so full Draft 2020-12 validation is active and the subset fallback is dormant (its `FormatChecker` has no `date-time` checker).
- Console encoding cp1252 (relevant to N-17).
- Base state for validator-level probes: read-only `V2_1\tests\fixtures\valid_four_person.json` (baseline `stage_b_role_ready=True`, 0 issues).

## Exact probe commands

All commands were run with cwd = `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1`; `-B` prevents bytecode writes into the protected V2.1 tree.

Validator-level probes (heredoc piped to `python -B -`, no files created) imported the read-only V2.1 engine:

```
sys.path.insert(0, r"C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1")
from engine import validator as v
p = v.load_policy(); s = v.load_schema()
b = v.load_json_strict(V21 + r"\tests\fixtures\valid_four_person.json")
# per-finding deep-copy mutation, then:
r = v.validate_state(mutated_state, p, s)
print(r.stage_b_role_ready, r.dimensions, [i.code for i in r.issues])
```

CLI probes:

```
python -B C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1\cli\validate.py --state C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT\tests\cases\c02_deep_5000_arrays.json
python -B C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1\cli\validate.py --state C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT\tests\cases\c04d_json_lone_surrogate_escape.json
python -B C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1\cli\validate.py --state C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT\tests\cases\c01_dup_nested_approval.json
python -B C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1\cli\validate.py --state C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT\tests\cases
python -B .\cli\validate.py --state ..\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT\tests\cases\c10_relative_state.json
```

Policy-usage probe: read-only quoted-field-name counts of every `policy/role_constraints.json` key in `engine/validator.py`.

## Independent probe results (summary)

| Probe | Result | Finding |
|---|---|---|
| BASE `valid_four_person.json` | ready=True, 0 issues | control |
| escalation.contact = `'   '` | ready=True, 0 issues | N-04 |
| combination roles with duplicate CONTINUE_STOP_OWNER | ready=True, 0 issues | N-05 |
| approval.evidence_id = `e-does-not-exist` | ready=False, `E-EVIDENCE-UNKNOWN`, but `evidence_integrity=PASS` | N-06 |
| referenced hash `'0'*64`; dangling hash `'bad'` | both ready=True, 0 issues | N-07 / S-02 |
| exact evidence copy under second ID; copy reused by another role for PO/onboarding evidence | ready=True, 0 issues | N-08 |
| evidence timestamp 1999; acceptance 2020; combo decision 2019 | all ready=True, 0 issues | N-09 / N-10 |
| combination decision 2026-11-26 before acceptance 2026-11-27 | ready=True, 0 issues | N-11 |
| fully consistent whitespace candidate ref (candidate, roles, appointments, approvals, evidence keys/subjects/appointment_refs) | ready=True, 0 issues | N-12 |
| evidence `revoked=true` / `revoked_at` set | ready=False, `E-EVIDENCE-REVOKED` | N-14 (partial improvement) |
| role `formal.revoked`, combo `revoked`, role `history` | `E-SCHEMA` (fail-closed, not evaluated) | N-14 |
| naive `recognition.decision_date` | ready=True, 0 issues | S-01 |
| `unresolvable_ref_schema.json` used as schema | ready=False, single `E-SCHEMA-REFERENCE`, **no exception** | S-03 (verified closed) |
| fallback `validate_schema` with `uniqueItems` / boolean subschema | returns `[]` / raises `TypeError` (dormant path) | S-04 |
| evidence key vs `evidence_id` field: referenced / unreferenced (original E06) | `E-EVIDENCE-ID-MISMATCH` / ready=True, 0 issues | S-05 (partial improvement) |
| duplicate combination approval copy | ready=True, 0 issues | S-07 (appointment duplicates are blocked at 479-489) |
| c02 deep arrays via CLI | exit 1, empty stdout, `RecursionError` traceback | N-16 |
| c04d lone surrogate via CLI | exit 1, empty stdout, `UnicodeEncodeError` at cli:57 | N-17 |
| directory as `--state` | exit 2, `E-FILE-NOT-FOUND: PermissionError` | N-19 |
| nested duplicate key (`basis`) | exit 2, `E-DUPLICATE-JSON-KEY: basis`, no path | N-20 |
| relative `../` state from V2.1 cwd | normal report, `Source: c10_relative_state.json` | N-18 |
| quoted-field-name counts in validator.py | 0 refs for `missing_appointment_states`, `evidence_fields`, `acceptance_evidence_binding`, `timestamp_fields`, `require_combination_approval_for_multi_role` | N-21 |

V2.1's own harness results (`tests/results/independent_adversarial_results.json`) were used only as corroboration, never as closure proof. Notably its ID-03 and ID-07 cases are blocked incidentally by N-03 evidence binding / exact-key approval requirements, not by the underlying identity defects; a fully consistent whitespace-ref mutation independently reached ready=True.

## Classification rationale

- **A — must fix before Stage B readiness (4):** N-04, N-08, N-11, N-12. Each independently produced `stage_b_role_ready=True` for a state that is semantically invalid at the governance gate (no real escalation contact; one evidence artifact reused for two roles; approval before acceptance; whitespace-only candidate identity). These misstate formal appointment readiness.
- **B / C (0 each):** no lower finding can flip `recruitment_authorized` or `field_validation_authorized` — both are hard-coded `False` (`engine/validator.py:83-84, 565`). Assigning B or C would be factually unsupported.
- **D — acceptable residual with documented rationale (14):** N-05, N-06, S-01, S-03, S-04, S-05, S-06, S-07, N-16, N-17, N-18, N-19, N-20, N-21. These are diagnostics-only, fail-closed, dormant in the current environment, or (S-03) independently verified closed. N-05 is idempotent under set semantics; N-06 keeps readiness fail-closed via `not issues` at 561-565; S-01 affects only ungated fields; S-04's fallback is never reached with jsonschema installed; S-07's duplicate approvals are still individually validated.
- **E — still requires investigation (6):** N-07, N-09, N-10, N-13, N-14, S-02. Resolution needs an authoritative source digest/timeline, a governance-defined freshness window, an identity authority, or a revocation/history model. The state alone cannot adjudicate these; they are kept OPEN pending that design decision.

`blocks_eventual_operational_use` is `yes` for all A and E findings and `no` for D findings (with recommended mitigations documented per finding).

## Incidental V2.1 changes (explicitly not treated as closure)

- **S-03** was incidentally fixed by the N-15 remediation: `validator.py:24-40` exception tuple + `220-233` catch + `378-389` terminal return. Independently verified with `unresolvable_ref_schema.json` → `E-SCHEMA-REFERENCE`, no traceback. Status `verified_closed`, original MEDIUM severity retained.
- **N-14** partially improved: evidence-level `revoked`/`revoked_at` now evaluated (`validator.py:278-280`); role/combination revocation and decision history remain unsupported.
- **S-05** partially improved: `E-EVIDENCE-ID-MISMATCH` at `validator.py:275-277` covers referenced records; the original E06 unreferenced mismatch still passes.
- **N-12**: the shipped ID-03 harness mutation is blocked incidentally by N-03 subject binding, but a consistent mutation is not — kept OPEN.
- **N-03 fix did not cover S-07 or N-08**; no duplicate-evidence or duplicate-approval detection was added.
- **N-01/N-02 fixes (`meaningful_text`) were not extended** to escalation contact (N-04) or candidate ref (N-12).

**Bottom line:** 23 findings remain OPEN at their original severity; only S-03 is independently verified closed. Four findings (N-04, N-08, N-11, N-12) are A blockers for Stage B readiness; six need investigation before any operational reliance on the evidence/identity/temporal gates. No V2.1 test pass was accepted as proof of closure, and no V2.1 test was modified or run against protected directories in a way that writes to them.
