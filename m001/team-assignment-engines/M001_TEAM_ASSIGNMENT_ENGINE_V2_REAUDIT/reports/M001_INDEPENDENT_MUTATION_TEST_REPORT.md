# M001 Independent Mutation Test Report

**Mission:** M001-TEAM-005  
**Date:** 2026-11-27  
**Evidence:** `mutation/independent_mutation_harness.py`, `mutation/independent_canary.py`, `mutation/results/independent_mutation_results.json`, `reports/MUTATION_AGENT_NOTES.md`

## Independence

The audit did not reuse V2's mutation harness or canary as proof. A separate harness and a
separate canary were written inside the re-audit workspace. Mutants are disposable copies
containing only `engine/`, `policy/`, `schemas/` and `tests/fixtures/`; the canary imports the
validator from `--root` only. V2 itself was never modified.

## Final results

| Metric | Count |
|---|---|
| Introduced mutations | 30 |
| Detected | **30** |
| Survived | **0** |
| Excluded with documented reasons | 3 |
| Final canary baseline | `CANARY_PASS 44/44` |

Command output: `INTRODUCED 30 DETECTED 30 SURVIVED 0 EXCLUDED 3`.

The mutations covered: duplicate-key parser bypass, naive timestamp acceptance, role
timestamp bypass, evidence subject removal, global evidence-verification removal, candidate
key/reference substitution, duplicate candidate bypass, unknown candidate bypass (role and
appointment), authorization boundary bypass, topology approval bypass, formal state bypass
(engine and policy), candidate acceptance bypass, role PO approval bypass, formal approval flag
bypass, empty approval basis bypass, formal record bypass, onboarding bypass, combination
approval missing/outcome/PO/rationale/timestamp bypasses, discouraged combination bypass, hard
incompatibility bypass (engine and policy), evidence separation bypass, and timestamp-order
bypass.

## Exclusions (with reasons)

- `X01_stage_b_topology_redundant` — semantically equivalent under the shipped policy. Removing
  the topology clause from the final Stage B expression changes nothing because a PROPOSED
  topology already emits `E-TOPOLOGY-UNAPPROVED` and forces the dimension/issue condition false.
  Differential fingerprint identical on 42 inputs. Caveat: conditional on the shipped policy
  flag being true.
- `X02_patch_target_absent` — patch target not found; no mutation was actually introduced.
- `X03_comment_only_noop` — comment-only change; no semantic effect, identical fingerprint on 42 inputs.

## Survivor triage (transparency)

The **first** canary run had two survivors. Neither was accepted without investigation:

- `M05_evidence_unverified_bypass` removes the global evidence verification gate at
  `validator.py:307`. Manual differential showed it is **not** equivalent: with a dangling
  evidence record marked `PENDING`, unmodified V2 emits `E-EVIDENCE-UNVERIFIED` with readiness
  NO while the mutant reports zero issues with readiness YES. Canary property `A42` was added;
  M05 is now detected.
- `M28_unapproved_appointment_bypass` removes the appointment-level formal-state guard at
  `validator.py:393`. It is decision-equivalent (the role-level loop still emits
  `E-APPOINTMENT-MISSING`, so readiness stays NO) but **not diagnostic-equivalent**: the
  independent `E-UNAPPROVED-APPOINTMENT` error disappears. Canary property `A43` was added;
  M28 is now detected.

This triage is recorded because the first independent result differed from V2's own 16/16
claim until the canary was strengthened. The final independent result matches it: 30/30.

## Reproduce

```powershell
cd C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT
python mutation/independent_canary.py --root C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2
python mutation/independent_mutation_harness.py
```
