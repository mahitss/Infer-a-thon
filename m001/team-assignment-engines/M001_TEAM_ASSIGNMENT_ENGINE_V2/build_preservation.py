#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify that preserved workspaces and the repository remain unchanged.

Read-only. Writes only reports/preservation_check.json inside V2.
"""
import hashlib
import json
import subprocess
from pathlib import Path

V1 = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE')
AUD = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_AUDIT')
ZIP = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_EVIDENCE_FREEZE\M001_DIAGNOSTIC_EVIDENCE_FREEZE_CANDIDATE.zip')
REPO = Path(r'C:\Users\pc\OneDrive\Desktop\Infer-a-Thon')
OUT = Path(__file__).resolve().parent / 'reports' / 'preservation_check.json'

ANCHORS = {
    'v1_validator': ('engine/validator.py', '9CB8729278763DAC773E0C4E250A77951FC16C349AC1F8FBC69EC69D1C440E70'),
    'frozen_evidence_zip': (str(ZIP), '82B58946963C1DBAEA4A180DBA7833C5217852A847222C5726A321C2B7B6CB3D'),
}
EXPECTED_HEAD = '30db9a1929bbccf73a538f6657cb10f49758688e'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest().upper()


def tree(root):
    return {str(p.relative_to(root)).replace('\\', '/'): sha256(p)
            for p in sorted(root.rglob('*')) if p.is_file()}


v1_tree = tree(V1)
audit_tree = tree(AUD)
anchors = {}
for key, (rel, expected) in ANCHORS.items():
    actual = zip_hash = (sha256(ZIP) if key == 'frozen_evidence_zip' else v1_tree[rel])
    anchors[key] = {'expected': expected, 'actual': actual, 'match': actual == expected}

head = subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'],
                      capture_output=True, text=True).stdout.strip()
status = subprocess.run(['git', '-C', str(REPO), 'status', '--porcelain'],
                        capture_output=True, text=True).stdout.strip()

payload = {
    'v1_file_count': len(v1_tree),
    'v1_tree_sha256': v1_tree,
    'audit_file_count': len(audit_tree),
    'audit_tree_sha256': audit_tree,
    'anchors': anchors,
    'repository': {'expected_head': EXPECTED_HEAD, 'actual_head': head,
                   'head_match': head == EXPECTED_HEAD,
                   'status_porcelain': status, 'clean': status == ''},
}
payload['all_checks_pass'] = (all(a['match'] for a in anchors.values()) and
                              payload['repository']['head_match'] and
                              payload['repository']['clean'])
OUT.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
print('V1 files:', len(v1_tree), '| AUDIT files:', len(audit_tree))
for k, a in anchors.items():
    print(k, 'MATCH' if a['match'] else 'MISMATCH', a['actual'])
print('HEAD', head, 'MATCH' if head == EXPECTED_HEAD else 'MISMATCH')
print('repo clean:', status == '')
print('ALL PRESERVATION CHECKS:', 'PASS' if payload['all_checks_pass'] else 'FAIL')
