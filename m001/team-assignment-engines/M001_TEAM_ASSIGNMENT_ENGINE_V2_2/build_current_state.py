# -*- coding: utf-8 -*-
"""Build V2 current assignment state from established evidence only."""
import json, os
D = r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_2'
ROLES = ['RESEARCH_OWNER','MODERATOR','NOTE_TAKER','DATA_CUSTODIAN','ANALYST','CONTINUE_STOP_OWNER']

def blank(state='UNASSIGNED', recognition=None):
    return {
        'state': state,
        'candidate_ref': None,
        'recognition': recognition or {'status': None, 'decision_date': None, 'formal': False, 'evidence_text': None},
        'acceptance': {'candidate_accepted': False, 'evidence_id': None, 'candidate_accepted_at': None},
        'approval': {'product_owner_approved': False, 'formal': False, 'evidence_id': None, 'basis': None, 'product_owner_approved_at': None},
        'formal': {'formally_appointed': False, 'evidence_id': None, 'formal_appointed_at': None},
        'availability': {'confirmed': False},
        'conflict_disclosure': {'provided': False},
        'confidentiality': {'acknowledged': False},
        'onboarding': {'completed': False, 'evidence_id': None},
        'escalation': {'contact': None}
    }

ro = blank('ACCEPTED_IN_CONVERSATION', {
    'status': 'ACCEPTED_IN_CONVERSATION',
    'decision_date': '2026-11-26',
    'formal': False,
    'evidence_text': 'Explicit written confirmation by Product Owner in conversation; formal signature NOT PROVIDED; official register update NOT AUTHORIZED'
})
state = {
    'schema_version': '2.0',
    'governance': {'m001_status':'OPEN','m002_status':'UNAUTHORIZED','recruitment':'UNAUTHORIZED','field_validation':'NOT_STARTED'},
    'topology': {'status':'PROPOSED','model':'FOUR_PERSON'},
    'candidates': {},
    'evidence': {},
    'roles': {r: (ro if r=='RESEARCH_OWNER' else blank()) for r in ROLES},
    'appointments': [],
    'combination_approvals': []
}
json.dump(state, open(os.path.join(D,'state','current_assignment_state.json'),'w',encoding='utf-8'), indent=2)
print('current state written')
