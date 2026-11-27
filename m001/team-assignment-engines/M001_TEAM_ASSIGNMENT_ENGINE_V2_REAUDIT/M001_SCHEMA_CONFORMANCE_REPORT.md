# M001 Independent JSON Schema Conformance Report

**Mission:** M001-TEAM-005  
**Date:** 2026-11-27  
**Primary evidence:** `reports/SCHEMA_AGENT_NOTES.md`, `schema/schema_results.json` (independently executed by the audit's schema stream; no reliance on V2's README claims).

## Environment and wiring

- Python 3.13.5; `jsonschema` **4.26.0** obtained via `importlib.metadata.version` (not from V2 documentation).
- `jsonschema.validators.validator_for(schema)` selects **Draft202012Validator** because the schema declares `https://json-schema.org/draft/2020-12/schema`. `check_schema` **passes**.
- V2's `structural_schema_errors()` (`validator.py:176-194`) calls the full validator once per validation and does **not** fall back while `jsonschema` is importable. Forced-fallback output matched `validate_schema()` exactly; both paths were deterministic over 20 repeated runs.
- No `format_checker` is passed at `validator.py:188`.

## What the schema actually enforces

Root `required`: `schema_version, governance, topology, candidates, evidence, roles, appointments, combination_approvals`. Root `additionalProperties: false`; all five `$defs` and all nine nested `roleRecord` objects also use `additionalProperties: false`. Nine enums, ten local `$ref`s and three `items` declarations were confirmed.

Keyword scan: `format=0`, `pattern=0`, `if/then/else=0`, `allOf=0`, `anyOf=0`, `oneOf=0`, `not=0`, `const=0`, `uniqueItems=0`, `minItems=0`, `maxItems=0`. The schema performs type/enum/required/additionalProperties checks only.

## Timestamps and hashes are NOT validated by JSON Schema

| Field | Schema declaration | Actual lexical validation |
|---|---|---|
| `evidence.timestamp`, `candidate_accepted_at`, `product_owner_approved_at`, `formal_appointed_at`, `decision_timestamp`, `recognition.decision_date` | `["string","null"]` | **none** by JSON Schema; naive `"2026-01-01T00:00:00"` accepted by both validators |
| `content_hash` | `["string","null"]` | **none** by JSON Schema; 64-hex rule is engine-only at `validator.py:242-245` |

Demonstration that a format declaration alone would not help: even with `format: date-time`, default and `FormatChecker`-enabled validation both accepted `"not-a-timestamp-at-all"` because the `date-time` checker is absent from this environment. `date` checker exists but no such format is declared. The engine enforces timezone-aware timestamps separately at `validator.py:197-210`.

## Fallback parity

An 18-instance corpus (valid, missing required at root/nested, extra properties at root/nested/evidence, wrong types, enum mismatch, bad hash, naive timestamp, whitespace, duplicate roles/appointments, numeric-vs-string coercion, boolean-vs-number coercion, bad `$ref`) found **0 accept/reject parity gaps** on the shipped schema between the subset and full validator. Diagnostic strings differ, which is not an accept/reject gap.

Latent gaps in the subset were proven with synthetic schemas (not in V2's shipped schema): `pattern`, `if/then`, `allOf`, `uniqueItems`, `minLength`, boolean-vs-int `enum`, integer-vs-float `type`, JSON Pointer escaping (`~1`), and a `TypeError` crash on boolean subschemas. These matter only if `jsonschema` is absent or the schema is extended.

## Independent findings

| ID | Finding | Severity | Source |
|---|---|---|---|
| S-01 (D1) | No timestamp `format`/`pattern`; no `FormatChecker`; `date-time` checker absent. Schema cannot detect naive/invalid timestamps. | MEDIUM | schema L64, L79, L89, L99, L107, L136; `validator.py:185-188` |
| S-02 (D2) | `content_hash` has no `pattern`; engine's 64-hex regex applies only to *referenced* evidence. A dangling evidence record with a bad hash is accepted by both schema and engine. | MEDIUM | schema L62; `validator.py:242-245` |
| S-03 (D3) | An unresolvable local `$ref` passes `check_schema` but raises `_WrappedReferencingError` out of `structural_schema_errors()` because only `SchemaError` is caught. This can surface as an unhandled exception. | MEDIUM | `validator.py:183-194` |
| S-04 (D4) | Fallback subset silently ignores six keywords and can crash on boolean subschemas; latent unsoundness. | MEDIUM (latent) | `validator.py:108-173` |
| S-05 (D5) | Evidence dict key vs `evidence_id` field consistency is unchecked; duplicate JSON keys handled only in loader. | LOW | `validator.py:74-97`, `:300-310` |
| S-06 (D6) | Schema `$id` is a relative URI; fragile for future external `$ref`s. | LOW | schema L3 |
| S-07 (D7) | No `uniqueItems`/`minItems` on appointments or approvals; duplicate approval entries are schema-legal and `approval_map[key]` is last-wins. | LOW | schema L42-43, L131; `validator.py:408-409` |

## Important limitation statement

V2's claim that it "uses full Draft 2020-12 validation" is **true for structural keywords** only. It must not be read as format or timestamp validation, nor as conditional/ business-rule validation. All such rules live in engine code, where the HIGH/MEDIUM defects recorded elsewhere in this re-audit were found.
