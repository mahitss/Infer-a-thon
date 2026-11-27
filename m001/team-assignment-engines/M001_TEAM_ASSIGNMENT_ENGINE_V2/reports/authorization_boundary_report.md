# Authorization Boundary Report — M001 Team Assignment Engine V2

**Date:** 2026-11-27  
**Scope:** governance preservation, authorization non-inference, and separation of validation dimensions.

## Preserved governance state

| Item | Required | V2 state | Verified |
|---|---|---|---|
| M001 | OPEN | `governance.m001_status = OPEN` | YES |
| M002 | UNAUTHORIZED | `governance.m002_status = UNAUTHORIZED` | YES |
| Decision register D-PO-01…17 | unchanged | not touched by V2 | YES |
| D-PO-04 | REVISE only | not modified | YES |
| D-PO-18/19/20 | PROPOSED | not modified | YES |
| ADR-001 | PROPOSED | not modified | YES |
| Field validation | NOT STARTED | `governance.field_validation = NOT_STARTED` | YES |
| Recruitment | UNAUTHORIZED | `governance.recruitment = UNAUTHORIZED` | YES |
| Research Owner | ACCEPTED IN CONVERSATION, not formally appointed | preserved with `formal=false`, no legal name/ID | YES |
| Other five roles | UNASSIGNED | preserved | YES |
| Topology | PROPOSED | `topology.status = PROPOSED` | YES |

The 5–8 participant exploratory research scope remains an approved-in-principle scope only.
Operational safeguards, recruitment authorization and field validation remain separate gates
that V2 does not open.

## Authorization non-inference

`ValidationResult` hard-codes `recruitment_authorized=False` and
`field_validation_authorized=False`. These fields are never derived from topology status,
compatibility results, candidate acceptance, combination approval, Stage B readiness or any
other dimension. The CLI always prints both as `NO`.

Evidence of non-inference:
- Valid four-person fixture: Stage B readiness YES, yet both authorizations NO (exit 0).
- Current real state: Stage B readiness NO, both authorizations NO (exit 1).
- Tampered fixture with `recruitment=AUTHORIZED`: rejected with `E-AUTHORIZATION-STATE` and
  `E-SCHEMA`; both authorizations still NO (exit 1).
- Mutation M15 disables the guard and is detected by canary C15.

The engine emits no appointment decision, no Stage B sign-off, no recruitment permission and
no consent/participant-data capability.

## Separation of validation dimensions

V2 reports eight independent dimensions plus Stage B role-readiness (see
`reports/current_assignment_validation.md`). A structurally valid PROPOSED topology can be
emitted while appointment completeness fails. Formal appointment validity, evidence
integrity and onboarding are reported separately, so a PASS on one cannot be read as a PASS
on another. Stage B readiness is a conjunction of approved topology, all eight dimensions
PASS and zero issues; it is not a generic `Valid: YES`.

## Combination and compatibility authority

Hard incompatibilities (`MODERATOR+ANALYST`, `MODERATOR+DATA_CUSTODIAN`) are unoverridable:
no approval path, evidence record or policy option can make them pass. Mutations M01, M02
and M16 confirm this.

Discouraged combinations (`RESEARCH_OWNER+MODERATOR`, `DATA_CUSTODIAN+ANALYST`) retain their
`NOT_RECOMMENDED` classification and block validation until an exact, PO-approved
combination review with structured evidence is present. This is the PO review already
required by the authoritative defect correction, not a newly invented override: there is no
general bypass field, no severity downgrade and no alternative acceptance path. Mutations
M09 and the exact-approval regression confirm the boundary. Conditional combinations
require evidence separation (`MODERATOR+NOTE_TAKER`) or an explicit additional appointment
(`RESEARCH_OWNER+CONTINUE_STOP_OWNER`).

## Evidence and identity integrity

No evidence was fabricated: `evidence/` is empty, the real state has zero evidence records,
and all evidence in tests is marked `SYNTHETIC_TEST_DATA`. Boolean flags never substitute
for evidence references. Candidate registry references are unique and stable; unknown,
inactive and duplicate identities fail closed. No Product Owner or participant identity was
invented, and no collaborator or participant was contacted.

## Workspace and repository preservation

`reports/preservation_check.json` records SHA-256 hashes of all 47 V1 files and all 485
audit files, plus these anchors, all matching the task-start baseline:

- V1 `engine/validator.py`: `9CB8729278763DAC773E0C4E250A77951FC16C349AC1F8FBC69EC69D1C440E70`
- Frozen evidence ZIP: `82B58946963C1DBAEA4A180DBA7833C5217852A847222C5726A321C2B7B6CB3D`
- Repository HEAD: `30db9a1929bbccf73a538f6657cb10f49758688e`, working tree clean

No repository file was modified; the staffing pack was not regenerated; no register, ADR,
storage, ACL or consent change was made. All preservation checks: PASS.
