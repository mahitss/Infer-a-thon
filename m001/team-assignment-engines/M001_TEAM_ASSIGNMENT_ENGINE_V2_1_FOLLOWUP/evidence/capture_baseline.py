#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read-only SHA-256 baseline capture for all preserved workspaces."""
import hashlib, json, subprocess, sys
from pathlib import Path
ROOTS = {
    'V1': Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE'),
    'V2': Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2'),
    'AUDIT': Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT'),
    'V21': Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1'),
}
REPO = Path(r'C:\Users\pc\OneDrive\Desktop\Infer-a-Thon')
OUT = Path(__file__).resolve().parent / (sys.argv[1] if len(sys.argv) > 1 else 'BASELINE_START.json')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest().upper()


def tree(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and p.suffix != '.pyc'
            and not any(x in ('__pycache__', 'mutants', 'independent_mutants') for x in p.relative_to(root).parts)}


data = {k: {'root': str(v), 'files': tree(v)} for k, v in ROOTS.items()}
data['repository'] = {
    'head': subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip(),
    'status': subprocess.run(['git', '-C', str(REPO), 'status', '--porcelain'], capture_output=True, text=True).stdout.strip(),
}
OUT.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
for k in ROOTS:
    print(k, len(data[k]['files']), 'authored files')
print('HEAD', data['repository']['head'], 'clean:', data['repository']['status'] == '')
print('V21 validator', data['V21']['files']['engine/validator.py'])
print('V2 validator', data['V2']['files']['engine/validator.py'])
