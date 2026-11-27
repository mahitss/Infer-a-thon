#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Independent capture driver for M001-TEAM-007.

Runs every assigned command with PYTHONDONTWRITEBYTECODE=1, records exact
command / cwd / exit / stdout / stderr (full + tail), and checks that the
preserved V2_1 workspace (and the other preserved roots) did not change.
Writes ONLY inside the FOLLOWUP workspace.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

FOLLOWUP = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1_FOLLOWUP')
V21 = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1')
DISP = FOLLOWUP / 'tests' / 'disposable_v21'
RAW = FOLLOWUP / 'tests' / 'results' / '_raw_capture.json'
BASELINE = FOLLOWUP / 'evidence' / 'BASELINE_START.json'
ROOTS = {
    'V1': Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE'),
    'V2': Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2'),
    'AUDIT': Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_REAUDIT'),
    'V21': V21,
}
REPO = Path(r'C:\Users\pc\OneDrive\Desktop\Infer-a-Thon')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest().upper()


def tree(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and p.suffix != '.pyc'
            and not any(x in ('__pycache__', 'mutants', 'independent_mutants')
                        for x in p.relative_to(root).parts)}


def state_snapshot():
    return {
        'roots': {k: {'root': str(v), 'files': tree(v)} for k, v in ROOTS.items()},
        'repository': {
            'head': subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'],
                                   capture_output=True, text=True).stdout.strip(),
            'status': subprocess.run(['git', '-C', str(REPO), 'status', '--porcelain'],
                                     capture_output=True, text=True).stdout.strip(),
        },
    }


ENV = dict(os.environ)
ENV['PYTHONDONTWRITEBYTECODE'] = '1'

# ---- Build disposable mirror of the V2_1 source tree (no writes to V2_1) ----
if DISP.exists():
    shutil.rmtree(DISP)
DISP.mkdir(parents=True)
for rel in ('engine', 'policy', 'schemas', 'tests', 'cli', 'state'):
    src = V21 / rel
    if src.is_dir():
        shutil.copytree(src, DISP / rel,
                        ignore=shutil.ignore_patterns('__pycache__', 'mutants'))
    elif src.is_file():
        shutil.copy2(src, DISP / rel)
(DISP / 'tests' / 'results').mkdir(parents=True, exist_ok=True)

pre = state_snapshot()
state_before = sha(V21 / 'state' / 'current_assignment_state.json')

COMMANDS = [
    dict(id='ADV', label='adversarial unittest discover',
         cmd=['python', '-m', 'unittest', 'discover', '-s', 'tests/adversarial',
              '-p', 'test_*.py', '-v'], cwd=str(V21)),
    dict(id='REG', label='regression unittest discover',
         cmd=['python', '-m', 'unittest', 'discover', '-s', 'tests/regression',
              '-p', 'test_*.py', '-v'], cwd=str(V21)),
    dict(id='IND_ADV', label='independent adversarial 50-case corpus',
         cmd=['python', 'tests/independent/independent_adversarial_v21.py'],
         cwd=str(DISP),
         note='Relocated runner: the script hardcodes V2_1 as its READ target but '
              'writes results to parents[2]. Run from the disposable mirror so the '
              'write lands in FOLLOWUP, never in V2_1. Script bytes are identical '
              'to V2_1/tests/independent/independent_adversarial_v21.py.'),
    dict(id='REFINED', label='refined cases',
         cmd=['python', 'tests/independent/refined_cases_v21.py'],
         cwd=str(DISP),
         note='Relocated runner for the same no-write reason as IND_ADV.'),
    dict(id='CANARY', label='mutation canary baseline',
         cmd=['python', 'tests/mutation/canary_v21.py', '--root', '.'],
         cwd=str(V21)),
    dict(id='MUTATION', label='mutation harness (disposable copy)',
         cmd=['python', 'tests/mutation/mutation_harness_v21.py'],
         cwd=str(DISP),
         note='Harness writes mutants and results into its ROOT; executed in the '
              'disposable mirror so V2_1 is untouched.'),
]

CLI_BASE = ['python', 'cli/validate.py', '--state']
for cid, label, arg in [
    ('CLI_CURRENT', 'current state', 'state/current_assignment_state.json'),
    ('CLI_VALID4', 'valid_four_person', 'tests/fixtures/valid_four_person.json'),
    ('CLI_SCHEMA_INVALID', 'schema_invalid_assignment', 'tests/fixtures/schema_invalid_assignment.json'),
    ('CLI_MALFORMED', 'malformed.json', 'tests/fixtures/malformed.json'),
    ('CLI_INVALID_UTF8', 'invalid_utf8.bin', 'tests/fixtures/invalid_utf8.bin'),
    ('CLI_DUP_KEY', 'duplicate_json_key.json', 'tests/fixtures/duplicate_json_key.json'),
    ('CLI_MISSING', 'does_not_exist', 'tests/fixtures/does_not_exist'),
    ('CLI_MISSING_JSON', 'does_not_exist.json (regression-suite spelling)',
     'tests/fixtures/does_not_exist.json'),
]:
    COMMANDS.append(dict(id=cid, label=label, cmd=CLI_BASE + [arg], cwd=str(V21)))

# Determinism: same state file, two different cwds.
det_cwds = [str(V21), tempfile.gettempdir()]
det_runs = []
for i, cwd in enumerate(det_cwds):
    cmd = CLI_BASE + ['state/current_assignment_state.json']
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', env=ENV)
    det_runs.append(dict(index=i, cwd=cwd, cmd=cmd, exit_code=p.returncode,
                         stdout=p.stdout, stderr=p.stderr,
                         stdout_tail='\n'.join(p.stdout.splitlines()[-30:]),
                         stderr_tail='\n'.join(p.stderr.splitlines()[-30:])))

runs = []
for spec in COMMANDS:
    started = datetime.now(timezone.utc).isoformat()
    p = subprocess.run(spec['cmd'], cwd=spec['cwd'], capture_output=True,
                       text=True, encoding='utf-8', errors='replace', env=ENV)
    runs.append({
        'id': spec['id'], 'label': spec['label'],
        'command': ' '.join(spec['cmd']), 'argv': spec['cmd'], 'cwd': spec['cwd'],
        'env_PYTHONDONTWRITEBYTECODE': '1',
        'started_utc': started,
        'exit_code': p.returncode,
        'stdout': p.stdout,
        'stderr': p.stderr,
        'stdout_tail': '\n'.join(p.stdout.splitlines()[-40:]),
        'stderr_tail': '\n'.join(p.stderr.splitlines()[-40:]),
        'note': spec.get('note', ''),
    })

post = state_snapshot()
state_after = sha(V21 / 'state' / 'current_assignment_state.json')
BASELINE_DATA = json.loads(BASELINE.read_text(encoding='utf-8'))


def diff_snapshot(pre_snap, post_snap):
    out = {}
    for k in ROOTS:
        a, b = pre_snap['roots'][k]['files'], post_snap['roots'][k]['files']
        changed = sorted(set([f for f in a if f not in b or a[f] != b[f]] +
                             [f for f in b if f not in a]))
        out[k] = {'changed': changed, 'pre_count': len(a), 'post_count': len(b)}
    out['repository_head_changed'] = (
        pre_snap['repository']['head'] != post_snap['repository']['head'])
    out['repository_status_changed'] = (
        pre_snap['repository']['status'] != post_snap['repository']['status'])
    out['repo_status_pre'] = pre_snap['repository']['status']
    out['repo_status_post'] = post_snap['repository']['status']
    return out


def diff_baseline(base, snap):
    out = {}
    for k in ROOTS:
        a = base[k]['files']
        b = snap['roots'][k]['files']
        changed = sorted(set([f for f in a if f not in b or a[f] != b[f]] +
                             [f for f in b if f not in a]))
        out[k] = {'changed': changed, 'baseline_count': len(a), 'current_count': len(b)}
    out['repository_head_match'] = base['repository']['head'] == snap['repository']['head']
    out['repository_status_match'] = base['repository']['status'] == snap['repository']['status']
    return out

payload = {
    'captured_utc': datetime.now(timezone.utc).isoformat(),
    'python_version': sys.version,
    'python_executable': sys.executable,
    'disposable_root': str(DISP),
    'commands': runs,
    'determinism': {
        'runs': det_runs,
        'stdout_equal': det_runs[0]['stdout'] == det_runs[1]['stdout'],
        'stderr_equal': det_runs[0]['stderr'] == det_runs[1]['stderr'],
        'exit_equal': det_runs[0]['exit_code'] == det_runs[1]['exit_code'],
    },
    'integrity': {
        'v21_state_sha_before': state_before,
        'v21_state_sha_after': state_after,
        'v21_state_identical': state_before == state_after,
        'pre_vs_post': diff_snapshot(pre, post),
        'baseline_vs_final': diff_baseline(BASELINE_DATA, post),
    },
}
RAW.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
print('WROTE', RAW)
for r in runs:
    print(r['id'], 'exit=', r['exit_code'], 'stdout_len=', len(r['stdout']),
          'stderr_len=', len(r['stderr']))
print('STATE_IDENTICAL', payload['integrity']['v21_state_identical'])
