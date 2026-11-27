#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Controlled mutation testing of a copied validator; original untouched."""
import json, shutil, subprocess, sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parent
ORIG = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE')
MUT = AUDIT / 'mutations'
CANARY = AUDIT / 'mutation_canary.py'
if MUT.exists():
    shutil.rmtree(MUT)
MUT.mkdir(parents=True)

mutants = {}

def patch_validator(name, old, new):
    mutants[name] = ('validator', old, new)

def patch_policy(name, fn):
    mutants[name] = ('policy', fn, None)

patch_policy('M01_remove_moderator_analyst', lambda p: p['hard_incompatibilities'].__setitem__(
    slice(0,1), [c for c in p['hard_incompatibilities'] if c['roles'] != ['MODERATOR','ANALYST']]))
patch_policy('M02_remove_moderator_custodian', lambda p: p['hard_incompatibilities'].__setitem__(
    slice(0,len(p['hard_incompatibilities'])), [c for c in p['hard_incompatibilities'] if c['roles'] != ['MODERATOR','DATA_CUSTODIAN']]))
patch_validator('M03_ignore_evidence_separation',
    "if conditional.get(combo['requirement']) is not True:",
    "if False and conditional.get(combo['requirement']) is not True:")
patch_validator('M04_ignore_explicit_cs',
    "if conditional.get(combo['requirement']) is not True:",
    "if False and conditional.get(combo['requirement']) is not True:")
patch_validator('M05_promote_conversation_to_formal',
    "if _state_of(state, 'RESEARCH_OWNER') == 'ACCEPTED_IN_CONVERSATION':",
    "if False and _state_of(state, 'RESEARCH_OWNER') == 'ACCEPTED_IN_CONVERSATION':")
patch_validator('M06_ignore_po_approval',
    "return record.get('approval', {}).get('product_owner_approved') is True",
    "return True")
patch_validator('M07_ignore_candidate_acceptance',
    "return record.get('acceptance', {}).get('candidate_accepted') is True",
    "return True")
patch_validator('M08_ignore_onboarding',
    "return record.get('onboarding', {}).get('completed') is True",
    "return True")
patch_validator('M09_allow_discouraged_without_review',
    "if not resolved:",
    "if False and not resolved:")
patch_policy('M10_infer_appointments_from_topology',
    lambda p: p.__setitem__('missing_appointment_states', []))

rows = []
for name, (kind, old_or_fn, new) in mutants.items():
    dst = MUT / name
    shutil.copytree(ORIG, dst)
    for pyc in dst.rglob('*.pyc'):
        pyc.unlink()
    if kind == 'validator':
        p = dst / 'engine' / 'validator.py'
        text = p.read_text(encoding='utf-8')
        if old_or_fn not in text:
            raise RuntimeError('patch target missing: '+name)
        if name == 'M04_ignore_explicit_cs':
            text = text.replace(old_or_fn, new)
            text = text.replace(
                "if cs_state in ('UNASSIGNED', 'DEFERRED', 'REJECTED', 'PROPOSED'):",
                "if False and cs_state in ('UNASSIGNED', 'DEFERRED', 'REJECTED', 'PROPOSED'):")
        else:
            text = text.replace(old_or_fn, new)
        p.write_text(text, encoding='utf-8')
    else:
        p = dst / 'policy' / 'role_constraints.json'
        data = json.loads(p.read_text(encoding='utf-8'))
        old_or_fn(data)
        p.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    cp = subprocess.run([sys.executable, str(CANARY), '--root', str(dst)],
                        capture_output=True, text=True)
    detected = cp.returncode != 0
    rows.append(dict(mutation=name, kind=kind, detected=detected,
                     canary_exit=cp.returncode, output=cp.stdout.strip()))

baseline = subprocess.run([sys.executable, str(CANARY), '--root', str(ORIG)],
                          capture_output=True, text=True)
summary = dict(baseline_exit=baseline.returncode, baseline_output=baseline.stdout.strip(),
               mutants=rows, total=len(rows), detected=sum(1 for r in rows if r['detected']),
               survived=[r['mutation'] for r in rows if not r['detected']])
(AUDIT / 'mutation_results.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
print('BASELINE_EXIT', baseline.returncode)
print('DETECTED %d/%d' % (summary['detected'], summary['total']))
for r in rows:
    print('%s %s exit=%s' % ('DETECTED' if r['detected'] else 'SURVIVED', r['mutation'], r['canary_exit']))
