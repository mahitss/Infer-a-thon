# Regression Test Report — M001 Team Assignment Engine V2

**Date:** 2026-11-27  
**Evidence:** `reports/verification_runs.json`, `reports/logs/*.txt`  
**Runner:** `python verify_all.py` (captures command, cwd, stdout, stderr and exit code for every step)

## Summary

| Suite | Command | Result | Exit | Log |
|---|---|---|---|---|
| Original 24 independent adversarial checks against V2 | `python -m unittest discover -s tests/adversarial -p 'test_*.py' -v` | 24 tests, OK | 0 | `reports/logs/adversarial.txt` |
| V2 regression + CLI + 20 explicit scenarios | `python -m unittest discover -s tests/regression -p 'test_*.py' -v` | 31 tests, OK | 0 | `reports/logs/regression.txt` |
| V2 mutation canary (baseline) | `python tests/mutation/mutation_canary.py --root .` | 18/18 PASS | 0 | `reports/logs/canary.txt` |
| V2 mutation harness | `python tests/mutation/mutation_harness.py` | 16/16 detected, 0 survived | 0 | `reports/logs/mutation.txt` |
| Original V1 mutation canary (read-only, against preserved V1) | `python <AUDIT>/mutation_canary.py --root <V1>` | 10/10 PASS | 0 | `reports/logs/original_v1_mutation_canary.txt` |
| Determinism | current-state CLI from workspace root vs system temp cwd | stdout/stderr/exit identical | — | `reports/verification_runs.json` |

The original audit harness was not re-executed in place because it writes into the
preserved audit workspace. Its read-only canary was re-run against V1 instead, producing
10/10 PASS, matching the baseline recorded in the frozen audit's `mutation_results.json`
(10 mutants, 10 detected, 0 survived).

## 24 adversarial checks — V2 results

Every check observes the expected secure behaviour (PASS). The checks cover: hard
incompatibilities (ADV-01/02), discouraged combinations (ADV-03/04/13), boolean-only
evidence (ADV-05), forged evidence IDs (ADV-06), duplicate and unknown candidates
(ADV-07/08), PROPOSED and ACCEPTED_IN_CONVERSATION not appointed (ADV-09/10), formal flag
mismatch (ADV-11), empty approval basis (ADV-12), naive/missing timestamps (ADV-14),
duplicate JSON keys (ADV-15), unapproved topology (ADV-16), rejected candidate retained
(ADV-17), missing onboarding (ADV-18), malformed JSON (ADV-19), invalid UTF-8 (ADV-20),
missing file (ADV-21), no authorization inference (ADV-22), different combination
approval (ADV-23), and deterministic output (ADV-24).

## 20 explicitly required scenarios

| # | Required scenario | Test | Observed |
|---|---|---|---|
| 1 | Multi-role without PO approval | `test_01_multi_role_without_po_combination_approval` | `E-COMBINATION-APPROVAL-MISSING`, readiness NO |
| 2 | Approval for different combination | `test_02_approval_for_different_combination` | `E-COMBINATION-APPROVAL-MISSING`, readiness NO |
| 3 | PROPOSED treated as appointed | `test_03_proposed_treated_as_appointed` | `E-APPOINTMENT-MISSING` (MODERATOR), readiness NO |
| 4 | ACCEPTED_IN_CONVERSATION treated as formal | `test_04_accepted_conversation_not_formal` | `E-APPOINTMENT-MISSING` (MODERATOR), readiness NO |
| 5 | Boolean evidence without reference | `test_05_boolean_evidence_without_reference` | `E-EVIDENCE-MISSING` |
| 6 | Forged evidence identifier | `test_06_forged_evidence_identifier` | `E-EVIDENCE-UNKNOWN` |
| 7 | Duplicate candidate identities | `test_07_duplicate_candidate_identities` | `E-CANDIDATE-DUPLICATE` |
| 8 | Unknown candidate identity | `test_08_unknown_candidate_identity` | `E-CANDIDATE-UNKNOWN` |
| 9 | FORMALLY_APPOINTED missing formal approval | `test_09_formally_appointed_with_missing_formal_approval` | `E-PO-APPROVAL` / `E-FORMAL-APPROVAL-MISMATCH` |
| 10 | Empty approval basis | `test_10_empty_approval_basis` | `E-DECISION-EVIDENCE-EMPTY` |
| 11 | Discouraged combination without review | `test_11_discouraged_combination_without_po_review` | `E-DISCOURAGED-RO-MODERATOR`, readiness NO |
| 12 | Missing timestamps | `test_12_missing_timestamps` | `E-TIMESTAMP-MISSING` |
| 13 | Duplicate JSON keys | `test_13_duplicate_json_keys` | `DuplicateKeyError` (`E-DUPLICATE-JSON-KEY`) |
| 14 | Unapproved topology as Stage B ready | `test_14_unapproved_topology_not_stage_b_ready` | `E-TOPOLOGY-UNAPPROVED`, readiness NO |
| 15 | Rejected candidate retained | `test_15_rejected_candidate_not_active` | `E-UNAPPROVED-APPOINTMENT` / `E-APPOINTMENT-MISSING` |
| 16 | Missing onboarding | `test_16_missing_onboarding` | `E-ONBOARDING` |
| 17 | Malformed JSON | `test_17_malformed_json` | `ValueError` `E-JSON-INVALID` |
| 18 | Invalid UTF-8 | `test_18_invalid_utf8` | `ValueError` `E-ENCODING-INVALID` |
| 19 | Missing state file | `test_19_missing_state_file` | `ValueError` `E-FILE-NOT-FOUND` |
| 20 | Authorization inferred from passing topology | `test_20_no_authorization_from_passing_topology` | `E-AUTHORIZATION-STATE`; both authorizations NO even when readiness YES |

## CLI safe-input behaviour

| Input | Exit code | Stable code | Traceback on stderr |
|---|---|---|---|
| `state/current_assignment_state.json` | 1 | 6 × `E-APPOINTMENT-MISSING`, `E-TOPOLOGY-UNAPPROVED` | none |
| `tests/fixtures/valid_four_person.json` | 0 | none; readiness YES | none |
| `tests/fixtures/malformed.json` | 2 | `E-JSON-INVALID` | none |
| `tests/fixtures/invalid_utf8.bin` | 2 | `E-ENCODING-INVALID` | none |
| `tests/fixtures/duplicate_json_key.json` | 2 | `E-DUPLICATE-JSON-KEY` | none |
| `tests/fixtures/does_not_exist.json` | 2 | `E-FILE-NOT-FOUND` | none |
| `tests/fixtures/recruitment_inferred.json` | 1 | `E-AUTHORIZATION-STATE` + `E-SCHEMA` | none |

Machine-readable output was verified with `--json-only`: valid JSON, `stage_b_role_ready=true`,
`blocking_error_count=0`, and both authorization flags `false`.

## Determinism

Two runs of the current-state CLI with different working directories produced byte-identical
stdout and stderr and identical exit codes. All engine output is sorted by severity, code,
dimension, role, candidate and message; dimension keys are sorted; JSON uses `sort_keys=True`.

## Full JSON Schema validation

`jsonschema` was found available locally (no install, no network) and is used as the
primary structural validator with `Draft202012Validator` plus `check_schema`. The schema
is valid and all synthetic fixtures pass except the intentionally tampered
`recruitment_inferred.json`, which is rejected. The documented subset fallback remains
for environments without `jsonschema`.
