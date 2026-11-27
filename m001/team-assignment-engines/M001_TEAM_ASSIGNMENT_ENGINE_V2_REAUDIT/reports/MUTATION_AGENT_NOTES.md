# Independent Mutation Audit Notes — M001-TEAM-005 (M001 V2 re-audit)

**Role:** independent subagent auditor. **Date:** 2026-11-27.
**Workspace:** `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT`

**State of record (important):** there were two harness executions. The
**first** produced 30 introduced / 28 detected / **2 survived** (M05 and M28)
and is reproduced verbatim in §2.1; the two survivors are analysed in §4 with
the exact requested findings. After that triage I strengthened my own canary
(`A42`, `A43`, `A00`) and re-ran, so the results JSON **currently on disk**
records the **final** execution: 30 introduced / 30 detected / 0 survived,
44/44 baseline (§2.4). The first-run numbers/output are preserved here in
§2.1 and §4; they are not lost, but they are no longer the contents of the
machine-readable file.

## 1. Boundaries and method

- V1 (`...\M001_TEAM_ASSIGNMENT_ENGINE`), the prior audit
  (`...\M001_TEAM_ASSIGNMENT_ENGINE_AUDIT`), V2
  (`...\M001_TEAM_ASSIGNMENT_ENGINE_V2`) and the git repo were **read only**.
  All writes are inside the REAUDIT workspace.
- I authored `mutation/independent_mutation_harness.py` and
  `mutation/independent_canary.py` from scratch. I read V2's
  `tests/mutation/mutation_harness.py` and `mutation_canary.py` only to
  understand the target; no code from them is imported, copied or reused as
  proof. My canary has 44 properties (V2's has 18) and covers parser,
  evidence, timestamp-ordering, candidate-identity, appointment-formality and
  diagnostic-completeness invariants V2's canary does not check.
- For every mutant the harness copies only `engine/`, `policy/`, `schemas/`
  and `tests/fixtures/` from V2 into
  `REAUDIT/mutation/independent_mutants/<mutant_name>/`, excluding
  `__pycache__`, `*.pyc` and `mutants`. The destination is never a descendant
  of a copied source, so the recursive-copy bug of the original V1 harness
  cannot recur. Each introduced mutant applies **one** controlled textual
  change (or one policy-list change); a patch must match exactly once or the
  mutant is rejected and excluded.
- The canary imports the validator exclusively from `--root`
  (`sys.path.insert(0, root); from engine import validator as V`) and loads
  policy/schema from that root. Fixtures are the unmodified V2 copies under
  `<root>/tests/fixtures` plus **my own** 13 adversarial fixtures generated
  into `REAUDIT/mutation/fixtures` (outside every mutant tree). The canary
  exits 0 only if all properties pass; it also fails explicitly if the
  validator raises on any fixture (`A00`).

## 2. Commands and outputs (verbatim, abbreviated only where noted)

All shell commands were run with working directory
`C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT\mutation`.

### 2.1 First baseline + first harness run

```
python independent_mutation_harness.py
```
```
BASELINE_EXIT 0
CANARY_PASS 41/41
INTRODUCED 30 DETECTED 28 SURVIVED 2 EXCLUDED 3
...
SURVIVED M05_evidence_unverified_bypass exit=0
...
SURVIVED M28_unapproved_appointment_bypass exit=0
EXCLUDED X01_stage_b_topology_redundant | EXCLUDED: semantically equivalent under shipped policy; canary survived and differential comparison found no observable difference on 41 inputs
EXCLUDED X02_patch_target_absent | EXCLUDED: patch target not found (patch target occurrences=0 (expected exactly 1))
EXCLUDED X03_comment_only_noop | EXCLUDED: semantically equivalent under shipped policy; canary survived and differential comparison found no observable difference on 41 inputs
```
M02 exited 1 but produced **no** FAIL line; its stderr was:
```
TypeError: can't compare offset-naive and offset-aware datetimes
  ... validator.py, line 362, in validate_state
      if ts_a and ts_p and ts_f and not (ts_a <= ts_p <= ts_f):
```

### 2.2 Manual triage of the two survivors (see §4)

```
python -c "import sys, json, importlib.util; from pathlib import Path
R=Path(r'...\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT'); V2=R.parent/'M001_TEAM_ASSIGNMENT_ENGINE_V2'
def load(label,p):
 s=importlib.util.spec_from_file_location(label,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
base=load('base',V2/'engine'/'validator.py')
m05=load('m05',R/'mutation'/'independent_mutants'/'M05_evidence_unverified_bypass'/'engine'/'validator.py')
m28=load('m28',R/'mutation'/'independent_mutants'/'M28_unapproved_appointment_bypass'/'engine'/'validator.py')
x01=load('x01',R/'mutation'/'independent_mutants'/'X01_stage_b_topology_redundant'/'engine'/'validator.py')
P=base.load_policy(); S=base.load_schema()
orphan=R/'mutation'/'fixtures'/'orphan_unverified_evidence.json'; d=base.load_json_strict(orphan)
for label,m in [('BASE',base),('M05',m05)]:
 r=m.validate_state(d,P,S); print('M05-MANUAL',label,'stage_b=',r.stage_b_role_ready,'errors=',[i.code for i in r.errors])
d2=base.load_json_strict(V2/'tests'/'fixtures'/'rejected_active_appointment.json')
for label,m in [('BASE',base),('M28',m28)]:
 r=m.validate_state(d2,P,S); print('M28-MANUAL',label,'stage_b=',r.stage_b_role_ready,'codes=',[i.code for i in r.errors])
...
```
```
M05-MANUAL BASE stage_b= False errors= ['E-EVIDENCE-UNVERIFIED']
M05-MANUAL M05 stage_b= True errors= []
M28-MANUAL BASE stage_b= False codes= ['E-APPOINTMENT-MISSING', 'E-UNAPPROVED-APPOINTMENT']
M28-MANUAL M28 stage_b= False codes= ['E-APPOINTMENT-MISSING']
X01-MANUAL baseline_fp= 43bff7c1305d781ead6680ef391d7f810d068d6bdcdff0a9e1332712d6f05c00
X01-MANUAL mutant_fp= 43bff7c1305d781ead6680ef391d7f810d068d6bdcdff0a9e1332712d6f05c00
```

### 2.3 Final baseline canary (direct command)

```
python independent_canary.py --root "C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2"
```
All 44 checks print `PASS`; final line:
```
CANARY_PASS 44/44
```
Exit code `0`. Notable checks: `A08` revoked combination approval, `A11`
combination timestamp, `A12` six non-formal roles, `A21/A22` both distinct
candidate-uniqueness messages, `A36` duplicate JSON key, `A42` orphan
unverified evidence, `A43` unapproved appointment record, `A00` no crash.

### 2.4 Final harness run

```
python independent_mutation_harness.py
```
```
BASELINE_EXIT 0
CANARY_PASS 44/44
INTRODUCED 30 DETECTED 30 SURVIVED 0 EXCLUDED 3
DETECTED M01_duplicate_json_key_parser_bypass exit=1 A36
DETECTED M02_valid_timestamp_naive_bypass exit=1 A11,A30,A00
DETECTED M03_role_timestamp_field_bypass exit=1 A30,A31
DETECTED M04_evidence_subject_bypass exit=1 A27,A28
DETECTED M05_evidence_unverified_bypass exit=1 A42
DETECTED M06_candidate_key_reference_substitution exit=1 A21,A22
DETECTED M07_duplicate_candidate_identity_bypass exit=1 A22
DETECTED M08_role_unknown_candidate_bypass exit=1 A23
DETECTED M09_appointment_unknown_candidate_bypass exit=1 A24
DETECTED M10_authorization_boundary_bypass exit=1 A35
DETECTED M11_topology_approval_bypass exit=1 A33
DETECTED M12_formal_state_bypass exit=1 A12,A13,A14
DETECTED M13_formal_state_policy_bypass exit=1 A12,A13
DETECTED M14_candidate_acceptance_bypass exit=1 A19
DETECTED M15_role_po_approval_bypass exit=1 A17
DETECTED M16_formal_approval_flag_bypass exit=1 A15
DETECTED M17_approval_basis_bypass exit=1 A18
DETECTED M18_formal_record_bypass exit=1 A16
DETECTED M19_onboarding_bypass exit=1 A20
DETECTED M20_combination_approval_missing_bypass exit=1 A04,A06,A07
DETECTED M21_combination_outcome_revocation_bypass exit=1 A08
DETECTED M22_combination_po_approval_bypass exit=1 A09
DETECTED M23_combination_rationale_bypass exit=1 A10
DETECTED M24_combination_timestamp_bypass exit=1 A11
DETECTED M25_discouraged_combination_bypass exit=1 A03
DETECTED M26_hard_incompatibility_bypass exit=1 A01,A02
DETECTED M27_evidence_separation_bypass exit=1 A05
DETECTED M28_unapproved_appointment_bypass exit=1 A43
DETECTED M29_timestamp_order_bypass exit=1 A32
DETECTED M30_hard_incompatibility_policy_removal exit=1 A02
EXCLUDED X01_stage_b_topology_redundant | EXCLUDED: semantically equivalent under shipped policy; canary survived and differential comparison found no observable difference on 42 inputs
EXCLUDED X02_patch_target_absent | EXCLUDED: patch target not found (patch target occurrences=0 (expected exactly 1))
EXCLUDED X03_comment_only_noop | EXCLUDED: semantically equivalent under shipped policy; canary survived and differential comparison found no observable difference on 42 inputs
RESULTS C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT\mutation\results\independent_mutation_results.json
```

### 2.5 Spot checks of individual canary runs

```
python independent_canary.py --root "...\independent_mutants\M05_evidence_unverified_bypass" | Select-String '^FAIL|^CANARY_PASS'
```
```
FAIL A42 unreferenced unverified evidence still blocked | MISSING E-EVIDENCE-UNVERIFIED | - | stage_b=True
CANARY_PASS 43/44
```
```
python independent_canary.py --root "...\independent_mutants\X01_stage_b_topology_redundant" | Select-String '^FAIL|^CANARY_PASS'
```
```
CANARY_PASS 44/44
```

## 3. Mutation coverage (30 introduced, all detected)

| Mutant | Required category | Single change | Detected by |
|---|---|---|---|
| M01 | duplicate-key parser bypass | `if k in out:` → `if False and k in out:` in `no_dupes` | A36 |
| M02 | timestamp bypass | `valid_timestamp` returns `True` unconditionally | A11, A30, A00 |
| M03 | timestamp bypass | per-role timestamp-field guard disabled | A30, A31 |
| M04 | evidence-subject validation removal | `if subject and record.get('subject') != subject:` disabled | A27, A28 |
| M05 | evidence validation removal (bonus) | global verification-status guard disabled | A42 |
| M06 | candidate-reference substitution | `if ref != key or not ref:` → `if not ref:` | A21, A22 |
| M07 | duplicate candidate identity | `if ref in seen:` disabled (second guard alone) | A22 |
| M08 | candidate-reference substitution | role-loop `if ref not in candidates:` disabled | A23 |
| M09 | candidate-reference substitution | appointment-loop `if ref not in candidates:` disabled | A24 |
| M10 | authorization-boundary bypass | field-validation half of governance guard dropped | A35 |
| M11 | topology-approval bypass | explicit topology gate disabled | A33 |
| M12 | formal-state bypass | `if st not in formal_states:` disabled | A12, A13, A14 |
| M13 | formal-state bypass | policy adds `ACCEPTED_IN_CONVERSATION` to formal states | A12, A13 |
| M14 | candidate-acceptance bypass | `candidate_accepted` guard disabled | A19 |
| M15 | approval check removal | role-level PO approval guard disabled | A17 |
| M16 | approval revocation/basis removal | `appr['formal'] is not True` guard disabled | A15 |
| M17 | approval revocation/basis removal | empty `basis` guard disabled | A18 |
| M18 | formal-state bypass (bonus) | `formally_appointed` guard disabled | A16 |
| M19 | onboarding bypass | `onboarding.completed` guard disabled | A20 |
| M20 | removal of combination-approval checks | exact-combination `if not ca:` guard disabled | A04, A06, A07 |
| M21 | approval revocation/basis removal | combination `outcome != 'APPROVED'` guard disabled | A08 |
| M22 | removal of combination-approval checks | combination PO-flag guard disabled | A09 |
| M23 | removal of combination-approval checks | combination rationale guard disabled | A10 |
| M24 | timestamp bypass | combination decision-timestamp guard disabled | A11 |
| M25 | discouraged-combination bypass | discouraged-without-review guard disabled | A03 |
| M26 | removal of combination-approval checks | hard-incompatibility guard disabled | A01, A02 |
| M27 | removal of combination-approval checks (bonus) | conditional evidence-separation guard disabled | A05 |
| M28 | formal-state bypass | appointment-backed-by-formal-role guard disabled | A43 |
| M29 | timestamp bypass | decision-order guard disabled | A32 |
| M30 | removal of combination-approval checks | policy deletes `MODERATOR+DATA_CUSTODIAN` rule | A02 |

All 12 required categories are covered. Several categories have multiple
independently applied mutants so that a single guard cannot hide another
(e.g. M06/M07/M08/M09, M02/M03/M24/M29, M12/M13/M18/M28).

## 4. Survivor verification (independent, requirement 5)

The **first** run had two surviving introduced mutants. I did not simply
declare them equivalent; I examined the code paths and ran the manual
comparisons in §2.2.

### 4.1 M05 — real surviving defect (canary blind spot), now detected

- Mutation: `engine/validator.py:307`,
  `if rec.get('verification_status') not in policy['verification_statuses']:`
  → `if False and ...`, i.e. removal of the **global evidence verification
  gate** in the evidence loop of `validate_state`.
- My initial extra fixture made a **referenced** evidence record unverified.
  `evidence_check()` independently emits `E-EVIDENCE-UNVERIFIED`, so the
  canary still passed. Manual check showed the two guards are NOT equivalent:
  `evidence_check()` only runs for evidence ids referenced by an
  acceptance/approval/formal/onboarding/combination record. A **dangling /
  orphan PENDING evidence record** has no such second guard: the differential
  probe changes readiness.
- Manual proof (§2.2): with `orphan_unverified_evidence.json` (a dangling
  evidence record whose `verification_status` is `PENDING`), baseline gives
  `stage_b=False, errors=['E-EVIDENCE-UNVERIFIED']`; M05 gives
  `stage_b=True, errors=[]`. The dangling PENDING evidence therefore flips
  Stage B readiness — a genuine decision-level weakening and a real canary
  coverage gap, not semantic equivalence.
- Fix: added fixture `orphan_unverified_evidence.json` and property `A42`.
  Final run: M05 detected (`CANARY_PASS 43/44`, FAIL A42, `stage_b=True`).

### 4.2 M28 — decision-equivalent under the shipped schema, but not
### diagnostic-equivalent; now detected by an explicit diagnostic property

- Mutation: `engine/validator.py:393`,
  `if role_records.get(role,{}).get('state') not in formal_states:`
  → `if False and ...`, removal of the appointment formal-state guard
  (`E-UNAPPROVED-APPOINTMENT`).
- Manual analysis: for any appointment whose role has a non-formal state, the
  earlier role loop already emits `E-APPOINTMENT-MISSING` for that same role
  (and the schema requires all six role records to be present). Therefore the
  **Stage B decision is still blocked** by another guard: `stage_b=False` in
  both baseline and mutant (§2.2). At the decision level this mutation is
  semantically equivalent under the shipped schema/policy.
- It is **not** output-equivalent: baseline reports two independent errors
  (`E-APPOINTMENT-MISSING`, `E-UNAPPROVED-APPOINTMENT`, the latter tied to the
  appointment's role and candidate); M28 reports only the first. For an audit
  tool the missing appointment-level record is a real diagnostic loss, so I
  did **not** accept the survivor. I added property `A43` requiring the
  appointment-level error explicitly. Final run: M28 detected (FAIL A43).
- Honest caveat: if only positive authorization mattered, M28 could fairly be
  called equivalent; my canary deliberately treats loss of an independent
  blocking diagnostic as a defect.

### 4.3 M02 — detected by crash on the first run; hardened afterwards

- Mutation: `valid_timestamp()` returns `True` for any non-empty string.
  The first canary aborted with `TypeError` while comparing a now-naive
  datetime with aware datetimes in the ordering guard; exit was 1 (detected),
  but no named property failed. I added `A00` and a `_Broken` stand-in so the
  canary records the crash as a failed property and continues checking the
  remaining invariants. Final run: FAILs A11, A30 and A00. The mutation is a
  genuine defect (naive timestamps both accepted and then crash the
  validator), not an equivalent mutation.

## 5. Excluded mutations and reasons

| ID | Reason | Evidence |
|---|---|---|
| X01 `stage_b_topology_redundant` | **Semantically equivalent under shipped policy.** Removing `topology.get('status')=='APPROVED'` from the final `stage_b` expression changes nothing: with `require_topology_approved_for_stage_b=true`, a PROPOSED topology always triggers `E-TOPOLOGY-UNAPPROVED`, which sets `dims['structural_topology_validity']='FAIL'` and adds an issue, so `all(dims==PASS) and not issues` is already False. Canary exit 0 (44/44) and differential fingerprint identical on all 42 fixtures/inputs (SHA-256 `43bff7c1...5c00`). Caveat: if the policy flag were false, this edit would be a real defect — the equivalence is conditional on the shipped policy. | results JSON `excluded[0].differential` |
| X02 `patch_target_absent` | **Invalid mutation.** Patch target `if governance.get('recruitment') == 'AUTHORIZED':` occurs 0 times (the real guard is `!= 'UNAUTHORIZED' or field_validation != 'NOT_STARTED'`). Harness rejected it before creating a mutant. | `patch_occurrences=0` |
| X03 `comment_only_noop` | **No semantic effect.** Comment-only edit to `# No positive authorization may be inferred.`. Canary exit 0 and differential identical on all 42 inputs. | results JSON `excluded[2].differential` |

The harness applies a differential comparator to every exclusion that can be
applied: it loads baseline and mutant validators under distinct module names
and compares loader outcomes plus full `ValidationResult.to_dict()` for all
42 available input files. This is an extra independent check beyond the
canary's property assertions.

## 6. Conclusion

- Baseline canary: **44/44 PASS, exit 0** on the untouched V2 tree.
- Introduced mutations: **30**, covering all 12 required bypass categories.
- Detected: **30/30**. Surviving introduced mutants in the final run: **0**.
- Excluded with documented reasons: **3** (two equivalent, one invalid patch).
- Independent survivor triage found one **real canary blind spot** (M05) and
  one **decision-equivalent but diagnostically real** defect (M28); both were
  fixed by strengthening my own canary rather than by relaxing the mutant set.
- Caveat on mutation testing generally: 100% detection shows these 30
  specific guards are covered by my 44 properties; it does not prove the
  absence of other defects. In particular the equivalence of X01 is
  conditional on the shipped policy file, and the diagnostic-vs-decision
  distinction for M28 is a deliberate policy of this audit.

## 7. Deliverables

- `mutation/independent_mutation_harness.py` — harness (mutant builder, canary
  runner, differential comparator, results writer).
- `mutation/independent_canary.py` — 44-property canary, `--root` driven.
- `mutation/results/independent_mutation_results.json` — machine-readable
  baseline, every command, full stdout/stderr, per-mutant failure lines and
  exclusion reasons.
- `reports/MUTATION_AGENT_NOTES.md` — this narrative.
- Generated inside REAUDIT only: `mutation/fixtures/` (13 fixtures),
  `mutation/independent_mutants/` (34 disposable trees incl. exclusions),
  `mutation/results/` (results JSON).
