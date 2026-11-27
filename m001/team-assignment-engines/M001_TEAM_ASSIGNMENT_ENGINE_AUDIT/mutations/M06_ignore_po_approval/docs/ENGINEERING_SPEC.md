# Engineering Specification

**Governance:** M001 OPEN; M002 UNAUTHORIZED; recruitment UNAUTHORIZED; field validation NOT STARTED; Research Owner ACCEPTED IN CONVERSATION (Product Owner, 2026-11-26; no legal name, signature or official register update); other five roles UNASSIGNED. This is diagnostic engineering tooling, not an appointment, implementation or authorization.

## Inputs

The validator accepts an assignment state JSON containing governance status, topology, six role records and zero or more assignment records. Role states are not interchangeable: `UNASSIGNED`, `PROPOSED`, `ACCEPTED_IN_CONVERSATION`, `CANDIDATE_ACCEPTED`, `FORMALLY_APPOINTED`, `REJECTED`, `DEFERRED`.

## Policy

`policy/role_constraints.json` is the source of role identifiers, state requirements and combination classifications.

Hard incompatibilities (blocking): Moderator+Analyst; Moderator+Data Custodian.
Discouraged combinations (warnings unless resolved): Research Owner+Moderator; Data Custodian+Analyst.
Conditional combinations (blocking unless evidence present): Moderator+Note-taker requires `evidence_separation_documented`; Research Owner+Continue/Stop requires `explicit_additional_appointment`.

## Validation outputs

Stable error and warning identifiers are emitted with severity, role, person and message. The CLI writes a human-readable report and a machine-readable JSON result. Deterministic ordering is by severity, code, role, person and message. No timestamps appear in generated output.

## Standard-library schema validation

`validate_schema()` supports type (including null unions), required, properties, additionalProperties, enum, items and local `$ref`. This subset is sufficient for this state schema and is documented as a limitation relative to a full JSON Schema implementation.

