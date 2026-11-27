#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Capture every V2.1 verification command with stdout/stderr/exit code."""
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / 'reports'
LOGS = REPORTS / 'logs'
LOGS.mkdir(parents=True, exist_ok=True)
PY = sys.executable

RUNS = [
    ('adversarial_24', [PY, '-m', 'unittest', 'discover', '-s', 'tests/adversarial', '-p', 'test_*.py', '-v']),
    ('regression_53', [PY, '-m', 'unittest', 'discover', '-s', 'tests/regression', '-p', 'test_*.py', '-v']),
    ('independent_50', [PY, 'tests/independent/independent_adversarial_v21.py']),
    ('refined', [PY, 'tests/independent/refined_cases_v21.py']),
    ('canary', [PY, 'tests/mutation/canary_v21.py', '--root', '.']),
    ('mutation', [PY, 'tests/mutation/mutation_harness_v21.py']),
    ('cli_current', [PY, 'cli/validate.py', '--state', 'state/current_assignment_state.json']),
    ('cli_valid_four', [PY, 'cli/validate.py', '--state', 'tests/fixtures/valid_four_person.json']),
    ('cli_schema_failure', [PY, 'cli/validate.py', '--state', 'tests/fixtures/schema_invalid_assignment.json']),
    ('cli_malformed', [PY, 'cli/validate.py', '--state', 'tests/fixtures/malformed.json']),
    ('cli_bad_utf8', [PY, 'cli/validate.py', '--state', 'tests/fixtures/invalid_utf8.bin']),
    ('cli_dup_key', [PY, 'cli/validate.py', '--state', 'tests/fixtures/duplicate_json_key.json']),
    ('cli_no_file', [PY, 'cli/validate.py', '--state', 'tests/fixtures/does_not_exist.json']),
]

results = {}
for name, cmd in RUNS:
    cp = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                        encoding='utf-8', errors='replace')
    results[name] = {'command': ' '.join(cmd), 'exit_code': cp.returncode,
                     'stdout': cp.stdout, 'stderr': cp.stderr}
    (LOGS / (name + '.txt')).write_text(
        'COMMAND: %s\nEXIT: %s\n--- STDOUT ---\n%s\n--- STDERR ---\n%s\n' %
        (' '.join(cmd), cp.returncode, cp.stdout, cp.stderr), encoding='utf-8')


def run_current(cwd):
    return subprocess.run([PY, str(ROOT / 'cli' / 'validate.py'), '--state',
                           str(ROOT / 'state' / 'current_assignment_state.json')],
                          cwd=str(cwd), capture_output=True, text=True,
                          encoding='utf-8', errors='replace')
a, b = run_current(ROOT), run_current(Path(tempfile.gettempdir()))
results['determinism'] = {
    'command': 'current-state CLI from workspace root vs system temp cwd',
    'exit_codes': [a.returncode, b.returncode],
    'pass': a.stdout == b.stdout and a.stderr == b.stderr and a.returncode == b.returncode,
}
(REPORTS / 'verification_runs.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
print('VERIFICATION SUMMARY')
for name, r in results.items():
    print('%-20s %s' % (name, r['pass'] if name == 'determinism' else r['exit_code']))
