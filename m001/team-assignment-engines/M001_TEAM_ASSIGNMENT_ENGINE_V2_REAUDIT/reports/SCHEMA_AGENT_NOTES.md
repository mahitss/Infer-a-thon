# M001-TEAM-005 — Independent JSON Schema Conformance Audit (V2)

Auditor: INDEPENDENT schema subagent. Date: 2026-11-27.
Workspace: `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT`
Machine-readable companion: `schema/schema_results.json`.

Nothing in V1, the prior audit, V2, or the git repo was written. Only the two declared
output files were written. All facts below were obtained by **executing** Python 3.13.5
with the already-installed `jsonschema` 4.26.0. No installs, no network.

---

## 0. Method / exact commands

All harness code was fed to the interpreter via stdin (no helper files created):

```powershell
$code = @'
<python harness>
'@
$code | python -
```

Key one-liners actually run (paths are read-only V2 reads):

```powershell
python -c "import sys, importlib.metadata as m; print('python', sys.version); print('jsonschema version', m.version('jsonschema'))"
```

```python
schema = json.loads(Path(r"C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2\schemas\team_assignment.schema.json").read_text(encoding="utf-8"))
cls = jsonschema.validators.validator_for(schema); cls.check_schema(schema)
spec = importlib.util.spec_from_file_location("v2validator", V2 / "engine" / "validator.py")
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
```
`importlib.util.spec_from_file_location` was used instead of importing from V2's `sys.path`
so no file was modified and no import side effects were triggered.

Source files read:
- `...V2\schemas\team_assignment.schema.json` (140 lines)
- `...V2\engine\validator.py` (480 lines)
- `...V2\policy\role_constraints.json` (27 lines) — read to drive engine-level probes.

---

## 1. Environment, validator selection, schema validity

Exact output:

```
PYTHON 3.13.5
JSONSCHEMA_VERSION 4.26.0
SCHEMA_DRAFT https://json-schema.org/draft/2020-12/schema
SCHEMA_ID m001-team-assignment-state-v2
VALIDATOR_CLASS Draft202012Validator jsonschema.validators
VALIDATOR_META_SCHEMA https://json-schema.org/draft/2020-12/schema
CHECK_SCHEMA PASS
HAS_FORMAT_CHECKER_DEFAULT <FormatChecker checkers=['date', 'email', 'idn-email', 'idn-hostname', 'ipv4', 'ipv6', 'json-pointer', 'regex', 'relative-json-pointer', 'uuid']>
```

- Version was obtained with `importlib.metadata.version("jsonschema")`, not from text files.
- `validator_for(schema)` selects `jsonschema.validators.Draft202012Validator` because the
  schema declares `$schema: https://json-schema.org/draft/2020-12/schema` (schema L2).
- `Draft202012Validator.check_schema(schema)` **passes**: the schema is meta-schema valid.
- Important: `check_schema` validates *schema shape*, not `$ref` resolvability. A schema with
  `#/$defs/DOES_NOT_EXIST` still passes `check_schema` (verified below).
- `validator_for(...)` keyword set includes `$dynamicRef, $ref, additionalProperties, allOf,
  anyOf, const, contains, dependentRequired, dependentSchemas, enum, exclusiveMaximum,
  exclusiveMinimum, format, if, items, maxItems, maxLength, maxProperties, maximum, minItems,
  minLength, minProperties, minimum, multipleOf, not, oneOf, pattern, patternProperties,
  prefixItems, properties, propertyNames, required, type, unevaluatedItems,
  unevaluatedProperties, uniqueItems`. The shipped schema uses only a small subset.

Schema `$id` is the relative URI `m001-team-assignment-state-v2` (L3), not an absolute URI.
It caused no failure here because all refs are local fragments, but it would be fragile if
external `$ref`s were ever added.

---

## 2. What the schema actually declares (independent keyword scan)

A recursive scan of every dict key in the schema produced:

```
KEYWORD_COUNTS {"$defs": 1, "$id": 1, "$ref": 10, "$schema": 1, "additionalProperties": 20,
                "enum": 9, "items": 3, "properties": 18, "required": 9, "type": 74, ...}
KW format 0
KW pattern 0
KW patternProperties 0
KW if 0
KW then 0
KW else 0
KW allOf 0
KW anyOf 0
KW oneOf 0
KW not 0
KW dependentSchemas 0
KW unevaluatedProperties 0
KW uniqueItems 0
KW minItems 0
KW maxItems 0
KW minimum 0
KW maximum 0
KW const 0
KW propertyNames 0
KW contains 0
```

### Required and additionalProperties
`ROOT_REQUIRED = ["schema_version","governance","topology","candidates","evidence","roles",
"appointments","combination_approvals"]` (schema L7). `ROOT_ADDITIONAL_PROPERTIES = false`
(L6). All five `$defs` declare `additionalProperties: false`: `candidate`, `evidence`,
`roleRecord`, `appointment`, `combinationApproval` (L47, L56, L70, L118, L127). The nine
nested objects inside `roleRecord` (`recognition`, `acceptance`, `approval`, `formal`,
`availability`, `conflict_disclosure`, `confidentiality`, `onboarding`, `escalation`,
L76–L114) also declare `additionalProperties: false`. No `$def` lacks the key.
The two map-like fields `candidates` and `evidence` use
`"additionalProperties": {"$ref": ...}` (L28–29).

### Enums (9 declarations)
`schema_version` ["2.0"] L9; `governance.m001_status` ["OPEN"] L14;
`m002_status` ["UNAUTHORIZED"] L15; `recruitment` ["UNAUTHORIZED"] L16;
`field_validation` ["NOT_STARTED"] L17; `topology.status` ["PROPOSED","APPROVED"] L24;
`topology.model` ["FOUR_PERSON","FIVE_PERSON","SIX_PERSON","OTHER"] L25;
`roleRecord.state` 7 states L73; `combinationApproval.outcome` ["APPROVED","REJECTED"] L132.

### Local $refs (10 declarations)
All are local JSON Pointers: `#/$defs/candidate` (L28), `#/$defs/evidence` (L29), six copies
of `#/$defs/roleRecord` (L34–39), `#/$defs/appointment` (L42), `#/$defs/combinationApproval`
(L43). Local `$ref` resolution was exercised by every corpus case containing roles/evidence/
appointments (e.g. C01, C08, C15, C16) — both validators resolved them identically.

### items (3 declarations)
`appointments` L42, `combination_approvals` L43, `combinationApproval.roles` L131.
No `uniqueItems`, `minItems`, or `maxItems` anywhere: duplicate appointments and duplicate
role strings are **schema-legal** (case C12).

### Conditionals and format
**No** `if`/`then`/`else`, `allOf`, `anyOf`, `oneOf`, `not`, `const`, `pattern`,
`patternProperties`, `unevaluatedProperties` are present. **No `format` keyword is declared
anywhere in the schema.** The schema therefore performs **zero** lexical validation beyond
`type` and `enum`.

---

## 3. CRITICAL: timestamps and `content_hash` are NOT validated by JSON Schema

Timestamp fields in the schema:
- `$defs/evidence.timestamp` L64 — `{"type": ["string","null"]}`
- `roleRecord.acceptance.candidate_accepted_at` L89 — `["string","null"]`
- `roleRecord.approval.product_owner_approved_at` L99 — `["string","null"]`
- `roleRecord.formal.formal_appointed_at` L107 — `["string","null"]`
- `combinationApproval.decision_timestamp` L136 — `["string","null"]`
- `roleRecord.recognition.decision_date` L79 — `["string","null"]`

None has `format`, `pattern`, or any other constraint. Case C10 (naive timestamp
`"2026-01-01T00:00:00"`) and case C09 (hash `"not-a-64-hex-hash"`) are **accepted by both
validators**:

```
C09_bad_hash_format | subset=True full=True | GAP=False
   subset_errors= []
   full_errors= []
C10_naive_timestamp | subset=True full=True | GAP=False
   subset_errors= []
   full_errors= []
```

Demonstration that a `format` declaration alone would not fix this, and that even supplying a
`FormatChecker` would not help for `date-time` in this environment:

```
FORMAT_CHECKER_KEYS ["date", "email", "idn-email", "idn-hostname", "ipv4", "ipv6", "json-pointer", "regex", "relative-json-pointer", "time", "uuid"]
declared format=date-time, value='not-a-timestamp-at-all'
  full_default_errors= []
  full_with_FormatChecker= []
  subset= []
declared format=date (checker available), value='not-a-timestamp-at-all'
  full_default_errors= []
  full_with_FormatChecker= ["'not-a-timestamp-at-all' is not a 'date'"]
  subset= []
ORIGINAL_SCHEMA full_with_FormatChecker naive_timestamp= []
```

Interpretation:
1. The shipped schema declares no `format`, so no checker can act.
2. `structural_schema_errors()` (validator.py L185–188) constructs `cls(schema)` **without**
   `format_checker=`, so even a declared format would be ignored by the engine.
3. Additionally, `date-time` is absent from `FormatChecker.checkers` (the optional
   `rfc3339-validator` dependency is not installed), so declaring `format: date-time` would
   still not validate in this environment. `format: date` would work if a checker were passed.
4. `content_hash` (schema L62) has **no** `pattern` constraint: `{"type": ["string","null"]}`
   only. The 64-hex rule lives solely in engine code at validator.py L242–245
   (`re.fullmatch(r'[0-9a-fA-F]{64}', str(h))`).

---

## 4. Corpus parity: subset `validate_schema()` vs full jsonschema

Harness ran, for each instance, `v.validate_schema(inst, schema)` and
`jsonschema.validators.validator_for(schema)(schema).iter_errors(inst)` with default
format checker (matching engine construction). 18 instances (≥12 required): valid, missing
required (root + nested), extra property (root + nested defs), wrong type, enum mismatch,
nested wrong type, bad ref, bad hash, naive timestamp, whitespace, duplicate roles,
numeric-vs-string coercion, items type, boolean-vs-number coercion.

**Result: 0 accept/reject parity gaps on the shipped schema.** Every case both validators
accept or both reject. Diagnostics differ (subset emits short custom strings; full emits
JSON-Schema messages and can emit two errors for one enum/type field), but that is not an
accept/reject gap.

```
C01_valid_baseline | subset=True full=True | GAP=False
   subset_errors= [] ; full_errors= []
C02_missing_required_root | subset=False full=False | GAP=False
   subset_errors= ["$: missing roles"]
   full_errors= ["$: 'roles' is a required property"]
C03_extra_property_root | subset=False full=False | GAP=False
   subset_errors= ["$: unexpected surprise"]
   full_errors= ["$: Additional properties are not allowed ('surprise' was unexpected)"]
C04_wrong_type_root | subset=False full=False | GAP=False
   subset_errors= ["$.topology: type mismatch"]
   full_errors= ["topology: 'APPROVED' is not of type 'object'"]
C05_enum_mismatch | subset=False full=False | GAP=False
   subset_errors= ["$.schema_version: enum mismatch"]
   full_errors= ["schema_version: '1.0' is not one of ['2.0']"]
C06_nested_wrong_type | subset=False full=False | GAP=False
   subset_errors= ["$.roles.RESEARCH_OWNER.state: type mismatch"]
   full_errors= ["roles/RESEARCH_OWNER/state: 123 is not of type 'string'",
                 "roles/RESEARCH_OWNER/state: 123 is not one of ['UNASSIGNED', 'PROPOSED', 'ACCEPTED_IN_CONVERSATION', 'CANDIDATE_ACCEPTED', 'REJECTED', 'DEFERRED', 'FORMALLY_APPOINTED']"]
C07_nested_additional_property | subset=False full=False | GAP=False
   subset_errors= ["$.roles.RESEARCH_OWNER.availability: unexpected extra"]
   full_errors= ["roles/RESEARCH_OWNER/availability: Additional properties are not allowed ('extra' was unexpected)"]
C08_evidence_extra_property | subset=False full=False | GAP=False
   subset_errors= ["$.evidence.e1: unexpected foo"]
   full_errors= ["evidence/e1: Additional properties are not allowed ('foo' was unexpected)"]
C09_bad_hash_format | subset=True full=True | GAP=False
   subset_errors= [] ; full_errors= []
C10_naive_timestamp | subset=True full=True | GAP=False
   subset_errors= [] ; full_errors= []
C11_whitespace | subset=True full=True | GAP=False   (candidate_ref = "   ")
   subset_errors= [] ; full_errors= []
C12_duplicate_roles | subset=True full=True | GAP=False   (two identical appointments)
   subset_errors= [] ; full_errors= []
C13_numeric_vs_string | subset=False full=False | GAP=False   (schema_version = 2.0)
   subset_errors= ["$.schema_version: type mismatch"]
   full_errors= ["schema_version: 2.0 is not of type 'string'",
                 "schema_version: 2.0 is not one of ['2.0']"]
C14_numeric_in_boolean | subset=False full=False | GAP=False   (candidates.c1.active = 1)
   subset_errors= ["$.candidates.c1.active: type mismatch"]
   full_errors= ["candidates/c1/active: 1 is not of type 'boolean'"]
C15_missing_required_nested | subset=False full=False | GAP=False
   subset_errors= ["$.evidence.e1: missing evidence_type", ... 7 total]
   full_errors= ["evidence/e1: 'evidence_type' is a required property", ... 7 total]
C16_items_wrong_type | subset=False full=False | GAP=False
   subset_errors= ["$.appointments[0]: type mismatch"]
   full_errors= ["appointments/0: 'not-an-object' is not of type 'object'"]
C17_role_enum_number | subset=False full=False | GAP=False
   subset_errors= ["$.combination_approvals[0].outcome: type mismatch"]
   full_errors= ["combination_approvals/0/outcome: 1 is not of type 'string'",
                 "combination_approvals/0/outcome: 1 is not one of ['APPROVED', 'REJECTED']"]
C18_bad_ref_schema | subset=False full=False | GAP=False on accept/reject, but full RAISED
   subset_errors= ["$.topology: unresolved $ref #/$defs/DOES_NOT_EXIST"]
   full_exception= "_WrappedReferencingError: PointerToNowhere: '/$defs/DOES_NOT_EXIST' does not exist within {...}"
```

C18 is a real **behavioral divergence in error handling**, not an accept/reject gap: with a
meta-schema-valid but unresolvable `$ref` (`check_schema` PASSES), the subset returns a clean
error string while full jsonschema raises `_WrappedReferencingError` (wrapping
`referencing.exceptions.PointerToNowhere`). `structural_schema_errors()` catches only
`jsonschema.exceptions.SchemaError` at validator.py L192, so this exception propagates out of
`validate_state()`. Verified:

```
check_schema(badref)=PASS
structural_schema_errors(badref) RAISED _WrappedReferencingError PointerToNowhere: '/$defs/DOES_NOT_EXIST' does not exist within {...}
subset(badref)= ['$.topology: unresolved $ref #/$defs/DOES_NOT_EXIST']
```

`jsonschema.exceptions.RefResolutionError` is deprecated since 4.18; the concrete exception
here is `_WrappedReferencingError`, which is not a `SchemaError`.

---

## 5. Latent parity gaps in the subset fallback (synthetic schemas)

These keywords are **not** in the shipped schema, so they do not affect the 18-case corpus,
but they prove the documented subset is unsound if relied upon or if the schema grows.

```
LATENT_pattern | subset_accepts= True | full_accepts= False | GAP=True
  subset= []  full= ["'B' does not match '^A'"]
LATENT_enum_bool_vs_int | subset_accepts= True | full_accepts= False | GAP=True
  subset= []  full= ["True is not one of [1]"]        # Python True == 1
LATENT_integer_float | subset_accepts= False | full_accepts= True | GAP=True
  subset= ["$: type mismatch"]  full= []               # 1.0 is a JSON Schema integer
LATENT_if_then_triggered | subset_accepts= True | full_accepts= False | GAP=True
  subset= []  full= ["'y' is a required property"]
LATENT_allOf | subset_accepts= True | full_accepts= False | GAP=True
  subset= []  full= ["'y' is a required property"]
LATENT_uniqueItems | subset_accepts= True | full_accepts= False | GAP=True
  subset= []  full= ["[1, 1] has non-unique elements"]
LATENT_minLength | subset_accepts= True | full_accepts= False | GAP=True
  subset= []  full= ["'a' is too short"]
LATENT_boolean_schema_False | subset RAISED TypeError: argument of type 'bool' is not iterable
  full= ["False schema does not allow 1"]
LATENT_ref_pointer_escape (schema def key "a/b", $ref "#/$defs/a~1b", instance {"x": 1})
  subset= ['$.x: unresolved $ref #/$defs/a~1b']  full= []   # subset does not unescape ~1
```

The subset's `resolve()` (validator.py L116–124) splits the fragment on `/` without JSON
Pointer unescaping; `type_ok()` (L126–140) treats `1.0` as non-integer; `enum` uses Python
`in` (L153) so `True` equals `1`; `walk()` (L142–172) supports only `$ref`, `type`, `enum`,
`required`, `properties`, `additionalProperties`, `items` and crashes on boolean subschemas.

---

## 6. Engine wiring and determinism

Instrumentation (patched `jsonschema.validators.validator_for` and `v.validate_schema`):

```
_JSONSCHEMA_AVAILABLE= True validator_for_calls= 2315 fallback_calls= 0 errors= []
```
The 2315 count includes internal `validator_for` calls made recursively by `check_schema`;
the refined counter for the *exact* schema object is:

```
exact validator_for(schema) calls= 1 fallback calls= 0 errors= []
```

Confirmed: `structural_schema_errors()` (validator.py L176–194) uses the full validator when
`jsonschema` is importable — `validator_for(schema)` at L185, `check_schema` at L186, sorted
`iter_errors` at L187–191 — and only reaches the subset at L194 when `_JSONSCHEMA_AVAILABLE`
is False. Forcing that flag False produced output identical to `validate_schema()`:

```
forced fallback output= [] matches validate_schema= True
```

Determinism (20 repeated calls on an instance with 8 schema errors — extra root property plus
an incomplete evidence record):

```
structural_schema_errors 20 runs identical= True count= 8
first= ["$: Additional properties are not allowed ('surprise' was unexpected)",
        "evidence/e1: 'content_hash' is a required property",
        "evidence/e1: 'evidence_type' is a required property",
        "evidence/e1: 'recording_authority' is a required property",
        "evidence/e1: 'source_ref' is a required property",
        "evidence/e1: 'subject' is a required property",
        "evidence/e1: 'timestamp' is a required property",
        "evidence/e1: 'verification_status' is a required property"]
validate_schema 20 runs identical= True
```

Sort key is `(absolute_path parts, message)` (L189); dict iteration order is stable for the
same input object, so both paths are deterministic. No `format_checker` is passed (L188), and
`check_schema` is re-run on every call (per-instance overhead, not a correctness issue here).

---

## 7. Business rules enforced only in engine code (not in the schema)

Executed `validate_state(inst, policy, schema)` against schema-valid instances:

```
E00_valid_baseline_schema_valid stage_b= False errors= 6 codes= 6x E-APPOINTMENT-MISSING
E01_dangling_bad_hash stage_b= False errors= 6 codes= 6x E-APPOINTMENT-MISSING
E02_referenced_bad_hash stage_b= False errors= 7 codes= 6x E-APPOINTMENT-MISSING + E-EVIDENCE-HASH
E03_naive_timestamp_dangling stage_b= False errors= 7 codes= 6x E-APPOINTMENT-MISSING + E-TIMESTAMP-INVALID
E04_whitespace_candidate_ref stage_b= False errors= 7 codes= 6x E-APPOINTMENT-MISSING + E-CANDIDATE-DUPLICATE ("Candidate key/reference mismatch")
E05_duplicate_appointments stage_b= False errors= 9 codes= 6x E-APPOINTMENT-MISSING + E-CANDIDATE-DUPLICATE("Duplicate appointment") + 2x E-UNAPPROVED-APPOINTMENT
E06_evidence_id_key_vs_field_mismatch stage_b= False errors= 6 codes= 6x E-APPOINTMENT-MISSING
```

Notable: a schema-valid state is still rejected by the engine (E00), and a *dangling* evidence
record with a bad hash is **not** flagged at all (E01) — hash checking at L242–245 only runs
through `evidence_check()`, i.e. only for evidence ids referenced by a role/approval
(L341–346, L372, L416). Naive timestamps in dangling evidence are caught by the evidence loop
(L309–310). Evidence dict key vs `evidence_id` field mismatch (E06) is neither schema- nor
engine-checked.

Rules enforced only in engine code (with source lines):
- authorization posture `recruitment == UNAUTHORIZED`, `field_validation == NOT_STARTED` (L293–294); recruitment/field authorization always returned False (L453).
- topology must be APPROVED for Stage B (L297–298).
- evidence `evidence_type` / `verification_status` membership in policy, timestamp validity (L305–310); evidence type/status/subject checks via `evidence_check` (L227–241).
- timezone-aware timestamp parsing and ordering `accepted <= approved <= appointed`, and required decision timestamps (L197–210, L355–363, L418–419).
- content hash 64-hex regex (L242–245) — referenced evidence only.
- candidate registry key == `candidate_ref`, duplicate identity, `active is True` (L249–263).
- role names must be in policy `roles`; appointment state must be in policy and FORMALLY_APPOINTED (L319–329).
- acceptance evidence, PO approval + formal flag + basis, formal record, availability, conflict disclosure, confidentiality, onboarding, escalation contact (L336–375).
- appointment duplicates, candidate/role existence, formal-role coverage (L377–400).
- combination approval outcome/PO approval/rationale/evidence/timestamp (L402–419); exact combination approval matching, hard incompatibilities, discouraged and conditional combinations (L421–448).
- Stage B computation over policy dimensions (L450–453).
- Duplicate JSON object keys rejected by the loader (L74–97) — JSON Schema itself cannot see duplicate keys after parsing.

Schema-enforced only: types, the enums listed in §2, required fields, additionalProperties
false, local `$ref`s, and `items` object shapes.

---

## 8. Limitations of both validators

**Full jsonschema 4.26.0 / Draft202012Validator as wired by the engine**
1. No `format_checker` is supplied (validator.py L188), and the shipped schema declares no `format` anyway → zero lexical validation of timestamps.
2. `date-time` format checker is not installed (`FormatChecker.checkers` lacks it), so even adding `format: date-time` would not validate here.
3. `check_schema` does not verify `$ref` resolvability; the only caught exception is `SchemaError` (L192), so unresolvable refs crash with `_WrappedReferencingError`.
4. No `pattern` for hashes, no `uniqueItems` for appointment arrays, no `minItems`/`maxItems`, no conditionals — these are design omissions of the schema, not validator bugs.
5. Enum/type equality is spec-correct; it does not coerce numeric strings or numbers to strings.
6. Full validator does not enforce cross-field/business semantics (evidence references, authorization, chronology, combinations) — by design.

**Subset `validate_schema()` (validator.py L108–173)**
1. Supports only `$ref`, `type`, `required`, `properties`, `additionalProperties`, `enum`, `items`; silently ignores all other keywords (latent gaps proven in §5).
2. `resolve()` is a naive `#/` string split: no JSON Pointer unescaping (`~1`, `~0`), no external refs, no `$id`-relative resolution.
3. `type_ok()` rejects `1.0` for `integer`; boolean is special-cased correctly for `boolean`.
4. `enum` uses Python membership: `True == 1`, `1 == 1.0` (JSON Schema distinguishes these).
5. Crashes (`TypeError`) on boolean subschemas (`true`/`false`).
6. `$ref` siblings are ignored (same as 2020-12), but an unresolvable ref is reported as a plain string error rather than raising.
7. Errors are strings with a different path notation (`$.a.b` vs `a/b`) and one error per failed keyword instead of full detail; not an accept/reject gap but not interchangeable diagnostics.
8. It does not check `format` and is never used while jsonschema is importable.

---

## 9. Defect register (facts + severity suggestions)

| ID | Finding | Severity suggestion | Evidence / source |
|----|---------|---------------------|-------------------|
| D1 | No timestamp `format`/`pattern` on any of 6 timestamp fields; engine does not pass a `FormatChecker`; `date-time` checker absent even if declared. Naive timestamps pass both schema validators. | MEDIUM | §3; schema L64, L79, L89, L99, L107, L136; validator.py L185–188 |
| D2 | `content_hash` has no `pattern` constraint; only engine regex enforces 64-hex, and only for *referenced* evidence. Dangling bad-hash evidence passes schema and engine. | MEDIUM | §3, §7 E01/E02; schema L62; validator.py L242–245 |
| D3 | `structural_schema_errors()` catches only `SchemaError`; an unresolvable local `$ref` (which passes `check_schema`) raises `_WrappedReferencingError` out of `validate_state()`. | MEDIUM | §4 C18; validator.py L183–194, especially L192 |
| D4 | Subset fallback silently ignores `pattern`, `if/then`, `allOf`, `uniqueItems`, `minLength`, `const`, boolean schemas; latent accept/reject gaps and a crash proven by execution. | MEDIUM (latent; only if jsonschema absent or schema extended) | §5; validator.py L108–173 |
| D5 | Evidence dict key vs `evidence_id` field consistency unchecked anywhere; duplicate JSON keys handled only in loader. | LOW | §7 E06; validator.py L74–97, L300–310 |
| D6 | Schema `$id` is a relative URI; acceptable for current local-only refs, fragile for future external refs. | LOW | schema L3 |
| D7 | No `uniqueItems` on `appointments` / `combination_approvals` arrays and no `minItems`; duplicates are schema-legal (engine catches some, combination approvals silently overwrite by key). | LOW | schema L42–43, L131; §4 C12; validator.py L408–409 |

No accept/reject parity gap was found between the two validators on the shipped schema across
the 18-case corpus. The gaps found are at the schema-semantics layer (D1, D2, D6, D7), the
schema-error-handling layer (D3), and the fallback layer (D4, D5).
