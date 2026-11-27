#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Prove V1, V2, the prior audit and the repo were unchanged during this audit."""
import hashlib, json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
start = json.loads((HERE / 'AUDIT_START_BASELINE.json').read_text(encoding='utf-8'))


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest().upper()


def tree(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and p.suffix != '.pyc'
            and not any(part in ('__pycache__', 'mutants') for part in p.relative_to(root).parts)}


bad = []
for name in ('V1', 'AUDIT', 'V2'):
    root = Path(start[name]['root'])
    now = tree(root)
    before = start[name]['files']
    if now != before:
        differing = [k for k in set(now) | set(before) if now.get(k) != before.get(k)]
        bad.append((name, differing[:20]))

repo = Path(r'C:\Users\pc\OneDrive\Desktop\Infer-a-Thon')
head = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
status = subprocess.run(['git', '-C', str(repo), 'status', '--porcelain'], capture_output=True, text=True).stdout.strip()
if head != start['repository']['head']:
    bad.append(('repository HEAD', head))
if status != start['repository']['status_porcelain']:
    bad.append(('repository status', status))

print('V1/V2/AUDIT unchanged:', not bad)
print('HEAD unchanged:', head == start['repository']['head'])
print('repo clean:', status == '')
for item in bad:
    print('CHANGED', item)
sys.exit(0 if not bad else 1)
