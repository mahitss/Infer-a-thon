#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify every SHA-256 recorded in the V2 artifact manifest."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'SHA256_MANIFEST.json'
data = json.loads(MANIFEST.read_text(encoding='utf-8'))

missing, mismatch, extra = [], [], []
for rel, expected in data['files'].items():
    path = ROOT / rel
    if not path.is_file():
        missing.append(rel)
        continue
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    if h.hexdigest().upper() != expected:
        mismatch.append(rel)

listed = set(data['files'])
excluded_dirs = set(data['excluded'][:2])
for path in sorted(ROOT.rglob('*')):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT).as_posix()
    if rel == 'SHA256_MANIFEST.json' or rel in listed:
        continue
    if any(part in excluded_dirs for part in path.relative_to(ROOT).parts) or path.suffix == '.pyc':
        continue
    extra.append(rel)

print('expected files:', data['file_count'])
print('missing:', len(missing))
print('mismatches:', len(mismatch))
print('unlisted artifacts:', len(extra))
if mismatch:
    for rel in mismatch:
        print('MISMATCH', rel)
if extra:
    for rel in extra:
        print('UNLISTED', rel)
ok = not (missing or mismatch or extra)
print('MANIFEST_VERIFY:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
