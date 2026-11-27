#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Independent adversarial audit tests for the M001 Team Assignment Engine."""
import json, os, subprocess, sys
from pathlib import Path

A = Path(__file__).resolve().parent
O = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE')
F = A / 'adversarial_fixtures'
sys.path.insert(0, str(O))
from engine.validator import load_json, load_policy, load_schema, validate_state, validate_schema  # noqa: E402

POLICY = load_policy(); SCHEMA = load_schema()
results = []

def rec(tid, claim, ok, detail=''):
    results.append((tid, claim, 'PASS' if ok else 'FAIL', detail))

def fixture(name):
    return load_json(F / name)

def codes(res, sev=None):
    return [i.code for i in res.issues if sev is None or i.severity == sev]

def v(name):
    return validate_state(fixture(name), POLICY, SCHEMA)

# Hard incompatibilities
for tid, name, code in [
    ('ADV-01','hard_moderator_analyst.json','E-HARD-MODERATOR-ANALYST'),
    ('ADV-02','hard_moderator_custodian.json','E-HARD-MODERATOR-CUSTODIAN')]:
    r = v(name); rec(tid, 'hard incompatibility is blocking', code in codes(r,'ERROR'),
                     'codes=%s valid=%s' % (codes(r,'ERROR'), r.valid))

# Discouraged combinations must be review-gated, not merely warned
for tid, name, code in [
    ('ADV-03','discouraged_ro_moderator.json','W-DISCOURAGED-RO-MODERATOR'),
    ('ADV-04','discouraged_custodian_analyst.json','W-DISCOURAGED-CUSTODIAN-ANALYST')]:
    r = v(name); blocking = any(c.startswith('E-') and 'COMBINATION' in c for c in codes(r,'ERROR'))
    rec(tid, 'discouraged combination requires PO-documented review', blocking,
        'valid=%s errors=%s warnings=%s' % (r.valid, codes(r,'ERROR'), codes(r,'WARNING')))

# Conditional evidence content, not just booleans
for tid, name in [('ADV-05','false_evidence_moderator_notetaker.json'),
                  ('ADV-06','false_evidence_continue_stop.json')]:
    r = v(name); rec(tid, 'true boolean without evidence reference is rejected', not r.valid,
                     'valid=%s errors=%s' % (r.valid, codes(r,'ERROR')))

# Multi-role documentation
r = v('compatible_combination_no_approval.json')
rec('ADV-07', 'multi-role assignment requires explicit PO combination approval', not r.valid,
    'valid=%s errors=%s' % (r.valid, codes(r,'ERROR')))

# Identity integrity
r = v('duplicate_candidate_identifier.json')
rec('ADV-08', 'duplicate candidate identifier across roles is rejected', not r.valid,
    'valid=%s errors=%s' % (r.valid, codes(r,'ERROR')))
r = v('unknown_human_reference.json')
rec('ADV-09', 'unknown human reference is rejected', not r.valid,
    'valid=%s errors=%s' % (r.valid, codes(r,'ERROR')))

# State integrity
r = v('proposed_treated_as_appointed.json')
rec('ADV-10', 'PROPOSED role is not treated as appointed', not r.valid,
    'valid=%s errors=%s' % (r.valid, codes(r,'ERROR')))
r = v('formal_state_formal_approval_false.json')
rec('ADV-11', 'FORMALLY_APPOINTED with approval.formal=false is rejected', not r.valid,
    'valid=%s errors=%s' % (r.valid, codes(r,'ERROR')))
r = v('rejected_still_assigned.json')
rec('ADV-12', 'REJECTED candidate still assigned is rejected', not r.valid,
    'errors=%s' % codes(r,'ERROR'))
r = v('deferred_still_assigned.json')
rec('ADV-13', 'DEFERRED candidate still assigned is rejected', not r.valid,
    'errors=%s' % codes(r,'ERROR'))

# Evidence and timestamps
r = v('weak_decision_evidence.json')
rec('ADV-14', 'empty Product Owner decision basis is rejected', not r.valid,
    'valid=%s errors=%s' % (r.valid, codes(r,'ERROR')))
state = load_json(O / 'fixtures' / 'valid_four_person.json')
has_ts = any('timestamp' in json.dumps(x).lower() for rkey in state['roles'].values() for x in [rkey])
rec('ADV-15', 'structured decision timestamps are required', has_ts,
    'timestamp_fields_present=%s' % has_ts)

# Authorization boundaries
r = v('topology_proposed_all_formal.json')
rec('ADV-16', 'unapproved topology blocks Stage B readiness', not r.valid,
    'valid=%s warnings=%s' % (r.valid, codes(r,'WARNING')))
current = load_json(O / 'state' / 'current_assignment_state.json')
r = validate_state(current, POLICY, SCHEMA)
rec('ADV-17', 'current state is blocked with five missing appointments',
    len([i for i in r.errors if i.code=='E-APPOINTMENT-MISSING']) == 5 and not r.valid,
    'errors=%s' % codes(r,'ERROR'))
rec('ADV-18', 'Research Owner not promoted to formal appointment',
    'I-RO-NOT-FORMAL' in codes(r,'INFO') and current['roles']['RESEARCH_OWNER']['state']=='ACCEPTED_IN_CONVERSATION',
    'info=%s' % codes(r,'INFO'))

# Schema robustness
schema_errors = validate_schema(load_json(O / 'fixtures' / 'valid_four_person.json'), SCHEMA)
rec('ADV-19', 'valid fixture conforms to schema', not schema_errors, str(schema_errors))
raw = (F / 'duplicate_json_key.json').read_text(encoding='utf-8')
parsed = json.loads(raw)
rec('ADV-20', 'duplicate JSON keys are detected', parsed['schema_version'] != '9.9',
    'last_wins_value=%s' % parsed['schema_version'])

# CLI robustness
for tid, args, expect in [
    ('ADV-21', ['--state', str(F / 'malformed.json')], 'clean error'),
    ('ADV-22', ['--state', str(F / 'missing_file.json')], 'clean error'),
    ('ADV-23', ['--state', str(F / 'invalid_utf8.bin')], 'clean error')]:
    p = subprocess.run([sys.executable, str(O / 'cli' / 'validate.py'), *args],
                       capture_output=True, text=True)
    clean = p.returncode != 0 and 'Traceback' not in p.stderr
    rec(tid, 'CLI handles invalid input cleanly', clean,
        'exit=%s stderr_head=%s' % (p.returncode, p.stderr[:80].replace('\n',' ')))

# Determinism
inputs = ['valid_four_person.json','hard_moderator_analyst.json','current_assignment_state.json']
deterministic = True
for name in inputs:
    path = (O / 'state' / name) if name == 'current_assignment_state.json' else (
        O / 'fixtures' / name if name == 'valid_four_person.json' else F / name)
    a = validate_state(load_json(path), POLICY, SCHEMA).to_dict()
    b = validate_state(load_json(path), POLICY, SCHEMA).to_dict()
    deterministic = deterministic and a == b
rec('ADV-24', 'repeated validation is deterministic', deterministic, '')

for tid, claim, status, detail in results:
    print('%s %-4s %s | %s' % (status, tid, claim, detail))
fails = [r for r in results if r[2]=='FAIL']
print('TOTAL %d PASS %d FAIL %d' % (len(results), len(results)-len(fails), len(fails)))
print('FAILED_IDS ' + ','.join(r[0] for r in fails))
json.dump([{'id':r[0],'claim':r[1],'status':r[2],'detail':r[3]} for r in results],
          open(A / 'independent_test_results.json','w',encoding='utf-8'), indent=2)
sys.exit(0 if not fails else 1)
