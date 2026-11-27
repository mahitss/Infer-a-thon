# -*- coding: utf-8 -*-
"""Build V2.1 synthetic fixtures. All candidate data is SYNTHETIC_TEST_DATA."""
import copy, hashlib, json, os
D = r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1\tests\fixtures'
os.makedirs(D, exist_ok=True)
ROLES = ['RESEARCH_OWNER', 'MODERATOR', 'NOTE_TAKER', 'DATA_CUSTODIAN', 'ANALYST', 'CONTINUE_STOP_OWNER']
TS = ['2026-11-27T00:00:00+00:00', '2026-11-27T01:00:00+00:00',
      '2026-11-27T02:00:00+00:00', '2026-11-27T03:00:00+00:00']
MARK = 'SYNTHETIC_TEST_DATA'


def evid(eid, etype, subject, role=None, appointment_ref=None, decision_ref=None):
    return {
        'evidence_id': eid, 'evidence_type': etype, 'source_ref': 'synthetic://' + eid,
        'content_hash': hashlib.sha256(eid.encode()).hexdigest(),
        'recording_authority': MARK, 'timestamp': TS[0], 'verification_status': 'VERIFIED',
        'subject': subject, 'role': role, 'appointment_ref': appointment_ref,
        'decision_ref': decision_ref, 'revoked': False, 'revoked_at': None,
    }


def state(assign_map, topology='APPROVED'):
    st = {
        'schema_version': '2.0',
        'governance': {'m001_status': 'OPEN', 'm002_status': 'UNAUTHORIZED',
                       'recruitment': 'UNAUTHORIZED', 'field_validation': 'NOT_STARTED'},
        'topology': {'status': topology, 'model': 'FOUR_PERSON'},
        'candidates': {}, 'evidence': {}, 'roles': {}, 'appointments': [], 'combination_approvals': [],
    }
    for cand, roles in assign_map:
        st['candidates'][cand] = {'candidate_ref': cand, 'active': True, 'fixture_marker': MARK}
        for role in roles:
            subject = cand + ':' + role
            acc = 'e-acc-' + cand + '-' + role
            apo = 'e-po-' + cand + '-' + role
            form = 'e-form-' + cand + '-' + role
            onb = 'e-onb-' + cand + '-' + role
            st['evidence'][acc] = evid(acc, 'CANDIDATE_ACCEPTANCE', subject, role,
                                       subject, 'acc-decision-' + cand + '-' + role)
            st['evidence'][apo] = evid(apo, 'PRODUCT_OWNER_APPROVAL', cand)
            st['evidence'][form] = evid(form, 'FORMAL_APPOINTMENT', cand)
            st['evidence'][onb] = evid(onb, 'ONBOARDING', cand)
            st['roles'][role] = {
                'state': 'FORMALLY_APPOINTED', 'candidate_ref': cand,
                'recognition': {'status': None, 'decision_date': None, 'formal': False, 'evidence_text': None},
                'acceptance': {'candidate_accepted': True, 'evidence_id': acc, 'candidate_accepted_at': TS[0]},
                'approval': {'product_owner_approved': True, 'formal': True, 'evidence_id': apo,
                             'basis': MARK + ' documented approval for ' + subject,
                             'product_owner_approved_at': TS[1]},
                'formal': {'formally_appointed': True, 'evidence_id': form, 'formal_appointed_at': TS[2]},
                'availability': {'confirmed': True}, 'conflict_disclosure': {'provided': True},
                'confidentiality': {'acknowledged': True},
                'onboarding': {'completed': True, 'evidence_id': onb},
                'escalation': {'contact': 'synthetic-escalation-' + cand},
            }
            st['appointments'].append({'candidate_ref': cand, 'role': role, 'state': 'FORMALLY_APPOINTED'})
        if len(roles) > 1:
            key = '+'.join(sorted(roles))
            ce = 'e-combo-' + cand + '-' + key
            st['evidence'][ce] = evid(ce, 'COMBINATION_REVIEW', cand + ':' + key)
            if set(roles) == {'MODERATOR', 'NOTE_TAKER'}:
                se = 'e-sep-' + cand
                st['evidence'][se] = evid(se, 'EVIDENCE_SEPARATION', cand + ':' + key)
            st['combination_approvals'].append({
                'candidate_ref': cand, 'roles': sorted(roles), 'outcome': 'APPROVED',
                'rationale': MARK + ' explicit PO approval for exact combination ' + cand + ':' + key,
                'evidence_id': ce, 'product_owner_approved': True, 'decision_timestamp': TS[1],
            })
    return st


def save(name, obj):
    json.dump(obj, open(os.path.join(D, name), 'w', encoding='utf-8'), indent=2)


four = state([('C-P1', ['RESEARCH_OWNER', 'CONTINUE_STOP_OWNER']),
              ('C-P2', ['MODERATOR', 'NOTE_TAKER']),
              ('C-P3', ['DATA_CUSTODIAN']), ('C-P4', ['ANALYST'])])
save('valid_four_person.json', four)
five = state([('C-P1', ['RESEARCH_OWNER']), ('C-P2', ['MODERATOR', 'NOTE_TAKER']),
              ('C-P3', ['DATA_CUSTODIAN']), ('C-P4', ['ANALYST']), ('C-P5', ['CONTINUE_STOP_OWNER'])])
five['topology']['model'] = 'FIVE_PERSON'
save('valid_five_person.json', five)
six = state([('C-P%d' % i, [r]) for i, r in enumerate(ROLES, 1)])
six['topology']['model'] = 'SIX_PERSON'
save('valid_six_person.json', six)

# Original V2 regression variants.
x = copy.deepcopy(four); x['combination_approvals'] = []; save('multi_role_no_approval.json', x)
x = copy.deepcopy(four); x['combination_approvals'][0]['roles'] = ['RESEARCH_OWNER', 'MODERATOR']; save('approval_different_combination.json', x)
x = copy.deepcopy(four); x['roles']['MODERATOR']['state'] = 'PROPOSED'; save('proposed_treated_as_appointed.json', x)
x = copy.deepcopy(four); x['roles']['MODERATOR']['state'] = 'ACCEPTED_IN_CONVERSATION'; save('accepted_conversation_formal.json', x)
x = copy.deepcopy(four); x['roles']['MODERATOR']['acceptance']['evidence_id'] = None; save('boolean_evidence_without_ref.json', x)
x = copy.deepcopy(four); x['roles']['MODERATOR']['acceptance']['evidence_id'] = 'e-FORGED'; save('forged_evidence_id.json', x)
x = copy.deepcopy(four); x['candidates']['C-P2']['candidate_ref'] = 'C-P1'; save('duplicate_candidate_identity.json', x)
x = copy.deepcopy(four); x['roles']['MODERATOR']['candidate_ref'] = 'C-UNKNOWN'; save('unknown_candidate_identity.json', x)
x = copy.deepcopy(four); x['roles']['MODERATOR']['approval']['formal'] = False; save('formal_missing_formal_approval.json', x)
x = copy.deepcopy(four); x['roles']['MODERATOR']['approval']['basis'] = ''; save('empty_approval_basis.json', x)
x = state([('C-P1', ['RESEARCH_OWNER', 'MODERATOR']), ('C-P2', ['NOTE_TAKER']),
           ('C-P3', ['DATA_CUSTODIAN']), ('C-P4', ['ANALYST']), ('C-P5', ['CONTINUE_STOP_OWNER'])])
x['combination_approvals'] = []; save('discouraged_no_review.json', x)
x = copy.deepcopy(four); x['roles']['MODERATOR']['formal']['formal_appointed_at'] = None; save('missing_timestamps.json', x)
x = copy.deepcopy(four); x['topology']['status'] = 'PROPOSED'; save('topology_unapproved_stage_b.json', x)
x = copy.deepcopy(four); x['roles']['ANALYST']['state'] = 'REJECTED'; save('rejected_active_appointment.json', x)
x = copy.deepcopy(four); x['roles']['ANALYST']['onboarding']['completed'] = False; save('missing_onboarding.json', x)
x = copy.deepcopy(four); x['governance']['recruitment'] = 'AUTHORIZED'; save('recruitment_inferred.json', x)
x = state([('C-P1', ['MODERATOR', 'ANALYST']), ('C-P2', ['RESEARCH_OWNER']),
           ('C-P3', ['NOTE_TAKER']), ('C-P4', ['DATA_CUSTODIAN']), ('C-P5', ['CONTINUE_STOP_OWNER'])])
save('hard_incompatibility_approved.json', x)
x = copy.deepcopy(four); del x['evidence']['e-sep-C-P2']; save('conditional_missing_separation.json', x)
x = copy.deepcopy(four); x['roles']['ANALYST']['formal']['formal_appointed_at'] = '2026-11-27T02:00:00'; save('naive_timestamp.json', x)
x = copy.deepcopy(four); x['roles']['ANALYST']['acceptance']['candidate_accepted'] = False; save('missing_candidate_acceptance.json', x)
x = copy.deepcopy(four); x['roles']['DATA_CUSTODIAN']['candidate_ref'] = 'C-P2'
x['appointments'] = [a for a in x['appointments'] if a['role'] != 'DATA_CUSTODIAN']
x['appointments'].append({'candidate_ref': 'C-P2', 'role': 'DATA_CUSTODIAN', 'state': 'FORMALLY_APPOINTED'})
save('hard_incompatibility_mdc.json', x)
x = copy.deepcopy(four); x['roles']['ANALYST']['approval']['product_owner_approved'] = False; save('po_approval_missing.json', x)

# Required V2.1 HIGH-finding regression cases.
for name, value in (
    ('basis_empty.json', ''), ('basis_ascii_ws.json', '  \t\n '),
    ('basis_unicode_ws.json', '\u00a0\u2003\u3000'), ('basis_null.json', None),
    ('basis_nonstring.json', 12345),
):
    x = copy.deepcopy(four); x['roles']['RESEARCH_OWNER']['approval']['basis'] = value; save(name, x)
x = copy.deepcopy(four); del x['roles']['RESEARCH_OWNER']['approval']['basis']; save('basis_missing.json', x)
for name, value in (
    ('rationale_empty.json', ''), ('rationale_ws.json', '  \t\n '),
    ('rationale_unicode_ws.json', '\u00a0\u2003\u3000'), ('rationale_null.json', None),
    ('rationale_nonstring.json', ['approved']),
):
    x = copy.deepcopy(four); x['combination_approvals'][0]['rationale'] = value; save(name, x)
x = copy.deepcopy(four); del x['combination_approvals'][0]['rationale']; save('rationale_missing.json', x)

# Acceptance evidence role/candidate/appointment binding cases.
x = copy.deepcopy(four)
x['roles']['CONTINUE_STOP_OWNER']['acceptance']['evidence_id'] = 'e-acc-C-P1-RESEARCH_OWNER'
save('acceptance_wrong_role.json', x)
x = copy.deepcopy(four)
x['roles']['CONTINUE_STOP_OWNER']['acceptance']['evidence_id'] = 'e-acc-C-P4-ANALYST'
save('acceptance_wrong_candidate.json', x)
x = copy.deepcopy(four)
x['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER']['appointment_ref'] = 'C-P1:OTHER_ROLE'
save('acceptance_other_appointment.json', x)
x = copy.deepcopy(four)
x['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER']['subject'] = 'C-P1:ANOTHER_ROLE'
save('acceptance_subject_mismatch.json', x)
x = copy.deepcopy(four)
x['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER']['verification_status'] = 'PENDING'
save('acceptance_unverified.json', x)
x = copy.deepcopy(four)
x['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER']['revoked'] = True
save('acceptance_revoked.json', x)
x = copy.deepcopy(four)
x['roles']['CONTINUE_STOP_OWNER']['acceptance']['evidence_id'] = None
save('acceptance_missing.json', x)
x = copy.deepcopy(four)
x['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER']['decision_ref'] = 'acc-decision-C-P1-RESEARCH_OWNER'
save('acceptance_decision_reused.json', x)

# Schema failure cases.
open(os.path.join(D, 'schema_invalid_assignment.json'), 'w', encoding='utf-8').write(json.dumps({
    'schema_version': '2.0', 'governance': None, 'topology': 'APPROVED',
    'candidates': {}, 'evidence': {}, 'roles': {}, 'appointments': [], 'combination_approvals': []}))
open(os.path.join(D, 'invalid_schema.json'), 'w', encoding='utf-8').write('{"type": 123, "required": "not-an-array"}')
badref = json.load(open(os.path.join(D, 'valid_four_person.json'), encoding='utf-8'))
schema_text = open(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1\schemas\team_assignment.schema.json', encoding='utf-8').read()
schema_text = schema_text.replace('#/$defs/candidate', '#/$defs/DOES_NOT_EXIST')
open(os.path.join(D, 'unresolvable_ref_schema.json'), 'w', encoding='utf-8').write(schema_text)

current = json.load(open(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1\state\current_assignment_state.json', encoding='utf-8'))
save('current_assignment_state.json', current)
open(os.path.join(D, 'malformed.json'), 'w', encoding='utf-8').write('{ bad json')
open(os.path.join(D, 'invalid_utf8.bin'), 'wb').write(b'{"schema_version":"2.0",\xff}')
raw = json.dumps(four)[:-1] + ', "schema_version":"2.0"}'
open(os.path.join(D, 'duplicate_json_key.json'), 'w', encoding='utf-8').write(raw)
print('V2.1 fixtures:', len([f for f in os.listdir(D)]))
