# M001 Team Assignment Engine V2 — Governance Defect Remediation

**Mission:** M001-TEAM-004 (V2d)  
**Engine:** `M001_TEAM_ASSIGNMENT_ENGINE_V2`  
**Date:** 2026-11-27  
**Verdict:** `REMEDIATION COMPLETE — READY FOR INDEPENDENT RE-AUDIT`

## Purpose

V2 is a **diagnostic control**, not an appointment authority. Its purpose is to make it
impossible for an unsupported appointment to masquerade as an approved one. It does not
appoint people, promote states, grant recruitment or field-validation authorization,
contact collaborators or participants, modify the decision register, change D-PO or ADR
statuses, configure storage/ACLs, or change consent records.

V1 (`M001_TEAM_ASSIGNMENT_ENGINE`) and the independent audit
(`M001_TEAM_ASSIGNMENT_ENGINE_AUDIT`) are preserved byte-for-byte. No repository file was
changed. No network access or paid API was used. Python standard library is used except
for the locally pre-installed `jsonschema` package, whose presence is detected at import
time; it is never installed or fetched automatically.

## Governance state (unchanged)

| Item | Status |
|---|---|
| M001 | OPEN |
| M002 | UNAUTHORIZED |
| Decision register D-PO-01…17 | unchanged; D-PO-04 REVISE only |
| D-PO-18/19/20, ADR-001 | PROPOSED |
| Field validation | NOT STARTED |
| Recruitment | UNAUTHORIZED |
| Research Owner | ACCEPTED IN CONVERSATION — **not formally appointed** |
| Other five roles | UNASSIGNED |
| Topology | PROPOSED |

No legal name or candidate identifier was invented for the Product Owner or any role.

## Workspace layout

```text
M001_TEAM_ASSIGNMENT_ENGINE_V2/
├── README.md
├── schemas/team_assignment.schema.json      # full Draft 2020-12 schema
├── policy/role_constraints.json             # machine-readable governance policy
├── state/current_assignment_state.json      # real current state, never promoted
├── evidence/                                # reserved; no fabricated evidence
├── engine/validator.py                      # hardened deterministic validator
├── cli/validate.py                          # safe CLI, machine-readable output
├── build_current_state.py                   # one-time real-state builder
├── build_fixtures.py                        # synthetic fixture builder
├── verify_all.py                            # captures every verification command
├── build_preservation.py                    # read-only preservation hash check
├── tests/
│   ├── regression/                          # V2 semantics, CLI, 20 explicit scenarios
│   ├── adversarial/                         # 24 independent audit checks against V2
│   ├── mutation/                            # 18-check canary + 16-mutation harness
│   └── fixtures/                            # SYNTHETIC_TEST_DATA only
├── reports/                                 # required reports + raw execution logs
├── M001_V2_ENGINE_AUDIT.md
└── SHA256_MANIFEST.json
```

## How to run

From the V2 root:

```powershell
python cli/validate.py --state state/current_assignment_state.json
python cli/validate.py --state tests/fixtures/valid_four_person.json --json-only
python -m unittest discover -s tests/adversarial -p 'test_*.py' -v
python -m unittest discover -s tests/regression  -p 'test_*.py' -v
python tests/mutation/mutation_canary.py --root .
python tests/mutation/mutation_harness.py
python verify_all.py
python build_preservation.py
```

Exit codes: `0` = Stage B role readiness YES; `1` = validation completed but readiness NO;
`2` = safe input error (`E-JSON-INVALID`, `E-ENCODING-INVALID`, `E-DUPLICATE-JSON-KEY`,
`E-FILE-NOT-FOUND`). Expected input failures never emit a traceback.

## Separate output dimensions

The engine never collapses outcomes into a generic `Valid: YES`. It reports independently:

1. structural topology validity
2. role-assignment completeness
3. human candidate acceptance
4. formal appointment validity
5. Product Owner combination approval
6. evidence integrity
7. role compatibility
8. onboarding readiness
9. Stage B role-readiness

Recruitment and field-validation authorization are always emitted as `NO`. A passing
topology or role validator never grants either authorization.

## JSON Schema validation scope

`jsonschema` was inspected and **is available locally** (`Draft202012Validator`). It is
used as the primary structural validator, with the schema declaring
`https://json-schema.org/draft/2020-12/schema`. The schema itself is checked with
`check_schema`, and errors are sorted deterministically by instance path and message.

If `jsonschema` is unavailable, `validate_schema()` provides a deterministic documented
subset that validates exactly: `$ref` (local `#/` pointers), `type`, `required`,
`properties`, `additionalProperties` (`false` or a schema), `enum`, and `items`.

The subset does **not** validate: `format`, `pattern`, `minLength`/`maxLength`, numeric
bounds, `uniqueItems`, `const`, `default`, `allOf`/`anyOf`/`oneOf`/`not`, `dependencies`,
`unevaluatedProperties`, `$schema` dialect semantics, or remote references. Business
rules (compatibility, exact combination approval, evidence integrity, timezone-aware
timestamps and ordering, onboarding, authorization boundaries) are enforced by
`engine/validator.py`, not by the schema, and remain active under both validators.

## Evidence

Evidence is structured, never boolean-only. Each record carries `evidence_id`,
`evidence_type`, `source_ref`, `content_hash`, `recording_authority`, timezone-aware
`timestamp`, `verification_status` and `subject`. Unknown IDs, wrong types, unverified
records, incomplete records, broken subjects, invalid hashes and naive timestamps fail
closed. No evidence was fabricated; the `evidence/` directory is empty and the real
state contains zero evidence records.

All synthetic candidate data is labelled `SYNTHETIC_TEST_DATA` and exists only under
`tests/fixtures/`. Synthetic fixtures are never inserted into
`state/current_assignment_state.json`.
