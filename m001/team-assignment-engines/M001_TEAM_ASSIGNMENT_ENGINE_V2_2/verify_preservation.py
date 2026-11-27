#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Prove V2, the re-audit, V1, the prior audit and repo are unchanged."""
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
base = json.loads((ROOT / 'evidence' / 'PRESERVED_BASELINE.json').read_text(encoding='utf-8'))


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest().upper()


def tree(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and p.suffix != '.pyc'
            and not any(x in ('__pycache__', 'mutants', 'independent_mutants',
                              'disposable_v2', 'disposable_v21') for x in p.relative_to(root).parts)}


bad = []
for name in ('V1', 'V2', 'AUDIT', 'V21', 'FOLLOWUP'):
    root = Path(base[name]['root'])
    now = tree(root)
    before = base[name]['files']
    if now != before:
        bad.append((name, [k for k in set(now) | set(before) if now.get(k) != before.get(k)][:10]))

repo = Path(r'C:\Users\pc\OneDrive\Desktop\Infer-a-Thon')
head = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
status = subprocess.run(['git', '-C', str(repo), 'status', '--porcelain'], capture_output=True, text=True).stdout.strip()
if head != base['repository']['head']:
    bad.append(('HEAD', head))
if status != base['repository']['status']:
    bad.append(('repo status', status))
print('V2 / REAUDIT / V1 / AUDIT unchanged:', not any(x[0] in ('V2', 'REAUDIT', 'V1', 'AUDIT') for x in bad))
print('HEAD unchanged:', head == base['repository']['head'], head)
print('repo clean:', status == '')
for item in bad:
    print('CHANGED', item)
sys.exit(0 if not bad else 1)
