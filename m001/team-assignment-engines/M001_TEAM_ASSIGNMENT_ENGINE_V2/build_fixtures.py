# -*- coding: utf-8 -*-
"""Build synthetic V2 fixtures. All candidate data is explicitly labelled."""
import copy, hashlib, json, os
D = r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2\tests\fixtures'
os.makedirs(D, exist_ok=True)
ROLES = ['RESEARCH_OWNER','MODERATOR','NOTE_TAKER','DATA_CUSTODIAN','ANALYST','CONTINUE_STOP_OWNER']
TS = ['2026-11-27T00:00:00+00:00','2026-11-27T01:00:00+00:00','2026-11-27T02:00:00+00:00','2026-11-27T03:00:00+00:00']

def evid(eid, etype, subject):
    return {'evidence_id':eid,'evidence_type':etype,'source_ref':'synthetic://%s' % eid,
            'content_hash':hashlib.sha256(eid.encode()).hexdigest(),
            'recording_authority':'SYNTHETIC_TEST_DATA','timestamp':TS[0],
            'verification_status':'VERIFIED','subject':subject}

def state(assign_map, topology='APPROVED'):
    st = {
      'schema_version':'2.0',
      'governance':{'m001_status':'OPEN','m002_status':'UNAUTHORIZED','recruitment':'UNAUTHORIZED','field_validation':'NOT_STARTED'},
      'topology':{'status':topology,'model':'FOUR_PERSON'},
      'candidates':{},'evidence':{},'roles':{},'appointments':[],'combination_approvals':[]}
    for cand, roles in assign_map:
        st['candidates'][cand] = {'candidate_ref':cand,'active':True,'fixture_marker':'SYNTHETIC_TEST_DATA'}
        for role in roles:
            acc='e-acc-'+cand; apo='e-po-'+cand; f='e-form-'+cand; onb='e-onb-'+cand
            st['evidence'][acc]=evid(acc,'CANDIDATE_ACCEPTANCE',cand)
            st['evidence'][apo]=evid(apo,'PRODUCT_OWNER_APPROVAL',cand)
            st['evidence'][f]=evid(f,'FORMAL_APPOINTMENT',cand)
            st['evidence'][onb]=evid(onb,'ONBOARDING',cand)
            st['roles'][role]={
              'state':'FORMALLY_APPOINTED','candidate_ref':cand,
              'recognition':{'status':None,'decision_date':None,'formal':False,'evidence_text':None},
              'acceptance':{'candidate_accepted':True,'evidence_id':acc,'candidate_accepted_at':TS[0]},
              'approval':{'product_owner_approved':True,'formal':True,'evidence_id':apo,
                          'basis':'synthetic PO decision for '+role,'product_owner_approved_at':TS[1]},
              'formal':{'formally_appointed':True,'evidence_id':f,'formal_appointed_at':TS[2]},
              'availability':{'confirmed':True},'conflict_disclosure':{'provided':True},
              'confidentiality':{'acknowledged':True},
              'onboarding':{'completed':True,'evidence_id':onb},
              'escalation':{'contact':'synthetic-escalation-'+cand}}
            st['appointments'].append({'candidate_ref':cand,'role':role,'state':'FORMALLY_APPOINTED'})
        if len(roles)>1:
            key='+'.join(sorted(roles)); ce='e-combo-'+cand+'-'+key
            st['evidence'][ce]=evid(ce,'COMBINATION_REVIEW',cand+':'+key)
            if set(roles)=={'MODERATOR','NOTE_TAKER'}:
                se='e-sep-'+cand; st['evidence'][se]=evid(se,'EVIDENCE_SEPARATION',cand+':'+key)
            st['combination_approvals'].append({
              'candidate_ref':cand,'roles':sorted(roles),'outcome':'APPROVED',
              'rationale':'SYNTHETIC_TEST_DATA explicit PO approval for exact combination',
              'evidence_id':ce,'product_owner_approved':True,'decision_timestamp':TS[1]})
    # add evidence separation for M+N if not already
    return st

def save(n,obj): json.dump(obj,open(os.path.join(D,n),'w',encoding='utf-8'),indent=2)

four=state([('C-P1',['RESEARCH_OWNER','CONTINUE_STOP_OWNER']),
            ('C-P2',['MODERATOR','NOTE_TAKER']),('C-P3',['DATA_CUSTODIAN']),('C-P4',['ANALYST'])])
save('valid_four_person.json',four)
five=state([('C-P1',['RESEARCH_OWNER']),('C-P2',['MODERATOR','NOTE_TAKER']),
            ('C-P3',['DATA_CUSTODIAN']),('C-P4',['ANALYST']),('C-P5',['CONTINUE_STOP_OWNER'])])
five['topology']['model']='FIVE_PERSON'; save('valid_five_person.json',five)
six=state([('C-P%d'%i,[r]) for i,r in enumerate(ROLES,1)])
six['topology']['model']='SIX_PERSON'; save('valid_six_person.json',six)

# 20 explicit adversarial cases
x=copy.deepcopy(four); x['combination_approvals']=[]; save('multi_role_no_approval.json',x)
x=copy.deepcopy(four); x['combination_approvals'][0]['roles']=['RESEARCH_OWNER','MODERATOR']; save('approval_different_combination.json',x)
x=copy.deepcopy(four); x['roles']['MODERATOR']['state']='PROPOSED'; save('proposed_treated_as_appointed.json',x)
x=copy.deepcopy(four); x['roles']['MODERATOR']['state']='ACCEPTED_IN_CONVERSATION'; save('accepted_conversation_formal.json',x)
x=copy.deepcopy(four); x['roles']['MODERATOR']['acceptance']['evidence_id']=None; save('boolean_evidence_without_ref.json',x)
x=copy.deepcopy(four); x['roles']['MODERATOR']['acceptance']['evidence_id']='e-FORGED'; save('forged_evidence_id.json',x)
x=copy.deepcopy(four); x['candidates']['C-P2']['candidate_ref']='C-P1'; save('duplicate_candidate_identity.json',x)
x=copy.deepcopy(four); x['roles']['MODERATOR']['candidate_ref']='C-UNKNOWN'; save('unknown_candidate_identity.json',x)
x=copy.deepcopy(four); x['roles']['MODERATOR']['approval']['formal']=False; save('formal_missing_formal_approval.json',x)
x=copy.deepcopy(four); x['roles']['MODERATOR']['approval']['basis']=''; save('empty_approval_basis.json',x)
# discouraged without review: RO + MODERATOR, approvals removed
x=state([('C-P1',['RESEARCH_OWNER','MODERATOR']),('C-P2',['NOTE_TAKER']),('C-P3',['DATA_CUSTODIAN']),('C-P4',['ANALYST']),('C-P5',['CONTINUE_STOP_OWNER'])])
x['combination_approvals']=[]; save('discouraged_no_review.json',x)
x=copy.deepcopy(four); x['roles']['MODERATOR']['formal']['formal_appointed_at']=None; save('missing_timestamps.json',x)
x=copy.deepcopy(four); x['topology']['status']='PROPOSED'; save('topology_unapproved_stage_b.json',x)
x=copy.deepcopy(four); x['roles']['ANALYST']['state']='REJECTED'; save('rejected_active_appointment.json',x)
x=copy.deepcopy(four); x['roles']['ANALYST']['onboarding']['completed']=False; save('missing_onboarding.json',x)
x=copy.deepcopy(four); x['governance']['recruitment']='AUTHORIZED'; save('recruitment_inferred.json',x)
# hard incompatibility even if approved
x=state([('C-P1',['MODERATOR','ANALYST']),('C-P2',['RESEARCH_OWNER']),('C-P3',['NOTE_TAKER']),('C-P4',['DATA_CUSTODIAN']),('C-P5',['CONTINUE_STOP_OWNER'])])
save('hard_incompatibility_approved.json',x)
# current state copy from real state
current=json.load(open(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2\state\current_assignment_state.json',encoding='utf-8'))
save('current_assignment_state.json',current)
open(os.path.join(D,'malformed.json'),'w',encoding='utf-8').write('{ bad json')
open(os.path.join(D,'invalid_utf8.bin'),'wb').write(b'{"schema_version":"2.0",\xff}')
raw=json.dumps(four)[:-1]+', "schema_version":"2.0"}'
open(os.path.join(D,'duplicate_json_key.json'),'w',encoding='utf-8').write(raw)
print('fixtures',len([f for f in os.listdir(D)]))
