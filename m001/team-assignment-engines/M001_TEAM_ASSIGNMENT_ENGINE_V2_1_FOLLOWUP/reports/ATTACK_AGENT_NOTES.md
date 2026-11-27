# M001-TEAM-007 — Independent attack reproduction notes (V2 vs V2.1)

**Role:** independent security subagent. **Date:** 2026-11-27.
**Verdict:** all four canonical HIGH findings reproduce against disposable V2 and are rejected by disposable V2.1. One residual gap in the N-01 fix and two behavioural notes are recorded below. No unrelated V2.1 regression was found.

## 1. Scope, boundaries, environment

- All work performed only in `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1_FOLLOWUP`.
- Source directories V1, V2, V2_REAUDIT, V2_1 and the git repo were **read only**. No writes, installs, or network access.
- Every Python run used `$env:PYTHONDONTWRITEBYTECODE=1`.
- Environment: Python 3.13.5; `jsonschema` 4.26.0 is importable, so both engines used the full Draft 2020-12 path (`structural_schema_errors`), not the documented subset fallback.
- V2.1's own regression tests, mutation reports and result JSON files were **not** trusted or used as evidence; every state was authored here by deep-copying a fixture and mutating it.

## 2. Exact commands / setup

Copy step (PowerShell here-string piped to `python -`, working directory = FOLLOWUP):

```powershell
$env:PYTHONDONTWRITEBYTECODE=1
$script = @'
import shutil
from pathlib import Path
base = Path(r"C:\Users\pc\AppData\Local\Temp\opencode")
followup = base / "M001_TEAM_ASSIGNMENT_ENGINE_V2_1_FOLLOWUP"
pairs = [
    (base / "M001_TEAM_ASSIGNMENT_ENGINE_V2",   followup / "tests" / "disposable_v2"),
    (base / "M001_TEAM_ASSIGNMENT_ENGINE_V2_1", followup / "tests" / "disposable_v21"),
]
ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "mutants")
for src, dst in pairs:
    if dst.exists():
        raise SystemExit("REFUSING to overwrite existing destination: %s" % dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    for sub in ("engine", "policy", "schemas"):
        shutil.copytree(src / sub, dst / sub, ignore=ignore)
    shutil.copytree(src / "tests" / "fixtures", dst / "tests" / "fixtures", ignore=ignore)
'@
$script | python -
```

Result: `disposable_v2/` created with only `engine/`, `policy/`, `schemas/`, `tests/fixtures/` (no `__pycache__`, no `mutants`); output printed `COPIED M001_TEAM_ASSIGNMENT_ENGINE_V2 -> tests\disposable_v2` plus its 35 copied files.

`tests/disposable_v21/` **already existed** from earlier work in the workspace, so the copy step correctly refused to overwrite it. Before reuse I hash-compared all 55 relevant files (validator, policy, schema, every fixture) between V2.1 source and the existing copy: **0 mismatches**. V2.1 validator SHA-256 `58082f5cc1f0d54809c79a6bdba34cdbb08750a5efcc61901f77a6bef91a1b2f`; V2 validator SHA-256 recorded in the results JSON. No sibling agent's work was modified.

Harness invocation (same here-string pattern):

```powershell
$env:PYTHONDONTWRITEBYTECODE=1
$script = @'
# importlib.util.spec_from_file_location -> isolated module auditor_validator_v2 / _v21
# state = copy.deepcopy semantics via json.loads of each version's own valid_four_person.json
# capture() wraps validate_state() in try/except BaseException and records issues/exception
'@
$script | python -
```

Modules were loaded with `importlib.util.spec_from_file_location("auditor_validator_<tag>", <disposable>/engine/validator.py)`, so each version's `ROOT` resolves to its own disposable copy and policy/schema loading is isolated. Final results written to `tests/results/attack_reproduction_results.json` (79,053 bytes).

## 3. Baseline sanity

| version | own `valid_four_person.json` | stage_b_role_ready | codes |
|---|---|---|---|
| V2 | clean | `True` | none |
| V2.1 | clean | `True` | none |

Both versions' `valid_four_person`, `valid_five_person`, `valid_six_person` fixtures pass. No baseline defect.

## 4. N-01 — whitespace approval basis

Mutation: `roles.RESEARCH_OWNER.approval.basis`.

| case (exact value) | V2 ready / codes | V2.1 ready / codes |
|---|---|---|
| `'  \t\n '` (space, tab, newline) | `True` / none — **REPRODUCED** | `False` / `E-DECISION-EVIDENCE-EMPTY` |
| `'\u00a0\u2003\u3000'` (NBSP, EM SPACE, IDEOGRAPHIC SPACE) | `True` / none — **REPRODUCED** | `False` / `E-DECISION-EVIDENCE-EMPTY` |
| meaningful text `'PO decision recorded 2026-11-27 for C-P1:RESEARCH_OWNER'` | `True` / none | `True` / none — genuine basis still passes |
| `'\u200b'` (ZERO WIDTH SPACE) | `True` / none | `True` / none — **residual gap, see §8** |

Placeholder check: for both whitespace cases V2.1 produced exactly one issue, `ERROR E-DECISION-EVIDENCE-EMPTY` with message `Approval basis is missing, non-string or contains only whitespace`. No replacement/placeholder rationale was inserted; the state's `basis` value after validation is still the original whitespace string (repr `'  \t\n '` / `'\xa0\u2003\u3000'`). V2, by contrast, emitted **zero** issues and kept `stage_b_role_ready=True`, i.e. the approval decision was accepted on whitespace only.

Root cause confirmed by source: V2 uses bare truthiness `if not appr.get('basis')`; V2.1 uses `meaningful_text()` = `isinstance(value, str) and bool(value.strip())`.

## 5. N-02 — whitespace / reused combination rationale

Mutation: `combination_approvals[*].rationale`.

| case | V2 ready / codes | V2.1 ready / codes |
|---|---|---|
| approval[0] rationale = `'  \t\n '` | `True` / none — **REPRODUCED** | `False` / `E-COMBINATION-RATIONALE` |
| approval[0] rationale = `'\u00a0\u2003\u3000'` | `True` / none — **REPRODUCED** | `False` / `E-COMBINATION-RATIONALE` |
| meaningful rationale copied verbatim from approval[0] (C-P1) to unrelated approval[1] (C-P2) | `True` / none — **REPRODUCED** | `False` / `E-COMBINATION-RATIONALE-REUSED` |
| same rationale copied with padding/whitespace differences (`"  " + text + "\t"`) | `True` / none — **REPRODUCED** | `False` / `E-COMBINATION-RATIONALE-REUSED` (normalised via `' '.join(split())`) |

Note: V2.1's reuse check is global across all approvals, so identical boilerplate on two *different candidates'* combinations is rejected. That is the intended N-02 fix, but it is strict — see §8.

## 6. N-03 — acceptance evidence not role-bound

**Primary attack.** Candidate `C-P1` holds `RESEARCH_OWNER` + `CONTINUE_STOP_OWNER`. Both roles' `acceptance.evidence_id` were pointed at one evidence record with V2-style `subject: "C-P1"` and no role/appointment/decision binding (role-bound fields removed in V2.1's copy; they do not exist in V2's fixture).

| version | stage_b_role_ready | codes |
|---|---|---|
| V2 | `True` (zero issues) — **REPRODUCED** | none |
| V2.1 | `False` | `E-EVIDENCE-SUBJECT` (x2), `E-ACCEPTANCE-ROLE` (x2), `E-ACCEPTANCE-APPOINTMENT` (x2), `E-ACCEPTANCE-DECISION` (x2) |

**Mutation matrix** (target = `RESEARCH_OWNER` acceptance evidence from each version's baseline):

| mutation | V2 ready / codes | V2.1 ready / codes |
|---|---|---|
| evidence `role` → `ANALYST` | `True` / none (field absent in V2 data model — not representable) | `False` / `E-ACCEPTANCE-ROLE` |
| evidence `subject` → `C-P4:RESEARCH_OWNER` (+ appointment_ref) | `False` / `E-EVIDENCE-SUBJECT` | `False` / `E-EVIDENCE-SUBJECT`, `E-ACCEPTANCE-APPOINTMENT` |
| `appointment_ref` → `C-P1:CONTINUE_STOP_OWNER` | `True` / none (field absent in V2) | `False` / `E-ACCEPTANCE-APPOINTMENT` |
| `verification_status` → `PENDING` | `False` / `E-EVIDENCE-UNVERIFIED` | `False` / `E-EVIDENCE-UNVERIFIED` |
| `revoked` → `true` | `True` / none (field absent in V2) | `False` / `E-EVIDENCE-REVOKED` |
| `acceptance.evidence_id` → `null` | `False` / `E-EVIDENCE-MISSING` | `False` / `E-EVIDENCE-MISSING` |
| both C-P1 roles given the same `decision_ref` | `True` / none (field absent in V2) | `False` / `E-ACCEPTANCE-DECISION-REUSED` |

V2.1's binding is enforced in `acceptance_evidence_check()` (exact `candidate:role` subject, `role`, `appointment_ref`, non-empty distinct `decision_ref`, verified/unrevoked record). V2 checks only the candidate ref as subject and cannot express any of the four extra bindings.

## 7. N-15 — schema errors non-fatal → AttributeError tracebacks

States built from each version's own `valid_four_person.json`; schemas injected via `validate_state(state, schema=...)` where noted.

| malformed input | V2 result | V2.1 result |
|---|---|---|
| `governance: null` | **uncaught `AttributeError: 'NoneType' object has no attribute 'get'`** | controlled `ValidationResult`, `stage_b_role_ready=False`, `E-SCHEMA`, all 8 dimensions `FAIL` |
| `topology: 'x'` | **uncaught `AttributeError: 'str' object has no attribute 'get'`** | same controlled `E-SCHEMA` result |
| `roles.RESEARCH_OWNER.acceptance: 'yes'` | **uncaught `AttributeError: 'str' object has no attribute 'get'`** | same controlled `E-SCHEMA` result |
| all three combined | **uncaught `AttributeError: 'NoneType' object has no attribute 'get'`** | same controlled `E-SCHEMA` result |
| unresolvable `$ref` (`#/$defs/DOES_NOT_EXIST`) in schema | **uncaught `jsonschema.exceptions._WrappedReferencingError` / `PointerToNowhere`** | controlled `E-SCHEMA-REFERENCE` result, all dimensions `FAIL` |
| whole schema is unresolvable `$ref` | **uncaught `_WrappedReferencingError`** | controlled `E-SCHEMA-REFERENCE` |
| invalid schema structure `{"type": 123, "required": "not-an-array"}` | controlled `E-SCHEMA` (`SchemaError` is caught in V2) | controlled `E-SCHEMA-REFERENCE` (mislabelled — see §8) |
| non-object schema `"not-a-schema"` | controlled `E-SCHEMA` | controlled `E-SCHEMA-REFERENCE` |

Root cause confirmed: V2 appends schema errors with `fail(...)` then continues into `governance.get(...)`, `topology.get(...)`, `acc.get(...)`; V2.1 returns immediately on any schema error and catches the narrow schema/reference exception classes. The canonical `AttributeError` traceback symptom was reproduced exactly; the uncaught `$ref` resolution error is an additional N-15 variant reproduced in V2 and fixed in V2.1.

## 8. Unintended regression scan / new defects

**No unrelated regression found.**
- V2.1 passes its own valid four/five/six-person fixtures.
- Feeding V2's valid state into V2.1 produced only these codes: `E-EVIDENCE-SUBJECT`, `E-ACCEPTANCE-ROLE`, `E-ACCEPTANCE-APPOINTMENT`, `E-ACCEPTANCE-DECISION` (N-03) and `E-COMBINATION-RATIONALE-REUSED` (N-02). Every rejection is attributable to one of the four fixes. No new, unexplained failure code or crash appeared.

**New/residual observations (reported, not silently accepted):**
1. **Residual N-01 gap:** `meaningful_text()` relies on `str.strip()`, which does not remove `U+200B` ZERO WIDTH SPACE. A basis of `'\u200b'` is accepted by V2.1 (`stage_b_role_ready=True`, no issues). This is invisible content and should arguably be rejected; V2 accepts it too, so it is not a regression but the fix is incomplete.
2. **Cosmetic defect in V2.1 N-15 mapping:** `jsonschema.exceptions.SchemaError` caused by an invalid schema *structure* is caught by `_SCHEMA_EXCEPTION_TYPES` first and emitted as `E-SCHEMA-REFERENCE` rather than `E-SCHEMA-INVALID`. Controlled, but the code misdescribes the fault.
3. **Strictness change from N-02:** `E-COMBINATION-RATIONALE-REUSED` compares normalised rationale text across all approvals, including different candidates; identical legitimate boilerplate is rejected (this is why V2's own otherwise-valid fixture fails when cross-fed). Expected from the fix, but a compatibility consideration.

## 9. Not reproduced

- No V2.1 crash/traceback for any N-15 input tested (malformed state values, unresolvable `$ref`, invalid schema structure, non-object schema).
- No valid V2.1 state rejected for a reason unrelated to the four fixes.
- V2 did **not** crash on a structurally invalid schema object: `jsonschema.SchemaError` is caught by V2. Its N-15 crash requires either schema-invalid *state values* or unresolvable `$ref`s; both were reproduced.

## 10. Conclusion

| finding | V2 | V2.1 |
|---|---|---|
| N-01 whitespace approval basis | reproduced (accepted) | rejected |
| N-02 whitespace/reused combination rationale | reproduced (accepted) | rejected |
| N-03 acceptance evidence not role-bound | reproduced (accepted) | rejected |
| N-15 schema errors non-fatal → tracebacks | reproduced (uncaught exceptions) | controlled fail-closed result |

All four HIGH vulnerabilities are independently reproduced on disposable V2 and demonstrably fixed on disposable V2.1. Follow-up recommended for the U+200B residual gap and the `E-SCHEMA-REFERENCE` mislabel; the rationale-reuse strictness is a deliberate behavioural change worth documenting for downstream consumers.

## 11. Artifacts

- `tests/results/attack_reproduction_results.json` — full machine-readable results: per-case codes, code counts, issue messages, dimensions, exception types/messages/traceback tails, provenance hashes, verdicts.
- `tests/disposable_v2/`, `tests/disposable_v21/` — isolated disposable copies used for execution (V2.1 copy pre-existed and was hash-verified before reuse).
