#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mutation canary tests; imports validator from --root only."""
import argparse, json, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--root', required=True)
args = ap.parse_args()
root = Path(args.root)
sys.path.insert(0, str(root))
from engine.validator import load_json, load_policy, load_schema, validate_state  # noqa: E402

POLICY = load_policy(root / 'policy' / 'role_constraints.json')
SCHEMA = load_schema(root / 'schemas' / 'team_assignment.schema.json')
AUDIT = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_AUDIT')
ADV = AUDIT / 'adversarial_fixtures'
ORIG = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE')

def codes(r, sev=None):
    return [i.code for i in r.issues if sev is None or i.severity == sev]

def v(path):
    return validate_state(load_json(path), POLICY, SCHEMA)

checks = []
def add(cid, claim, ok, detail=''):
    checks.append((cid, claim, bool(ok), detail))

r = v(ADV / 'hard_moderator_analyst.json')
add('C1','hard Moderator+Analyst error','E-HARD-MODERATOR-ANALYST' in codes(r,'ERROR'), codes(r,'ERROR'))
r = v(ADV / 'hard_moderator_custodian.json')
add('C2','hard Moderator+Custodian error','E-HARD-MODERATOR-CUSTODIAN' in codes(r,'ERROR'), codes(r,'ERROR'))
r = v(ORIG / 'fixtures' / 'missing_evidence_separation.json')
add('C3','evidence separation error','E-COND-EVIDENCE-SEPARATION' in codes(r,'ERROR'), codes(r,'ERROR'))
r = v(ORIG / 'fixtures' / 'missing_explicit_cs.json')
add('C4','explicit CS error','E-COND-EXPLICIT-CS' in codes(r,'ERROR'), codes(r,'ERROR'))
r = v(ORIG / 'state' / 'current_assignment_state.json')
add('C5','RO not formal info','I-RO-NOT-FORMAL' in codes(r,'INFO'), codes(r,'INFO'))
r = v(ORIG / 'fixtures' / 'missing_po_approval.json')
add('C6','PO approval error','E-PO-APPROVAL' in codes(r,'ERROR'), codes(r,'ERROR'))
r = v(ORIG / 'fixtures' / 'missing_candidate_acceptance.json')
add('C7','candidate acceptance error','E-CANDIDATE-ACCEPTANCE' in codes(r,'ERROR'), codes(r,'ERROR'))
r = v(ORIG / 'fixtures' / 'missing_onboarding.json')
add('C8','onboarding error','E-ONBOARDING' in codes(r,'ERROR'), codes(r,'ERROR'))
r = v(ADV / 'discouraged_ro_moderator.json')
add('C9','discouraged warning','W-DISCOURAGED-RO-MODERATOR' in codes(r,'WARNING'), codes(r,'WARNING'))
r = v(ORIG / 'state' / 'current_assignment_state.json')
add('C10','five missing appointments',len([i for i in r.errors if i.code=='E-APPOINTMENT-MISSING'])==5,
    len([i for i in r.errors if i.code=='E-APPOINTMENT-MISSING']))

for cid,claim,ok,detail in checks:
    print('%s %s %s | %s' % ('PASS' if ok else 'FAIL',cid,claim,detail))
print('CANARY_PASS %d/%d' % (sum(1 for c in checks if c[2]), len(checks)))
sys.exit(0 if all(c[2] for c in checks) else 1)
