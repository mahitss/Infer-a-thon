#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read-only SHA-256 baseline capture for all audited workspaces and the repo."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOTS = {
    'V1': Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE'),
    'AUDIT': Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_AUDIT'),
    'V2': Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2'),
}
REPO = Path(r'C:\Users\pc\OneDrive\Desktop\Infer-a-Thon')
OUT = Path(__file__).resolve().parent / (sys.argv[1] if len(sys.argv) > 1 else 'AUDIT_START_BASELINE.json')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest().upper()


def tree(root, skip=()):
    out = {}
    for p in sorted(root.rglob('*')):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(part in skip for part in p.relative_to(root).parts) or p.suffix == '.pyc':
            continue
        out[rel] = sha(p)
    return out


payload = {name: {'root': str(root), 'file_count': len(tree(root, ('__pycache__', 'mutants'))),
                  'files': tree(root, ('__pycache__', 'mutants'))}
           for name, root in ROOTS.items()}
payload['repository'] = {
    'head': subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip(),
    'status_porcelain': subprocess.run(['git', '-C', str(REPO), 'status', '--porcelain'], capture_output=True, text=True).stdout.strip(),
}
payload['jsonschema_version'] = None
try:
    import jsonschema
    payload['jsonschema_version'] = getattr(jsonschema, '__version__', 'unknown')
except Exception:
    pass
OUT.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
print('wrote', OUT.name)
for k in ('V1', 'AUDIT', 'V2'):
    print(k, payload[k]['file_count'], 'files')
print('HEAD', payload['repository']['head'], '| clean:', payload['repository']['status_porcelain'] == '')
print('jsonschema', payload['jsonschema_version'])
