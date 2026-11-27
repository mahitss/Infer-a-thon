#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Controlled mutations for the four V2.1 HIGH remediation areas."""
import json, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
MUT = ROOT / 'tests' / 'mutation' / 'mutants'
CANARY = ROOT / 'tests' / 'mutation' / 'canary_v21.py'
if MUT.exists():
    shutil.rmtree(MUT)
MUT.mkdir(parents=True)

MUTANTS = [
    ('M1_basis_check_removed', 'validator',
     "if not meaningful_text(appr.get('basis')):",
     "if False and not meaningful_text(appr.get('basis')):"),
    ('M2_rationale_check_removed', 'validator',
     "if not meaningful_text(rationale):",
     "if False and not meaningful_text(rationale):"),
    ('M3_acceptance_role_binding_removed', 'validator',
     "                            subject, 'evidence_integrity', issues,\n                            code_prefix='E-EVIDENCE')",
     "                            ref, 'evidence_integrity', issues,\n                            code_prefix='E-EVIDENCE')"),
    ('M4_schema_terminal_return_removed', 'validator',
     "        return ValidationResult({k: 'FAIL' for k in dims}, issues, False)\n\n    governance",
     "        pass\n\n    governance"),
]

rows = []
base = subprocess.run([sys.executable, str(CANARY), '--root', str(ROOT)],
                      capture_output=True, text=True)
for name, kind, old, new in MUTANTS:
    dst = MUT / name
    dst.mkdir(parents=True)
    for rel in ('engine', 'policy', 'schemas', 'tests'):
        src = ROOT / rel
        if src.is_dir():
            shutil.copytree(src, dst / rel,
                            ignore=shutil.ignore_patterns('__pycache__', 'mutants'))
        elif src.is_file():
            shutil.copy2(src, dst / rel)
    p = dst / 'engine' / 'validator.py'
    text = p.read_text(encoding='utf-8')
    if old not in text:
        rows.append({'mutation': name, 'detected': False, 'error': 'patch target absent',
                     'exit': None})
        continue
    p.write_text(text.replace(old, new, 1), encoding='utf-8')
    cp = subprocess.run([sys.executable, str(CANARY), '--root', str(dst)],
                        capture_output=True, text=True)
    rows.append({'mutation': name, 'detected': cp.returncode != 0, 'exit': cp.returncode,
                 'output': cp.stdout.strip(), 'error': ''})

summary = {
    'baseline_exit': base.returncode,
    'baseline_output': base.stdout.strip(),
    'total': len(rows),
    'detected': sum(1 for r in rows if r['detected']),
    'survived': [r['mutation'] for r in rows if not r['detected']],
    'mutants': rows,
}
(ROOT / 'tests' / 'results' / 'mutation_results.json').write_text(
    json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print('BASELINE_EXIT', base.returncode)
print('DETECTED %d/%d' % (summary['detected'], summary['total']))
for r in rows:
    print('%s %s exit=%s' % ('DETECTED' if r['detected'] else 'SURVIVED',
                             r['mutation'], r['exit']))
