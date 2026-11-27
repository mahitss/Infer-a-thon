#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V2 controlled mutation harness; original engine untouched."""
import json, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
MUT = ROOT / 'tests' / 'mutation' / 'mutants'
CANARY = ROOT / 'tests' / 'mutation' / 'mutation_canary.py'
if MUT.exists(): shutil.rmtree(MUT)
MUT.mkdir(parents=True)

def policy_mut(name, fn):
    return (name, 'policy', fn, None)
def val_mut(name, old, new, count=0):
    return (name, 'validator', old, new, count)

mutants = [
 policy_mut('M01_remove_hard_MA', lambda p: p.__setitem__('hard_incompatibilities', [c for c in p['hard_incompatibilities'] if c['roles']!=['MODERATOR','ANALYST']])),
 policy_mut('M02_remove_hard_MDC', lambda p: p.__setitem__('hard_incompatibilities', [c for c in p['hard_incompatibilities'] if c['roles']!=['MODERATOR','DATA_CUSTODIAN']])),
 val_mut('M03_ignore_evidence_separation', "if combo['requirement'] == 'evidence_separation':", "if False and combo['requirement'] == 'evidence_separation':"),
 val_mut('M04_ignore_combination_approval', "if not ca:\n            fail('product_owner_combination_approval','E-COMBINATION-APPROVAL-MISSING'", "if False and not ca:\n            fail('product_owner_combination_approval','E-COMBINATION-APPROVAL-MISSING'"),
 policy_mut('M05_promote_conversation_to_formal', lambda p: p['formal_appointment_states'].append('ACCEPTED_IN_CONVERSATION')),
 val_mut('M06_ignore_po_approval', "if appr.get('product_owner_approved') is not True:", "if False and appr.get('product_owner_approved') is not True:"),
 val_mut('M07_ignore_candidate_acceptance', "if acc.get('candidate_accepted') is not True:", "if False and acc.get('candidate_accepted') is not True:"),
 val_mut('M08_ignore_onboarding', "if rec.get('onboarding',{}).get('completed') is not True:", "if False and rec.get('onboarding',{}).get('completed') is not True:"),
 val_mut('M09_allow_discouraged_without_review', "if set(combo['roles']).issubset(held) and not ca:", "if False and set(combo['roles']).issubset(held) and not ca:"),
 val_mut('M10_allow_unknown_candidate', "if ref not in candidates:", "if False and ref not in candidates:", -1),
 val_mut('M11_allow_broken_evidence', "if not isinstance(record, dict):\n        issues.append(Issue('ERROR', code_prefix + '-UNKNOWN', dimension,\n                            message='Unknown evidence id %s' % eid))\n        return None", "if not isinstance(record, dict):\n        return record"),
 val_mut('M12_allow_naive_timestamp', "    try:\n        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))\n    except ValueError:\n        return False\n    return dt.tzinfo is not None and dt.utcoffset() is not None", "    return isinstance(value, str) and bool(value)"),
 val_mut('M13_ignore_topology_approval', "if topology.get('status') != 'APPROVED' and policy.get('require_topology_approved_for_stage_b'):", "if False and topology.get('status') != 'APPROVED' and policy.get('require_topology_approved_for_stage_b'):"),
 val_mut('M14_allow_duplicate_candidate',
         "        if ref != key or not ref:\n            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE','candidate data',candidate=key,message='Candidate key/reference mismatch'))\n        if ref in seen:\n            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE','candidate data',candidate=ref,message='Duplicate candidate identity'))",
         "        if False and ref != key or not ref:\n            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE','candidate data',candidate=key,message='Candidate key/reference mismatch'))\n        if False and ref in seen:\n            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE','candidate data',candidate=ref,message='Duplicate candidate identity'))"),
 val_mut('M15_ignore_authorization_state', "if governance.get('recruitment') != 'UNAUTHORIZED' or governance.get('field_validation') != 'NOT_STARTED':", "if False and governance.get('recruitment') != 'UNAUTHORIZED':"),
 val_mut('M16_allow_hard_incompatibility', "if set(combo['roles']).issubset(held):\n                fail('role_compatibility',combo['code'],message='Hard incompatibility cannot be approved')", "if False and set(combo['roles']).issubset(held):\n                fail('role_compatibility',combo['code'],message='Hard incompatibility cannot be approved')"),
]
rows=[]
for m in mutants:
    name=m[0]; kind=m[1]; dst=MUT/name
    # Copy only the inputs the canary reads. Copying ROOT wholesale would
    # recurse into the destination (tests/mutation/mutants) forever.
    dst.mkdir(parents=True)
    for rel in ('engine', 'policy', 'schemas', 'tests'):
        src = ROOT / rel
        if src.is_dir():
            shutil.copytree(src, dst / rel,
                            ignore=shutil.ignore_patterns('__pycache__', 'mutants'))
        elif src.is_file():
            shutil.copy2(src, dst / rel)
    p = dst/'policy'/'role_constraints.json' if kind=='policy' else dst/'engine'/'validator.py'
    if kind=='policy':
        data=json.loads(p.read_text(encoding='utf-8')); m[2](data); p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    else:
        text=p.read_text(encoding='utf-8'); old=m[2]; new=m[3]; count=m[4] if len(m)>4 else 0
        if old not in text: raise RuntimeError('patch target missing: '+name)
        text = text.replace(old,new) if count == -1 else text.replace(old,new,1 if count==0 else count)
        p.write_text(text,encoding='utf-8')
    cp=subprocess.run([sys.executable,str(CANARY),'--root',str(dst)],capture_output=True,text=True)
    rows.append(dict(mutation=name,detected=cp.returncode!=0,exit=cp.returncode,output=cp.stdout.strip()))
baseline=subprocess.run([sys.executable,str(CANARY),'--root',str(ROOT)],capture_output=True,text=True)
summary=dict(baseline_exit=baseline.returncode,baseline_output=baseline.stdout.strip(),
             total=len(rows),detected=sum(1 for r in rows if r['detected']),
             survived=[r['mutation'] for r in rows if not r['detected']],mutants=rows)
(ROOT/'reports'/'mutation_results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print('BASELINE_EXIT',baseline.returncode)
print('DETECTED %d/%d' % (summary['detected'],summary['total']))
for r in rows: print('%s %s exit=%s' % ('DETECTED' if r['detected'] else 'SURVIVED',r['mutation'],r['exit']))
