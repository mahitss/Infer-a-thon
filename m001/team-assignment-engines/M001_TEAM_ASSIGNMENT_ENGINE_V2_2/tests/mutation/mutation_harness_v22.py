#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Controlled mutations for the five V2.2 Stage-B blockers."""
import json, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
MUT = ROOT / 'tests' / 'mutation' / 'mutants'
CANARY = ROOT / 'tests' / 'mutation' / 'canary_v22.py'
if MUT.exists():
    shutil.rmtree(MUT)
MUT.mkdir(parents=True)

MUTANTS = [
    ('M1_F007_predicate_reverted', 'validator',
     "    return any(unicodedata.category(ch) not in NON_CONTENT_CATEGORIES for ch in value)",
     "    return isinstance(value, str) and bool(value)"),
    ('M2_N04_escalation_check_removed', 'validator',
     "        if not meaningful_text(rec.get('escalation', {}).get('contact')):",
     "        if False and not meaningful_text(rec.get('escalation', {}).get('contact')):"),
    ('M3_N08_duplicate_check_removed', 'validator',
     "        if prior is not None:\n            fail('evidence_integrity','E-EVIDENCE-DUPLICATE',",
     "        if False and prior is not None:\n            fail('evidence_integrity','E-EVIDENCE-DUPLICATE',"),
    ('M4_N11_ordering_check_removed', 'validator',
     "            if accepted and decision_ts < max(accepted):",
     "            if False and accepted and decision_ts < max(accepted):"),
    ('M5_N12_ref_check_removed', 'validator',
     "        if not meaningful_text(ref) or (isinstance(ref, str) and ref != ref.strip()):\n            issues.append(Issue('ERROR','E-CANDIDATE-REF-INVALID','candidate data',",
     "        if False:\n            issues.append(Issue('ERROR','E-CANDIDATE-REF-INVALID','candidate data',"),
]

rows = []
base = subprocess.run([sys.executable, str(CANARY), '--root', str(ROOT)], capture_output=True, text=True)
for name, kind, old, new in MUTANTS:
    dst = MUT / name
    dst.mkdir(parents=True)
    for rel in ('engine', 'policy', 'schemas', 'tests'):
        src = ROOT / rel
        if src.is_dir():
            shutil.copytree(src, dst / rel, ignore=shutil.ignore_patterns('__pycache__', 'mutants'))
        elif src.is_file():
            shutil.copy2(src, dst / rel)
    p = dst / 'engine' / 'validator.py'
    text = p.read_text(encoding='utf-8')
    if old not in text:
        rows.append({'mutation': name, 'detected': False, 'error': 'patch target absent', 'exit': None})
        continue
    p.write_text(text.replace(old, new, 1), encoding='utf-8')
    cp = subprocess.run([sys.executable, str(CANARY), '--root', str(dst)], capture_output=True, text=True)
    rows.append({'mutation': name, 'detected': cp.returncode != 0, 'exit': cp.returncode,
                 'output': cp.stdout.strip(), 'error': ''})

summary = {'baseline_exit': base.returncode, 'baseline_output': base.stdout.strip(),
           'total': len(rows), 'detected': sum(1 for r in rows if r['detected']),
           'survived': [r['mutation'] for r in rows if not r['detected']], 'mutants': rows}
(ROOT / 'tests' / 'results' / 'mutation_results.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print('BASELINE_EXIT', base.returncode)
print('DETECTED %d/%d' % (summary['detected'], summary['total']))
for r in rows:
    print('%s %s exit=%s' % ('DETECTED' if r['detected'] else 'SURVIVED', r['mutation'], r['exit']))
