# Validation Report

**Governance:** M001 OPEN; M002 UNAUTHORIZED; recruitment UNAUTHORIZED; field validation NOT STARTED; Research Owner ACCEPTED IN CONVERSATION (Product Owner, 2026-11-26; no legal name, signature or official register update); other five roles UNASSIGNED. This is diagnostic engineering tooling, not an appointment, implementation or authorization.

## Executed evidence

| Check | Result | Report |
|---|---|---|
| Schema validation, current state + 15 fixtures | PASS; exit 0 | `reports/schema_validation.txt` |
| Unit tests | 16 tests, OK; exit 0 | `reports/unit_tests.txt` |
| Integration tests | 4 tests, OK; exit 0 | `reports/integration_tests.txt` |
| CLI current assignment state | Blocking errors: 5; exit 1 | `reports/cli_current_state.txt` |
| CLI valid four-person fixture | Valid YES; exit 0 | `reports/cli_valid_four.txt` |
| Determinism across two working directories | stdout/stderr identical; exit 1 expected | `reports/determinism.txt` |

## Current state result

Research Owner is `ACCEPTED_IN_CONVERSATION`; Moderator, Note-taker, Data Custodian, Analyst and Continue/Stop Owner are `UNASSIGNED`. The validator reports five `E-APPOINTMENT-MISSING` errors, one `W-TOPOLOGY-PROPOSED` warning and one `I-RO-NOT-FORMAL` info. It does not promote the Research Owner to formal appointment.

## High-severity invariants demonstrated

- Hard incompatibilities produce blocking errors.
- Discouraged combinations produce warnings unless resolved.
- Conditional combinations produce blocking errors without required evidence.
- Missing acceptance, approval, availability, conflict disclosure, confidentiality, escalation and onboarding produce distinct blocking errors.
- Duplicate and unknown roles produce blocking errors.
- Valid four-, five- and six-person models produce no blocking errors.
- Invalid three-person model produces a hard incompatibility error.

## Limitations

Schema validation is a documented standard-library subset. No actual application parser, UI or field research was executed. Unittest timing lines vary; determinism is asserted on CLI output only. Synthetic fixtures are not appointment records.

