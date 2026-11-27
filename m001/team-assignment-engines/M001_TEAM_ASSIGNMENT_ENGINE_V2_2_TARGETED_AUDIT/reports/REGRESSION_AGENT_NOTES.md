# Independent regression and mutation evidence — M001-TEAM-009 (V2.2)

**Role:** independent auditor. **Date:** 2026-11-28.
**Environment:** Python 3.13.5 (`C:\Users\pc\AppData\Local\Programs\Python\Python313\python.exe`).
Every command ran with `PYTHONDONTWRITEBYTECODE=1`; no installs, no network.
Machine-readable evidence: `tests/results/regression_results.json`.

V2.2's own reports were treated as unverified claims. Every number below is from a command I executed; three result files were regenerated and hash-compared to V2.2's claimed copies.

## Boundary handling

Read-only commands were run verbatim from the V2.2 root: both `unittest discover` suites, the two focused test modules, `canary_v22.py --root .`, all seven CLI checks, and the two-cwd determinism check.

Three runners **write into their own root** (`parents[2]` of the script): `independent_adversarial_v21.py` and `refined_cases_v21.py` write `tests/results/*.json`; `mutation_harness_v22.py` deletes/recreates `tests/mutation/mutants` and copies four source trees. They were **not** run from V2.2. Byte-identical copies of `engine`, `policy`, `schemas`, `tests`, `cli`, `state` (572 files) were placed in `tests/disposable_v22/` inside this audit workspace and the runners were executed there. The independent scripts still hardcode `V2 = ...\M001_TEAM_ASSIGNMENT_ENGINE_V2_2`, so the engine and fixtures under test remain the real preserved V2.2 files; only the writes were redirected. **V2.2 was never written.**

## 1. Adversarial suite — EXECUTED, PASS

```
cwd: ...\M001_TEAM_ASSIGNMENT_ENGINE_V2_2
python -m unittest discover -s tests/adversarial -p 'test_*.py' -v
```
Exit `0`; stdout empty. Stderr tail: `Ran 24 tests in 1.296s` / `OK`. 24 executed, 24 passed, 0 failed. Claim of 24 checks confirmed.

## 2. Regression suite — EXECUTED, PASS

```
cwd: ...\M001_TEAM_ASSIGNMENT_ENGINE_V2_2
python -m unittest discover -s tests/regression -p 'test_*.py' -v
```
Exit `0`; stdout empty. Stderr tail: `Ran 66 tests in 28.490s` / `OK`. 66 executed, 66 passed, 0 failed. Claim of 66 confirmed (53 V2.1 + 13 blockers).

## 3. Independent 50-case corpus — EXECUTED (relocated runner)

```
cwd: ...TARGETED_AUDIT\tests\disposable_v22
python tests/independent/independent_adversarial_v21.py
```
Exit `0`, stderr empty. Stdout: `TOTAL 50 SECURE 43 DEFECT 7` plus seven `DEFECT` lines: `COMB-03, COMB-12, EVID-03, EVID-06, ST-02, ID-02, ID-07`. Generated `independent_adversarial_results.json` is **byte-identical** to V2.2's claimed file (SHA-256 `BAD4DB51...F3B900`) — an executed reproduction, not a copied claim.

## 4. V2.1 focused remediation tests — EXECUTED, PASS

```
python -m unittest discover -s tests/regression -p 'test_v2_1_high_findings.py' -v
```
Exit `0`; `Ran 22 tests in 9.400s` / `OK`. 22/22 passed.

## 5. V2.2 blocker tests — EXECUTED, PASS

```
python -m unittest discover -s tests/regression -p 'test_v2_2_blockers.py' -v
```
Exit `0`; `Ran 13 tests in 2.441s` / `OK`. 13/13 passed.

## 6. Canary and mutation — EXECUTED

```
cwd: ...V2_2
python tests/mutation/canary_v22.py --root .
```
Exit `0`, stderr empty; `B00`–`B07` all `PASS`, `CANARY_PASS 8/8`.

```
cwd: ...TARGETED_AUDIT\tests\disposable_v22
python tests/mutation/mutation_harness_v22.py
```
Exit `0`, stderr empty; `BASELINE_EXIT 0`, `DETECTED 5/5`, all five mutants (`M1_F007_predicate_reverted`, `M2_N04_escalation_check_removed`, `M3_N08_duplicate_check_removed`, `M4_N11_ordering_check_removed`, `M5_N12_ref_check_removed`) detected with exit 1, 0 survived. Generated `mutation_results.json` is byte-identical to V2.2's claim (SHA-256 `9A82B967...679EC9`). **Not executed from V2.2 root** by design.

Supporting evidence (not explicitly assigned): `refined_cases_v21.py` was also run from the disposable copy; 14 cases reproduced, output byte-identical to V2.2's claim (`F6F20691...38009E6`). Used only to classify the open cases.

## 7. CLI checks — EXECUTED from V2.2 root

All `python cli/validate.py --state <state>`, `cwd=V2_2`. Every stderr was empty and no stdout/stderr contained `Traceback`.

| state | expected | observed | observed tail | verdict |
|---|---|---|---|---|
| `state/current_assignment_state.json` | 1 | 1 | `E-APPOINTMENT-MISSING`, `E-TOPOLOGY-UNAPPROVED` | PASS |
| `tests/fixtures/valid_four_person.json` | 0 | 0 | `Blocking errors: 0` | PASS |
| `tests/fixtures/schema_invalid_assignment.json` | 1 | 1 | `E-SCHEMA` ×8, all dimensions FAIL | PASS |
| `tests/fixtures/malformed.json` | 2 | 2 | `E-JSON-INVALID` | PASS |
| `tests/fixtures/invalid_utf8.bin` | 2 | 2 | `E-ENCODING-INVALID` | PASS |
| `tests/fixtures/duplicate_json_key.json` | 2 | 2 | `E-DUPLICATE-JSON-KEY: schema_version` | PASS |
| `tests/fixtures/does_not_exist.json` | 2 | 2 | `E-FILE-NOT-FOUND` | PASS |

7/7 expected exit codes, empty stderr, no traceback.

## 8. Determinism — EXECUTED, PASS

Absolute script and state paths were used in both locations:

```
python ...\V2_2\cli\validate.py --state ...\V2_2\state\current_assignment_state.json
cwd 1 = ...\M001_TEAM_ASSIGNMENT_ENGINE_V2_2
cwd 2 = C:\Users\pc\AppData\Local\Temp
```
Both exits `1`, both stderr empty, stdout byte-identical (1300 chars, 7 blocking errors). `stdout_equal = stderr_equal = exit_equal = true`.

## 9. Preservation — VERIFIED

- V2.2 tree vs `evidence/BASELINE_START.json`: **132 files before and after, 0 missing, 0 added, 0 changed**. Pre-vs-post also 0 changed.
- `state/current_assignment_state.json` SHA-256 before **and** after: `E6DDC93C94506BA499878D642CBD29E71E1930409F4FBC9498FAE6A3009D094F` — unchanged.
- `engine/validator.py` SHA-256: `BAA3634DF3A82F9ECFF158552F263843F97372DADBC16E0D65D6C6D884BC5B5F` — unchanged.
- V2.2's three `tests/results/*.json` files unchanged (hashes in the JSON evidence).
- Git HEAD `30db9a1929bbccf73a538f6657cb10f49758688e` unchanged; `git status --porcelain` empty.
- No `.pyc`/`__pycache__` added to preserved workspaces.

## 10. The 7 open corpus cases — reproduced and classified individually

Each case was re-run directly from the corpus module (`COMB-03, COMB-12, EVID-03, EVID-06, ST-02, ID-02, ID-07`) with full observation. The corpus evaluator labels all seven `DEFECT` because the specific expected code is absent — **not** automatically accepted as genuine defects here. V2.2's own "open" list (remediation matrix) names exactly these seven.

| ID | observed codes | ready | blocking errors | classification |
|---|---|---|---|---|
| COMB-03 | `[]` | YES | 0 | expectation artifact |
| COMB-12 | `[]` | YES | 0 | expectation artifact |
| EVID-03 | `[]` | YES | 0 | genuine residual |
| EVID-06 | `[]` | YES | 0 | genuine residual |
| ST-02 | `[]` | YES | 0 | expectation artifact |
| ID-02 | `[]` | YES | 0 | genuine residual |
| ID-07 | `E-ACCEPTANCE-APPOINTMENT`, `E-COMBINATION-APPROVAL-MISSING`, `E-EVIDENCE-SUBJECT` | NO | 11 | inconclusive |

Per-case reasoning:

- **COMB-03 — duplicate approval roles → expectation artifact.** `pair_key()` uses `sorted(set(roles))`, so the duplicated role collapses into the legitimate two-role key; all dimensions stay PASS. The demanded `E-COMBINATION-APPROVAL-DUPLICATE` does not exist in the engine, policy or schema. Set semantics for approvals are intentional. A stricter malformed-record rule could be added, but no documented contract requires it.
- **COMB-12 — approval reuse for unrelated combination → expectation artifact (construction defect).** The mutation adds `C-P5` but the appended approval deepcopy keeps `candidate_ref='C-P1'`; `C-P5` holds no roles and `C-P1`'s exact approval is intact, so no approval is missing. The described scenario was not built. The refined variant that actually changes `candidate_ref` to `C-P2` does block (with `E-COMBINATION-APPROVAL-MISSING`, `E-COND-EXPLICIT-CS`, `E-EVIDENCE-SUBJECT`). Inconclusive as to the real attack.
- **EVID-03 — source-hash correspondence → genuine residual.** `evidence_check()` only regex-checks `[0-9a-fA-F]{64}`; `'0'*64` is well-formed and accepted. `E-EVIDENCE-HASH` is emitted only for format-invalid hashes; no hash-to-content verification exists. Caveat: no source bytes are present in the state, so the engine cannot fully verify correspondence — the residual is the unverifiable claim being accepted.
- **EVID-06 — evidence timestamp vs source → genuine residual.** Evidence timestamps get only `valid_timestamp()` (ISO-8601 + timezone) validation. `E-EVIDENCE-STALE` does not exist and no ordering between evidence timestamps and the decision timeline is enforced. Caveat: an authoritative source timestamp is not in the state model.
- **ST-02 — stale acceptance → expectation artifact.** The engine's `E-TIMESTAMP-ORDER` check enforces `candidate_accepted_at <= product_owner_approved_at <= formal_appointed_at`. Setting acceptance to 2020 while the other timestamps remain in 2026 preserves that order, so the check correctly does not fire. No freshness contract exists; the refined case is explicitly labelled "ordering still valid". If freshness is required, that is an unimplemented feature rather than a failure of the implemented rule.
- **ID-02 — Unicode-equivalent identifiers → genuine residual.** `candidate_registry_check()` compares refs by exact equality; there is no `unicodedata.normalize` collision detection and no `E-CANDIDATE-NORMALIZATION` code. `C-P1` and fullwidth `C-P１` coexist and Stage B stays ready. Caveat: the added candidate is unused in this case, so no concrete conflict is exercised.
- **ID-07 — split identities → inconclusive.** The state is blocked (`ready=NO`, 11 errors), but solely because the mutation leaves stale evidence bindings and an approval gap; `E-IDENTITY-ALIAS` does not exist. The corpus's `DEFECT` label reflects the absent expected code. Cannot conclude the alias-splitting attack is remediated: a consistent rewrite of all references would not be stopped by any alias check.

## Tests not executed / limitations

- No assigned suite was skipped. The three writing runners were relocated to `tests/disposable_v22/` for the boundary reason above; the engine under test remained the real V2.2 engine.
- The supporting `refined_cases_v21.py` run is extra evidence, not a substituted requirement.
- V2.2's `M001_V2_2_REMEDIATION_REPORT.md` claim of "5 detected, 0 survived" and "43/7" was independently reproduced and the result files hash-matched; the claims themselves were not trusted.
- All seven open cases are reported individually with their observed behaviour; none were auto-passed or auto-failed.
