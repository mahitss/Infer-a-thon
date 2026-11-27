#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Independently verify real state and authorization boundaries in V2.1."""
import hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
V21 = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1')


def load(name, root):
    spec = importlib.util.spec_from_file_location(name, root / 'engine' / 'validator.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


V = load('auditor_state', V21)
P, S = V.load_policy(), V.load_schema()
state_path = V21 / 'state' / 'current_assignment_state.json'
before = hashlib.sha256(state_path.read_bytes()).hexdigest().upper()
st = V.load_json_strict(state_path)
r = V.validate_state(st, P, S)
checks = []


def chk(name, ok, detail=''):
    checks.append({'check': name, 'pass': bool(ok), 'detail': str(detail)})


EXPECTED = {'RESEARCH_OWNER': 'ACCEPTED_IN_CONVERSATION', 'MODERATOR': 'UNASSIGNED',
            'NOTE_TAKER': 'UNASSIGNED', 'DATA_CUSTODIAN': 'UNASSIGNED',
            'ANALYST': 'UNASSIGNED', 'CONTINUE_STOP_OWNER': 'UNASSIGNED'}
for role, expect in EXPECTED.items():
    chk('state_' + role, st['roles'][role]['state'] == expect, st['roles'][role]['state'])
chk('research_owner_not_formal', st['roles']['RESEARCH_OWNER']['state'] != 'FORMALLY_APPOINTED')
chk('research_owner_formal_false', st['roles']['RESEARCH_OWNER']['formal']['formally_appointed'] is False)
chk('research_owner_no_candidate', st['roles']['RESEARCH_OWNER']['candidate_ref'] is None)
chk('no_continue_stop_inference', st['roles']['CONTINUE_STOP_OWNER']['state'] == 'UNASSIGNED')
chk('no_synthetic_candidates', st['candidates'] == {})
chk('no_fabricated_evidence', st['evidence'] == {})
chk('no_appointments', st['appointments'] == [])
chk('no_combination_approvals', st['combination_approvals'] == [])
chk('topology_proposed_four_person', st['topology'] == {'status': 'PROPOSED', 'model': 'FOUR_PERSON'})
chk('m001_open', st['governance']['m001_status'] == 'OPEN')
chk('m002_unauthorized', st['governance']['m002_status'] == 'UNAUTHORIZED')
chk('recruitment_unauthorized', st['governance']['recruitment'] == 'UNAUTHORIZED')
chk('field_validation_not_started', st['governance']['field_validation'] == 'NOT_STARTED')
chk('stage_b_not_ready', r.stage_b_role_ready is False)
chk('recruitment_flag_false', r.recruitment_authorized is False)
chk('field_validation_flag_false', r.field_validation_authorized is False)
chk('six_missing_appointments', len([i for i in r.errors if i.code == 'E-APPOINTMENT-MISSING']) == 6)
chk('topology_block_error', 'E-TOPOLOGY-UNAPPROVED' in [i.code for i in r.errors])

# Authorization boundary on a passing synthetic state.
valid = V.load_json_strict(V21 / 'tests' / 'fixtures' / 'valid_four_person.json')
rv = V.validate_state(valid, P, S)
chk('passing_staffing_still_stage_b', rv.stage_b_role_ready)
chk('passing_staffing_no_recruitment', rv.recruitment_authorized is False)
chk('passing_staffing_no_field_validation', rv.field_validation_authorized is False)
chk('eight_dimensions_present', len(rv.dimensions) == 8, sorted(rv.dimensions))
chk('no_storage_dimension', not any('storage' in k.lower() for k in rv.dimensions))
chk('no_consent_dimension', not any('consent' in k.lower() for k in rv.dimensions))

# Engine cannot modify governance decisions: no positive grant code path.
src = (V21 / 'engine' / 'validator.py').read_text(encoding='utf-8') + (V21 / 'cli' / 'validate.py').read_text(encoding='utf-8')
chk('authorizations_hardcoded_false', 'recruitment_authorized: bool = False' in src and 'field_validation_authorized: bool = False' in src)
chk('result_hardcodes_false', 'return ValidationResult(dims, issues, stage_b, False, False)' in src)
code = '\n'.join(l.split('#')[0] for l in src.splitlines() if not l.strip().startswith(('"""', '*', '#')))
import re
chk('no_positive_grant_or_state_write',
    not re.search(r'recruitment_authorized\s*=\s*True|field_validation_authorized\s*=\s*True'
                  r'|\bopen\s*\([^)]*[\'\"]w|write_text\s*\([^)]*state', code))

cp = subprocess.run([sys.executable, str(V21 / 'cli' / 'validate.py'), '--state', str(state_path)],
                    cwd=str(V21), capture_output=True, text=True)
chk('cli_exit_1', cp.returncode == 1)
chk('cli_stage_b_no', 'Stage B role readiness: NO' in cp.stdout)
chk('cli_both_authorizations_no', 'Recruitment authorized: NO' in cp.stdout and 'Field validation authorized: NO' in cp.stdout)
chk('cli_empty_stderr', cp.stderr == '')
after = hashlib.sha256(state_path.read_bytes()).hexdigest().upper()
chk('state_unchanged_after_validation', before == after)

out = {'checks': checks, 'pass': sum(1 for c in checks if c['pass']),
       'fail': sum(1 for c in checks if not c['pass']),
       'cli_stdout': cp.stdout, 'cli_stderr': cp.stderr, 'cli_exit': cp.returncode}
(HERE / 'tests' / 'results' / 'state_boundary_results.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
print('STATE/BOUNDARY', out['pass'], 'PASS /', out['fail'], 'FAIL')
for c in checks:
    if not c['pass']:
        print('FAIL', c['check'], c['detail'])
