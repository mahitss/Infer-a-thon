#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run every V2 verification command and capture deterministic evidence.

Produces reports/verification_runs.json and reports/logs/<step>.txt.
This script never mutates engine, policy, schema, or state artifacts.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / 'reports'
LOGS = REPORTS / 'logs'
LOGS.mkdir(parents=True, exist_ok=True)
PY = sys.executable

RUNS = [
    ('adversarial',    [PY, '-m', 'unittest', 'discover', '-s', 'tests/adversarial', '-p', 'test_*.py', '-v'], ROOT),
    ('regression',     [PY, '-m', 'unittest', 'discover', '-s', 'tests/regression',  '-p', 'test_*.py', '-v'], ROOT),
    ('cli_current',    [PY, 'cli/validate.py', '--state', 'state/current_assignment_state.json'], ROOT),
    ('cli_valid_four', [PY, 'cli/validate.py', '--state', 'tests/fixtures/valid_four_person.json'], ROOT),
    ('cli_malformed',  [PY, 'cli/validate.py', '--state', 'tests/fixtures/malformed.json'], ROOT),
    ('cli_bad_utf8',   [PY, 'cli/validate.py', '--state', 'tests/fixtures/invalid_utf8.bin'], ROOT),
    ('cli_dup_key',    [PY, 'cli/validate.py', '--state', 'tests/fixtures/duplicate_json_key.json'], ROOT),
    ('cli_no_file',    [PY, 'cli/validate.py', '--state', 'tests/fixtures/does_not_exist.json'], ROOT),
    ('cli_recruit',    [PY, 'cli/validate.py', '--state', 'tests/fixtures/recruitment_inferred.json'], ROOT),
    ('canary',         [PY, 'tests/mutation/mutation_canary.py', '--root', '.'], ROOT),
    ('mutation',       [PY, 'tests/mutation/mutation_harness.py'], ROOT),
]

results = {}
for name, cmd, cwd in RUNS:
    cp = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding='utf-8', errors='replace')
    results[name] = {
        'command': ' '.join(cmd),
        'cwd': str(cwd),
        'exit_code': cp.returncode,
        'stdout': cp.stdout,
        'stderr': cp.stderr,
    }
    (LOGS / (name + '.txt')).write_text(
        'COMMAND: %s\nCWD: %s\nEXIT: %s\n--- STDOUT ---\n%s\n--- STDERR ---\n%s\n' %
        (' '.join(cmd), cwd, cp.returncode, cp.stdout, cp.stderr), encoding='utf-8')

# Determinism: same state from two different working directories.
def run_current(cwd):
    return subprocess.run([PY, str(ROOT/'cli'/'validate.py'), '--state',
                           str(ROOT/'state'/'current_assignment_state.json')],
                          cwd=str(cwd), capture_output=True, text=True,
                          encoding='utf-8', errors='replace')
a = run_current(ROOT)
b = run_current(Path(tempfile.gettempdir()))
results['determinism'] = {
    'command': 'current-state CLI from workspace root vs system temp cwd',
    'exit_codes': [a.returncode, b.returncode],
    'stdout_identical': a.stdout == b.stdout,
    'stderr_identical': a.stderr == b.stderr,
    'pass': a.stdout == b.stdout and a.stderr == b.stderr and a.returncode == b.returncode,
}

(REPORTS / 'verification_runs.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
print('VERIFICATION SUMMARY')
for name, r in results.items():
    if name == 'determinism':
        print('%-16s pass=%s' % (name, r['pass']))
    else:
        print('%-16s exit=%s' % (name, r['exit_code']))
