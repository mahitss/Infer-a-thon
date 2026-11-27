#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Independent governance-state and authority-boundary verification."""
import hashlib, importlib.util, json, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
V22 = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_2')


def load(name):
    spec = importlib.util.spec_from_file_location(name, V22 / 'engine' / 'validator.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


V = load('audit_v22')
P, S = V.load_policy(), V.load_schema()
path = V22 / 'state' / 'current_assignment_state.json'
before = hashlib.sha256(path.read_bytes()).hexdigest().upper()
st = V.load_json_strict(path)
r = V.validate_state(st, P, S)
checks = []
def chk(n, ok, d=''):
    checks.append({'check': n, 'pass': bool(ok), 'detail': str(d)})

expected = {'RESEARCH_OWNER':'ACCEPTED_IN_CONVERSATION','MODERATOR':'UNASSIGNED',
            'NOTE_TAKER':'UNASSIGNED','DATA_CUSTODIAN':'UNASSIGNED','ANALYST':'UNASSIGNED',
            'CONTINUE_STOP_OWNER':'UNASSIGNED'}
for role, exp in expected.items():
    chk('role_'+role, st['roles'][role]['state']==exp, st['roles'][role]['state'])
chk('ro_not_formal', st['roles']['RESEARCH_OWNER']['state']!='FORMALLY_APPOINTED')
chk('ro_formal_false', st['roles']['RESEARCH_OWNER']['formal']['formally_appointed'] is False)
chk('ro_no_candidate', st['roles']['RESEARCH_OWNER']['candidate_ref'] is None)
chk('no_cs_inference', st['roles']['CONTINUE_STOP_OWNER']['state']=='UNASSIGNED')
chk('empty_registries', all(not st[k] for k in ('candidates','evidence','appointments','combination_approvals')))
chk('topology_proposed', st['topology']=={'status':'PROPOSED','model':'FOUR_PERSON'}, st['topology'])
chk('m001_open', st['governance']['m001_status']=='OPEN')
chk('m002_unauthorized', st['governance']['m002_status']=='UNAUTHORIZED')
chk('recruitment_unauthorized', st['governance']['recruitment']=='UNAUTHORIZED')
chk('field_validation_not_started', st['governance']['field_validation']=='NOT_STARTED')
chk('stage_b_not_ready', r.stage_b_role_ready is False)
chk('recruitment_no', r.recruitment_authorized is False)
chk('field_validation_no', r.field_validation_authorized is False)
chk('six_missing', len([i for i in r.errors if i.code=='E-APPOINTMENT-MISSING'])==6)
chk('topology_error', 'E-TOPOLOGY-UNAPPROVED' in [i.code for i in r.errors])

valid = V.load_json_strict(V22/'tests'/'fixtures'/'valid_four_person.json')
rv = V.validate_state(valid, P, S)
chk('passing_staffing_no_recruitment', rv.stage_b_role_ready and not rv.recruitment_authorized)
chk('passing_staffing_no_field_validation', not rv.field_validation_authorized)
chk('eight_dimensions', len(rv.dimensions)==8, sorted(rv.dimensions))
chk('no_storage_or_consent_dimension', not any(k in ('storage','consent') for k in rv.dimensions))
src = (V22/'engine'/'validator.py').read_text(encoding='utf-8')+(V22/'cli'/'validate.py').read_text(encoding='utf-8')
code='\n'.join(l.split('#')[0] for l in src.splitlines() if not l.strip().startswith(('"""','*','#')))
chk('no_positive_grant', not re.search(r'recruitment_authorized\s*=\s*True|field_validation_authorized\s*=\s*True',code))
chk('no_state_write', not re.search(r'\bopen\s*\([^)]*[\'\"]w|write_text\s*\([^)]*state',code))
cp=subprocess.run([sys.executable,str(V22/'cli'/'validate.py'),'--state',str(path)],cwd=str(V22),capture_output=True,text=True)
chk('cli_exit_1',cp.returncode==1)
chk('cli_no_traceback',cp.stderr=='' and 'Traceback' not in cp.stdout)
chk('state_immutable',before==hashlib.sha256(path.read_bytes()).hexdigest().upper())
out={'checks':checks,'pass':sum(1 for c in checks if c['pass']),'fail':sum(1 for c in checks if not c['pass']),
     'cli_stdout':cp.stdout,'cli_stderr':cp.stderr}
(HERE/'tests'/'results'/'governance_state.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print('GOVERNANCE',out['pass'],'PASS /',out['fail'],'FAIL')
for c in checks:
    if not c['pass']: print('FAIL',c['check'],c['detail'])
