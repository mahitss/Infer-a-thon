#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Deterministic SHA-256 manifest for all V2.1 deliverables and evidence."""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'SHA256_MANIFEST.json'
SKIP = {'__pycache__', 'mutants'}


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest().upper()


files = {}
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or p == MANIFEST or p.suffix == '.pyc':
        continue
    rel = p.relative_to(ROOT)
    if any(x in SKIP for x in rel.parts):
        continue
    files[rel.as_posix()] = sha(p)

payload = {
    'package': 'M001_TEAM_ASSIGNMENT_ENGINE_V2_1',
    'mission': 'M001-TEAM-006',
    'date': '2026-11-27',
    'algorithm': 'SHA-256',
    'note': 'Self-excluded. Generated mutant copies, bytecode caches and .pyc are excluded.',
    'excluded': sorted(SKIP) + ['SHA256_MANIFEST.json', '*.pyc'],
    'file_count': len(files),
    'files': dict(sorted(files.items())),
}
MANIFEST.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
print('manifest files:', len(files))
