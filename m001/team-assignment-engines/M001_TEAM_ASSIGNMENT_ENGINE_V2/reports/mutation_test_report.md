# Mutation Test Report — M001 Team Assignment Engine V2

**Date:** 2026-11-27  
**Evidence:** `reports/logs/canary.txt`, `reports/logs/mutation.txt`, `reports/mutation_results.json`, `reports/mutation_canary_baseline.txt`, `reports/logs/original_v1_mutation_canary.txt`

## Design

The canary imports the validator exclusively from `--root`, so a mutant is evaluated only
against its own copied source tree. The original V2 engine is never modified: the harness
copies only `engine/`, `policy/`, `schemas/` and `tests/` into isolated directories under
`tests/mutation/mutants/`, then introduces exactly one defect per mutant.

**Harness fix applied:** the initial harness used `shutil.copytree(ROOT, dst)` while `dst`
was inside `ROOT/tests/mutation/mutants`, causing infinite recursion (`RecursionError`).
The copy now targets only the four required inputs and ignores `mutants` and
`__pycache__`, so no destination is ever a descendant of a copied source.

## Baseline canary — 18/18 PASS

| Check | Claim | Result |
|---|---|---|
| C1 | Hard `MODERATOR+ANALYST` blocked | PASS |
| C2 | Discouraged combination PO review blocked | PASS |
| C3 | Conditional evidence separation blocked | PASS |
| C4 | Exact multi-role combination approval blocked | PASS |
| C5 | PROPOSED / conversation states never formal | PASS |
| C6 | Formal flag mismatch blocked | PASS |
| C7 | Independent candidate acceptance blocked | PASS |
| C8 | Onboarding blocked | PASS |
| C9 | Unknown candidate blocked | PASS |
| C10 | Broken evidence reference blocked | PASS |
| C11 | Naive timestamp blocked | PASS |
| C12 | Topology approval gate blocked | PASS |
| C13 | Empty approval basis blocked | PASS |
| C14 | Duplicate candidate identity blocked | PASS |
| C15 | Authorization-state tampering blocked | PASS |
| C16 | Valid synthetic model still passes | PASS |
| C17 | Hard `MODERATOR+DATA_CUSTODIAN` blocked | PASS |
| C18 | Role-level explicit PO approval blocked | PASS |

## Introduced mutations — 16/16 detected, 0 survived

| Mutation | Defect introduced | Detected |
|---|---|---|
| M01_remove_hard_MA | Remove `MODERATOR+ANALYST` from hard incompatibilities | YES (canary C1 failed) |
| M02_remove_hard_MDC | Remove `MODERATOR+DATA_CUSTODIAN` from hard incompatibilities | YES (canary C17 failed) |
| M03_ignore_evidence_separation | Disable conditional evidence-separation guard | YES (C3) |
| M04_ignore_combination_approval | Disable exact multi-role approval guard | YES (C4) |
| M05_promote_conversation_to_formal | Treat `ACCEPTED_IN_CONVERSATION` as formal | YES (C5) |
| M06_ignore_po_approval | Disable explicit Product Owner approval guard | YES (C18) |
| M07_ignore_candidate_acceptance | Disable independent candidate acceptance guard | YES (C7) |
| M08_ignore_onboarding | Disable onboarding guard | YES (C8) |
| M09_allow_discouraged_without_review | Allow discouraged combination without PO review | YES (C2) |
| M10_allow_unknown_candidate | Disable all unknown-candidate guards | YES (C9) |
| M11_allow_broken_evidence | Accept non-record evidence references | YES (C10) |
| M12_allow_naive_timestamp | Accept naive/non-ISO timestamps | YES (C11) |
| M13_ignore_topology_approval | Disable topology approval gate | YES (C12) |
| M14_allow_duplicate_candidate | Disable both candidate-uniqueness guards | YES (C14) |
| M15_ignore_authorization_state | Disable authorization-state guard | YES (C15) |
| M16_allow_hard_incompatibility | Disable hard-incompatibility guard | YES (C1) |

`DETECTED 16/16`; `survived: []`. No newly introduced security mutation survived.

Three initial survivors were resolved before final execution: M02 had no canary fixture
for the second hard incompatibility (added `hard_incompatibility_mdc.json`, canary C17);
M06 had no fixture where explicit role-level PO approval was the sole defect (added
`po_approval_missing.json`, canary C18); and M14 targeted a redundant guard while the
real duplicate check remained active (the mutation now disables both duplicate guards).

## Original M001 mutation tests

The preserved audit's read-only `mutation_canary.py` was re-run against V1: `CANARY_PASS
10/10`, exit 0. The frozen audit `mutation_results.json` records 10 original mutants,
10 detected, 0 survived. The original harness itself was not re-executed because it writes
mutant copies into the preserved audit workspace; V2's equivalent harness reproduces and
extends that coverage with 16 mutants.

## Reproduce

```powershell
python tests/mutation/mutation_canary.py --root .
python tests/mutation/mutation_harness.py
# expected: CANARY_PASS 18/18, DETECTED 16/16, no survivors
```
