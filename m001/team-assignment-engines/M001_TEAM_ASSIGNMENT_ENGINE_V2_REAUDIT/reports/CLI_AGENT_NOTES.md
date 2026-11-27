# M001-TEAM-005 — Independent V2 CLI / JSON-parser robustness re-audit

**Agent:** independent auditor (subagent)
**Mission:** M001-TEAM-005
**Scope:** `M001_TEAM_ASSIGNMENT_ENGINE_V2/cli/validate.py` and `M001_TEAM_ASSIGNMENT_ENGINE_V2/engine/validator.py`, exercised through the real CLI.
**Boundaries honoured:** V1, the previous audit, V2 and the git repo were **read only**. All generated inputs live in `REAUDIT/tests/cases/`. The only deliverables written are this file and `REAUDIT/tests/results/cli_robustness_results.json`.

## Environment

| Item | Value |
|---|---|
| Python | 3.13.5 |
| jsonschema | 4.26.0 (**installed** → full Draft 2020-12 validation is active, not the subset fallback) |
| CLI | `python V2/cli/validate.py --state <path>` |
| V2 root (`ROOT` in CLI) | `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2` |
| Base state used for mutations | `V2/state/current_assignment_state.json` (valid JSON, known validation failures: topology `PROPOSED`, roles not `FORMALLY_APPOINTED`) |
| Console encoding observed | `cp1252` (relevant to the surrogate finding) |
| Total cases executed | 35 (31 task cases + 4 determinism/verification repeats; plus 2 ad-hoc probes) |

Commands below use `$V2`, `$CASES` and `$CLI` as shorthand:

```
$V2    = C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2
$CASES = C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT\tests\cases
$CLI   = $V2\cli\validate.py
```

Every case was run with `cwd = $V2` unless noted. Exact argv, absolute paths, stdout hashes and stderr are in the JSON results file.

---

## Source review (read only, before testing)

1. **`cli/validate.py:38-49`** — the only error handler is `except (DuplicateKeyError, ValueError)`. `RecursionError`, `AttributeError`, `UnicodeEncodeError` and `TypeError` are *not* caught. The file docstring (line 3) claims "safe input-error handling", which the observed behaviour contradicts.
2. **`engine/validator.py:74-97`** — `load_json_strict` reads bytes, decodes UTF-8, then `json.loads(text, object_pairs_hook=no_dupes)`. Duplicate keys are rejected at **every** level. There is **no nesting-depth guard**, and `\uXXXX` surrogate escapes pass parsing.
3. **`engine/validator.py:108-194`** — full `jsonschema` validation when available. Schema errors are collected as `E-SCHEMA` issues.
4. **`engine/validator.py:288-289`** — schema errors are *recorded but not fatal*: `for err in structural_schema_errors(...): fail(...)` then execution continues. This is the root of the `AttributeError` class of crashes: a schema-invalid value flows into unguarded `.get()` calls.
5. **`engine/validator.py:217-246`** — evidence is resolved with `evidence.get(eid)` (dictionary lookup by ID). `source_ref` is only truth-tested (line 233). There is no `open()`/filesystem access anywhere in the validator.
6. **`cli/validate.py:33-36`** — a relative `--state` is resolved as `ROOT / state_path`, i.e. anchored to the V2 root rather than the caller's cwd; `source = state_path.name` keeps only the basename.
7. **`engine/validator.py:77-80`** — every `OSError` (missing file, directory, permission) is collapsed into `E-FILE-NOT-FOUND`.
8. **`cli/validate.py:57`** — `print(payload if args.json_only else text)`; the human report embeds raw field values (validator lines 456-473), while `json_result` (line 480) uses `json.dumps` with `ensure_ascii=True`.

---

## Case matrix

`exit` 0 = stage-B ready, 1 = validation failure, 2 = clean input error. "TB" = raw traceback on stderr.

| Case | Input / mutation | Command (shorthand) | exit | stdout first lines / salient line | stderr | TB |
|---|---|---|---|---|---|---|
| C00 | unmodified baseline | `python $CLI --state $CASES\control_baseline.json` | 1 | `M001 TEAM ASSIGNMENT VALIDATION V2` / `Source: control_baseline.json` / dimensions… / `Blocking errors: 7` | empty | no |
| C01 | duplicate `basis` inside `roles.RESEARCH_OWNER.approval` | `… c01_dup_nested_approval.json` | 2 | `input: FAIL`; `ERROR E-DUPLICATE-JSON-KEY [dimension=input]: E-DUPLICATE-JSON-KEY: basis` | empty | no |
| C01b | duplicate `schema_version` at root | `… c01b_dup_root_schema_version.json` | 2 | `ERROR E-DUPLICATE-JSON-KEY …: schema_version` | empty | no |
| **C02** | 5000 nested arrays (`[`×5000 + `]`×5000, 10 KB) | `… c02_deep_5000_arrays.json` | **1** | *(no stdout)* | **RecursionError traceback** | **yes** |
| **C02b** | 5000 nested objects (`{"a":`×5000, 30 KB) | `… c02b_deep_5000_objects.json` | **1** | *(no stdout)* | **RecursionError traceback** | **yes** |
| C03 | 21,004,552-byte valid JSON; 21 MB padding in `roles.RESEARCH_OWNER.recognition.evidence_text` | `… c03_large_21mb.json` | 1 | normal human report, `Blocking errors: 7`; ~3.97 s | empty | no |
| C04 | raw byte `0xFF` | `… c04_byte_ff.json` | 2 | `ERROR E-ENCODING-INVALID …: invalid UTF-8` | empty | no |
| C04b | truncated UTF-8 (`E2 82`) | `… c04b_truncated_utf8.json` | 2 | `ERROR E-ENCODING-INVALID …: invalid UTF-8` | empty | no |
| C04c | UTF-8-encoded lone surrogate (`ED A0 80`) | `… c04c_lone_surrogate_bytes.json` | 2 | `ERROR E-ENCODING-INVALID …: invalid UTF-8` | empty | no |
| **C04d** | JSON `\ud800` escape in an echoed `candidate_ref` | `… c04d_json_lone_surrogate_escape.json` | **1** | *(no stdout)* | **UnicodeEncodeError traceback** | **yes** |
| C05 | extra property at root | `… c05_extra_root.json` | 1 | `ERROR E-SCHEMA …: $: Additional properties are not allowed ('unexpected_root_field' was unexpected)` | empty | no |
| C05b | extra property at role | `… c05b_extra_role.json` | 1 | `ERROR E-SCHEMA …: roles/RESEARCH_OWNER: Additional properties are not allowed …` | empty | no |
| C05c | extra property at candidate | `… c05c_extra_candidate.json` | 1 | `ERROR E-SCHEMA … Additional properties are not allowed …` | empty | no |
| C05d | extra property at evidence | `… c05d_extra_evidence.json` | 1 | `ERROR E-SCHEMA … Additional properties are not allowed …` | empty | no |
| C05e | extra property at approval | `… c05e_extra_approval.json` | 1 | `ERROR E-SCHEMA … Additional properties are not allowed …` | empty | no |
| C06 | role `state: 1` | `… c06_role_state_int.json` | 1 | `E-SCHEMA … 1 is not of type 'string'` + `E-STATE-INVALID` | empty | no |
| C06b | `active: "true"` (boolean as string) | `… c06b_boolean_as_string.json` | 1 | `E-SCHEMA … 'true' is not of type 'boolean'` | empty | no |
| C06c | `candidates: []` | `… c06c_candidates_list.json` | 1 | `E-SCHEMA … [] is not of type 'object'`; execution safe via `isinstance` guard | empty | no |
| C06d | `evidence: true` | `… c06d_evidence_bool.json` | 1 | `E-SCHEMA … True is not of type 'object'`; safe | empty | no |
| C06e | `roles: null` | `… c06e_roles_null.json` | 1 | `E-SCHEMA … None is not of type 'object'`; safe | empty | no |
| C06f | `appointments: {}` | `… c06f_appointments_object.json` | 1 | `E-SCHEMA … {} is not of type 'array'`; safe | empty | no |
| **C06g** | `governance: null` (extra probe) | `… c06g_governance_null.json` | **1** | *(no stdout)* | **AttributeError traceback** | **yes** |
| **C06h** | `topology: "APPROVED"` (extra probe) | `… c06h_topology_string.json` | **1** | *(no stdout)* | **AttributeError traceback** | **yes** |
| **C06i** | `acceptance: "yes"` on a `FORMALLY_APPOINTED` role (extra probe) | `… c06i_acceptance_string.json` | **1** | *(no stdout)* | **AttributeError traceback** | **yes** |
| C07 | `candidate_ref: 123` in role | `… c07_candidate_ref_int.json` | 1 | `E-SCHEMA … 123 is not of type 'string'`; clean | empty | no |
| C07b | `verification_status: true` | `… c07b_verification_status_bool.json` | 1 | `E-SCHEMA` + `E-EVIDENCE-UNVERIFIED`; clean | empty | no |
| C07c | appointment `candidate_ref: 123` | `… c07c_appointment_candidate_ref_int.json` | 1 | `E-CANDIDATE-UNKNOWN … candidate=123`; clean | empty | no |
| C08 | missing file | `python $CLI --state $CASES\c08_this_file_does_not_exist.json` | 2 | `ERROR E-FILE-NOT-FOUND …: FileNotFoundError` | empty | no |
| C08b | directory passed as `--state` | `python $CLI --state $CASES` | 2 | `ERROR E-FILE-NOT-FOUND …: IsADirectoryError` (source shown as `cases`) | empty | no |
| C09 | evidence IDs and `source_ref` containing `../` traversal | `… c09_evidence_path_traversal.json` | 1 | `E-CANDIDATE-UNKNOWN … candidate=EV/../WINDOWS/win.ini`; **no file access** | empty | no |
| C10 | relative `--state` with `../` (cwd = `$V2`) | `python $CLI --state "..\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT\tests\cases\c10_relative_state.json"` | 1 | normal report; `Source: c10_relative_state.json` | empty | no |
| C10b | same relative path, cwd = REAUDIT | same command, different cwd | 1 | byte-identical to C10 | empty | no |
| C11a/b | control run twice, cwd = `$V2` | `… control_baseline.json` ×2 | 1/1 | identical (SHA-256 `5bd4141f…b0399c5`) | empty/empty | no |
| C11c | control from cwd = REAUDIT (absolute path) | `… control_baseline.json` | 1 | identical to C11a | empty | no |

Exit-code distribution: `1` × 28, `2` × 7. **No case produced exit 0**, which is correct — none of the generated states is stage-B ready.

---

## Detailed findings

### F-01 — Uncaught `RecursionError` on deeply nested JSON — **MEDIUM**

Cases C02 and C02b. Command (10 KB input):

```
python $CLI --state $CASES\c02_deep_5000_arrays.json
exit: 1   stdout: (empty)   stderr:
Traceback (most recent call last):
  File "...\cli\validate.py", line 62, in <module>
    sys.exit(main())
  File "...\cli\validate.py", line 39, in main
    state = load_json_strict(state_path)
  File "...\engine\validator.py", line 93, in load_json_strict
    return json.loads(text, object_pairs_hook=no_dupes)
  File "...\json\__init__.py", line 359, in loads
  File "...\json\decoder.py", line 345, in decode
  File "...\json\decoder.py", line 361, in raw_decode
RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string
```

C02b is the same traceback ending in `…JSON object from a unicode string`.

**Responsible lines:** `cli/validate.py:38-49` (exception tuple omits `RecursionError`); `engine/validator.py:74-97` (especially line 93 `json.loads` with no depth guard). Note that `jsonschema` recursion at `validator.py:183-191` would be the next exposure for deep-but-parseable structures.

**Impact:** a 10 KB input produces a raw traceback, no structured output, and exit code **1 — indistinguishable by exit code from an ordinary validation failure**. Cheap to trigger; fail-closed (never approves), but breaks callers that parse stdout and directly contradicts the "safe input-error handling" docstring.

### F-02 — `UnicodeEncodeError` on JSON `\u` lone surrogate reaching the human report — **MEDIUM**

Case C04d. The file is valid JSON containing `"candidate_ref": "\ud800"`; `json.loads` accepts it and the validator echoes it into an issue message.

```
python $CLI --state $CASES\c04d_json_lone_surrogate_escape.json
exit: 1   stdout: (empty)   stderr:
Traceback (most recent call last):
  File "...\cli\validate.py", line 62, in <module>
    sys.exit(main())
  File "...\cli\validate.py", line 57, in main
    print(payload if args.json_only else text)
  File "...\encodings\cp1252.py", line 19, in encode
UnicodeEncodeError: 'charmap' codec can't encode character '\ud800' in position 1285: character maps to <undefined>
```

**Responsible lines:** `cli/validate.py:57` (printing raw human text to a cp1252/pipe stdout); `engine/validator.py:456-473` (human report interpolates unescaped field values; e.g. line 470-471); `engine/validator.py:74-97` (loader accepts surrogate escapes without rejecting invalid Unicode scalars). `json_result` at `validator.py:480` is **safe** because `json.dumps` defaults to `ensure_ascii=True`.

**Mitigation verified:** adding `--json-only` to the identical input gives exit 1, empty stderr, no traceback, and stdout containing the literal `\ud800` escape. So the defect is confined to the default human-report path.

### F-03 — Schema errors are non-fatal; nested non-object values crash unguarded `.get()` calls — **HIGH**

Cases C06g, C06h, C06i. Schema validation correctly reports `E-SCHEMA` type mismatches, but `validate_state` keeps running and dereferences the invalid values:

```
python $CLI --state $CASES\c06g_governance_null.json
exit: 1   stdout: (empty)   stderr:
Traceback (most recent call last):
  File "...\cli\validate.py", line 62, in <module>
  File "...\cli\validate.py", line 42, in main
    result = validate_state(state, policy, schema)
  File "...\engine\validator.py", line 293, in validate_state
    if governance.get('recruitment') != 'UNAUTHORIZED' or governance.get('field_validation') != 'NOT_STARTED':
AttributeError: 'NoneType' object has no attribute 'get'
```

```
C06h → validator.py:297  if topology.get('status') != 'APPROVED' and policy.get(...):
       AttributeError: 'str' object has no attribute 'get'
C06i → validator.py:339  if acc.get('candidate_accepted') is not True:
       AttributeError: 'str' object has no attribute 'get'
```

**Responsible lines:** primary `engine/validator.py:288-289` (schema errors recorded but not short-circuited); crash sites `validator.py:293`, `297`, `339` (and the same unguarded pattern at 296, 312-314, 318-319, 323, 333-338, 341-375, 377, 380-384, 402-417). `cli/validate.py:38-49` does not catch `AttributeError`.

**Severity rationale:** HIGH because it is a general pattern, not a one-off: at least three trivially constructible inputs (`governance: null`, `topology: "x"`, `acceptance: "yes"`) crash the validator after the schema already told it the value is wrong. A one-line early return after line 289 (or type guards at each `.get()`) would remove the whole class. It still fails closed, so it is not CRITICAL.

**Contrast — values that ARE handled safely:** `candidates`, `evidence`, `roles`, `appointments` and `combination_approvals` are guarded with `isinstance(...)` at lines 300, 313, 318, 377 and 402 (cases C06c/C06d/C06e/C06f, C07b). Numeric/string coercion attempts (C06, C06b, C07, C07b, C07c) are clean.

### F-04 — Relative `--state` is anchored to V2 and `../` escapes the V2 root — **LOW (limitation)**

`python $CLI --state "..\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT\tests\cases\c10_relative_state.json"` succeeded from both cwd = `$V2` and cwd = REAUDIT with byte-identical output (`Source: c10_relative_state.json`). The file is outside V2.

**Responsible lines:** `cli/validate.py:33-36`. The path is used **only** by `load_json_strict` → `Path.read_bytes()` (`validator.py:78`); no write occurs. `--json-out` (lines 51-56) is a separate option and was not used in any case.

**Assessment:** documented as a limitation, not a security defect: the tool is a diagnostic validator whose purpose is to read a caller-supplied file; resolution against the install root rather than cwd is surprising but deterministic, read-only, and the reported `source` is only the basename (so full host paths are not echoed). Consumers should prefer absolute paths.

### F-05 — All `OSError`s collapse to `E-FILE-NOT-FOUND` — **LOW**

C08 (`FileNotFoundError`) and C08b (`IsADirectoryError`, from passing the `cases` directory) both exit 2 cleanly but report the same code/message: `ERROR E-FILE-NOT-FOUND [dimension=input]: E-FILE-NOT-FOUND: <ClassName>`. Only the class name in the message distinguishes them. **Responsible lines:** `engine/validator.py:77-80`; CLI mapping at `cli/validate.py:46-49`.

### F-06 — Duplicate-key error omits the JSON path — **LOW / informational**

C01 and C01b both report only the key name (`E-DUPLICATE-JSON-KEY: basis`, `…: schema_version`) with no nesting location, which slows triage for large states. Duplicate detection itself is correct at all depths. **Responsible lines:** `engine/validator.py:85-91` (message uses `% k` only); code derivation at `cli/validate.py:47`.

---

## Task-item coverage / positive observations

1. **Duplicate nested keys** — rejected correctly with exit 2, clean stderr (C01, C01b). No defect beyond F-06.
2. **Very deep nesting** — **defect F-01** (raw `RecursionError`, exit 1).
3. **Large file** — C03 (21,004,552 bytes) completed in ~3.97 s with a normal report, exit 1, empty stderr; no memory or encoding failure. No defect.
4. **Invalid Unicode** — raw `0xFF`, truncated UTF-8 and UTF-8-encoded lone surrogates are all rejected cleanly as `E-ENCODING-INVALID` / exit 2 (C04, C04b, C04c). A `\uD800` *escape* is a separate defect (**F-02**).
5. **Unexpected properties** — root, role, candidate, evidence and approval levels all produce `E-SCHEMA` "Additional properties are not allowed" issues with exit 1 and empty stderr (C05–C05e). No defect.
6. **Incorrect primitive types** — the six requested cases are all clean (C06–C06f). Three additional unguarded nested cases exposed **F-03**.
7. **Numeric/string coercion** — `candidate_ref: 123`, `state: 1`, `verification_status: true`, appointment `candidate_ref: 123` all produce schema issues and continue safely (C07–C07c). No coerce-and-accept behaviour observed; the validator never converts types.
8. **Missing file / directory** — both exit 2 with empty stderr (C08, C08b); see F-05 for message quality.
9. **"Incorrect evidence paths"** — `--help` shows only `-h/--help`, `--state`, `--json-out`, `--json-only`; **there is no evidence-path option**. Evidence is referenced exclusively by ID keys in the state (`evidence.get(eid)`, validator line 222). `source_ref` is only truth-tested (line 233). Ad-hoc probe A/B: changing `source_ref` from `..\..\..\..\Windows\win.ini` to `/definitely/not/a/real/file/ever` produced byte-identical validation output (only the `Source:` basename line differed). **No filesystem path is dereferenced — no defect.**
10. **Relative `../` traversal** — read-only, escapes V2 root, cwd-independent; see **F-04**.
11. **Determinism** — identical input twice (C11a/C11b) and from two working directories (C11a/C11c, C10/C10b) produced byte-identical stdout (SHA-256 `5bd4141fdf42bec09b1d7671513a83f2c4c9bc881b9fe5ae560699dbeb0399c5`), identical stderr and identical exit codes. Output uses `sort_keys=True` and `sorted_issues()`. **No defect.**
12. **Exit codes / stderr** — expected input failures (bad JSON, bad encoding, duplicate keys, missing file, directory) consistently exit **2** with **empty stderr** and a structured human report. Validation failures exit **1** with empty stderr **except** the six traceback cases (C02, C02b, C04d, C06g, C06h, C06i). Exit **0** was never returned for a non-ready state.

## Summary of severity suggestions

| ID | Defect | Severity | Source lines |
|---|---|---|---|
| F-01 | Uncaught `RecursionError` on deeply nested JSON | MEDIUM | `cli/validate.py:38-49`; `engine/validator.py:74-97` (93) |
| F-02 | `UnicodeEncodeError` from lone surrogate in human report | MEDIUM | `cli/validate.py:57`; `engine/validator.py:456-473` (470-471), 74-97 |
| F-03 | Non-fatal schema errors → `AttributeError` on nested wrong types | HIGH | `engine/validator.py:288-289`, 293, 297, 339 (and similar unguarded `.get()` sites) |
| F-04 | Relative `--state` anchored to V2; `../` escapes root (read-only) | LOW (limitation) | `cli/validate.py:33-36`; `engine/validator.py:78` |
| F-05 | All `OSError`s mapped to `E-FILE-NOT-FOUND` | LOW | `engine/validator.py:77-80`; `cli/validate.py:46-49` |
| F-06 | Duplicate-key error lacks JSON path | LOW | `engine/validator.py:85-91`; `cli/validate.py:47` |

**Bottom line:** the parser is deterministic, rejects duplicate keys and malformed bytes cleanly, handles a 21 MB state, does not dereference evidence paths, and never wrongly reports stage-B readiness. Its robustness gap is concentrated in exception handling: six input-controlled raw tracebacks, of which the schema-error-continues class (F-03) is the most pervasive and is rated HIGH.

*Full machine-readable evidence (commands, argv, cwd, input sizes, stdout hashes, complete stderr for every case) is in `REAUDIT/tests/results/cli_robustness_results.json`.*
