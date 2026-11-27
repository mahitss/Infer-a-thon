# -*- coding: utf-8 -*-
"""Create synthetic fixtures for the team assignment validator."""
import copy, json, os
D = r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE\fixtures'
os.makedirs(D, exist_ok=True)
ROLES = ['RESEARCH_OWNER','MODERATOR','NOTE_TAKER','DATA_CUSTODIAN','ANALYST','CONTINUE_STOP_OWNER']

def role(state='FORMALLY_APPOINTED', candidate='P', acceptance=True, evidence='synthetic acceptance',
         approval=True, availability=True, conflict=True, confidentiality=True, onboarding=True,
         contact='ESC', formal=True):
    return {
        'state': state,
        'candidate_id': candidate if state not in ('UNASSIGNED',) else None,
        'acceptance': {'candidate_accepted': acceptance, 'evidence': evidence},
        'approval': {'product_owner_approved': approval, 'formal': formal,
                     'basis': 'synthetic Product Owner decision'},
        'availability': {'confirmed': availability},
        'conflict_disclosure': {'provided': conflict},
        'confidentiality': {'acknowledged': confidentiality},
        'onboarding': {'completed': onboarding},
        'escalation': {'contact': contact}
    }

def state(assignments, model='FOUR_PERSON', topology='APPROVED'):
    return {
        'schema_version': '1.0',
        'governance': {'m001_status':'OPEN','m002_status':'UNAUTHORIZED',
                       'recruitment':'UNAUTHORIZED','field_validation':'NOT_STARTED'},
        'topology': {'status':topology,'model':model},
        'roles': {r: role(candidate='P'+str(i+1)) for i,r in enumerate(ROLES)},
        'assignments': assignments
    }

def assignment(pid, roles, evidence=None, resolutions=None):
    a = {'person_id': pid, 'roles': roles}
    if evidence is not None:
        a['conditional_evidence'] = evidence
    if resolutions is not None:
        a['resolutions'] = resolutions
    return a

def save(name, obj):
    json.dump(obj, open(os.path.join(D,name),'w',encoding='utf-8'), indent=2)

valid4 = state([
 assignment('P1',['RESEARCH_OWNER','CONTINUE_STOP_OWNER'],
             {'explicit_additional_appointment': True}),
 assignment('P2',['MODERATOR','NOTE_TAKER'],
             {'evidence_separation_documented': True}),
 assignment('P3',['DATA_CUSTODIAN']),
 assignment('P4',['ANALYST'])])
save('valid_four_person.json', valid4)

valid5 = state([
 assignment('P1',['RESEARCH_OWNER']),
 assignment('P2',['MODERATOR','NOTE_TAKER'], {'evidence_separation_documented': True}),
 assignment('P3',['DATA_CUSTODIAN']),
 assignment('P4',['ANALYST']),
 assignment('P5',['CONTINUE_STOP_OWNER'])], 'FIVE_PERSON')
save('valid_five_person.json', valid5)

valid6 = state([
 assignment('P1',['RESEARCH_OWNER']), assignment('P2',['MODERATOR']),
 assignment('P3',['NOTE_TAKER']), assignment('P4',['DATA_CUSTODIAN']),
 assignment('P5',['ANALYST']), assignment('P6',['CONTINUE_STOP_OWNER'])], 'SIX_PERSON')
save('valid_six_person.json', valid6)

# invalid three-person: hard Moderator+Analyst
inv3 = state([
 assignment('P1',['RESEARCH_OWNER','CONTINUE_STOP_OWNER'], {'explicit_additional_appointment': True}),
 assignment('P2',['MODERATOR','ANALYST']),
 assignment('P3',['NOTE_TAKER','DATA_CUSTODIAN'])], 'OTHER')
save('invalid_three_person.json', inv3)

hard_ma = state([
 assignment('P1',['RESEARCH_OWNER']), assignment('P2',['MODERATOR','ANALYST']),
 assignment('P3',['NOTE_TAKER']), assignment('P4',['DATA_CUSTODIAN']),
 assignment('P5',['CONTINUE_STOP_OWNER'])], 'FIVE_PERSON')
save('hard_moderator_analyst.json', hard_ma)

hard_mc = state([
 assignment('P1',['RESEARCH_OWNER']), assignment('P2',['MODERATOR','DATA_CUSTODIAN']),
 assignment('P3',['NOTE_TAKER']), assignment('P4',['ANALYST']),
 assignment('P5',['CONTINUE_STOP_OWNER'])], 'FIVE_PERSON')
save('hard_moderator_custodian.json', hard_mc)

disc_ro_m = state([
 assignment('P1',['RESEARCH_OWNER','MODERATOR']),
 assignment('P2',['NOTE_TAKER']), assignment('P3',['DATA_CUSTODIAN']),
 assignment('P4',['ANALYST']), assignment('P5',['CONTINUE_STOP_OWNER'])], 'FIVE_PERSON')
save('discouraged_ro_moderator.json', disc_ro_m)

disc_dc_a = state([
 assignment('P1',['RESEARCH_OWNER']),
 assignment('P2',['MODERATOR','NOTE_TAKER'], {'evidence_separation_documented': True}),
 assignment('P3',['DATA_CUSTODIAN','ANALYST']),
 assignment('P4',['CONTINUE_STOP_OWNER'])], 'FOUR_PERSON')
save('discouraged_custodian_analyst.json', disc_dc_a)

miss_ev = copy.deepcopy(valid4)
miss_ev['assignments'][1]['conditional_evidence'] = {'evidence_separation_documented': False}
save('missing_evidence_separation.json', miss_ev)

miss_cs = copy.deepcopy(valid4)
miss_cs['assignments'][0]['conditional_evidence'] = {'explicit_additional_appointment': False}
save('missing_explicit_cs.json', miss_cs)

miss_acc = copy.deepcopy(valid4)
miss_acc['roles']['RESEARCH_OWNER']['acceptance']['candidate_accepted'] = False
save('missing_candidate_acceptance.json', miss_acc)

miss_po = copy.deepcopy(valid4)
miss_po['roles']['RESEARCH_OWNER']['approval']['product_owner_approved'] = False
save('missing_po_approval.json', miss_po)

miss_onb = copy.deepcopy(valid4)
miss_onb['roles']['DATA_CUSTODIAN']['onboarding']['completed'] = False
save('missing_onboarding.json', miss_onb)

current = json.load(open(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE\state\current_assignment_state.json',encoding='utf-8'))
save('ro_accepted_others_unassigned.json', current)
save('deterministic_state.json', current)

print('fixtures', len([f for f in os.listdir(D) if f.endswith('.json')]))
