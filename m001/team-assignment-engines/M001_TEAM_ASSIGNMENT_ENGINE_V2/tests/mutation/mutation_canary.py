#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V2 mutation canary: imports validator from --root only."""
import argparse, sys
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument('--root', required=True); args = ap.parse_args()
root = Path(args.root); sys.path.insert(0, str(root))
from engine.validator import load_json_strict, load_policy, load_schema, validate_state  # noqa: E402
P = load_policy(root/'policy'/'role_constraints.json'); S = load_schema(root/'schemas'/'team_assignment.schema.json')
F = root/'tests'/'fixtures'
def v(n): return validate_state(load_json_strict(F/n), P, S)
def codes(r): return [i.code for i in r.issues]
checks=[]
def add(cid, claim, ok, detail=''): checks.append((cid, claim, bool(ok), detail))
r=v('hard_incompatibility_approved.json'); add('C1','hard incompatibility blocked','E-HARD-MODERATOR-ANALYST' in codes(r),codes(r))
r=v('discouraged_no_review.json'); add('C2','discouraged review blocked','E-DISCOURAGED-RO-MODERATOR' in codes(r),codes(r))
r=v('conditional_missing_separation.json'); add('C3','evidence separation blocked','E-COND-EVIDENCE-SEPARATION' in codes(r),codes(r))
r=v('multi_role_no_approval.json'); add('C4','multi-role approval blocked',any(c.startswith('E-COMBINATION-APPROVAL-MISSING') for c in codes(r)),codes(r))
r=v('current_assignment_state.json'); add('C5','PROPOSED/conversation not formal',len([i for i in r.errors if i.code=='E-APPOINTMENT-MISSING'])==6,codes(r))
r=v('formal_missing_formal_approval.json'); add('C6','formal flag mismatch blocked','E-FORMAL-APPROVAL-MISMATCH' in codes(r),codes(r))
r=v('missing_candidate_acceptance.json'); add('C7','candidate acceptance blocked','E-CANDIDATE-ACCEPTANCE' in codes(r),codes(r))
r=v('missing_onboarding.json'); add('C8','onboarding blocked','E-ONBOARDING' in codes(r),codes(r))
r=v('unknown_candidate_identity.json'); add('C9','unknown candidate blocked','E-CANDIDATE-UNKNOWN' in codes(r),codes(r))
r=v('forged_evidence_id.json'); add('C10','broken evidence blocked','E-EVIDENCE-UNKNOWN' in codes(r),codes(r))
r=v('naive_timestamp.json'); add('C11','naive timestamp blocked','E-TIMESTAMP-MISSING' in codes(r),codes(r))
r=v('topology_unapproved_stage_b.json'); add('C12','topology approval blocked','E-TOPOLOGY-UNAPPROVED' in codes(r),codes(r))
r=v('empty_approval_basis.json'); add('C13','empty approval basis blocked','E-DECISION-EVIDENCE-EMPTY' in codes(r),codes(r))
r=v('duplicate_candidate_identity.json'); add('C14','duplicate candidate blocked','E-CANDIDATE-DUPLICATE' in codes(r),codes(r))
r=v('recruitment_inferred.json'); add('C15','authorization state blocked','E-AUTHORIZATION-STATE' in codes(r),codes(r))
r=v('valid_four_person.json'); add('C16','valid model still passes',r.stage_b_role_ready,codes(r))
r=v('hard_incompatibility_mdc.json'); add('C17','hard MDC conflict blocked','E-HARD-MODERATOR-CUSTODIAN' in codes(r),codes(r))
r=v('po_approval_missing.json'); add('C18','role PO approval blocked','E-PO-APPROVAL' in codes(r),codes(r))
for cid,claim,ok,detail in checks: print('%s %s %s | %s' % ('PASS' if ok else 'FAIL',cid,claim,detail))
print('CANARY_PASS %d/%d' % (sum(1 for c in checks if c[2]),len(checks)))
sys.exit(0 if all(c[2] for c in checks) else 1)
