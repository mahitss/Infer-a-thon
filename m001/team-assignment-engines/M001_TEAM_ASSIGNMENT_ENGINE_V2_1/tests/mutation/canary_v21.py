#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V2.1 four-area canary. Imports the validator from --root only."""
import argparse, json, sys
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument('--root', required=True); args = ap.parse_args()
root = Path(args.root)
sys.path.insert(0, str(root))
from engine.validator import load_json_strict, load_policy, load_schema, validate_state  # noqa: E402
P = load_policy(root / 'policy' / 'role_constraints.json')
S = load_schema(root / 'schemas' / 'team_assignment.schema.json')
F = root / 'tests' / 'fixtures'


def v(name):
    return validate_state(load_json_strict(F / name), P, S)


def codes(r):
    return set(i.code for i in r.issues)


checks = []
def check(cid, claim, ok, detail=''):
    checks.append((cid, claim, bool(ok), detail))

r = v('valid_four_person.json')
check('B00', 'valid synthetic state passes', r.stage_b_role_ready and not r.errors)
r = v('basis_ascii_ws.json')
check('B01', 'ASCII whitespace basis blocked', not r.stage_b_role_ready and 'E-DECISION-EVIDENCE-EMPTY' in codes(r))
r = v('basis_unicode_ws.json')
check('B02', 'Unicode whitespace basis blocked', not r.stage_b_role_ready and 'E-DECISION-EVIDENCE-EMPTY' in codes(r))
r = v('rationale_ws.json')
check('B03', 'whitespace rationale blocked', not r.stage_b_role_ready and 'E-COMBINATION-RATIONALE' in codes(r))
r = v('acceptance_wrong_role.json')
check('B04', 'wrong-role acceptance blocked',
      not r.stage_b_role_ready and bool({'E-ACCEPTANCE-ROLE', 'E-EVIDENCE-SUBJECT', 'E-ACCEPTANCE-APPOINTMENT'} & codes(r)))
r = v('acceptance_revoked.json')
check('B05', 'revoked acceptance evidence blocked', not r.stage_b_role_ready and 'E-EVIDENCE-REVOKED' in codes(r))
r = v('schema_invalid_assignment.json')
check('B06', 'schema failure controlled and terminal',
      not r.stage_b_role_ready and 'E-SCHEMA' in codes(r) and all(d == 'FAIL' for d in r.dimensions.values()))
badref = load_schema(F / 'unresolvable_ref_schema.json')
r = validate_state(load_json_strict(F / 'valid_four_person.json'), P, badref)
check('B07', 'unresolvable schema ref controlled', not r.stage_b_role_ready and
      any(c.startswith('E-SCHEMA') for c in codes(r)))

for cid, claim, ok, detail in checks:
    print('%s %s %s | %s' % ('PASS' if ok else 'FAIL', cid, claim, detail))
print('CANARY_PASS %d/%d' % (sum(1 for c in checks if c[2]), len(checks)))
sys.exit(0 if all(c[2] for c in checks) else 1)
