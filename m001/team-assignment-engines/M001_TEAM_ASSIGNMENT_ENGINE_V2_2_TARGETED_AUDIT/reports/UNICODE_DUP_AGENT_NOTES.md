# M001-TEAM-009 — Independent targeted verification of F-007 and N-08 in V2.2

**Mission:** M001-TEAM-009 (independent security auditor)
**Work directory (only directory written):** `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_2_TARGETED_AUDIT`
**Target (read-only):** `C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_2`
**Date:** 2026-11-28
**Outputs written:** `tests/results/unicode_duplicate_results.json`, `reports/UNICODE_DUP_AGENT_NOTES.md`
**No installs, no network, no writes to V1/V2/V2_1/V2_2/follow-up/git repo.**

## 1. Method and exact commands

The V2.2 validator was imported directly from its read-only path and all states were built in memory by
`copy.deepcopy` of V2.2's own fixture `tests/fixtures/valid_four_person.json`. No V2.2 test, report or
result file was trusted as evidence. Every run used `PYTHONDONTWRITEBYTECODE=1` so no `__pycache__`
was created in the read-only tree. Commands were PowerShell here-strings piped to `python -`; the
common loader block was:

```powershell
$env:PYTHONDONTWRITEBYTECODE=1; @'
import os,json,copy,importlib.util
B=r"C:\Users\pc\AppData\Local\Temp\opencode"
V=os.path.join(B,"M001_TEAM_ASSIGNMENT_ENGINE_V2_2")
spec=importlib.util.spec_from_file_location("vv",os.path.join(V,"engine","validator.py"))
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
pol=v.load_policy(os.path.join(V,"policy","role_constraints.json"))
sch=v.load_schema(os.path.join(V,"schemas","team_assignment.schema.json"))
BASE=json.load(open(os.path.join(V,"tests","fixtures","valid_four_person.json"),encoding="utf-8"))
...
'@ | python -
```

Executed stages (all stdout captured; key lines reproduced below):

1. **Init/inspection** — load validator, policy, schema, fixture; record SHA-256 of validator,
   Python version, `jsonschema` availability. Output:
   `BASELINE ready=True issues=0`; `STAGE1_INIT_OK`.
   Validator SHA-256 recorded in the JSON `meta` block. Python 3.13.5; `jsonschema` available.
2. **F-007 reject group** — 104 cases (18 invisible/whitespace/null/non-string values × basis,
   rationale, contact, candidate_ref, decision_ref, recording_authority). Output:
   `REJECT count=104 mismatches=['nonstring_int_basis','nonstring_int_rationale','nonstring_int_contact']`;
   inspection of those three showed `ready=False codes=['E-SCHEMA']` (fail-closed via schema rather than
   the targeted code), so they were reclassified `OK` with a note.
3. **F-007 meaningful group** — 60 cases (12 meaningful strings × 5 fields). Output:
   `MEANINGFUL count=60 mismatches=[]`, e.g. `english_basis True ready=True codes=[]`.
4. **F-007 boundary + immutability** — 11 boundary cases plus whole-state/string comparison.
   Output lines included `mn_only_acute cats=Mn mt=True ready=True []`,
   `variation_selector_only cats=Mn mt=True ready=True []`,
   `surrogate_escaped_only cats=Cs mt=True ready=True []`,
   `tag_chars_only cats=Cf mt=False ready=False ['E-DECISION-EVIDENCE-EMPTY']`,
   `IMMUTABILITY {"whole_state_identical": true, ...}`; `STAGE4_OK`.
5. **N-08 first 12 cases** — output `STAGE5_N08A_OK count=12`; all 12 `OK`.
6. **N-08 final 6 cases + summary** — output:
   `EXPLOIT_one_po_artifact_two_roles exp=True dup=False ready=True MISMATCH`,
   `EXPLOIT_one_onboarding_artifact_two_roles exp=True dup=False ready=True MISMATCH`,
   `EXPLOIT_one_formal_artifact_two_roles exp=True dup=False ready=True MISMATCH`,
   `N08 {"total":18,"ok":15,"mismatch":3,...}`,
   `BOUNDARY_ACCEPTED [...]`, `IMMUT {... all true ...}`.
7. Final verification read-back: `f007.reject 104`, `f007.meaningful 60`, `f007.boundary 11`,
   `f007.immutability 1`, `n08 18`.

## 2. Algorithm as actually implemented

`engine/validator.py`:

- `NON_CONTENT_CATEGORIES = frozenset(('Cc', 'Cf', 'Zs', 'Zl', 'Zp'))` (line 58).
- `meaningful_text(value)` (lines 61–70): returns `False` for non-`str`; otherwise
  `any(unicodedata.category(ch) not in NON_CONTENT_CATEGORIES for ch in value)`. It only classifies;
  it never strips, normalises or coerces.
- Applied at lines **304** (`recording_authority`), **343** (`decision_ref`), **364** (`candidate_ref`),
  **486** (approval `basis`), **511** (`escalation.contact`), **554** (combination `rationale`).
- N-08 duplicate signature in `validate_state` evidence loop, lines **430–433**:

```python
signature = (rec.get('evidence_type'), rec.get('source_ref'),
             rec.get('recording_authority'), rec.get('timestamp'),
             rec.get('subject'), rec.get('content_hash'),
             rec.get('role'), rec.get('appointment_ref'), rec.get('decision_ref'))
```

`evidence_id` is deliberately excluded (correct). `seen_evidence[signature] = eid`; a second hit emits
`E-EVIDENCE-DUPLICATE` (`evidence_integrity`, ERROR) but does not alter or remove either record.

## 3. F-007 — verdict

### Reproduced: original F-007 is fixed

- All standalone `U+200B`, `U+200E`, `U+2060`, BOM-only, ZWJ-only (`U+200D`), soft hyphen,
  mixed-Cf, ASCII+invisible mixes, ASCII whitespace, NBSP, `U+2028`, `U+2029`, tag characters,
  Arabic Letter Mark and Mongolian Vowel Separator are rejected on **all six** gates:
  `E-DECISION-EVIDENCE-EMPTY`, `E-COMBINATION-RATIONALE`, `E-ESCALATION-CONTACT`,
  `E-CANDIDATE-REF-INVALID`, `E-ACCEPTANCE-DECISION`, `E-EVIDENCE-INCOMPLETE`; readiness `NO`.
- Null fails closed on the predicate; a non-string integer fails closed earlier as `E-SCHEMA`.
- Meaningful content passes with **zero issues** and readiness `YES` for English, accented Latin,
  Hindi including conjunct+virama (`क् + ष = क्ष`), Arabic RTL with and without legitimate LRM/RLM,
  ZWJ emoji (`👩‍💻`, `👨‍👩‍👧‍👦`), meaningful text containing Cf marks, `U+FE0F` alongside real content,
  and decomposed `e + U+0301`. No false positive was found among the required meaningful scripts.
- Original strings are not modified: whole-state deep equality `true`; basis, rationale, contact,
  candidate_ref, decision_ref and source_ref all unchanged after `validate_state`.

### Not reproduced

The original V2.1 failure (invisible-only basis/rationale yielding Stage B YES with zero issues) could
not be reproduced on V2.2 for any tested Cf/Zs/Zl/Zp-only string.

### New residual defect candidates (F-007 scope, not the original finding)

`meaningful_text` equates "non-Cc/Cf/Zs/Zl/Zp" with "visually substantive". Seven tested strings that
have no base letter are accepted with Stage B YES and zero issues:

| Case | Categories | `meaningful_text` | Result |
|---|---|---|---|
| combining acute only (`U+0301`×5) | Mn | True | accepted |
| Devanagari vowel-sign aa only (`U+093E`×3) | Mc | True | accepted |
| enclosing circle only (`U+20DD`×3) | Me | True | accepted |
| private use only (`U+E000`×3) | Co | True | accepted |
| unassigned only (`U+0378`×3) | Cn | True | accepted |
| lone surrogates from JSON escapes (`\ud800`×3) | Cs | True | accepted |
| variation selectors only (`U+FE0F`×3) | Mn | True | accepted |

This is a real fail-open of the decision-text gates: an approval basis consisting solely of floating
diacritics, private-use/unassigned code points, escaped lone surrogates or variation selectors passes.
It is **not** the canonical F-007 (which concerned Cf format characters) and does not reopen it; it is a
new "non-base-character content" weakness. A string containing real content plus `U+2028` is correctly
accepted (`Ll,Lu,Zl,Zs`), so the remediation did not over-reject legitimate text.

## 4. N-08 — verdict (18 cases; 15 OK, 3 MISMATCH)

### Reproduced: original N-08 core is fixed

| Case | Expected | Observed | Class |
|---|---|---|---|
| `exact_duplicate_acceptance` | duplicate | `E-EVIDENCE-DUPLICATE`, ready NO | reproduced fixed |
| `identical_content_different_ids` (PO approval clone; evidence_id excluded) | duplicate | `E-EVIDENCE-DUPLICATE`, ready NO | reproduced fixed |
| `ambiguous_null_hash` (two records with `content_hash=None`) | duplicate | `E-EVIDENCE-DUPLICATE`, ready NO | reproduced fixed |
| `reversed_insertion_order` | duplicate | duplicate still detected, ready NO | OK |
| `evidence_state_immutable_before_after` | evidence unchanged | `state_unchanged=True` | OK |
| `deterministic_repeat` | identical result | `to_dict()` identical across two runs | OK |

### Not reproduced / by design (no normalisation, no silent provenance loss)

| Case | Expected | Observed | Interpretation |
|---|---|---|---|
| `crlf_vs_lf_source_ref` | not duplicate | no duplicate code, ready YES | no string normalisation; consistent with "no silent provenance loss" |
| `nfc_vs_nfd_source_ref` | not duplicate | no duplicate code, ready YES | same; Unicode-equivalent identifiers remain a known OPEN residual in V2.2's own register |
| `whitespace_only_difference` (trailing space in authority) | not duplicate | no duplicate code, ready YES | exact-string semantics |
| `different_content_same_metadata` (different hash+source_ref) | not duplicate | no duplicate code, ready YES | correct: genuinely distinct artifact |
| `genuinely_distinct_acceptance` (different role-bound subject/decision/source/hash) | not duplicate | no duplicate code, ready YES | no false rejection of distinct evidence |
| `inconsistent_source_metadata` (same source_ref, different timestamp/authority) | not duplicate | no duplicate code, ready YES | signature compares metadata; contradiction itself is separate N-07/N-09 territory, not duplication |
| `canonical_tuple_role_tweak` / `_decisionref_tweak` / `_appointmentref_tweak` | not duplicate | no duplicate code | expected under V2.2's 9-field signature; see new defect below |

Hash collisions: a practical SHA-256 collision was not constructible; with `content_hash=None` two
records collapse onto the same signature and are flagged (conservative ambiguity handling), which is
the only practical ambiguity case and is recorded above.

### New defect found — N-08 bypass for non-acceptance evidence (3 variants, MISMATCH)

The canonical N-08 remediation (V2 re-audit register and V2.1 follow-up triage) specifies the semantic
tuple `(evidence_type, source_ref, recording_authority, timestamp, subject, content_hash)`. V2.2 added
`role`, `appointment_ref` and `decision_ref` to that tuple. For `PRODUCT_OWNER_APPROVAL`,
`FORMAL_APPOINTMENT` and `ONBOARDING` evidence, `evidence_check` only enforces `subject` (the candidate
ref); it does **not** validate the record's `role`, `appointment_ref` or `decision_ref`. Therefore an
attacker can deep-copy one such artifact under a second ID, change only its `role` field, and thereby
change the signature while leaving the six canonical fields identical. Replacing the genuine
`CONTINUE_STOP_OWNER` record with that clone and repointing the role's evidence_id yields:

- `EXPLOIT_one_po_artifact_two_roles`: `duplicate_detected=False`, `ready=True`, codes `[]`
- `EXPLOIT_one_onboarding_artifact_two_roles`: `duplicate_detected=False`, `ready=True`, codes `[]`
- `EXPLOIT_one_formal_artifact_two_roles`: `duplicate_detected=False`, `ready=True`, codes `[]`

This is exactly the canonical N-08 harm — "one underlying approval/onboarding artifact reused for two
roles" — still achievable for non-acceptance evidence. The same class of bypass applies to
`decision_ref` and `appointment_ref` tweaks (confirmed by the three `canonical_tuple_*` cases, which
show those fields alone change the signature). CANDIDATE_ACCEPTANCE is protected because its subject,
role and appointment_ref are role-bound and enforced.

**Recommendation:** compute the duplicate signature over the canonical six fields only (optionally add
`evidence_id` exclusion explicitly), and enforce role binding for non-acceptance evidence rather than
using unvalidated role fields as a distinction. Do not rely on mutable, unchecked metadata as a
duplicate-discriminator.

## 5. Policy basis for "duplicate"

- Canonical N-08 (`M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT/M001_FINAL_DEFECT_REGISTER.json`, lines 100–107):
  "Duplicate evidence records under different IDs are not detected"; reproduction `EVID-04`, identical
  evidence under `e-acc-C-P1-P1-copy`; observed `stage_b_role_ready=True, issues=[]`.
- `M001_TEAM_ASSIGNMENT_ENGINE_V2_1_FOLLOWUP/analysis/lower_severity_triage.json` (N-08): one
  underlying artifact must not appear under two IDs; recommended registry-level duplicate detection
  over `(evidence_type, source_ref, recording_authority, timestamp, subject, content_hash)` with
  `E-EVIDENCE-DUPLICATE`; also notes copies reusable across roles of one candidate when evidence is
  bound only to the candidate.
- Role/staffing packs (`M001_RESEARCH_ROLE_CHARTER.md`, `M001_MINIMUM_TEAM_STAFFING_MODELS.md`) require
  per-role evidence and evidence-type separation (Moderator+Note-taker only with documented separation;
  RO+CS only with explicit separate appointment), which is why one artifact reused for two roles is a
  governance defect.
- Canonical F-007 (`M001_FOLLOWUP_DEFECT_REGISTER.json`, lines 19–26): invisible Unicode format
  characters (`U+200B`, `U+200E`, `U+2060`) satisfy `meaningful_text()`; residual variant of N-01/N-02.

## 6. Overall classification

| Finding | Status |
|---|---|
| F-007 canonical (Cf-only basis/rationale/contact/ref) | **Not reproduced** — fixed across all six gates; no input mutation |
| F-007 new boundary weakness (Mn/Mc/Me/Co/Cn/Cs/FE0F-only text) | **Reproduced** — new defect candidate, MEDIUM-worthy |
| N-08 canonical exact duplicate under second ID | **Not reproduced** — fixed; `E-EVIDENCE-DUPLICATE` emitted |
| N-08 distinct-evidence false rejection / immutability / determinism | **Not reproduced** — all checks OK |
| N-08 new 9-field-signature bypass via unchecked `role` on non-acceptance evidence | **Reproduced** — new defect candidate, 3 variants; Stage B YES with zero issues |
| CRLF/LF, NFC/NFD, whitespace-only, inconsistent metadata | **Inconclusive / by design** — not flagged; no normalisation rule exists in policy, so not classified as a confirmed defect |
