#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Independent mutation harness for mission M001-TEAM-005.

Authored from scratch for the re-audit.  It does not import or reuse V2's
mutation harness/canary.  V2 is treated as READ-ONLY: only engine/, policy/,
schemas/ and tests/fixtures/ are copied into disposable directories under
REAUDIT/mutation/independent_mutants/<mutant_name>/.  __pycache__ and any
mutants directories are excluded, and no destination is a descendant of a
copied source.

Writes (only inside the REAUDIT workspace):
  mutation/fixtures/*                    generated adversarial fixtures
  mutation/independent_mutants/*          disposable mutant trees
  mutation/results/independent_mutation_results.json
"""
import argparse
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REAUDIT = HERE.parent
V2 = REAUDIT.parent / 'M001_TEAM_ASSIGNMENT_ENGINE_V2'
MUT_ROOT = HERE / 'independent_mutants'
FIX_OUT = HERE / 'fixtures'
RESULTS = HERE / 'results' / 'independent_mutation_results.json'
CANARY = HERE / 'independent_canary.py'

ap = argparse.ArgumentParser(description='Independent V2 mutation harness')
ap.add_argument('--no-clean', action='store_true',
                help='do not wipe REAUDIT/mutation/independent_mutants first')
ap.add_argument('--only', default=None,
                help='run only mutants whose name contains this substring')
args = ap.parse_args()

IGNORE = shutil.ignore_patterns('__pycache__', 'mutants', '*.pyc')
SOURCE_FIX = V2 / 'tests' / 'fixtures'


# --------------------------------------------------------------------------- specs
def validator_spec(name, category, old, new, note=''):
    return dict(name=name, category=category, kind='validator',
                old=old, new=new, note=note)


def policy_spec(name, category, fn, note=''):
    return dict(name=name, category=category, kind='policy', fn=fn, note=note)


def negate(condition):
    """Prefix a guard with `False and` (one controlled textual change)."""
    return condition.replace('        if ', '        if False and ', 1)


SPECS = [
    validator_spec(
        'M01_duplicate_json_key_parser_bypass', 'duplicate-key parser bypass',
        "            if k in out:\n                raise DuplicateKeyError('E-DUPLICATE-JSON-KEY: %s' % k)",
        "            if False and k in out:\n                raise DuplicateKeyError('E-DUPLICATE-JSON-KEY: %s' % k)",
        'loader silently accepts the last duplicate key'),

    validator_spec(
        'M02_valid_timestamp_naive_bypass', 'timestamp bypass',
        "    return dt.tzinfo is not None and dt.utcoffset() is not None",
        "    return True",
        'all ISO-like strings become valid timestamps'),

    validator_spec(
        'M03_role_timestamp_field_bypass', 'timestamp bypass',
        "            if not valid_timestamp(holder.get(tfield)):",
        "            if False and not valid_timestamp(holder.get(tfield)):",
        'three per-role decision timestamps no longer checked'),

    validator_spec(
        'M04_evidence_subject_bypass', 'evidence-subject validation removal',
        "    if subject and record.get('subject') != subject:",
        "    if False and subject and record.get('subject') != subject:",
        'evidence may be rebound to another candidate'),

    validator_spec(
        'M05_evidence_unverified_bypass', 'evidence validation removal (bonus)',
        "        if rec.get('verification_status') not in policy['verification_statuses']:",
        "        if False and rec.get('verification_status') not in policy['verification_statuses']:",
        'global evidence verification gate removed'),

    validator_spec(
        'M06_candidate_key_reference_substitution', 'candidate-reference substitution',
        "        if ref != key or not ref:\n            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE','candidate data',candidate=key,message='Candidate key/reference mismatch'))",
        "        if not ref:\n            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE','candidate data',candidate=key,message='Candidate key/reference mismatch'))",
        'candidate registry key no longer bound to candidate_ref'),

    validator_spec(
        'M07_duplicate_candidate_identity_bypass', 'candidate identity (bonus)',
        "        if ref in seen:\n            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE','candidate data',candidate=ref,message='Duplicate candidate identity'))",
        "        if False and ref in seen:\n            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE','candidate data',candidate=ref,message='Duplicate candidate identity'))",
        'second uniqueness guard removed independently of the key/ref guard'),

    validator_spec(
        'M08_role_unknown_candidate_bypass', 'candidate-reference substitution',
        "        if ref not in candidates:\n            fail('formal_appointment_validity','E-CANDIDATE-UNKNOWN',role=role,candidate=str(ref),message='Unknown candidate')",
        "        if False and ref not in candidates:\n            fail('formal_appointment_validity','E-CANDIDATE-UNKNOWN',role=role,candidate=str(ref),message='Unknown candidate')",
        'role record may point to an unregistered candidate'),

    validator_spec(
        'M09_appointment_unknown_candidate_bypass', 'candidate-reference substitution',
        "        if ref not in candidates:\n            fail('human_candidate_acceptance','E-CANDIDATE-UNKNOWN',role=str(role),candidate=str(ref),message='Appointment references unknown candidate')",
        "        if False and ref not in candidates:\n            fail('human_candidate_acceptance','E-CANDIDATE-UNKNOWN',role=str(role),candidate=str(ref),message='Appointment references unknown candidate')",
        'appointment may point to an unregistered candidate'),

    validator_spec(
        'M10_authorization_boundary_bypass', 'authorization-boundary bypass',
        "    if governance.get('recruitment') != 'UNAUTHORIZED' or governance.get('field_validation') != 'NOT_STARTED':",
        "    if governance.get('recruitment') != 'UNAUTHORIZED':",
        'field_validation half of the governance guard removed'),

    validator_spec(
        'M11_topology_approval_bypass', 'topology-approval bypass',
        "    if topology.get('status') != 'APPROVED' and policy.get('require_topology_approved_for_stage_b'):",
        "    if False and topology.get('status') != 'APPROVED' and policy.get('require_topology_approved_for_stage_b'):",
        'explicit topology error removed'),

    validator_spec(
        'M12_formal_state_bypass', 'formal-state bypass',
        "        if st not in formal_states:\n            fail('role_assignment_completeness','E-APPOINTMENT-MISSING',role=role,\n                 message='Role is not FORMALLY_APPOINTED')\n            continue",
        "        if False and st not in formal_states:\n            fail('role_assignment_completeness','E-APPOINTMENT-MISSING',role=role,\n                 message='Role is not FORMALLY_APPOINTED')\n            continue",
        'non-formal states fall through into the formal-record checks'),

    policy_spec(
        'M13_formal_state_policy_bypass', 'formal-state bypass',
        lambda p: p['formal_appointment_states'].append('ACCEPTED_IN_CONVERSATION'),
        'policy reclassifies conversation acceptance as formal'),

    validator_spec(
        'M14_candidate_acceptance_bypass', 'candidate-acceptance bypass',
        "        if acc.get('candidate_accepted') is not True:",
        "        if False and acc.get('candidate_accepted') is not True:",
        'candidate acceptance no longer required'),

    validator_spec(
        'M15_role_po_approval_bypass', 'approval check removal',
        "        if appr.get('product_owner_approved') is not True:",
        "        if False and appr.get('product_owner_approved') is not True:",
        'role-level PO approval no longer required'),

    validator_spec(
        'M16_formal_approval_flag_bypass', 'approval revocation/basis check removal',
        "        if appr.get('formal') is not True:",
        "        if False and appr.get('formal') is not True:",
        'FORMALLY_APPOINTED with formal=false tolerated'),

    validator_spec(
        'M17_approval_basis_bypass', 'approval revocation/basis check removal',
        "        if not appr.get('basis'):",
        "        if False and not appr.get('basis'):",
        'empty approval basis tolerated'),

    validator_spec(
        'M18_formal_record_bypass', 'formal-state bypass (bonus)',
        "        if formal.get('formally_appointed') is not True:",
        "        if False and formal.get('formally_appointed') is not True:",
        'formal record flag no longer required'),

    validator_spec(
        'M19_onboarding_bypass', 'onboarding bypass',
        "        if rec.get('onboarding',{}).get('completed') is not True:",
        "        if False and rec.get('onboarding',{}).get('completed') is not True:",
        'onboarding completion no longer required'),

    validator_spec(
        'M20_combination_approval_missing_bypass', 'removal of combination-approval checks',
        "        if not ca:\n            fail('product_owner_combination_approval','E-COMBINATION-APPROVAL-MISSING',candidate=str(candidate),\n                 message='No exact Product Owner approval for combination %s' % key[1])",
        "        if False and not ca:\n            fail('product_owner_combination_approval','E-COMBINATION-APPROVAL-MISSING',candidate=str(candidate),\n                 message='No exact Product Owner approval for combination %s' % key[1])",
        'exact combination approval no longer required'),

    validator_spec(
        'M21_combination_outcome_revocation_bypass', 'approval revocation/basis check removal',
        "        if ca.get('outcome') != 'APPROVED':",
        "        if False and ca.get('outcome') != 'APPROVED':",
        'revoked/rejected combination approval tolerated'),

    validator_spec(
        'M22_combination_po_approval_bypass', 'removal of combination-approval checks',
        "        if ca.get('product_owner_approved') is not True:",
        "        if False and ca.get('product_owner_approved') is not True:",
        'combination PO flag no longer required'),

    validator_spec(
        'M23_combination_rationale_bypass', 'removal of combination-approval checks',
        "        if not ca.get('rationale'):",
        "        if False and not ca.get('rationale'):",
        'combination rationale no longer required'),

    validator_spec(
        'M24_combination_timestamp_bypass', 'timestamp bypass',
        "        if not valid_timestamp(ca.get('decision_timestamp')):",
        "        if False and not valid_timestamp(ca.get('decision_timestamp')):",
        'combination decision timestamp no longer checked'),

    validator_spec(
        'M25_discouraged_combination_bypass', 'discouraged-combination bypass',
        "            if set(combo['roles']).issubset(held) and not ca:\n                fail('role_compatibility',combo['code'],message='Discouraged combination lacks PO review')",
        "            if False and set(combo['roles']).issubset(held) and not ca:\n                fail('role_compatibility',combo['code'],message='Discouraged combination lacks PO review')",
        'discouraged combination review requirement removed'),

    validator_spec(
        'M26_hard_incompatibility_bypass', 'removal of combination-approval checks',
        "            if set(combo['roles']).issubset(held):\n                fail('role_compatibility',combo['code'],message='Hard incompatibility cannot be approved')",
        "            if False and set(combo['roles']).issubset(held):\n                fail('role_compatibility',combo['code'],message='Hard incompatibility cannot be approved')",
        'hard incompatibility no longer blocks Stage B'),

    validator_spec(
        'M27_evidence_separation_bypass', 'removal of combination-approval checks (bonus)',
        "                if not found:\n                    fail('role_compatibility','E-COND-EVIDENCE-SEPARATION',message='Evidence separation record missing')",
        "                if False and not found:\n                    fail('role_compatibility','E-COND-EVIDENCE-SEPARATION',message='Evidence separation record missing')",
        'conditional evidence separation no longer required'),

    validator_spec(
        'M28_unapproved_appointment_bypass', 'formal-state bypass',
        "        if role_records.get(role,{}).get('state') not in formal_states:",
        "        if False and role_records.get(role,{}).get('state') not in formal_states:",
        'appointment may be backed by a non-formal role record'),

    validator_spec(
        'M29_timestamp_order_bypass', 'timestamp bypass',
        "        if ts_a and ts_p and ts_f and not (ts_a <= ts_p <= ts_f):",
        "        if False and ts_a and ts_p and ts_f and not (ts_a <= ts_p <= ts_f):",
        'contradictory decision sequence tolerated'),

    policy_spec(
        'M30_hard_incompatibility_policy_removal', 'removal of combination-approval checks',
        lambda p: p.__setitem__('hard_incompatibilities',
                               [c for c in p['hard_incompatibilities']
                                if c['roles'] != ['MODERATOR', 'DATA_CUSTODIAN']]),
        'second hard-incompatibility rule deleted from policy'),
]

# Controls deliberately excluded from the "introduced" population.
EXCLUSIONS = [
    validator_spec(
        'X01_stage_b_topology_redundant', 'semantic-equivalence control',
        "    stage_b = (topology.get('status')=='APPROVED' and\n               all(dims.get(k)=='PASS' for k in policy['stage_b_dimensions']) and",
        "    stage_b = (all(dims.get(k)=='PASS' for k in policy['stage_b_dimensions']) and",
        'redundant topology clause in the final Stage B expression'),
    validator_spec(
        'X02_patch_target_absent', 'invalid-mutation control',
        "    if governance.get('recruitment') == 'AUTHORIZED':",
        "    if False:",
        'target condition does not exist in V2'),
    validator_spec(
        'X03_comment_only_noop', 'semantic-equivalence control',
        "    # No positive authorization may be inferred.",
        "    # No positive authorization may be inferred. (re-audit no-op)",
        'comment-only edit; no executable effect'),
]


# --------------------------------------------------------------------- fixtures
def build_extras():
    """Create my own adversarial fixtures; never writes to V2."""
    FIX_OUT.mkdir(parents=True, exist_ok=True)
    base = json.loads((SOURCE_FIX / 'valid_four_person.json').read_text(encoding='utf-8'))

    def dump(name, obj):
        (FIX_OUT / name).write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')

    def variant(fn):
        obj = copy.deepcopy(base)
        fn(obj)
        return obj

    dump('combo_rejected.json', variant(
        lambda d: d['combination_approvals'][0].__setitem__('outcome', 'REJECTED')))
    dump('combo_po_flag_false.json', variant(
        lambda d: d['combination_approvals'][0].__setitem__('product_owner_approved', False)))
    dump('combo_rationale_empty.json', variant(
        lambda d: d['combination_approvals'][0].__setitem__('rationale', '')))
    dump('combo_naive_timestamp.json', variant(
        lambda d: d['combination_approvals'][0].__setitem__('decision_timestamp',
                                                            '2026-11-27T01:00:00')))
    dump('formal_record_missing.json', variant(
        lambda d: d['roles']['MODERATOR']['formal'].__setitem__('formally_appointed', False)))
    dump('candidate_key_substitution.json', variant(
        lambda d: d.__setitem__('candidates', {
            ('C-PX' if k == 'C-P4' else k): v for k, v in d['candidates'].items()})))
    dump('appointment_unknown_candidate.json', variant(
        lambda d: d['appointments'][3].__setitem__('candidate_ref', 'C-UNKNOWN')))
    dump('evidence_subject_swap.json', variant(
        lambda d: d['evidence']['e-acc-C-P2'].__setitem__('subject', 'C-P3')))
    dump('evidence_unverified.json', variant(
        lambda d: d['evidence']['e-po-C-P2'].__setitem__('verification_status', 'PENDING')))
    dump('timestamp_order_reversed.json', variant(
        lambda d: d['roles']['ANALYST']['acceptance'].__setitem__(
            'candidate_accepted_at', '2026-11-27T03:00:00+00:00')))
    dump('field_validation_inferred.json', variant(
        lambda d: d['governance'].__setitem__('field_validation', 'IN_PROGRESS')))
    dump('extra_top_level_key.json', variant(
        lambda d: d.__setitem__('extra_unexpected_field', 'x')))
    orphan = {
        'evidence_id': 'e-orphan',
        'evidence_type': 'DECISION_BASIS',
        'source_ref': 'synthetic://e-orphan',
        'content_hash': '0' * 64,
        'recording_authority': 'SYNTHETIC_TEST_DATA',
        'timestamp': '2026-11-27T00:00:00+00:00',
        'verification_status': 'PENDING',
        'subject': 'C-P1',
    }
    dump('orphan_unverified_evidence.json', variant(
        lambda d: d['evidence'].__setitem__('e-orphan', orphan)))
    return sorted(p.name for p in FIX_OUT.glob('*.json'))


def make_tree(dest):
    if dest.exists():
        shutil.rmtree(dest)
    (dest / 'tests').mkdir(parents=True)
    for rel in ('engine', 'policy', 'schemas'):
        shutil.copytree(V2 / rel, dest / rel, ignore=IGNORE)
    shutil.copytree(SOURCE_FIX, dest / 'tests' / 'fixtures', ignore=IGNORE)


def apply_spec(spec, dest):
    """Return (applied, reason, occurrences)."""
    make_tree(dest)
    if spec['kind'] == 'policy':
        path = dest / 'policy' / 'role_constraints.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        spec['fn'](data)
        path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        return True, '', 1
    path = dest / 'engine' / 'validator.py'
    text = path.read_text(encoding='utf-8')
    count = text.count(spec['old'])
    if count != 1:
        return False, 'patch target occurrences=%d (expected exactly 1)' % count, count
    path.write_text(text.replace(spec['old'], spec['new'], 1), encoding='utf-8')
    return True, '', 1


def run_canary(root):
    cmd = [sys.executable, str(CANARY), '--root', str(root)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return cmd, proc.returncode, proc.stdout, proc.stderr


def load_module(label, path):
    spec = importlib.util.spec_from_file_location(label, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fingerprint(module, root):
    """Compare observable behaviour of two trees on every available fixture."""
    policy = module.load_policy(root / 'policy' / 'role_constraints.json')
    schema = module.load_schema(root / 'schemas' / 'team_assignment.schema.json')
    paths = sorted(SOURCE_FIX.glob('*')) + sorted(FIX_OUT.glob('*'))
    out = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            data = module.load_json_strict(path)
        except Exception as exc:
            out.append([path.name, 'LOAD', type(exc).__name__, str(exc)])
            continue
        try:
            rep = module.validate_state(data, policy, schema)
            out.append([path.name, 'RESULT', json.dumps(rep.to_dict(), sort_keys=True)])
        except Exception as exc:
            out.append([path.name, 'EXC', type(exc).__name__, str(exc)])
    return out


def differential(mut_root):
    base = load_module('_ri_base_validator', V2 / 'engine' / 'validator.py')
    mut = load_module('_ri_mut_validator', mut_root / 'engine' / 'validator.py')
    left = fingerprint(base, V2)
    right = fingerprint(mut, mut_root)
    diffs = [(a, b) for a, b in zip(left, right) if a != b]
    return dict(identical=not diffs and len(left) == len(right),
                compared_inputs=len(left), differences=len(diffs),
                first_difference=diffs[0] if diffs else None)


# -------------------------------------------------------------------------- main
if not CANARY.exists() or not V2.exists():
    raise SystemExit('missing canary or read-only V2 source: %s / %s' % (CANARY, V2))

extras = build_extras()
if not args.no_clean and MUT_ROOT.exists():
    shutil.rmtree(MUT_ROOT)
MUT_ROOT.mkdir(parents=True, exist_ok=True)
RESULTS.parent.mkdir(parents=True, exist_ok=True)

baseline_cmd, baseline_exit, baseline_out, baseline_err = run_canary(V2)
if baseline_exit != 0:
    raise SystemExit('baseline canary failed; refusing to mutate:\n%s\n%s' %
                     (baseline_out, baseline_err))

rows = []
excluded_rows = []
selected = [s for s in SPECS
            if args.only is None or args.only in s['name']]
selected_x = [s for s in EXCLUSIONS
              if args.only is None or args.only in s['name']]

for spec in selected:
    dest = MUT_ROOT / spec['name']
    applied, reason, occurrences = apply_spec(spec, dest)
    if not applied:
        excluded_rows.append(dict(name=spec['name'], category=spec['category'],
                                  reason='EXCLUDED: %s' % reason,
                                  patch_occurrences=occurrences,
                                  note=spec['note']))
        continue
    cmd, exit_code, out, err = run_canary(dest)
    failed = [line for line in out.splitlines() if line.startswith('FAIL')]
    pass_line = next((l for l in out.splitlines() if l.startswith('CANARY_PASS')), '')
    rows.append(dict(name=spec['name'], category=spec['category'],
                     kind=spec['kind'], note=spec['note'],
                     patch_occurrences=occurrences, dest=str(dest),
                     applied_change=dict(old=spec.get('old', '<policy callable>'),
                                         new=spec.get('new', '<policy callable>')),
                     command=' '.join(cmd), exit=exit_code,
                     detected=exit_code != 0,
                     canary_pass=pass_line, failed_checks=failed,
                     stdout=out, stderr=err))

for spec in selected_x:
    dest = MUT_ROOT / spec['name']
    applied, reason, occurrences = apply_spec(spec, dest)
    if not applied:
        excluded_rows.append(dict(name=spec['name'], category=spec['category'],
                                  reason='EXCLUDED: patch target not found (%s)' % reason,
                                  patch_occurrences=occurrences, note=spec['note']))
        continue
    cmd, exit_code, out, err = run_canary(dest)
    diff = differential(dest)
    if diff['identical'] and exit_code == 0:
        final_reason = ('EXCLUDED: semantically equivalent under shipped policy; '
                        'canary survived and differential comparison found no '
                        'observable difference on %d inputs' % diff['compared_inputs'])
    elif diff['identical']:
        final_reason = ('EXCLUDED: differential comparison found no observable '
                        'difference on %d inputs (canary exit %d)' %
                        (diff['compared_inputs'], exit_code))
    else:
        final_reason = ('NOT EXCLUDED: differential found %d change(s); '
                        'manual review required' % diff['differences'])
    excluded_rows.append(dict(name=spec['name'], category=spec['category'],
                              reason=final_reason, patch_occurrences=occurrences,
                              note=spec['note'], command=' '.join(cmd),
                              exit=exit_code, canary_pass=next(
                                  (l for l in out.splitlines()
                                   if l.startswith('CANARY_PASS')), ''),
                              differential=diff, stdout=out, stderr=err))

detected = [r for r in rows if r['detected']]
survived = [r for r in rows if not r['detected']]
result = dict(
    audit='M001-TEAM-005 independent re-audit mutation harness',
    source_tree=str(V2), source_tree_mode='READ-ONLY',
    canary=str(CANARY), extras=extras,
    interpreter=sys.version.split()[0],
    baseline=dict(command=' '.join(baseline_cmd), exit=baseline_exit,
                  stdout=baseline_out, stderr=baseline_err),
    summary=dict(total_introduced=len(rows), detected=len(detected),
                 survived=len(survived), excluded=len(excluded_rows),
                 detected_names=[r['name'] for r in detected],
                 survived_names=[r['name'] for r in survived],
                 excluded_names=[e['name'] for e in excluded_rows]),
    mutants=rows, excluded=excluded_rows,
)
RESULTS.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

print('BASELINE_EXIT', baseline_exit)
print(next((l for l in baseline_out.splitlines() if l.startswith('CANARY_PASS')), ''))
s = result['summary']
print('INTRODUCED %d DETECTED %d SURVIVED %d EXCLUDED %d' %
      (s['total_introduced'], s['detected'], s['survived'], s['excluded']))
for r in rows:
    print('%s %s exit=%s %s' %
          ('DETECTED' if r['detected'] else 'SURVIVED', r['name'],
           r['exit'], ','.join(x.split()[1] for x in r['failed_checks'])))
for e in excluded_rows:
    print('EXCLUDED %s | %s' % (e['name'], e['reason']))
print('RESULTS', RESULTS)
