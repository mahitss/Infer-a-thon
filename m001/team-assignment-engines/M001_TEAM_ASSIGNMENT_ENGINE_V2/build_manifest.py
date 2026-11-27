#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build a deterministic SHA-256 manifest of all V2 deliverable artifacts."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'SHA256_MANIFEST.json'
EXCLUDED_DIRS = {'__pycache__', 'mutants'}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest().upper()


files = {}
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path == MANIFEST:
        continue
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in rel.parts) or path.suffix == '.pyc':
        continue
    files[rel.as_posix()] = sha256(path)

payload = {
    'package': 'M001_TEAM_ASSIGNMENT_ENGINE_V2',
    'mission': 'M001-TEAM-004',
    'algorithm': 'SHA-256',
    'generated': '2026-11-27',
    'note': 'The manifest file excludes itself. Generated mutant copies, __pycache__ and .pyc files are excluded as non-deliverable build artifacts.',
    'excluded': sorted(EXCLUDED_DIRS) + ['SHA256_MANIFEST.json', '*.pyc'],
    'file_count': len(files),
    'files': dict(sorted(files.items())),
}
MANIFEST.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
print('manifest files:', len(files))
