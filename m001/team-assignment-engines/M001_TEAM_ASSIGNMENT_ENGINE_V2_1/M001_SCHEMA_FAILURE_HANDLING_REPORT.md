# M001 V2.1 — Schema Failure Handling Report (N-15)

**Mission:** M001-TEAM-006  
**Source:** independent register finding N-15 (schema errors non-fatal → `AttributeError` tracebacks)  
**Implementation:** `engine/validator.py` `structural_schema_errors()` and `validate_state()`

## Root cause in V2

V2 collected `E-SCHEMA` issues at lines 288–289 but continued execution. Schema-invalid values
then reached unguarded `.get()` calls (`governance: null` → line 293, `topology: "x"` → line 297,
`acceptance: "yes"` → line 339), producing `AttributeError` tracebacks and exit 1 with empty
stdout. V2 also raised `_WrappedReferencingError` for an unresolvable `$ref`.

## V2.1 controls

1. `structural_schema_errors()` catches a narrow tuple of schema/reference exception classes
   (SchemaError, `referencing` exceptions, deprecated `RefResolutionError`,
   `_WrappedReferencingError`) plus `TypeError/AttributeError/ValueError/KeyError` arising from
   malformed schema or instance. Messages are prefixed and bounded: `E-SCHEMA`,
   `E-SCHEMA-REFERENCE`, `E-SCHEMA-INVALID`; exception text is truncated to 180 characters.
2. `validate_state()` returns immediately on any schema error with a
   `ValidationResult` whose dimensions are all `FAIL`, whose issues contain the schema
   diagnostics, and whose readiness is `False`. No downstream business validation runs.
3. Non-dict state produces `E-SCHEMA-INVALID` with the same controlled shape.
4. Unexpected engine programming errors are not broadly caught; only input/schema-condition
   exceptions are converted.

## Verified cases

| Case | Command / test | Result |
|---|---|---|
| `governance: null` | copied V2 CLI case c06g, test 20 | bounded `E-SCHEMA`, all dimensions FAIL, no traceback |
| `topology: "APPROVED"` (string) | copied V2 CLI case c06h | controlled, no traceback |
| `acceptance: "yes"` | copied V2 CLI case c06i | controlled, no traceback |
| Invalid schema structure (`invalid_schema.json`) | test 18 | `E-SCHEMA-REFERENCE`, no exception |
| Unresolvable `$ref` | test 19 | `E-SCHEMA-REFERENCE`, message <250 chars, no exception |
| Assignment blocked after schema failure | test 20 | `E-SCHEMA` only; no `E-APPOINTMENT-MISSING` downstream |
| CLI stability | test 21; `reports/logs/cli_schema_failure.txt` | exit 1, empty stderr, `Stage B role readiness: NO` |
| Schema-fallback subset | `structural_schema_errors()` subset branch | same `E-SCHEMA*` prefixes, no exception |

Machine-readable output preserves all diagnostics via `ValidationResult.to_dict()` (sorted
issues, severity, code, dimension, role, candidate, message).

## Mutation proof

`M4_schema_terminal_return_removed` replaces the early return with `pass`; the canary fails
(B06) with exit 1. All four remediation mutations detected, 0 survived.

## Note on adapted expectations

Two inherited V2 tests expected `E-AUTHORIZATION-STATE` for a governance enum tamper, and two new
tests expected business-level codes for non-string basis and missing rationale. Under terminal
schema handling these produce `E-SCHEMA` instead. The assertions were widened to accept the
stable schema-level block; readiness NO and zero authorization grants remain mandatory. This is
a semantic consequence of the N-15 fix, not a downgrade.
