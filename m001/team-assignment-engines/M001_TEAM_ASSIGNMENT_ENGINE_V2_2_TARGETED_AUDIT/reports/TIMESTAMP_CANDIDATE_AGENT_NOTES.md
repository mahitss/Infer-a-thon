# M001-TEAM-009 — Independent targeted verification of N-11 and N-12 in V2.2

**Auditor role:** independent security subagent (no trust in V2.2's own reports, tests or result JSON).
**Working boundary:** all writes confined to `M001_TEAM_ASSIGNMENT_ENGINE_V2_2_TARGETED_AUDIT`; only the two declared output files were written. V1/V2/V2_1/V2_2/follow-up/git repo were read only. `PYTHONDONTWRITEBYTECODE=1` on every Python invocation. No installs, no network.

**Declared outputs**
- `tests/results/timestamp_candidate_results.json` (49 case records, probes, source review, new defect register)
- `reports/TIMESTAMP_CANDIDATE_AGENT_NOTES.md` (this file)

---

## 1. Method and environment

The V2.2 validator was **imported from its read-only path** with `importlib.util.spec_from_file_location`; policy/schema were loaded from their read-only V2.2 paths; the fixture `valid_five_person.json` was loaded once and every case ran against an independent `copy.deepcopy`. No V2.2 test, expected-value table or result JSON was consulted for the verdict.

Fingerprints recorded in the JSON:
- engine `validator.py` SHA-256 `baa3634df3a82f9ecff158552f263843f97372dadbc16e0d65d6c6d884bc5b5f`
- fixture `valid_five_person.json` SHA-256 `ae7ad33b6c6dce3fa0759f9ac2952275891ba42fd50512994082460601172f85`
- Python `3.13.5`, `jsonschema 4.26.0` available (so full Draft 2020-12 schema validation is active, not the subset fallback), `PYTHONDONTWRITEBYTECODE=1`.

Baseline verification (unmodified fixture) produced `stage_b_role_ready=True`, 0 errors, 0 warnings, all eight dimensions PASS. This confirms the mutation base is a clean passing state.

### Exact commands (principal runs)

Environment / discovery (PowerShell, working directory irrelevant for absolute paths):

```
$env:PYTHONDONTWRITEBYTECODE=1; python -c "import sys,jsonschema; print(sys.version); print('jsonschema',jsonschema.__version__)"
```
Output: `3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)]` / `jsonschema 4.26.0` (plus a `__version__` DeprecationWarning).

```
$env:PYTHONDONTWRITEBYTECODE=1; Select-String -Path "...\V2_2\engine\validator.py" -Pattern "now\(|utcnow|today|datetime\.|candidate_ref|decision_timestamp|combination_approvals" | ForEach-Object { "{0}: {1}" -f $_.LineNumber, $_.Line.Trim() }
```
Output: only `datetime.fromisoformat` at lines 261 and 270; all `candidate_ref` sites at 361, 469, 522, 536, 547, 550, 552, 556, 562, 566, 576, 584; `decision_timestamp` at 567 and 569; `combination_approvals` at 540. **No `now()`, `utcnow()` or `today()` call exists.**

All behavioural runs used the same invocation shape (PowerShell single-quoted here-string piped to `python -`, so no helper script file was created):

```
$env:PYTHONDONTWRITEBYTECODE=1; @'
<python harness source>
'@ | python -
```

Three harness passes were executed: (a) baseline + full case matrix, (b) deeper edge probes, (c) defect-confirmation and results-file update, followed by a JSON re-parse verification. Full per-case mutation descriptors, expectations and observed issue lists are stored verbatim in `tests/results/timestamp_candidate_results.json`; the console output of pass (a) is reproduced in §4.

---

## 2. Source review — exact implementation

### N-11 (combination decision timestamp ordering) — `validator.py` lines 540–585

```python
decision_ts = parse_timestamp(ca.get('decision_timestamp'))       # 567
if decision_ts is None:
    fail('product_owner_combination_approval','E-TIMESTAMP-INVALID', ... )  # 568-569
else:
    accepted = []
    for role_name in ca.get('roles', []):
        rr = role_records.get(role_name, {})
        if rr.get('candidate_ref') != ca.get('candidate_ref'):
            continue
        t = parse_timestamp(rr.get('acceptance', {}).get('candidate_accepted_at'))
        if t is not None:
            accepted.append(t)
    if accepted and decision_ts < max(accepted):                   # 581
        fail('product_owner_combination_approval',
             'E-COMBINATION-APPROVAL-TIMESTAMP-ORDER', ... )      # 582-585
```

- Ordering predicate is strict `<` against `max(accepted)`: a decision must be **at or after the latest acceptance** among the roles the candidate actually holds in `ca.roles` (`>=` semantics at equality).
- Error codes/dimensions:
  - invalid/naive/missing decision timestamp → `E-TIMESTAMP-INVALID`, dimension `product_owner_combination_approval`;
  - ordering violation → `E-COMBINATION-APPROVAL-TIMESTAMP-ORDER`, dimension `product_owner_combination_approval`.
  - (Separate, role-level chain `E-TIMESTAMP-ORDER` in `formal_appointment_validity` at lines 491–499 enforces `accepted <= approved <= formal`.)
- Timezone awareness: `valid_timestamp` (257–264) and `parse_timestamp` (267–270) reject any value without `tzinfo`/`utcoffset`; `datetime.fromisoformat` yields aware datetimes and Python compares them by absolute instant, not by wall-clock text. Direct probe: `parse_timestamp("2026-11-27T02:00:00+00:00") == parse_timestamp("2026-11-27T03:00:00+01:00")` → `True`; neither is `<` the other.
- Current-time substitution: none. The verdict is a pure function of stored fields (N11-02 past decision rejected, N11-16 year-2099 decision accepted).
- Schema terminal handling: `decision_timestamp` is required (schema line 133) but typed `["string","null"]` (line 141); a removed key stops at `E-SCHEMA`, a `null` reaches the validator and produces `E-TIMESTAMP-INVALID`. Non-string values stop at `E-SCHEMA`.

### N-12 (candidate-reference validity) — `validator.py` lines 355–375, 61–70

```python
NON_CONTENT_CATEGORIES = frozenset(('Cc','Cf','Zs','Zl','Zp'))       # 58
def meaningful_text(value):                                         # 61-70
    return isinstance(value,str) and any(
        unicodedata.category(ch) not in NON_CONTENT_CATEGORIES for ch in value)

def candidate_registry_check(candidates, policy, issues):           # 355-375
    for key, rec in candidates.items():
        ref = rec.get('candidate_ref')
        if not meaningful_text(ref) or (isinstance(ref,str) and ref != ref.strip()):
            issues.append(Issue('ERROR','E-CANDIDATE-REF-INVALID',...))
        if ref != key or not ref:
            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE',...))
        if ref in seen:
            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE',...))
        seen[ref] = rec
        if rec.get('active') is not True: ... E-CANDIDATE-INACTIVE
```

- Exact string equality against the registry key; **no** `lower()`, `casefold()` or `unicodedata.normalize()` anywhere. Distinct identities (case variants, NFC/NFD, fullwidth) remain distinct.
- `candidate_ref` in the candidate schema is `{"type":"string"}` (line 50), so `null`/numbers terminate at `E-SCHEMA` before the registry loop; no unhashable `ref` can reach `ref in seen`.
- All `candidate_ref` consumption sites inspected: registry check (361), role-record lookup (469–471), appointment lookup (522–528), formal-role/appointment reconciliation (534–538), `identity_subject` and evidence subject binding (73–75, 328–341, 565–566), and `cli/validate.py` (pass-through only).
- Note: `E-CANDIDATE-DUPLICATE` is also used for key/reference mismatch, not only for duplicate identities — naming observation, not a security defect.

---

## 3. Classification legend

- **reproduced-secure** — expected secure behaviour observed (invalid input rejected, valid input accepted, no crash, deterministic boundary).
- **defect** — observed behaviour contradicts the stated requirement.
- **inconclusive** / **not-applicable** — none occurred in this run.

---

## 4. Case results

Console output of the main harness (all 45 initial cases):

```
TOTAL 45 SECURE 45 DEFECT 0
N11-01     reproduced-secure  READY codes=-
N11-02     reproduced-secure  BLOCK codes=E-COMBINATION-APPROVAL-TIMESTAMP-ORDER
N11-03     reproduced-secure  BLOCK codes=E-COMBINATION-APPROVAL-TIMESTAMP-ORDER
N11-04     reproduced-secure  READY codes=-
N11-05     reproduced-secure  BLOCK codes=E-TIMESTAMP-INVALID
N11-06     reproduced-secure  BLOCK codes=E-SCHEMA
N11-07     reproduced-secure  BLOCK codes=E-TIMESTAMP-INVALID
N11-08     reproduced-secure  READY codes=-
N11-09     reproduced-secure  READY codes=-
N11-10     reproduced-secure  BLOCK codes=E-COMBINATION-APPROVAL-TIMESTAMP-ORDER
N11-11     reproduced-secure  READY codes=-
N11-12.1   reproduced-secure  BLOCK codes=E-TIMESTAMP-INVALID
N11-12.2   reproduced-secure  BLOCK codes=E-TIMESTAMP-INVALID
N11-12.3   reproduced-secure  BLOCK codes=E-TIMESTAMP-INVALID
N11-12.4   reproduced-secure  BLOCK codes=E-TIMESTAMP-INVALID
N11-13     reproduced-secure  BLOCK codes=E-COMBINATION-APPROVAL-TIMESTAMP-ORDER,E-TIMESTAMP-ORDER
N11-14     reproduced-secure  BLOCK codes=E-COMBINATION-APPROVAL-TIMESTAMP-ORDER
N11-15     reproduced-secure  BLOCK codes=E-TIMESTAMP-MISSING
N11-16     reproduced-secure  READY codes=-
N11-17     reproduced-secure  READY codes=-
N12-01     reproduced-secure  READY codes=-
N12-02     reproduced-secure  BLOCK codes=E-CANDIDATE-DUPLICATE,E-CANDIDATE-REF-INVALID
N12-03     reproduced-secure  BLOCK codes=E-CANDIDATE-REF-INVALID
N12-04     reproduced-secure  BLOCK codes=E-CANDIDATE-REF-INVALID
N12-05.1   reproduced-secure  BLOCK codes=E-CANDIDATE-REF-INVALID
N12-05.2   reproduced-secure  BLOCK codes=E-CANDIDATE-REF-INVALID
N12-05.3   reproduced-secure  BLOCK codes=E-CANDIDATE-REF-INVALID
N12-06.1   reproduced-secure  BLOCK codes=E-CANDIDATE-REF-INVALID
N12-06.2   reproduced-secure  BLOCK codes=E-CANDIDATE-REF-INVALID
N12-06.3   reproduced-secure  BLOCK codes=E-CANDIDATE-REF-INVALID
N12-06.4   reproduced-secure  BLOCK codes=E-CANDIDATE-REF-INVALID
N12-06.5   reproduced-secure  BLOCK codes=E-CANDIDATE-REF-INVALID
N12-07     reproduced-secure  BLOCK codes=E-SCHEMA
N12-08     reproduced-secure  BLOCK codes=E-SCHEMA
N12-09     reproduced-secure  BLOCK codes=E-CANDIDATE-DUPLICATE
N12-10     reproduced-secure  READY codes=-
N12-11     reproduced-secure  READY codes=-
N12-12     reproduced-secure  READY codes=-
N12-13     reproduced-secure  READY codes=-
N12-14     reproduced-secure  READY codes=-
N12-15     reproduced-secure  READY codes=-
N12-16     reproduced-secure  BLOCK codes=E-CANDIDATE-REF-INVALID
N12-17     reproduced-secure  BLOCK codes=E-APPOINTMENT-RECORD,E-CANDIDATE-UNKNOWN
N12-18     reproduced-secure  BLOCK codes=E-ACCEPTANCE-APPOINTMENT,E-APPOINTMENT-RECORD,E-CANDIDATE-UNKNOWN,E-EVIDENCE-SUBJECT
N12-19     reproduced-secure  BLOCK codes=E-APPOINTMENT-RECORD,E-CANDIDATE-UNKNOWN
PROBES exact_identity: True equivalent_instant: {'p1_lt_p2': False, 'p2_lt_p1': False, 'p1_eq_p2': True}
```

Four additional cases were appended after the deeper probes; final tally: **49 cases — 47 reproduced-secure, 2 defect (both D-01), 0 inconclusive, 0 not-applicable.**

### N-11 detail (20 cases)

| Case | Mutation | Observed | Verdict / reason |
|---|---|---|---|
| N11-01 | baseline; decision 01:00 UTC, acceptances 00:00 | no issues, READY | reproduced-secure — valid decision accepted |
| N11-02 | decision 2026-11-26T23:00+00:00, before both acceptances | `E-COMBINATION-APPROVAL-TIMESTAMP-ORDER`, combo dimension FAIL | reproduced-secure |
| N11-03 | two-role candidate C-P2: MODERATOR accepts 00:00, NOTE_TAKER 00:30, decision 00:15 | order error only (no spurious `E-TIMESTAMP-ORDER`) | reproduced-secure — `max(accepted)` used |
| N11-04 | acceptances 00:00/00:30, decision 00:45 | no issues, READY | reproduced-secure |
| N11-05 | `decision_timestamp=null` | `E-TIMESTAMP-INVALID`, combo dimension FAIL | reproduced-secure |
| N11-06 | required key removed | `E-SCHEMA`, structural dim FAIL, engine returns before dereference | reproduced-secure — schema terminal |
| N11-07 | naive `2026-11-27T01:00:00` | `E-TIMESTAMP-INVALID` | reproduced-secure — tz required |
| N11-08 | acceptance `02:00+00:00`, decision `03:00+01:00` (same instant) | no issues, READY | reproduced-secure — aware comparison, equality accepted |
| N11-09 | acceptance `02:00+00:00`, decision `03:30+01:00` (=02:30Z) | no issues, READY | reproduced-secure |
| N11-10 | acceptance `02:00+00:00`, decision `02:00+01:00` (=01:00Z) | order error | reproduced-secure — not wall-clock string comparison |
| N11-11 | acceptance/approval/formal/decision all `01:00+00:00` | no issues, READY | reproduced-secure — deterministic `>=` at equality |
| N11-12.1–.4 | `not-a-timestamp`, out-of-range date, empty string, date-only | `E-TIMESTAMP-INVALID` each, no exception | reproduced-secure |
| N11-13 | MODERATOR acceptance 03:00 after approval 01:00 | `E-TIMESTAMP-ORDER` + order error | reproduced-secure — role chain and combo chain both fire |
| N11-14 | approval record duplicated with old decision `2026-11-26T00:00Z` | order error count = 2 | reproduced-secure — no laundering by reuse |
| N11-15 | both acceptances null, old decision | `E-TIMESTAMP-MISSING`, no order error | reproduced-secure — N-11 skips unparseable instants; role-level errors still block authorization |
| N11-16 | decision `2099-01-01T00:00Z` | no issues, READY | reproduced-secure — combined with N11-02 rules out `datetime.now()` substitution |
| N11-17 | decision `2026-11-27T01:00:00Z` | no issues, READY | reproduced-secure — Z suffix normalised to `+00:00` |

### N-12 detail (29 cases)

| Case | Mutation | Observed | Verdict / reason |
|---|---|---|---|
| N12-01 | baseline C-P1…C-P5 | no issues, READY | reproduced-secure |
| N12-02 | C-P1 → empty string everywhere | `E-CANDIDATE-REF-INVALID` + `E-CANDIDATE-DUPLICATE` (`not ref`), human_acceptance FAIL | reproduced-secure |
| N12-03 | C-P1 → `"   "` | `E-CANDIDATE-REF-INVALID`, READY=false | reproduced-secure — cannot authorize appointment |
| N12-04 | C-P1 → `" C-P1 "` (content + padding) | `E-CANDIDATE-REF-INVALID` | reproduced-secure — padding check works even when `strip()` leaves content |
| N12-05.1–.3 | NBSP U+00A0, ideographic space U+3000, TAB | `E-CANDIDATE-REF-INVALID` each | reproduced-secure — Zs/Cc non-content |
| N12-06.1–.5 | ZWSP U+200B, BOM U+FEFF, LRM U+200E, WJ U+2060, ZWSP+LRM alone | `E-CANDIDATE-REF-INVALID` each | reproduced-secure — Cf non-content |
| N12-07 | `candidate_ref=null` | `E-SCHEMA`, no registry dereference | reproduced-secure — schema terminal |
| N12-08 | `candidate_ref=123` | `E-SCHEMA` | reproduced-secure — schema terminal |
| N12-09 | second key whose ref is `C-P1` | `E-CANDIDATE-DUPLICATE` | reproduced-secure |
| N12-10 | added `c-p1` alongside `C-P1` | no issues, READY | reproduced-secure — no case folding |
| N12-11 | added NFC `Café` and NFD `Cafe\u0301` | no issues, READY | reproduced-secure — no Unicode normalization |
| N12-12 | added fullwidth `Ｃ－Ｐ１` | no issues, READY | reproduced-secure — no width folding |
| N12-13 | C-P1 renamed to CJK `候補-甲` and propagated into a real appointment | no issues, READY | reproduced-secure — international refs stay valid |
| N12-14 | added Arabic-Indic ref | no issues | reproduced-secure |
| N12-15 | added ZWJ-emoji and accented refs | no issues | reproduced-secure — ZWJ inside substantive sequence preserved |
| N12-16 | C-P1 → ZWSP alone across all consumers | `E-CANDIDATE-REF-INVALID`, READY=false | reproduced-secure — registry membership alone is insufficient; any ERROR blocks authorization |
| N12-17 | appointment ref `C-UNKNOWN` | `E-CANDIDATE-UNKNOWN` + `E-APPOINTMENT-RECORD` | reproduced-secure |
| N12-18 | role record `candidate_ref=null` | `E-CANDIDATE-UNKNOWN` + evidence/subject errors | reproduced-secure |
| N12-19 | appointment `candidate_ref=null` | `E-CANDIDATE-UNKNOWN` + `E-APPOINTMENT-RECORD` | reproduced-secure |
| N12-20 | `C-P1` + trailing ZWSP | no issues, READY | reproduced-secure — documented F-007 policy keeps embedded Cf in substantive content; distinct identity preserved |
| N12-21 | standalone combining mark U+0301 as ref | no issues, READY | reproduced-secure — Mn is deliberately content; observation only |
| N12-22 | added valid `c-p1` + appointment `(c-p1, RESEARCH_OWNER)` | **no issues, READY** | **defect D-01** |
| N12-23 | added valid `C-NEW` + appointment `(C-NEW, RESEARCH_OWNER)` | **no issues, READY; all 8 dims PASS** | **defect D-01 confirmation** |

Direct registry probe: `candidate_registry_check` on `{C-P1, c-p1, NFC Café, NFD Cafe+acute, fullwidth, Arabic}` returned exactly the same six keys with zero candidate errors — confirming no silent normalization.

---

## 5. New defect

### D-01 — Appointment records are not bound to the candidate_ref of the formal role record

- **Severity:** MEDIUM. **Type:** new defect found while inspecting all `candidate_ref` consumption sites required by the N-12 brief; it is not itself a failure of the N-11 or N-12 predicates, which all reproduced secure.
- **Location:** `engine/validator.py` lines 515–538 (appointments loop and formal-role reconciliation).
- **Root cause:** the appointments loop checks that `ap.candidate_ref` is a registry key, that `ap.role` is known and that the role is in a formal state, but never asserts `ap.candidate_ref == role_records[ap.role].candidate_ref`. Reconciliation at 534–538 only verifies that the role record's *own* ref has an appointment; extra appointments under the same role for other candidates are not rejected. Any valid registry identity holding only that one role also avoids the multi-role combination-approval requirement.
- **Reproduction (exact in-memory mutation):**
  1. deep-copy `valid_five_person.json`;
  2. add `candidates["C-NEW"] = {"candidate_ref":"C-NEW","active":true,"fixture_marker":"SYNTHETIC_TEST_DATA"}`;
  3. append `appointments += [{"candidate_ref":"C-NEW","role":"RESEARCH_OWNER","state":"FORMALLY_APPOINTED"}]`;
  4. `validate_state(...)` → `stage_b_role_ready=true`, `blocking_error_count=0`, all dimensions PASS, `issues=[]`.
- **Observed output:** `SPARE_VALID_IDENTITY: {"ready": true, "codes": [], "dimensions": {…all PASS…}}` versus the invalid-identity control `SPARE_INVALID_IDENTITY: {"ready": false, "codes": ["E-CANDIDATE-REF-INVALID"]}`.
- **Impact:** a candidate with no acceptance, PO approval, formal-appointment or onboarding evidence can be recorded as appointed to a role formally held by someone else and the state still passes. Visually confusable identities (`c-p1` vs `C-P1`) can appear as co-appointees without detection. This weakens the "appointments must be backed by role-bound acceptance evidence" guarantee.
- **Recommended fix:** in the appointments loop add, for each appointment with a formal role, `if ap.candidate_ref != role_records.get(role, {}).get("candidate_ref"): fail("role_assignment_completeness", "E-APPOINTMENT-CANDIDATE-MISMATCH", ...)`; reject any `(candidate_ref, role)` pair that is not the authoritative pair for that role.

---

## 6. Conclusion

- **N-11 reproduced secure across all 20 cases:** strict `<` against `max(accepted)`, aware-datetime comparison, deterministic `>=` boundary, correct codes/dimensions (`E-COMBINATION-APPROVAL-TIMESTAMP-ORDER` / `E-TIMESTAMP-INVALID` in `product_owner_combination_approval`), no wall-clock substitution, no crash on malformed input, schema terminal handling intact.
- **N-12 reproduced secure across the 27 in-scope cases:** empty/whitespace/padded/invisible refs rejected, null/non-string stopped by schema, duplicates detected, case/NFC/NFD/fullwidth identities kept distinct, meaningful and international refs retained, invalid identities cannot produce an authorized appointment.
- **One new adjacent defect (D-01)** in appointment-to-role binding was found and independently confirmed twice; it does not negate the N-11/N-12 results but should be entered into the defect register.
