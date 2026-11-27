#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""INDEPENDENT V2 adversarial suite (M001-TEAM-005).

Reads V2 source/fixtures only. All mutations are applied to in-memory deep copies.
Writes results only into the REAUDIT workspace.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

V2 = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1')
REAUDIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(V2))
from engine.validator import (  # noqa: E402
    load_json_strict, load_policy, load_schema, validate_state,
    structural_schema_errors, validate_schema, valid_timestamp,
)

POLICY = load_policy()
SCHEMA = load_schema()
BASE = load_json_strict(V2 / 'tests' / 'fixtures' / 'valid_four_person.json')


def codes(r):
    return [i.code for i in r.issues]


def run(state):
    r = validate_state(state, POLICY, SCHEMA)
    return {
        'codes': sorted(set(codes(r))),
        'dimensions': dict(sorted(r.dimensions.items())),
        'stage_b_role_ready': r.stage_b_role_ready,
        'recruitment_authorized': r.recruitment_authorized,
        'field_validation_authorized': r.field_validation_authorized,
        'blocking_error_count': len(r.errors),
    }


CASES = []


def case(cid, category, description, mutate, expectation, expected_codes=()):
    CASES.append(dict(id=cid, category=category, description=description,
                      mutate=mutate, expectation=expectation,
                      expected_codes=list(expected_codes)))


def base():
    return copy.deepcopy(BASE)


# ---------- Combination-approval integrity ----------
case('COMB-01', 'combination', 'Approval contains an extra role not held by the candidate',
     lambda s: s['combination_approvals'][0].__setitem__('roles', ['RESEARCH_OWNER', 'CONTINUE_STOP_OWNER', 'ANALYST']),
     'BLOCK', ['E-COMBINATION-APPROVAL-MISSING'])
case('COMB-02', 'combination', 'Approval roles reordered (same exact set)',
     lambda s: s['combination_approvals'][0].__setitem__('roles', ['CONTINUE_STOP_OWNER', 'RESEARCH_OWNER']),
     'EXPECTED_PASS', [])
case('COMB-03', 'combination', 'Approval roles duplicated within the same record',
     lambda s: s['combination_approvals'][0].__setitem__('roles', ['RESEARCH_OWNER', 'CONTINUE_STOP_OWNER', 'CONTINUE_STOP_OWNER']),
     'BLOCK', ['E-COMBINATION-APPROVAL-DUPLICATE'])
case('COMB-04', 'combination', 'Approval references another candidate',
     lambda s: s['combination_approvals'][0].__setitem__('candidate_ref', 'C-P2'),
     'BLOCK', ['E-COMBINATION-APPROVAL-MISSING'])
case('COMB-05', 'combination', 'Approval reuses evidence from another decision',
     lambda s: s['combination_approvals'][0].__setitem__('evidence_id', 'e-combo-C-P2-MODERATOR+NOTE_TAKER'),
     'BLOCK', ['E-EVIDENCE-SUBJECT'])
case('COMB-06', 'combination', 'Approval is stale (timestamp years before appointment)',
     lambda s: s['combination_approvals'][0].__setitem__('decision_timestamp', '2019-01-01T00:00:00+00:00'),
     'BLOCK_STALE', ['E-COMBINATION-APPROVAL-STALE'])
case('COMB-07', 'combination', 'Approval marked revoked (unsupported property)',
     lambda s: s['combination_approvals'][0].__setitem__('revoked', True),
     'BLOCK', ['E-SCHEMA'])
case('COMB-08', 'combination', 'Approval outcome contradicts decision (REJECTED but PO approved)',
     lambda s: s['combination_approvals'][0].__setitem__('outcome', 'REJECTED'),
     'BLOCK', ['E-COMBINATION-APPROVAL-REJECTED'])
case('COMB-09', 'combination', 'Approval evidence is unverified',
     lambda s: s['evidence']['e-combo-C-P1-CONTINUE_STOP_OWNER+RESEARCH_OWNER'].__setitem__('verification_status', 'PENDING'),
     'BLOCK', ['E-EVIDENCE-UNVERIFIED'])
case('COMB-10', 'combination', 'Approval names an unauthorized actor (unsupported property)',
     lambda s: s['combination_approvals'][0].__setitem__('approved_by', 'UNKNOWN_ACTOR'),
     'BLOCK', ['E-SCHEMA'])
case('COMB-11', 'combination', 'Approval rationale contains whitespace only',
     lambda s: s['combination_approvals'][0].__setitem__('rationale', '   \t\n '),
     'BLOCK', ['E-COMBINATION-RATIONALE'])
case('COMB-12', 'combination', 'One valid approval reused for an unrelated second candidate combination',
     lambda s: (s['candidates'].__setitem__('C-P5', {'candidate_ref': 'C-P5', 'active': True, 'fixture_marker': 'SYNTHETIC_TEST_DATA'}),
                s['combination_approvals'].append(copy.deepcopy(s['combination_approvals'][0]))),
     'BLOCK', ['E-COMBINATION-APPROVAL-MISSING'])

# ---------- Evidence integrity ----------
case('EVID-01', 'evidence', 'Evidence subject resolves to a different candidate',
     lambda s: s['evidence']['e-acc-C-P1-RESEARCH_OWNER'].__setitem__('subject', 'C-P2'),
     'BLOCK', ['E-EVIDENCE-SUBJECT'])
case('EVID-02', 'evidence', 'Acceptance evidence is reused across roles of the same candidate',
     lambda s: s['roles']['CONTINUE_STOP_OWNER']['acceptance'].__setitem__('evidence_id', 'e-acc-C-P1-RESEARCH_OWNER'),
     'BLOCK_IF_ROLE_BOUND', ['E-ACCEPTANCE-ROLE', 'E-EVIDENCE-SUBJECT'])
case('EVID-03', 'evidence', 'Source hash does not match the referenced source (format still valid)',
     lambda s: s['evidence']['e-acc-C-P1-RESEARCH_OWNER'].__setitem__('content_hash', '0' * 64),
     'BLOCK', ['E-EVIDENCE-HASH'])
case('EVID-04', 'evidence', 'Evidence record duplicated under a second ID',
     lambda s: s['evidence'].__setitem__('e-acc-C-P1-copy', copy.deepcopy(s['evidence']['e-acc-C-P1-RESEARCH_OWNER'])),
     'BLOCK', ['E-EVIDENCE-DUPLICATE'])
case('EVID-05', 'evidence', 'Evidence record marked revoked (unsupported property)',
     lambda s: s['evidence']['e-acc-C-P1-RESEARCH_OWNER'].__setitem__('revoked', True),
     'BLOCK', ['E-SCHEMA', 'E-EVIDENCE-REVOKED'])
case('EVID-06', 'evidence', 'Evidence timestamp predates its claimed source/decision',
     lambda s: s['evidence']['e-form-C-P1-RESEARCH_OWNER'].__setitem__('timestamp', '1999-01-01T00:00:00+00:00'),
     'BLOCK', ['E-EVIDENCE-STALE'])
case('EVID-07', 'evidence', 'Verification status inconsistent with required approval',
     lambda s: s['evidence']['e-po-C-P1-RESEARCH_OWNER'].__setitem__('verification_status', 'UNVERIFIED'),
     'BLOCK', ['E-EVIDENCE-UNVERIFIED'])
case('EVID-08', 'evidence', 'Unverified evidence still leaves evidence_integrity dimension PASS',
     lambda s: s['evidence']['e-combo-C-P2-MODERATOR+NOTE_TAKER'].__setitem__('verification_status', 'PENDING'),
     'BLOCK', ['E-EVIDENCE-UNVERIFIED'])
case('EVID-09', 'evidence', 'Empty content hash string',
     lambda s: s['evidence']['e-acc-C-P1-RESEARCH_OWNER'].__setitem__('content_hash', ''),
     'BLOCK', ['E-EVIDENCE-HASH'])
case('EVID-10', 'evidence', 'Unknown evidence type identifier',
     lambda s: s['evidence']['e-acc-C-P1-RESEARCH_OWNER'].__setitem__('evidence_type', 'NOT_A_TYPE'),
     'BLOCK', ['E-EVIDENCE-TYPE'])

# ---------- Appointment state integrity ----------
case('ST-01', 'appointment', 'Candidate acceptance evidence belongs to another candidate',
     lambda s: s['roles']['ANALYST']['acceptance'].__setitem__('evidence_id', 'e-acc-C-P1-RESEARCH_OWNER'),
     'BLOCK', ['E-EVIDENCE-SUBJECT'])
case('ST-02', 'appointment', 'Formal appointment references obsolete acceptance timestamp',
     lambda s: s['roles']['RESEARCH_OWNER']['acceptance'].__setitem__('candidate_accepted_at', '2020-01-01T00:00:00+00:00'),
     'BLOCK_ORDER', ['E-TIMESTAMP-ORDER'])
case('ST-03', 'appointment', 'Combination approval timestamp precedes candidate acceptance',
     lambda s: s['combination_approvals'][0].__setitem__('decision_timestamp', '2026-11-26T00:00:00+00:00'),
     'BLOCK', ['E-COMBINATION-APPROVAL-TIMESTAMP-ORDER'])
case('ST-04', 'appointment', 'Rejected candidate retained in active appointment',
     lambda s: (s['roles']['ANALYST'].__setitem__('state', 'REJECTED'),
                s['appointments'].append({'candidate_ref': 'C-P4', 'role': 'ANALYST', 'state': 'FORMALLY_APPOINTED'})),
     'BLOCK', ['E-APPOINTMENT-MISSING'])
case('ST-05', 'appointment', 'Deferred candidate assigned',
     lambda s: s['roles']['NOTE_TAKER'].__setitem__('state', 'DEFERRED'),
     'BLOCK', ['E-APPOINTMENT-MISSING'])
case('ST-06', 'appointment', 'Formal appointment revoked but record remains active',
     lambda s: s['roles']['RESEARCH_OWNER']['formal'].__setitem__('revoked', True),
     'BLOCK', ['E-SCHEMA'])
case('ST-07', 'appointment', 'Contradictory appointment history supplied',
     lambda s: s['roles']['RESEARCH_OWNER'].__setitem__('history', [{'state': 'REJECTED'}, {'state': 'FORMALLY_APPOINTED'}]),
     'BLOCK', ['E-SCHEMA'])
case('ST-08', 'appointment', 'One candidate evidence reused for another candidate',
     lambda s: s['roles']['NOTE_TAKER']['onboarding'].__setitem__('evidence_id', 'e-onb-C-P1-RESEARCH_OWNER'),
     'BLOCK', ['E-EVIDENCE-SUBJECT'])
case('ST-09', 'appointment', 'Approval basis contains whitespace only',
     lambda s: s['roles']['RESEARCH_OWNER']['approval'].__setitem__('basis', '  \t\n '),
     'BLOCK', ['E-DECISION-EVIDENCE-EMPTY'])
case('ST-10', 'appointment', 'Escalation contact is whitespace only',
     lambda s: s['roles']['RESEARCH_OWNER']['escalation'].__setitem__('contact', '   '),
     'BLOCK', ['E-ESCALATION-CONTACT'])

# ---------- Identity integrity ----------
case('ID-01', 'identity', 'Case-only variant candidate reference consistent across records',
     lambda s: _case_variant(s),
     'BLOCK', ['E-EVIDENCE-SUBJECT'])
case('ID-02', 'identity', 'Unicode-equivalent candidate identifiers coexist',
     lambda s: s['candidates'].__setitem__('C-P１', {'candidate_ref': 'C-P１', 'active': True, 'fixture_marker': 'SYNTHETIC_TEST_DATA'}),
     'BLOCK', ['E-CANDIDATE-NORMALIZATION'])
case('ID-03', 'identity', 'Whitespace-only candidate reference',
     lambda s: _whitespace_ref(s),
     'BLOCK', ['E-CANDIDATE-REF-INVALID'])
case('ID-04', 'identity', 'Duplicate candidate identity records',
     lambda s: s['candidates'].__setitem__('C-P1-again', {'candidate_ref': 'C-P1', 'active': True, 'fixture_marker': 'SYNTHETIC_TEST_DATA'}),
     'BLOCK', ['E-CANDIDATE-DUPLICATE'])
case('ID-05', 'identity', 'Candidate inactive at appointment time',
     lambda s: s['candidates']['C-P1'].__setitem__('active', False),
     'BLOCK', ['E-CANDIDATE-INACTIVE'])
case('ID-06', 'identity', 'Identity changed after approval (no history support)',
     lambda s: s['candidates']['C-P1'].__setitem__('candidate_ref', 'C-RENAMED'),
     'BLOCK', ['E-CANDIDATE-DUPLICATE'])
case('ID-07', 'identity', 'One human split into two synthetic identities to avoid combination approval',
     lambda s: _split_identity(s),
     'BLOCK', ['E-IDENTITY-ALIAS'])

# ---------- Policy enforcement ----------
case('POL-01', 'policy', 'Hard Moderator+Analyst conflict with full approval',
     lambda s: _hard_conflict(s, 'MODERATOR', 'C-P4'),
     'BLOCK', ['E-HARD-MODERATOR-ANALYST'])
case('POL-02', 'policy', 'Hard Moderator+Data Custodian conflict with full approval',
     lambda s: _hard_conflict(s, 'MODERATOR', 'C-P3'),
     'BLOCK', ['E-HARD-MODERATOR-CUSTODIAN'])
case('POL-03', 'policy', 'Discouraged combination classification preserved in policy',
     lambda s: s,
     'EXPECTED_PASS', [])
case('POL-04', 'policy', 'Conditional evidence separation with wrong subject',
     lambda s: s['evidence']['e-sep-C-P2'].__setitem__('subject', 'C-P1:MODERATOR+NOTE_TAKER'),
     'BLOCK', ['E-COND-EVIDENCE-SEPARATION'])
case('POL-05', 'policy', 'Approved topology cannot appoint an unassigned role',
     lambda s: s['roles']['ANALYST'].__setitem__('state', 'UNASSIGNED'),
     'BLOCK', ['E-APPOINTMENT-MISSING'])
case('POL-06', 'policy', 'Proposed topology blocks Stage B even when all roles are formal',
     lambda s: s['topology'].__setitem__('status', 'PROPOSED'),
     'BLOCK', ['E-TOPOLOGY-UNAPPROVED'])
case('POL-07', 'policy', 'Combination evidence has wrong evidence type',
     lambda s: s['evidence']['e-combo-C-P1-CONTINUE_STOP_OWNER+RESEARCH_OWNER'].__setitem__('evidence_type', 'ONBOARDING'),
     'BLOCK', ['E-EVIDENCE-TYPE'])

# ---------- Authorization boundary ----------
case('AUTH-01', 'authorization', 'Passing staffing result must not authorize recruitment',
     lambda s: s,
     'EXPECTED_PASS', [])
case('AUTH-02', 'authorization', 'Recruitment governance flag altered to AUTHORIZED',
     lambda s: s['governance'].__setitem__('recruitment', 'AUTHORIZED'),
     'BLOCK', ['E-AUTHORIZATION-STATE', 'E-SCHEMA'])
case('AUTH-03', 'authorization', 'Field validation governance flag altered to IN_PROGRESS',
     lambda s: s['governance'].__setitem__('field_validation', 'IN_PROGRESS'),
     'BLOCK', ['E-AUTHORIZATION-STATE', 'E-SCHEMA'])

# ---------- Dimension reporting ----------
case('DIM-01', 'dimension', 'Evidence error present while evidence_integrity dimension reports PASS',
     lambda s: s['evidence']['e-acc-C-P1-RESEARCH_OWNER'].__setitem__('verification_status', 'PENDING'),
     'BLOCK', ['E-EVIDENCE-UNVERIFIED'])


def _case_variant(s):
    for k in list(s['candidates']):
        if k == 'C-P1':
            lower = k.lower()
            s['candidates'][lower] = s['candidates'].pop(k)
            s['candidates'][lower]['candidate_ref'] = lower
    for r in s['roles'].values():
        if r.get('candidate_ref') == 'C-P1':
            r['candidate_ref'] = 'c-p1'
        for holder in ('acceptance', 'approval', 'formal', 'onboarding'):
            if holder in r:
                pass
    for a in s['appointments']:
        if a['candidate_ref'] == 'C-P1':
            a['candidate_ref'] = 'c-p1'
    for ca in s['combination_approvals']:
        if ca['candidate_ref'] == 'C-P1':
            ca['candidate_ref'] = 'c-p1'


def _whitespace_ref(s):
    ws = '   '
    s['candidates'][ws] = {'candidate_ref': ws, 'active': True, 'fixture_marker': 'SYNTHETIC_TEST_DATA'}
    del s['candidates']['C-P1']
    for r in s['roles'].values():
        if r.get('candidate_ref') == 'C-P1':
            r['candidate_ref'] = ws
    for a in s['appointments']:
        if a['candidate_ref'] == 'C-P1':
            a['candidate_ref'] = ws
    for ca in s['combination_approvals']:
        if ca['candidate_ref'] == 'C-P1':
            ca['candidate_ref'] = ws
    for eid, e in list(s['evidence'].items()):
        if e['subject'] == 'C-P1':
            e['subject'] = ws
        if eid.endswith('C-P1'):
            new = eid[:-4] + ws
            s['evidence'][new] = s['evidence'].pop(eid)
            s['evidence'][new]['evidence_id'] = new
    for r in s['roles'].values():
        for h in ('acceptance', 'approval', 'formal', 'onboarding'):
            if h in r and isinstance(r[h], dict) and r[h].get('evidence_id', '').endswith('C-P1'):
                r[h]['evidence_id'] = r[h]['evidence_id'][:-4] + ws


def _split_identity(s):
    # Represent the two roles of C-P1 as two distinct registry identities.
    s['candidates']['C-P1a'] = {'candidate_ref': 'C-P1a', 'active': True, 'fixture_marker': 'SYNTHETIC_TEST_DATA'}
    s['candidates']['C-P1b'] = {'candidate_ref': 'C-P1b', 'active': True, 'fixture_marker': 'SYNTHETIC_TEST_DATA'}
    del s['candidates']['C-P1']
    s['roles']['RESEARCH_OWNER']['candidate_ref'] = 'C-P1a'
    s['roles']['CONTINUE_STOP_OWNER']['candidate_ref'] = 'C-P1b'
    for a in s['appointments']:
        if a['role'] == 'RESEARCH_OWNER':
            a['candidate_ref'] = 'C-P1a'
        if a['role'] == 'CONTINUE_STOP_OWNER':
            a['candidate_ref'] = 'C-P1b'
    s['combination_approvals'] = []


def _hard_conflict(s, role, candidate):
    s['roles'][role]['candidate_ref'] = candidate
    s['appointments'] = [a for a in s['appointments'] if a['role'] != role]
    s['appointments'].append({'candidate_ref': candidate, 'role': role, 'state': 'FORMALLY_APPOINTED'})


def evaluate(case, observed):
    """Independent verdict: did the engine exhibit the expected secure behavior?"""
    obs_codes = set(observed['codes'])
    exp = case['expected_codes']
    if case['expectation'] == 'EXPECTED_PASS':
        return 'SECURE' if not observed['blocking_error_count'] and observed['stage_b_role_ready'] else 'DEFECT'
    if exp and any(c in obs_codes for c in exp):
        return 'SECURE'
    return 'DEFECT'


def main():
    results = []
    for c in CASES:
        s = base()
        try:
            c['mutate'](s)
            observed = run(s)
        except Exception as exc:
            observed = {'codes': ['HARNESS-ERROR'], 'dimensions': {},
                        'stage_b_role_ready': None, 'blocking_error_count': -1,
                        'error': '%s: %s' % (type(exc).__name__, exc)}
        verdict = evaluate(c, observed)
        results.append({
            'id': c['id'], 'category': c['category'], 'description': c['description'],
            'expectation': c['expectation'], 'expected_codes': c['expected_codes'],
            'verdict': verdict, 'observed': observed,
            'dimension_note': ('evidence_integrity=PASS while evidence errors present'
                               if any(x.startswith('E-EVIDENCE-') for x in observed['codes'])
                               and observed['dimensions'].get('evidence_integrity') == 'PASS' else ''),
        })
    out = {
        'suite': 'M001_TEAM005_INDEPENDENT_ADVERSARIAL',
        'engine_root': str(V2),
        'policy_version': POLICY.get('version'),
        'policy_source': POLICY.get('source'),
        'total_cases': len(results),
        'secure': sum(1 for r in results if r['verdict'] == 'SECURE'),
        'defects': sum(1 for r in results if r['verdict'] == 'DEFECT'),
        'cases': results,
    }
    path = REAUDIT / 'tests' / 'results' / 'independent_adversarial_results.json'
    path.write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print('TOTAL', out['total_cases'], 'SECURE', out['secure'], 'DEFECT', out['defects'])
    for r in results:
        if r['verdict'] == 'DEFECT':
            print('DEFECT', r['id'], r['description'], '| observed:', r['observed']['codes'])
    print('wrote', path)


if __name__ == '__main__':
    main()
