# M001 V2.2 — Mutation Test Report

**Mission:** M001-TEAM-008  
**Evidence:** `tests/mutation/mutation_harness_v22.py`, `tests/mutation/canary_v22.py`, `tests/results/mutation_results.json`, `reports/logs/{canary,mutation}.txt`

## Independence and safety

V2's and V2.1's mutation harnesses were not reused as proof. Mutants are disposable copies under
`tests/mutation/mutants/` containing only `engine/`, `policy/`, `schemas/` and `tests/fixtures/`.
No preserved workspace was mutated. All runs used `PYTHONDONTWRITEBYTECODE=1`.

## Results

| Metric | Value |
|---|---|
| Baseline canary | `CANARY_PASS 8/8`, exit 0 |
| Introduced mutations | 5 (one per blocker) |
| Detected | **5** |
| Survived | **0** |
| Excluded | 0 |

| Mutation | Controlled defect | Detected |
|---|---|---|
| M1_F007_predicate_reverted | restore `bool(str)` semantics in `meaningful_text()` | YES (canary B01/B02 fail) |
| M2_N04_escalation_check_removed | disable escalation-contact gate | YES (B04) |
| M3_N08_duplicate_check_removed | disable evidence duplicate detection | YES (B05) |
| M4_N11_ordering_check_removed | disable combination timestamp ordering | YES (B06) |
| M5_N12_ref_check_removed | disable candidate-reference gate | YES (B07) |

Exact output: `BASELINE_EXIT 0`, `DETECTED 5/5`.

## Canary properties

B00 valid state passes; B01 invisible basis rejected; B02 invisible rationale rejected; B03
meaningful ZWJ emoji text accepted; B04 whitespace escalation contact rejected; B05 duplicate
evidence rejected; B06 combination before acceptance rejected; B07 whitespace candidate ref rejected.

## Mutation correction note

The first M5 mutant used `if False and A or B`, whose operator precedence left guard B active;
it survived. It was corrected to disable the whole guard and then detected. The invalid mutant was
excluded from the final counts and is documented here for transparency.
