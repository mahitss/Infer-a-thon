# M001 Team Assignment Engine

**Governance:** M001 OPEN; M002 UNAUTHORIZED; recruitment UNAUTHORIZED; field validation NOT STARTED; Research Owner ACCEPTED IN CONVERSATION (Product Owner, 2026-11-26; no legal name, signature or official register update); other five roles UNASSIGNED. This is diagnostic engineering tooling, not an appointment, implementation or authorization.

Executable Python standard-library tooling that validates human research-team assignments against machine-readable role policy.

## Contents

- `schemas/team_assignment.schema.json` — structural state schema.
- `policy/role_constraints.json` — six roles, appointment states and combination policy.
- `state/current_assignment_state.json` — current evidence-only state.
- `engine/validator.py` — deterministic validator and standard-library schema subset checker.
- `cli/validate.py` — CLI producing deterministic human and JSON output.
- `cli/validate_schema.py` — structural schema validation CLI.
- `tests/` — unit and integration tests.
- `fixtures/` — synthetic staffing models; never actual appointment records.
- `reports/` — executed validation evidence.
- `docs/` — engineering specification and validation report.

## Primary command

`python cli/validate.py --state state/current_assignment_state.json`

Exit status is nonzero when blocking errors exist. Current state correctly exits 1 because five appointments remain unassigned; `fixtures/valid_four_person.json` exits 0.

