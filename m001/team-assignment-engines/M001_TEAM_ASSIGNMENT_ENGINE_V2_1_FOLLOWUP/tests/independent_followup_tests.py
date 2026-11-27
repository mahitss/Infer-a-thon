#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Auditor-authored verification of the four HIGH remediations in V2.1."""
import copy, importlib.util, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
V21 = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1')
OUT = HERE / 'tests' / 'results' / 'independent_followup_results.json'


def load(name, root):
    spec = importlib.util.spec_from_file_location(name, root / 'engine' / 'validator.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V = load('auditor_v21', V21)
P, S = V.load_policy(), V.load_schema()
BASE = V.load_json_strict(V21 / 'tests' / 'fixtures' / 'valid_four_person.json')
F = V21 / 'tests' / 'fixtures'


def base():
    return copy.deepcopy(BASE)


def codes(r):
    return sorted(set(i.code for i in r.issues))


def result(r):
    return {'ready': r.stage_b_role_ready, 'codes': codes(r),
            'dimensions': dict(sorted(r.dimensions.items())),
            'errors': len(r.errors)}


CASES = []


def case(cid, area, mutation, expectation, expected=()):
    CASES.append((cid, area, mutation, expectation, list(expected)))


# N-01
case('AU-01', 'N-01', lambda s: s['roles']['RESEARCH_OWNER']['approval'].__setitem__('basis', ''),
     'BLOCK', ['E-DECISION-EVIDENCE-EMPTY'])
case('AU-02', 'N-01', lambda s: s['roles']['RESEARCH_OWNER']['approval'].__setitem__('basis', ' \t\n '),
     'BLOCK', ['E-DECISION-EVIDENCE-EMPTY'])
case('AU-03', 'N-01', lambda s: s['roles']['RESEARCH_OWNER']['approval'].__setitem__('basis', '\u00a0\u2003\u3000'),
     'BLOCK', ['E-DECISION-EVIDENCE-EMPTY'])
case('AU-04', 'N-01', lambda s: s['roles']['RESEARCH_OWNER']['approval'].__setitem__('basis', None),
     'BLOCK', ['E-DECISION-EVIDENCE-EMPTY'])
case('AU-05', 'N-01', lambda s: s['roles']['RESEARCH_OWNER']['approval'].__setitem__('basis', 12345),
     'BLOCK', ['E-SCHEMA', 'E-DECISION-EVIDENCE-EMPTY'])
case('AU-06', 'N-01', lambda s: None, 'PASS', [])
case('AU-07', 'N-01', lambda s: s['roles']['RESEARCH_OWNER']['approval'].__setitem__('basis', 'Dokumentierte PO-Entscheidung 日本  ✓'),
     'PASS', [])

# N-02
case('AU-08', 'N-02', lambda s: s['combination_approvals'][0].__setitem__('rationale', ''),
     'BLOCK', ['E-COMBINATION-RATIONALE'])
case('AU-09', 'N-02', lambda s: s['combination_approvals'][0].__setitem__('rationale', '  \t\n '),
     'BLOCK', ['E-COMBINATION-RATIONALE'])
case('AU-10', 'N-02', lambda s: s['combination_approvals'][0].__setitem__('rationale', '\u00a0\u2003\u3000'),
     'BLOCK', ['E-COMBINATION-RATIONALE'])
case('AU-11', 'N-02', lambda s: s['combination_approvals'][0].__setitem__('rationale', None),
     'BLOCK', ['E-COMBINATION-RATIONALE', 'E-SCHEMA'])
case('AU-12', 'N-02', lambda s: s['combination_approvals'][0].__setitem__('rationale', ['approved']),
     'BLOCK', ['E-SCHEMA'])
case('AU-13', 'N-02', lambda s: s['combination_approvals'][0].__setitem__('roles', ['RESEARCH_OWNER', 'MODERATOR']),
     'BLOCK', ['E-COMBINATION-APPROVAL-MISSING'])
case('AU-14', 'N-02', lambda s: _reuse_rationale(s),
     'BLOCK', ['E-COMBINATION-RATIONALE-REUSED'])

# N-03
case('AU-15', 'N-03', lambda s: _point_acc(s, 'CONTINUE_STOP_OWNER', 'e-acc-C-P1-RESEARCH_OWNER'),
     'BLOCK', ['E-ACCEPTANCE-ROLE', 'E-EVIDENCE-SUBJECT'])
case('AU-16', 'N-03', lambda s: _point_acc(s, 'CONTINUE_STOP_OWNER', 'e-acc-C-P4-ANALYST'),
     'BLOCK', ['E-ACCEPTANCE-ROLE', 'E-EVIDENCE-SUBJECT'])
case('AU-17', 'N-03', lambda s: s['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER'].__setitem__('appointment_ref', 'C-P1:RESEARCH_OWNER'),
     'BLOCK', ['E-ACCEPTANCE-APPOINTMENT'])
case('AU-18', 'N-03', lambda s: s['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER'].__setitem__('decision_ref', 'acc-decision-C-P1-RESEARCH_OWNER'),
     'BLOCK', ['E-ACCEPTANCE-DECISION-REUSED'])
case('AU-19', 'N-03', lambda s: s['roles']['CONTINUE_STOP_OWNER']['acceptance'].__setitem__('evidence_id', None),
     'BLOCK', ['E-EVIDENCE-MISSING'])
case('AU-20', 'N-03', lambda s: s['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER'].__setitem__('verification_status', 'PENDING'),
     'BLOCK', ['E-EVIDENCE-UNVERIFIED'])
case('AU-21', 'N-03', lambda s: s['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER'].__setitem__('revoked', True),
     'BLOCK', ['E-EVIDENCE-REVOKED'])
case('AU-22', 'N-03', lambda s: s['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER'].__setitem__('role', 'ANALYST'),
     'BLOCK', ['E-ACCEPTANCE-ROLE'])
case('AU-23', 'N-03', lambda s: s['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER'].__setitem__('recording_authority', '   '),
     'BLOCK', ['E-EVIDENCE-INCOMPLETE'])
case('AU-24', 'N-03', lambda s: s['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER'].__setitem__('timestamp', '2026-11-27T02:00:00'),
     'BLOCK', ['E-TIMESTAMP-INVALID'])
case('AU-25', 'N-03', lambda s: s['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER'].__setitem__('evidence_type', 'ONBOARDING'),
     'BLOCK', ['E-EVIDENCE-TYPE'])
case('AU-26', 'N-03', lambda s: s['evidence']['e-acc-C-P1-CONTINUE_STOP_OWNER'].__setitem__('evidence_id', 'e-acc-C-P1-CONTINUE_STOP_OWNER-copy'),
     'BLOCK', ['E-EVIDENCE-ID-MISMATCH'])
case('AU-27', 'N-03', lambda s: None, 'PASS', [])


def _point_acc(s, role, eid):
    s['roles'][role]['acceptance']['evidence_id'] = eid


def _reuse_rationale(s):
    s['candidates']['C-P9'] = {'candidate_ref': 'C-P9', 'active': True, 'fixture_marker': 'SYNTHETIC_TEST_DATA'}
    ca = copy.deepcopy(s['combination_approvals'][0])
    ca['candidate_ref'] = 'C-P9'
    s['combination_approvals'].append(ca)


def evaluate(expectation, expected, obs):
    if expectation == 'PASS':
        return 'PASS' if obs['ready'] and not obs['codes'] else 'FAIL'
    return 'PASS' if set(expected) & set(obs['codes']) and not obs['ready'] else 'FAIL'


rows = []
for cid, area, mutate, expectation, expected in CASES:
    s = base()
    try:
        mutate(s)
        obs = result(V.validate_state(s, P, S))
    except Exception as exc:
        obs = {'ready': None, 'codes': ['HARNESS-ERROR'], 'errors': -1,
               'detail': '%s: %s' % (type(exc).__name__, exc)}
    rows.append({'id': cid, 'area': area, 'expectation': expectation,
                 'expected_any': expected, 'verdict': evaluate(expectation, expected, obs),
                 'observed': obs})

# N-15: schema and assignment failures are terminal and structured.
schema_cases = []
for name in ('schema_invalid_assignment.json',):
    st = V.load_json_strict(F / name)
    r = V.validate_state(st, P, S)
    schema_cases.append({'case': name, 'source': 'assignment', **result(r)})
for name in ('invalid_schema.json', 'unresolvable_ref_schema.json'):
    bad_schema = V.load_schema(F / name)
    r = V.validate_state(base(), P, bad_schema)
    schema_cases.append({'case': name, 'source': 'schema', **result(r)})
# Missing required property and invalid nested/evidence structures.
for label, mutate in (
    ('missing_required_governance', lambda s: s.pop('governance')),
    ('invalid_nested_roles', lambda s: s.__setitem__('roles', ['not', 'an', 'object'])),
    ('invalid_evidence_structure', lambda s: s.__setitem__('evidence', {'e1': True})),
):
    s = base(); mutate(s)
    r = V.validate_state(s, P, S)
    schema_cases.append({'case': label, 'source': 'assignment', **result(r)})

# No broad suppression of unexpected programming errors: monkeypatch a helper
# to raise RuntimeError and confirm it propagates.
original = V.identity_subject
def boom(*a, **k):
    raise RuntimeError('unexpected engine programming error')
V.identity_subject = boom
propagated = False
try:
    V.validate_state(base(), P, S)
except RuntimeError:
    propagated = True
finally:
    V.identity_subject = original

summary = {
    'suite': 'M001_TEAM007_AUDITOR_FOLLOWUP',
    'engine_root': str(V21),
    'validator_sha256': __import__('hashlib').sha256((V21 / 'engine' / 'validator.py').read_bytes()).hexdigest().upper(),
    'atomic_cases': len(rows),
    'atomic_pass': sum(1 for r in rows if r['verdict'] == 'PASS'),
    'atomic_fail': sum(1 for r in rows if r['verdict'] == 'FAIL'),
    'cases': rows,
    'schema_cases': schema_cases,
    'unexpected_error_not_suppressed': propagated,
}
OUT.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print('ATOMIC', summary['atomic_pass'], 'PASS /', summary['atomic_fail'], 'FAIL of', summary['atomic_cases'])
for r in rows:
    if r['verdict'] == 'FAIL':
        print('FAIL', r['id'], r['observed'])
for c in schema_cases:
    print('SCHEMA', c['case'], 'ready=', c['ready'], 'codes=', c['codes'][:3])
print('unexpected error propagated:', propagated)
print('wrote', OUT)
