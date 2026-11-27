#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Independent verification of real current state and authorization boundary."""
import json, subprocess, sys
from pathlib import Path
V2 = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2')
REAUDIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V2))
from engine.validator import load_json_strict, load_policy, load_schema, validate_state  # noqa: E402

st = load_json_strict(V2 / 'state' / 'current_assignment_state.json')
P, S = load_policy(), load_schema()
r = validate_state(st, P, S)

EXPECTED = {
    'RESEARCH_OWNER': 'ACCEPTED_IN_CONVERSATION',
    'MODERATOR': 'UNASSIGNED',
    'NOTE_TAKER': 'UNASSIGNED',
    'DATA_CUSTODIAN': 'UNASSIGNED',
    'ANALYST': 'UNASSIGNED',
    'CONTINUE_STOP_OWNER': 'UNASSIGNED',
}
checks = []
def chk(name, ok, detail=''):
    checks.append({'check': name, 'pass': bool(ok), 'detail': str(detail)})

for role, expect in EXPECTED.items():
    actual = st['roles'][role]['state']
    chk('role_state_%s' % role, actual == expect, '%s (expected %s)' % (actual, expect))
chk('research_owner_not_formal', st['roles']['RESEARCH_OWNER']['state'] != 'FORMALLY_APPOINTED')
chk('research_owner_formal_flag_false', st['roles']['RESEARCH_OWNER']['formal']['formally_appointed'] is False)
chk('research_owner_no_candidate_ref', st['roles']['RESEARCH_OWNER']['candidate_ref'] is None)
chk('no_continue_stop_inference', st['roles']['CONTINUE_STOP_OWNER']['state'] == 'UNASSIGNED')
chk('no_synthetic_candidates', st['candidates'] == {}, list(st['candidates']))
chk('no_fabricated_evidence', st['evidence'] == {}, list(st['evidence']))
chk('no_appointments', st['appointments'] == [])
chk('no_combination_approvals', st['combination_approvals'] == [])
chk('topology_proposed', st['topology']['status'] == 'PROPOSED', st['topology'])
chk('m001_open', st['governance']['m001_status'] == 'OPEN')
chk('m002_unauthorized', st['governance']['m002_status'] == 'UNAUTHORIZED')
chk('recruitment_unauthorized', st['governance']['recruitment'] == 'UNAUTHORIZED')
chk('field_validation_not_started', st['governance']['field_validation'] == 'NOT_STARTED')
chk('stage_b_not_ready', r.stage_b_role_ready is False)
chk('recruitment_not_authorized', r.recruitment_authorized is False)
chk('field_validation_not_authorized', r.field_validation_authorized is False)
chk('six_missing_appointment_errors', len([i for i in r.errors if i.code == 'E-APPOINTMENT-MISSING']) == 6,
    len([i for i in r.errors if i.code == 'E-APPOINTMENT-MISSING']))
chk('topology_block_error', 'E-TOPOLOGY-UNAPPROVED' in [i.code for i in r.errors])

# Authorization boundary: which dimensions does the engine actually emit?
emitted = set(P['stage_b_dimensions']) | {'structural_topology_validity'}
chk('eight_dimensions_emitted', emitted == set(r.dimensions), sorted(r.dimensions))
chk('no_storage_safeguard_dimension', not any('storage' in k.lower() for k in r.dimensions))
chk('no_consent_safeguard_dimension', not any('consent' in k.lower() for k in r.dimensions))
chk('no_recruitment_positive_grant', not any(i.code.startswith('I-RECRUIT') for i in r.issues))

# CLI evidence for current state
cp = subprocess.run([sys.executable, str(V2 / 'cli' / 'validate.py'), '--state',
                     str(V2 / 'state' / 'current_assignment_state.json')],
                    cwd=str(V2), capture_output=True, text=True)
chk('cli_exit_1', cp.returncode == 1, cp.returncode)
chk('cli_stage_b_no', 'Stage B role readiness: NO' in cp.stdout)
chk('cli_recruitment_no', 'Recruitment authorized: NO' in cp.stdout)
chk('cli_field_validation_no', 'Field validation authorized: NO' in cp.stdout)
chk('cli_no_traceback', 'Traceback' not in cp.stderr)

# Source-level check: no operational authorization path exists in engine/CLI.
import re
source = (V2 / 'engine' / 'validator.py').read_text(encoding='utf-8') + (V2 / 'cli' / 'validate.py').read_text(encoding='utf-8')
code_only = '\n'.join(line.split('#')[0] for line in source.splitlines() if not line.strip().startswith(('"""', '*', '#')))
chk('no_storage_or_acl_authorization_code',
    not re.search(r'storage_authorized\s*=|consent_authorized\s*=|acl[_ ]?grant|encrypt\s*\(|withdraw\s*\(', code_only, re.I))
chk('authorizations_hardcoded_false', 'recruitment_authorized: bool = False' in source and 'field_validation_authorized: bool = False' in source)
chk('result_hardcodes_false', 'return ValidationResult(dims, issues, stage_b, False, False)' in source)

out = {
    'checks': checks,
    'pass_count': sum(1 for c in checks if c['pass']),
    'fail_count': sum(1 for c in checks if not c['pass']),
    'dimensions_emitted': sorted(r.dimensions),
    'cli_stdout': cp.stdout,
    'cli_stderr': cp.stderr,
    'cli_exit': cp.returncode,
    'result_json': r.to_dict(),
}
path = REAUDIT / 'tests' / 'results' / 'current_state_boundary_results.json'
path.write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
print('CHECKS', out['pass_count'], 'PASS /', out['fail_count'], 'FAIL')
for c in checks:
    if not c['pass']:
        print('FAIL', c['check'], c['detail'])
print('wrote', path)
