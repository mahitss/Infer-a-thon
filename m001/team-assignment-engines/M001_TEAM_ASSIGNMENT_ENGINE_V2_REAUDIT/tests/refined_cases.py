#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Refined independent checks for cases whose first construction was ambiguous."""
import copy, json, sys
from pathlib import Path
V2 = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2')
REAUDIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V2))
from engine.validator import load_json_strict, load_policy, load_schema, validate_state  # noqa: E402
P, S = load_policy(), load_schema()
F = V2 / 'tests' / 'fixtures'
BASE = load_json_strict(F / 'valid_four_person.json')


def run(st):
    r = validate_state(st, P, S)
    return {'codes': sorted(set(i.code for i in r.issues)),
            'dimensions': dict(sorted(r.dimensions.items())),
            'ready': r.stage_b_role_ready, 'errors': len(r.errors)}


def replace_all(obj, old, new):
    if isinstance(obj, dict):
        return {replace_all(k, old, new): replace_all(v, old, new) for k, v in obj.items()}
    if isinstance(obj, list):
        return [replace_all(x, old, new) for x in obj]
    if isinstance(obj, str):
        return obj.replace(old, new)
    return obj


out = {}

# DIM-02: unknown evidence ID -> dimension consistency
s = copy.deepcopy(BASE)
s['roles']['ANALYST']['acceptance']['evidence_id'] = 'e-DOES-NOT-EXIST'
out['DIM-02_unknown_evidence_id'] = run(s)

# DIM-03: subject-mismatched evidence (correctly constructed)
s = copy.deepcopy(BASE)
s['evidence']['e-acc-C-P1']['subject'] = 'C-P2'
out['DIM-03_subject_mismatch'] = run(s)

# ST-02 refined: stale acceptance timestamp, ordering still valid
s = copy.deepcopy(BASE)
s['roles']['RESEARCH_OWNER']['acceptance']['candidate_accepted_at'] = '2020-01-01T00:00:00+00:00'
out['ST-02_stale_acceptance_order_valid'] = run(s)

# COMB-12 refined: approval candidate substituted to another candidate with same roles
s = copy.deepcopy(BASE)
s['combination_approvals'][0]['candidate_ref'] = 'C-P2'
out['COMB-12_approval_reused_other_candidate'] = run(s)

# EVID-02 refined: one acceptance evidence record bound to two roles of one candidate
s = copy.deepcopy(BASE)
new_id = 'e-acc-shared-C-P1'
s['evidence'][new_id] = copy.deepcopy(s['evidence']['e-acc-C-P1'])
s['evidence'][new_id]['evidence_id'] = new_id
s['roles']['RESEARCH_OWNER']['acceptance']['evidence_id'] = new_id
s['roles']['CONTINUE_STOP_OWNER']['acceptance']['evidence_id'] = new_id
out['EVID-02_shared_acceptance_two_roles'] = run(s)

# ID-03 refined: whitespace-only candidate reference applied consistently everywhere
s = replace_all(copy.deepcopy(BASE), 'C-P1', '   ')
out['ID-03_whitespace_ref_consistent'] = run(s)

# ID-02 refined: unicode-equivalent identifier split across two single-role candidates
s = copy.deepcopy(BASE)
s['candidates']['C-P１'] = {'candidate_ref': 'C-P１', 'active': True, 'fixture_marker': 'SYNTHETIC_TEST_DATA'}
s['candidates']['C-P1b'] = {'candidate_ref': 'C-P1b', 'active': True, 'fixture_marker': 'SYNTHETIC_TEST_DATA'}
del s['candidates']['C-P1']
s['roles']['RESEARCH_OWNER']['candidate_ref'] = 'C-P１'
s['roles']['CONTINUE_STOP_OWNER']['candidate_ref'] = 'C-P1b'
s['appointments'] = [a for a in s['appointments'] if a['role'] not in ('RESEARCH_OWNER', 'CONTINUE_STOP_OWNER')]
s['appointments'].append({'candidate_ref': 'C-P１', 'role': 'RESEARCH_OWNER', 'state': 'FORMALLY_APPOINTED'})
s['appointments'].append({'candidate_ref': 'C-P1b', 'role': 'CONTINUE_STOP_OWNER', 'state': 'FORMALLY_APPOINTED'})
s['combination_approvals'] = []
for eid, e in s['evidence'].items():
    if e['subject'] == 'C-P1:CONTINUE_STOP_OWNER+RESEARCH_OWNER':
        e['subject'] = 'C-P１:RESEARCH_OWNER'
    elif e['subject'] == 'C-P1':
        e['subject'] = 'C-P１' if eid in ('e-acc-C-P1', 'e-po-C-P1', 'e-form-C-P1', 'e-onb-C-P1') else 'C-P1b'
for role, ref in (('RESEARCH_OWNER', 'C-P１'), ('CONTINUE_STOP_OWNER', 'C-P1b')):
    r = s['roles'][role]
    for h in ('acceptance', 'approval', 'formal', 'onboarding'):
        if h in r and isinstance(r[h], dict) and r[h].get('evidence_id'):
            r[h]['evidence_id'] = 'e-' + h[0] + '-' + ref
# build matching evidence entries with subjects set to the new refs
for ref in ('C-P１', 'C-P1b'):
    for h, typ, tag in (('acceptance', 'CANDIDATE_ACCEPTANCE', 'a'), ('approval', 'PRODUCT_OWNER_APPROVAL', 'p'),
                        ('formal', 'FORMAL_APPOINTMENT', 'f'), ('onboarding', 'ONBOARDING', 'o')):
        eid = 'e-' + h[0] + '-' + ref
        s['evidence'][eid] = copy.deepcopy(BASE['evidence']['e-acc-C-P1'])
        s['evidence'][eid]['evidence_id'] = eid
        s['evidence'][eid]['evidence_type'] = typ
        s['evidence'][eid]['subject'] = ref
out['ID-02_unicode_equivalent_split'] = run(s)

# ID-07 refined: six distinct identities, no combination approvals, all pass
out['ID-07_six_distinct_identities'] = run(load_json_strict(F / 'valid_six_person.json'))

# COMB-03 refined: duplicated role in approval (confirm accepted)
s = copy.deepcopy(BASE)
s['combination_approvals'][0]['roles'] = ['RESEARCH_OWNER', 'CONTINUE_STOP_OWNER', 'CONTINUE_STOP_OWNER']
out['COMB-03_duplicate_roles_approval'] = run(s)

# ST-09 / COMB-11 whitespace basis/rationale (confirm accepted)
s = copy.deepcopy(BASE)
s['roles']['RESEARCH_OWNER']['approval']['basis'] = '  \t\n '
out['ST-09_whitespace_basis'] = run(s)
s = copy.deepcopy(BASE)
s['combination_approvals'][0]['rationale'] = '  \t\n '
out['COMB-11_whitespace_rationale'] = run(s)

# EVID-03 / EVID-04 / EVID-06 confirm accepted
s = copy.deepcopy(BASE)
s['evidence']['e-acc-C-P1']['content_hash'] = '0' * 64
out['EVID-03_hash_mismatch'] = run(s)
s = copy.deepcopy(BASE)
s['evidence']['e-acc-C-P1-copy'] = copy.deepcopy(s['evidence']['e-acc-C-P1'])
out['EVID-04_duplicate_evidence'] = run(s)
s = copy.deepcopy(BASE)
s['evidence']['e-form-C-P1']['timestamp'] = '1999-01-01T00:00:00+00:00'
out['EVID-06_evidence_predates_source'] = run(s)

path = REAUDIT / 'tests' / 'results' / 'refined_case_results.json'
path.write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
for k, v in out.items():
    print(k, '| ready=', v['ready'], '| codes=', v['codes'], '| evidence_integrity=', v['dimensions'].get('evidence_integrity'))
print('wrote', path)
