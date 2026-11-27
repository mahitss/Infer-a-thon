#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V2.2 five-area canary; imports validator from --root only."""
import argparse, sys
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument('--root', required=True); args = ap.parse_args()
root = Path(args.root)
sys.path.insert(0, str(root))
from engine.validator import load_json_strict, load_policy, load_schema, validate_state  # noqa: E402
P = load_policy(root / 'policy' / 'role_constraints.json')
S = load_schema(root / 'schemas' / 'team_assignment.schema.json')
F = root / 'tests' / 'fixtures'


def v(name):
    r = validate_state(load_json_strict(F / name), P, S)
    return r, set(i.code for i in r.issues)


checks = []
def add(cid, claim, ok, detail=''):
    checks.append((cid, claim, bool(ok), detail))

r, c = v('valid_four_person.json')
add('B00', 'valid state passes', r.stage_b_role_ready and not c)
r, c = v('basis_invisible_zwsp.json')
add('B01', 'invisible basis rejected', not r.stage_b_role_ready and 'E-DECISION-EVIDENCE-EMPTY' in c)
r, c = v('rationale_invisible_wj.json')
add('B02', 'invisible rationale rejected', not r.stage_b_role_ready and 'E-COMBINATION-RATIONALE' in c)
r, c = v('basis_valid_emoji_zwj.json')
add('B03', 'meaningful ZWJ emoji text accepted', r.stage_b_role_ready and not c)
r, c = v('escalation_ws.json')
add('B04', 'whitespace escalation contact rejected', not r.stage_b_role_ready and 'E-ESCALATION-CONTACT' in c)
r, c = v('evidence_duplicate.json')
add('B05', 'duplicate evidence rejected', not r.stage_b_role_ready and 'E-EVIDENCE-DUPLICATE' in c)
r, c = v('combination_before_acceptance.json')
add('B06', 'combination before acceptance rejected',
    not r.stage_b_role_ready and 'E-COMBINATION-APPROVAL-TIMESTAMP-ORDER' in c)
r, c = v('candidate_whitespace_ref.json')
add('B07', 'whitespace candidate ref rejected', not r.stage_b_role_ready and 'E-CANDIDATE-REF-INVALID' in c)

for cid, claim, ok, detail in checks:
    print('%s %s %s | %s' % ('PASS' if ok else 'FAIL', cid, claim, detail))
print('CANARY_PASS %d/%d' % (sum(1 for x in checks if x[2]), len(checks)))
sys.exit(0 if all(x[2] for x in checks) else 1)
