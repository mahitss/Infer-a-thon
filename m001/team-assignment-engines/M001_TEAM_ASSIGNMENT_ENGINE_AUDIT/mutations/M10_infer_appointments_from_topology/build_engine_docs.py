# -*- coding: utf-8 -*-
"""Generate M001 Team Assignment Engine documentation and manifest."""
import hashlib, json, os
D = r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE'
G = """**Governance:** M001 OPEN; M002 UNAUTHORIZED; recruitment UNAUTHORIZED; field validation NOT STARTED; Research Owner ACCEPTED IN CONVERSATION (Product Owner, 2026-11-26; no legal name, signature or official register update); other five roles UNASSIGNED. This is diagnostic engineering tooling, not an appointment, implementation or authorization."""

def w(n,t): open(os.path.join(D,n),'w',encoding='utf-8').write(t)

w('README.md', f"""# M001 Team Assignment Engine

{G}

Executable Python standard-library tooling that validates human research-team assignments against machine-readable role policy.

## Contents

- `schemas/team_assignment.schema.json` — structural state schema.
- `policy/role_constraints.json` — six roles, appointment states and combination policy.
- `state/current_assignment_state.json` — current evidence-only state.
- `engine/validator.py` — deterministic validator and standard-library schema subset checker.
- `cli/validate.py` — CLI producing deterministic human and JSON output.
- `cli/validate_schema.py` — structural schema validation CLI.
- `tests/` — unit and integration tests.
- `fixtures/` — synthetic staffing models; never actual appointment records.
- `reports/` — executed validation evidence.
- `docs/` — engineering specification and validation report.

## Primary command

`python cli/validate.py --state state/current_assignment_state.json`

Exit status is nonzero when blocking errors exist. Current state correctly exits 1 because five appointments remain unassigned; `fixtures/valid_four_person.json` exits 0.

""")

w('docs/ENGINEERING_SPEC.md', f"""# Engineering Specification

{G}

## Inputs

The validator accepts an assignment state JSON containing governance status, topology, six role records and zero or more assignment records. Role states are not interchangeable: `UNASSIGNED`, `PROPOSED`, `ACCEPTED_IN_CONVERSATION`, `CANDIDATE_ACCEPTED`, `FORMALLY_APPOINTED`, `REJECTED`, `DEFERRED`.

## Policy

`policy/role_constraints.json` is the source of role identifiers, state requirements and combination classifications.

Hard incompatibilities (blocking): Moderator+Analyst; Moderator+Data Custodian.
Discouraged combinations (warnings unless resolved): Research Owner+Moderator; Data Custodian+Analyst.
Conditional combinations (blocking unless evidence present): Moderator+Note-taker requires `evidence_separation_documented`; Research Owner+Continue/Stop requires `explicit_additional_appointment`.

## Validation outputs

Stable error and warning identifiers are emitted with severity, role, person and message. The CLI writes a human-readable report and a machine-readable JSON result. Deterministic ordering is by severity, code, role, person and message. No timestamps appear in generated output.

## Standard-library schema validation

`validate_schema()` supports type (including null unions), required, properties, additionalProperties, enum, items and local `$ref`. This subset is sufficient for this state schema and is documented as a limitation relative to a full JSON Schema implementation.

""")

w('docs/SCHEMA_VALIDATION.md', f"""# Schema Validation Note

{G}

Schema validation was executed using `cli/validate_schema.py`, which calls the standard-library subset validator in `engine/validator.py`. No external `jsonschema` dependency was used.

Supported keywords: `$ref`, `type`, `required`, `properties`, `additionalProperties`, `enum`, `items`. Unsupported keywords are not used by `schemas/team_assignment.schema.json`. The schema declares all six roles and rejects unknown structural properties.

Command and output are captured in `reports/schema_validation.txt`. Result: 16 JSON files validated; exit 0.

""")

w('docs/VALIDATION_REPORT.md', f"""# Validation Report

{G}

## Executed evidence

| Check | Result | Report |
|---|---|---|
| Schema validation, current state + 15 fixtures | PASS; exit 0 | `reports/schema_validation.txt` |
| Unit tests | 16 tests, OK; exit 0 | `reports/unit_tests.txt` |
| Integration tests | 4 tests, OK; exit 0 | `reports/integration_tests.txt` |
| CLI current assignment state | Blocking errors: 5; exit 1 | `reports/cli_current_state.txt` |
| CLI valid four-person fixture | Valid YES; exit 0 | `reports/cli_valid_four.txt` |
| Determinism across two working directories | stdout/stderr identical; exit 1 expected | `reports/determinism.txt` |

## Current state result

Research Owner is `ACCEPTED_IN_CONVERSATION`; Moderator, Note-taker, Data Custodian, Analyst and Continue/Stop Owner are `UNASSIGNED`. The validator reports five `E-APPOINTMENT-MISSING` errors, one `W-TOPOLOGY-PROPOSED` warning and one `I-RO-NOT-FORMAL` info. It does not promote the Research Owner to formal appointment.

## High-severity invariants demonstrated

- Hard incompatibilities produce blocking errors.
- Discouraged combinations produce warnings unless resolved.
- Conditional combinations produce blocking errors without required evidence.
- Missing acceptance, approval, availability, conflict disclosure, confidentiality, escalation and onboarding produce distinct blocking errors.
- Duplicate and unknown roles produce blocking errors.
- Valid four-, five- and six-person models produce no blocking errors.
- Invalid three-person model produces a hard incompatibility error.

## Limitations

Schema validation is a documented standard-library subset. No actual application parser, UI or field research was executed. Unittest timing lines vary; determinism is asserted on CLI output only. Synthetic fixtures are not appointment records.

""")

w('docs/IMPLEMENTATION_COMPLETION_REPORT.md', f"""# Implementation Completion Report

{G}

## Completion criteria

| Criterion | Status | Evidence |
|---|---|---|
| Executable validator exists | MET | `engine/validator.py` |
| Machine-readable policy | MET | `policy/role_constraints.json` |
| CLI runs successfully | MET | `cli/validate.py`; valid fixture exit 0 |
| Synthetic tests execute | MET | 16 unit + 4 integration tests |
| Current state evaluated correctly | MET | 5 missing appointments; Research Owner not promoted |
| Reports and hashes generated | MET | `reports/`, `SHA256_MANIFEST.json` |
| Governance unchanged | MET | No repository/register/ADR/storage/participant action |

## Final statement

The engine implements the policy as executable validation logic. It does not appoint people, accept candidates, authorize recruitment, authorize field validation or complete Stage B.

""")

# manifest: exclude manifest itself
manifest=[]
for root, dirs, files in os.walk(D):
    dirs.sort()
    for fn in sorted(files):
        p=os.path.join(root,fn)
        rel=os.path.relpath(p,D).replace('\\','/')
        if rel == 'SHA256_MANIFEST.json':
            continue
        b=open(p,'rb').read()
        manifest.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
manifest.sort(key=lambda x:x['path'])
open(os.path.join(D,'SHA256_MANIFEST.json'),'w',encoding='utf-8').write(
    json.dumps({'package':'M001_TEAM_ASSIGNMENT_ENGINE','files':manifest},indent=2)+'\n')
print('manifest files',len(manifest))
for r in manifest: print(r['sha256'],r['bytes'],r['path'])
