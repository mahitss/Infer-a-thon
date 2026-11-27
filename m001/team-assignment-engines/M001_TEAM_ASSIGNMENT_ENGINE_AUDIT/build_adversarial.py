# -*- coding: utf-8 -*-
"""Generate independent adversarial fixtures; original implementation untouched."""
import copy, json, os
A = r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_AUDIT'
O = r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE'
F = os.path.join(A, 'adversarial_fixtures')
os.makedirs(F, exist_ok=True)
valid = json.load(open(os.path.join(O, 'fixtures', 'valid_four_person.json'), encoding='utf-8'))

def save(n, obj):
    json.dump(obj, open(os.path.join(F, n), 'w', encoding='utf-8'), indent=2)

# hard incompatibilities
x = copy.deepcopy(valid); x['assignments'][1]['roles'] = ['MODERATOR','ANALYST']; x['assignments'][3]['roles'] = ['NOTE_TAKER']; save('hard_moderator_analyst.json', x)
x = copy.deepcopy(valid); x['assignments'][1]['roles'] = ['MODERATOR','DATA_CUSTODIAN']; x['assignments'][2]['roles'] = ['NOTE_TAKER']; save('hard_moderator_custodian.json', x)

# discouraged combinations
x = copy.deepcopy(valid); x['assignments'][0]['roles'] = ['RESEARCH_OWNER','MODERATOR']; x['assignments'][1]['roles']=['NOTE_TAKER']; x['assignments'].append({'person_id':'P5','roles':['CONTINUE_STOP_OWNER']}); save('discouraged_ro_moderator.json', x)
x = copy.deepcopy(valid); x['assignments'][2]['roles'] = ['DATA_CUSTODIAN','ANALYST']; x['assignments'][3]['roles']=[]; save('discouraged_custodian_analyst.json', x)

# conditional with boolean true but no evidence content
x = copy.deepcopy(valid); x['assignments'][1]['conditional_evidence'] = {'evidence_separation_documented': True}; save('false_evidence_moderator_notetaker.json', x)
x = copy.deepcopy(valid); x['assignments'][0]['conditional_evidence'] = {'explicit_additional_appointment': True}; save('false_evidence_continue_stop.json', x)

# compatible combined role without explicit combination approval
x = copy.deepcopy(valid)
x['assignments'] = [
 {'person_id':'P1','roles':['RESEARCH_OWNER']},
 {'person_id':'P2','roles':['NOTE_TAKER','DATA_CUSTODIAN']},
 {'person_id':'P3','roles':['MODERATOR']},
 {'person_id':'P4','roles':['ANALYST','CONTINUE_STOP_OWNER']}]
save('compatible_combination_no_approval.json', x)

# duplicate candidate identifiers across roles/persons
x = copy.deepcopy(valid); x['roles']['MODERATOR']['candidate_id']='P-DUP'; x['roles']['ANALYST']['candidate_id']='P-DUP'; save('duplicate_candidate_identifier.json', x)

# PROPOSED treated as appointed
x = copy.deepcopy(valid); x['roles']['MODERATOR']['state']='PROPOSED'; x['roles']['MODERATOR']['candidate_id']='P2'; save('proposed_treated_as_appointed.json', x)

# formal state with formal approval false
x = copy.deepcopy(valid); x['roles']['RESEARCH_OWNER']['approval']['formal']=False; save('formal_state_formal_approval_false.json', x)

# rejected/deferred still assigned
x = copy.deepcopy(valid); x['roles']['ANALYST']['state']='REJECTED'; save('rejected_still_assigned.json', x)
x = copy.deepcopy(valid); x['roles']['ANALYST']['state']='DEFERRED'; save('deferred_still_assigned.json', x)

# unknown human reference
x = copy.deepcopy(valid); x['roles']['MODERATOR']['candidate_id']='UNKNOWN-HUMAN'; save('unknown_human_reference.json', x)

# weak decision evidence
x = copy.deepcopy(valid); x['roles']['RESEARCH_OWNER']['approval']['basis']=''; save('weak_decision_evidence.json', x)

# topology proposed with all roles formal
x = copy.deepcopy(valid); x['topology']['status']='PROPOSED'; save('topology_proposed_all_formal.json', x)

# raw robustness fixtures
open(os.path.join(F,'malformed.json'),'w',encoding='utf-8').write('{ "schema_version": "1.0", ')
open(os.path.join(F,'invalid_utf8.bin'),'wb').write(b'{"schema_version":"1.0",\xff}')
raw = json.dumps(valid)[:-1] + ', "schema_version": "9.9"}'
open(os.path.join(F,'duplicate_json_key.json'),'w',encoding='utf-8').write(raw)
open(os.path.join(F,'large_input.json'),'w',encoding='utf-8').write(json.dumps(valid) + '\n' * 200000)

print('adversarial fixtures', len([f for f in os.listdir(F)]))
