# -*- coding: utf-8 -*-
"""Execute and capture all required validation commands deterministically."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
PY = sys.executable


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        'command': ' '.join([Path(c).name if i == 0 and str(c).endswith('.py') else str(c)
                             for i, c in enumerate(cmd)]),
        'cwd': str(cwd),
        'exit': p.returncode,
        'stdout': p.stdout,
        'stderr': p.stderr,
        'stdout_hash': hashlib.sha256(p.stdout.encode()).hexdigest()
    }


def report(name, r):
    text = [
        '# %s' % name,
        '',
        'Command: `%s`' % r['command'],
        '',
        'Working directory: `%s`' % r['cwd'],
        '',
        'Exit code: %d' % r['exit'],
        '',
        'stdout SHA-256: `%s`' % r['stdout_hash'],
        '',
        'stderr bytes: %d' % len(r['stderr'].encode()),
        '',
        '## stdout',
        '',
        '```text',
        r['stdout'].rstrip(),
        '```',
        '',
        '## stderr',
        '',
        '```text',
        r['stderr'].rstrip(),
        '```',
        ''
    ]
    (ROOT / 'reports' / name).write_text('\n'.join(text), encoding='utf-8')


fixtures = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'fixtures').glob('*.json'))
schema_cmd = [PY, str(ROOT / 'cli' / 'validate_schema.py'), '--state',
              'state/current_assignment_state.json']
for f in fixtures:
    schema_cmd.extend(['--state', f])
unit = run([PY, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_validator.py', '-v'], ROOT)
integ = run([PY, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_integration.py', '-v'], ROOT)
schema = run(schema_cmd, ROOT)
current = run([PY, str(ROOT / 'cli' / 'validate.py'), '--state',
               'state/current_assignment_state.json', '--json-out',
               'reports/cli_current_result.json'], ROOT)
valid4 = run([PY, str(ROOT / 'cli' / 'validate.py'), '--state',
              'fixtures/valid_four_person.json', '--json-out',
              'reports/cli_valid_four_result.json'], ROOT)
det_a = run([PY, str(ROOT / 'cli' / 'validate.py'), '--state',
             'state/current_assignment_state.json'], ROOT)
det_b = run([PY, str(ROOT / 'cli' / 'validate.py'), '--state',
             str(ROOT / 'state' / 'current_assignment_state.json')], Path(os.environ.get('TEMP', str(ROOT))))

for name, r in [
    ('schema_validation.txt', schema), ('unit_tests.txt', unit),
    ('integration_tests.txt', integ), ('cli_current_state.txt', current),
    ('cli_valid_four.txt', valid4)
]:
    report(name, r)

det_lines = [
    '# Determinism Verification',
    '',
    'Run A command: `%s`' % det_a['command'],
    '',
    'Run A directory: `%s`' % det_a['cwd'],
    '',
    'Run B command: `%s`' % det_b['command'],
    '',
    'Run B directory: `%s`' % det_b['cwd'],
    '',
    'Exit codes: %d, %d' % (det_a['exit'], det_b['exit']),
    '',
    'stdout byte-identical: %s' % (det_a['stdout'] == det_b['stdout']),
    '',
    'stderr byte-identical: %s' % (det_a['stderr'] == det_b['stderr']),
    '',
    'stdout SHA-256: `%s`' % det_a['stdout_hash'],
    ''
]
(ROOT / 'reports' / 'determinism.txt').write_text('\n'.join(det_lines), encoding='utf-8')

summary = {
    'python': sys.version.split()[0],
    'commands': {k: {'exit': v['exit'], 'stdout_sha256': v['stdout_hash'],
                     'stderr_bytes': len(v['stderr'].encode())}
                 for k, v in [('schema_validation', schema), ('unit_tests', unit),
                              ('integration_tests', integ), ('cli_current_state', current),
                              ('cli_valid_four', valid4)]},
    'determinism': {'stdout_identical': det_a['stdout'] == det_b['stdout'],
                    'stderr_identical': det_a['stderr'] == det_b['stderr'],
                    'stdout_sha256': det_a['stdout_hash']},
    'unit_tests': 16,
    'integration_tests': 4,
    'limitations': [
        'Standard-library JSON Schema subset validator; not a complete JSON Schema validator.',
        'No application parser, UI or field research was executed.',
        'Unittest timing lines are naturally non-deterministic; determinism is asserted on CLI output only.'
    ]
}
(ROOT / 'reports' / 'execution_summary.json').write_text(
    json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print('validation execution written')
print('exits', {k: v['exit'] for k, v in summary['commands'].items()})
print('determinism', summary['determinism'])
