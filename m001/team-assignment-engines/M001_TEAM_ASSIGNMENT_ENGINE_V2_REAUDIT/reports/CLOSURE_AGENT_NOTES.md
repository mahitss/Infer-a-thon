# M001-TEAM-005 — Independent Closure Agent Notes (V2 re-audit)

**Verdict: all 16 registered findings F-01 … F-16 are CLOSED (16 CLOSED / 0 PARTIAL / 0 NOT CLOSED).**
This verdict was reached by reading V2 source and executing independent probes; V2's
`reports/defect_remediation_matrix.md` was read only to see what was claimed, and was **not** used as
evidence. Four residual observations (R-1 … R-4) are recorded below; they do not reopen F-01 … F-16 but
they matter for how the machine output should be consumed.

## 1. Boundaries, inputs, environment

- Work directory: `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT`.
- Only two files written: `tests/results/finding_closure_results.json` and this report.
- V1, the previous audit, V2, and the git repo were **read only**. No install, no network.
- Inputs read: `M001_TEAM_ASSIGNMENT_ENGINE_AUDIT/M001_DEFECT_REGISTER.json`; V1
  `engine/validator.py`, `policy/role_constraints.json`, `adversarial_fixtures/*`; V2
  `engine/validator.py`, `policy/role_constraints.json`, `schemas/team_assignment.schema.json`,
  `cli/validate.py`, `state/current_assignment_state.json`, `tests/fixtures/*`; authoritative
  `M001_ROLE_ASSIGNMENT_DECISION_PACK/M001_RESEARCH_ROLE_CHARTER.md` and
  `M001_TEAM_STAFFING_PACK/M001_MINIMUM_TEAM_STAFFING_MODELS.md` (read-only provenance check).
- Python 3.13.5; `jsonschema` 4.26.0 is installed, so V2 `structural_schema_errors()` takes the full
  Draft 2020-12 branch (lines 183–194). All in-memory states therefore had to be genuinely
  schema-valid; extra/unknown fields produce `E-SCHEMA`.

## 2. How the checks were executed (commands)

The V2 validator was imported from its path without installing anything:

```powershell
$py = @'
import importlib.util
spec = importlib.util.spec_from_file_location("v2validator",
    r"C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2\engine\validator.py")
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
policy = v.load_policy(); schema = v.load_schema()
'@
$py | python -
```

For findings F-01 … F-12 I generated a schema-valid six-candidate baseline in memory
(`schema_version="2.0"`, governance all `OPEN`/`UNAUTHORIZED`/`NOT_STARTED`, topology `APPROVED`,
six active candidates, four evidence records per role, timezone-aware timestamps
`00:00/01:00/02:00+00:00`, all six role records `FORMALLY_APPOINTED`, six appointment records, exact
`combination_approvals` where applicable), then applied one targeted mutation per finding and called:

```python
r = v.validate_state(state, policy, schema)
d = r.to_dict()   # stage_b_role_ready, dimensions, issues
```

For F-13 … F-16, V2's loader was exercised on **in-memory bytes** by temporarily replacing the
module-level `Path` with a fake object whose `read_bytes()` returns the crafted bytes (no file
written):

```python
class FakePath:
    def __init__(self, data): self.data = data
    def read_bytes(self):
        if isinstance(self.data, Exception): raise self.data
        return self.data
orig = v.Path
v.Path = lambda p: FakePath(b'{"schema_version":"1.0","schema_version":"9.9"}')
try: v.load_json_strict("in-memory")
finally: v.Path = orig
```

CLI checks used read-only V2 fixtures:

```powershell
python "...\M001_TEAM_ASSIGNMENT_ENGINE_V2\cli\validate.py" --state tests/fixtures/duplicate_json_key.json --json-only
python "...\M001_TEAM_ASSIGNMENT_ENGINE_V2\cli\validate.py" --state tests/fixtures/malformed.json --json-only
python "...\M001_TEAM_ASSIGNMENT_ENGINE_V2\cli\validate.py" --state tests/fixtures/invalid_utf8.bin --json-only
python "...\M001_TEAM_ASSIGNMENT_ENGINE_V2\cli\validate.py" --state tests/fixtures/this_file_does_not_exist_ZZZ.json --json-only
python "...\M001_TEAM_ASSIGNMENT_ENGINE_V2\cli\validate.py" --state tests/fixtures/valid_four_person.json --json-only
```

V1 defects were confirmed by importing V1's validator from its path and calling
`v1.validate_state(state, v1.load_policy(), v1.load_schema())` on V1's own adversarial fixtures.

### Baseline (must be PASS to make mutations meaningful)

```
probe: baseline_six_distinct_candidates
stage_b_role_ready: true ; codes: [] ; blocking errors: 0
all eight dimensions: PASS
CLI valid_four_person.json: exit_code 0, stderr "", stage_b_role_ready true, 8 dimensions PASS
```

## 3. Closure results, one line each

| Finding | Status | Exact issue code(s) observed | stage_b_role_ready | Governing dimension |
|---|---|---|---|---|
| F-01 | CLOSED | `E-COMBINATION-APPROVAL-MISSING`, `E-DISCOURAGED-RO-MODERATOR` | False | `role_compatibility` FAIL (+ `product_owner_combination_approval` FAIL) |
| F-02 | CLOSED | `E-COMBINATION-APPROVAL-MISSING`, `E-DISCOURAGED-CUSTODIAN-ANALYST` | False | `role_compatibility` FAIL |
| F-03 | CLOSED | `E-COND-EVIDENCE-SEPARATION` (+ `E-SCHEMA` if legacy boolean injected) | False | `role_compatibility` FAIL |
| F-04 | CLOSED | `E-COND-EXPLICIT-CS` (+ `E-APPOINTMENT-MISSING` / `E-UNAPPROVED-APPOINTMENT` or `E-COMBINATION-APPROVAL-MISSING`) | False | `role_compatibility` FAIL |
| F-05 | CLOSED | 2 × `E-COMBINATION-APPROVAL-MISSING` | False | `product_owner_combination_approval` FAIL |
| F-06 | CLOSED | `E-CANDIDATE-DUPLICATE` (registry dup / duplicate appointment); original V1 pair now `E-HARD-MODERATOR-ANALYST` | False | `human_candidate_acceptance` FAIL / `role_assignment_completeness` FAIL / `role_compatibility` FAIL |
| F-07 | CLOSED | `E-CANDIDATE-UNKNOWN`, `E-EVIDENCE-SUBJECT` | False | `formal_appointment_validity` FAIL + `human_candidate_acceptance` FAIL |
| F-08 | CLOSED | `E-APPOINTMENT-MISSING`, `E-UNAPPROVED-APPOINTMENT` | False | `role_assignment_completeness` FAIL |
| F-09 | CLOSED | `E-FORMAL-APPROVAL-MISMATCH` | False | `formal_appointment_validity` FAIL |
| F-10 | CLOSED | `E-DECISION-EVIDENCE-EMPTY` | False | `formal_appointment_validity` FAIL |
| F-11 | CLOSED | `E-TIMESTAMP-MISSING`, `E-TIMESTAMP-ORDER`, `E-TIMESTAMP-INVALID` | False | `formal_appointment_validity` FAIL / `evidence_integrity` FAIL |
| F-12 | CLOSED | `E-TOPOLOGY-UNAPPROVED` | False | `structural_topology_validity` FAIL |
| F-13 | CLOSED | `E-DUPLICATE-JSON-KEY` (CLI exit 2, empty stderr) | False | `input` FAIL |
| F-14 | CLOSED | `E-JSON-INVALID` (CLI exit 2, empty stderr) | False | `input` FAIL |
| F-15 | CLOSED | `E-FILE-NOT-FOUND` (CLI exit 2, empty stderr) | False | `input` FAIL |
| F-16 | CLOSED | `E-ENCODING-INVALID` (CLI exit 2, empty stderr) | False | `input` FAIL |

## 4. Finding-by-finding evidence

### F-01 / F-02 — discouraged pairs no longer warn-only
Source (`V2/engine/validator.py`):

```
421:    for candidate, held in by_candidate.items():
422:        if len(held) <= 1:
423:            continue
424:        key = (candidate, pair_key(held))
425:        ca = approval_map.get(key)
426:        if not ca:
427:            fail('product_owner_combination_approval','E-COMBINATION-APPROVAL-MISSING',candidate=str(candidate),
428:                 message='No exact Product Owner approval for combination %s' % key[1])
432:        for combo in policy['discouraged_combinations']:
433:            if set(combo['roles']).issubset(held) and not ca:
434:                fail('role_compatibility',combo['code'],message='Discouraged combination lacks PO review')
```

`V2/policy/role_constraints.json` lines 13–14 declare the pairs as `NOT_RECOMMENDED` with blocking
codes `E-DISCOURAGED-RO-MODERATOR` and `E-DISCOURAGED-CUSTODIAN-ANALYST`.

Exact mutation/output:
- F-01: RO + MODERATOR on C1, approvals emptied → codes
  `[E-COMBINATION-APPROVAL-MISSING, E-DISCOURAGED-RO-MODERATOR]`,
  `product_owner_combination_approval=FAIL`, `role_compatibility=FAIL`, `stage_b_role_ready=false`.
- F-02: DATA_CUSTODIAN + ANALYST on C5, approvals emptied → codes
  `[E-COMBINATION-APPROVAL-MISSING, E-DISCOURAGED-CUSTODIAN-ANALYST]`, same two dimensions FAIL.

V1 confirmation: `validate_state(discouraged_ro_moderator.json)` → `valid=True`,
`[W-DISCOURAGED-RO-MODERATOR]`; `discouraged_custodian_analyst.json` → `valid=True`,
`[W-DISCOURAGED-CUSTODIAN-ANALYST]`. The warning-only path is gone.

Nuance (R-3): line 433 suppresses the `E-DISCOURAGED-*` code whenever *any* approval record with the
exact key exists, even if `outcome=REJECTED`. Probe with `outcome=REJECTED` produced
`E-COMBINATION-APPROVAL-REJECTED`, `product_owner_combination_approval=FAIL`, `stage_b=false`; no
security regression, but the discouraged code is not a stand-alone signal.

### F-03 — boolean evidence flag for evidence separation
Source lines 435–445:

```
438:            if combo['requirement'] == 'evidence_separation':
439:                found = any(
440:                    e.get('evidence_type')=='EVIDENCE_SEPARATION' and
441:                    e.get('subject')=='%s:%s' % (candidate, pair_key(held)) and
442:                    e.get('verification_status')=='VERIFIED'
443:                    for e in evidence.values() if isinstance(e, dict))
444:                if not found:
445:                    fail('role_compatibility','E-COND-EVIDENCE-SEPARATION',message='Evidence separation record missing')
```

Mutation: MOD + NOTE on C3 with a valid exact combination approval but no separation record →
`E-COND-EVIDENCE-SEPARATION`, `role_compatibility=FAIL`, `stage_b=false`. Adding the legacy boolean
`conditional_evidence: {"evidence_separation_documented": true}` at state level produced
`[E-COND-EVIDENCE-SEPARATION, E-SCHEMA]` (schema `additionalProperties: false`, line 7). V1
`false_evidence_moderator_notetaker.json` → `valid=True, issues=[]`.

### F-04 — explicit Continue/Stop flag
Source lines 446–448:

```
446:            if combo['requirement'] == 'explicit_additional_appointment':
447:                if role_records.get('CONTINUE_STOP_OWNER',{}).get('state') not in formal_states or not ca:
448:                    fail('role_compatibility','E-COND-EXPLICIT-CS',message='No explicit Continue/Stop appointment evidence')
```

Two mutations: (a) CS state `PROPOSED` with approval present →
`[E-APPOINTMENT-MISSING, E-UNAPPROVED-APPOINTMENT, E-COND-EXPLICIT-CS]`;
(b) CS formal with approvals removed →
`[E-COMBINATION-APPROVAL-MISSING, E-COND-EXPLICIT-CS]`. Both `stage_b=false`,
`role_compatibility=FAIL`. V1 `false_evidence_continue_stop.json` → `valid=True, issues=[]`.

### F-05 — every multi-role holder needs an exact PO approval
Source lines 402–428 (approval map + `E-COMBINATION-APPROVAL-MISSING`) and 416–419
(`COMBINATION_REVIEW` evidence + `decision_timestamp`). Mutation: compatible pairs NOTE+DC (C1) and
ANALYST+CS (C2), approvals emptied → **two** `E-COMBINATION-APPROVAL-MISSING` errors,
`product_owner_combination_approval=FAIL`, `stage_b=false`, no discouraged/hard codes. V1
`compatible_combination_no_approval.json` → `valid=True, issues=[]`. Authoritative charter line 25
("One person may hold multiple roles only where explicitly documented by the Product Owner") supports
the rule; the exact machine schema is V2-specific (see §6).

### F-06 — duplicate candidate identifier
Source: lines 249–263 (`candidate_registry_check`: key/reference mismatch and duplicate ref both emit
`E-CANDIDATE-DUPLICATE`), 315–316 (any `E-CANDIDATE-*` → `human_candidate_acceptance=FAIL`),
386–388 (duplicate `(ref, role)` appointment → `E-CANDIDATE-DUPLICATE`), 429–431 (hard pair).
Mutations: (a) registry key `C-DUP` with `candidate_ref="C1"` → `E-CANDIDATE-DUPLICATE` ×2,
`human_candidate_acceptance=FAIL`; (b) duplicate appointment `(C1, RESEARCH_OWNER)` →
`E-CANDIDATE-DUPLICATE`, `role_assignment_completeness=FAIL`; (c) original V1 case MOD+ANALYST on one
person **with a fully valid approval** → `E-HARD-MODERATOR-ANALYST`, `role_compatibility=FAIL`,
`stage_b=false`. V1 `duplicate_candidate_identifier.json` → `valid=True`.

Semantic shift worth recording: V2 does not call "one human holding two roles" a duplicate identity;
it requires an exact approval (or hard-blocks the pair). The original exploit is unreachable, but the
exact code originally expected is emitted only for duplicate *identity records* / duplicate
*appointment records*.

### F-07 — unknown human reference
Source lines 333–335 and 389–390 (`E-CANDIDATE-UNKNOWN`), 261–262 (`E-CANDIDATE-INACTIVE`),
schema lines 46–54. Mutation: RO role record and appointment ref → `UNKNOWN-HUMAN` → codes
`[E-CANDIDATE-UNKNOWN, E-EVIDENCE-SUBJECT]`, 6 errors, `formal_appointment_validity=FAIL`,
`human_candidate_acceptance=FAIL`, `stage_b=false`. V1
`unknown_human_reference.json` → `valid=True`.

### F-08 — PROPOSED treated as appointed
Source: policy lines 5–7 (`formal_appointment_states = ["FORMALLY_APPOINTED"]`, `missing_appointment_states`
now includes `PROPOSED`, `ACCEPTED_IN_CONVERSATION`, `CANDIDATE_ACCEPTED`), validator 327–330 and
393–394. Mutation: MODERATOR `state="PROPOSED"` with appointment retained →
`[E-APPOINTMENT-MISSING, E-UNAPPROVED-APPOINTMENT]`, `role_assignment_completeness=FAIL`,
`stage_b=false`. V1 `proposed_treated_as_appointed.json` → `valid=True`.

Note: the validator actually consumes `formal_appointment_states`, **not** the declared
`missing_appointment_states` field (grep found no use of the latter).

### F-09 — formal state with `approval.formal=false`
Source lines 349–350:

```
349:        if appr.get('formal') is not True:
350:            fail('formal_appointment_validity','E-FORMAL-APPROVAL-MISMATCH',role=role,message='FORMALLY_APPOINTED with formal=false')
```

Mutation on MODERATOR → `E-FORMAL-APPROVAL-MISMATCH`, `formal_appointment_validity=FAIL`,
`stage_b=false`. V1 `formal_state_formal_approval_false.json` → `valid=True`.

### F-10 — empty PO decision basis
Source lines 351–352 (`E-DECISION-EVIDENCE-EMPTY`), 343–344 (`PRODUCT_OWNER_APPROVAL` evidence check),
218–221 (`E-EVIDENCE-MISSING` for empty evidence id). Mutation `approval.basis=""` →
`E-DECISION-EVIDENCE-EMPTY`, `formal_appointment_validity=FAIL`, `stage_b=false`. V1
`weak_decision_evidence.json` → `valid=True`. The code name differs from the register's expected
`E-DECISION-EVIDENCE-MISSING`, but it is a blocking ERROR on the governing dimension.

### F-11 — structured timestamps
Source: schema lines 84–114 (fields), policy line 23 (`timestamp_fields`), validator 197–210
(`valid_timestamp` requires tz-aware ISO-8601), 355–363 (presence, validity and ordering).
Four mutations produced:

```
missing candidate_accepted_at      -> E-TIMESTAMP-MISSING        formal_appointment_validity FAIL
naive role timestamp               -> E-TIMESTAMP-MISSING        formal_appointment_validity FAIL
out-of-order formal appointment    -> E-TIMESTAMP-ORDER          formal_appointment_validity FAIL
naive evidence timestamp           -> E-TIMESTAMP-INVALID        evidence_integrity FAIL
```

All four `stage_b=false`. V1 fixtures have no timestamp fields at all.

### F-12 — topology readiness
Source: policy line 24 (`require_topology_approved_for_stage_b: true`), validator 296–298
(`E-TOPOLOGY-UNAPPROVED`), 450–452 (`stage_b` requires topology APPROVED + all eight dimensions PASS
+ zero issues). Mutation `topology.status="PROPOSED"` with every role formal →
`E-TOPOLOGY-UNAPPROVED`, `structural_topology_validity=FAIL`, `stage_b=false`. V1
`topology_proposed_all_formal.json` → `valid=True, [W-TOPOLOGY-PROPOSED]`. V2's shipped
`state/current_assignment_state.json` has topology `PROPOSED` and several non-formal roles, so it
correctly reports not-ready.

### F-13 — duplicate JSON keys
Source lines 25–26 (`DuplicateKeyError`), 74–97 (`object_pairs_hook=no_dupes`, raises
`E-DUPLICATE-JSON-KEY`), CLI 38–49. Exact outputs:

```
in-memory bytes: DuplicateKeyError: E-DUPLICATE-JSON-KEY: schema_version
CLI duplicate_json_key.json: exit_code 2, stderr "", code E-DUPLICATE-JSON-KEY,
    dimensions {"input": "FAIL"}, stage_b_role_ready false
V1 load_json(duplicate_json_key.json): loaded schema_version "9.9"  (last duplicate wins)
```

### F-14 — malformed JSON
Source lines 96–97 (`except json.JSONDecodeError: raise ValueError('E-JSON-INVALID: malformed JSON')`),
CLI 17–23 + 46–49. Exact outputs:

```
in-memory bytes: ValueError: E-JSON-INVALID: malformed JSON
CLI malformed.json: exit_code 2, stderr "", code E-JSON-INVALID, dimensions {"input":"FAIL"}
V1 CLI malformed.json: Traceback on stderr, json.decoder.JSONDecodeError, exit 1
V1 load_json: JSONDecodeError "Expecting property name enclosed in double quotes: line 1 column 28"
```

### F-15 — missing file
Source lines 76–80 (`except OSError → E-FILE-NOT-FOUND`), CLI 46–49. Exact outputs:

```
in-memory OSError: ValueError: E-FILE-NOT-FOUND: FileNotFoundError
CLI nonexistent path: exit_code 2, stderr "", code E-FILE-NOT-FOUND
V1 load_json(missing path): FileNotFoundError (unhandled by V1 CLI -> traceback)
```

### F-16 — invalid UTF-8
Source lines 81–84 (`except UnicodeDecodeError → E-ENCODING-INVALID`), CLI 46–49. Exact outputs:

```
in-memory bytes b'\xff\xfe...': ValueError: E-ENCODING-INVALID: invalid UTF-8
CLI invalid_utf8.bin: exit_code 2, stderr "", code E-ENCODING-INVALID
V1 load_json(invalid_utf8.bin): UnicodeDecodeError "'utf-8' codec can't decode byte 0xff in position 24"
```

## 5. Hard incompatibilities: truly unoverridable (positive check)

Source lines 429–431:

```
429:        for combo in policy['hard_incompatibilities']:
430:            if set(combo['roles']).issubset(held):
431:                fail('role_compatibility',combo['code'],message='Hard incompatibility cannot be approved')
```

The `ca` (approval) variable is not consulted. Probes with a **fully valid** exact PO combination
approval:

```
MOD+ANALYST            -> E-HARD-MODERATOR-ANALYST   role_compatibility FAIL  stage_b false
MOD+DATA_CUSTODIAN     -> E-HARD-MODERATOR-CUSTODIAN role_compatibility FAIL  stage_b false
```

Neither V2's policy nor its schema defines any override/waiver field. A wrong-pair approval does not
help either: `RO+MOD` held with an approval recorded for `RO+CS` →
`[E-COMBINATION-APPROVAL-MISSING, E-DISCOURAGED-RO-MODERATOR, E-EVIDENCE-SUBJECT]`,
`stage_b=false`, because the key is the exact sorted role set (line 408 + 424).

## 6. Policy-source versions and newly introduced interpretation

| | V1 | V2 |
|---|---|---|
| `version` | `1.0` | `2.0` |
| `source` | `M001_ROLE_ASSIGNMENT_DECISION_PACK and M001_TEAM_STAFFING_PACK` | `M001_ROLE_ASSIGNMENT_DECISION_PACK, M001_TEAM_STAFFING_PACK, M001_ENGINE_INDEPENDENT_AUDIT defect register` |
| discouraged classification | `DISCOURAGED` | `NOT_RECOMMENDED` |
| discouraged codes | `W-DISCOURAGED-*` (warning) | `E-DISCOURAGED-*` (blocking ERROR) |
| review field | none | `review_requirement: "product_owner_combination_review"` |
| conditional requirement keys | `evidence_separation_documented`, `explicit_additional_appointment` | `evidence_separation`, `explicit_additional_appointment` |
| appointment states | `missing_appointment_states = [UNASSIGNED, DEFERRED, REJECTED]`; `accepted_formal_states = [CANDIDATE_ACCEPTED, FORMALLY_APPOINTED, ACCEPTED_IN_CONVERSATION]` | `formal_appointment_states = [FORMALLY_APPOINTED]`; `missing_appointment_states` expanded to include `PROPOSED`, `ACCEPTED_IN_CONVERSATION`, `CANDIDATE_ACCEPTED`, `REJECTED`, `DEFERRED` |
| added fields | — | `evidence_types`, `evidence_fields`, `verification_statuses`, `timestamp_fields`, `require_topology_approved_for_stage_b`, `require_combination_approval_for_multi_role`, `stage_b_dimensions` |
| removed fields | — | `state_requirements`, `requirement_codes`, `accepted_formal_states`, per-combination `message` |

Authoritative wording check: `M001_RESEARCH_ROLE_CHARTER.md` lines 20–23 say **Not recommended**
(RO+Moderator, Custodian+Analyst) and **Unacceptable** (Moderator+Analyst, Custodian+Moderator);
line 25 says "One person may hold multiple roles only where explicitly documented by the Product
Owner." `M001_MINIMUM_TEAM_STAFFING_MODELS.md` lines 13–18 use `UNACCEPTABLE` / `NOT RECOMMENDED` /
"Conditionally acceptable with documented evidence separation" / "explicit appointment", and line 32
requires a written evidence-separation procedure. So:

1. V2's `NOT_RECOMMENDED` label actually matches the authoritative packs better than V1's
   `DISCOURAGED`. However, V2 turns an advisory "not recommended" into a **blocking** rule; that
   strictness comes from the audit register's corrections (F-01/F-02), not from the packs.
2. V2's `source` field now cites the **audit defect register** itself. The policy provenance is
   therefore partly self-referential (remediation-driven) rather than purely governance-authoritative.
3. **Invented interpretation — what counts as a valid "Product Owner combination review":** V2
   requires an entry in `combination_approvals` whose `(candidate_ref, pair_key(roles))` exactly
   matches the held roles (sorted set), `outcome="APPROVED"`, `product_owner_approved=true`, non-empty
   `rationale`, timezone-aware `decision_timestamp`, and an `evidence_id` pointing to an evidence
   record with `evidence_type="COMBINATION_REVIEW"`, `verification_status="VERIFIED"`, valid
   `source_ref`, `recording_authority`, 64-hex `content_hash`, and `subject` literally
   `"candidate:PAIRKEY"`. The authoritative packs specify only "explicitly documented/explicitly
   appointed by the Product Owner"; they define none of these field requirements, the subject string
   format, the hash format, or a `decision_timestamp`. This is a V2-invented machine schema, not an
   authoritative policy rule. It is strict (wrong-pair and rejected approvals fail — verified) but it
   does not contradict the source; it over-specifies it.
4. **Invented override mechanism:** none found. There is no waiver/override field in V2 policy or
   schema, hard incompatibilities ignore approvals (§5), and `ca` only relaxes the *discouraged* and
   *conditional* checks — consistent with the source calling those pairs "not recommended" and
   "conditional" rather than "unacceptable".
5. **Policy is partly inert:** a grep of V2 `engine/validator.py` found **no** use of
   `missing_appointment_states`, `require_combination_approval_for_multi_role`, `evidence_fields`,
   `timestamp_fields`, or `review_requirement`; the engine reads `discouraged_combinations[].code` but
   not its `classification` string. The controls are hardcoded in Python. Editing these policy values
   would not change engine behaviour, so "policy as source of truth" is only partially true in V2.

## 7. Residual observations (skeptical reading of the output)

- **R-1 (MEDIUM) — evidence errors do not fail their dimension.** `evidence_check()` (lines 217–246)
  appends `Issue('ERROR', ..., 'evidence_integrity', ...)` but never calls `fail()`; only lines 279–282
  flip dimensions. Demonstrated: forged combination-evidence id → `E-EVIDENCE-UNKNOWN` with
  `evidence_integrity=PASS` and `blocking_error_count=1`; invalid content hash → `E-EVIDENCE-HASH`
  with `evidence_integrity=PASS`. `stage_b_role_ready` is still `false` because line 452 requires
  `not issues`. Consumers reading only `dimensions` can be misled; trust `stage_b_role_ready` and
  `issues`. Direct-loop evidence errors (unverified status, invalid timestamp) *do* call `fail()` and
  do flip `evidence_integrity`.
- **R-2 (LOW)** — policy partly inert / audit register cited as policy source (§6.5, §6.2).
- **R-3 (LOW)** — discouraged code suppressed by a matching but REJECTED approval; another blocking
  code still fires (§4 F-01 nuance).
- **R-4 (INFO)** — hard incompatibilities confirmed unoverridable (§5); positive finding.

## 8. Conclusion

Every original exploit path F-01 … F-16 was independently reproduced in memory against the V2
validator and is now blocked: the emitted codes are ERRORs, the governing Stage B dimension is FAIL,
and `stage_b_role_ready` is `false`. Loader/CLI robustness findings additionally produce stable codes
with exit code 2 and empty stderr. The controls are genuine in source, not merely claimed in the
remediation matrix. Closure is therefore **CLOSED for all 16**, with R-1/R-2/R-3 flagged as residual
quality issues for the consumer of the machine output.
