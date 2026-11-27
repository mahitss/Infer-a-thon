import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'cli' / 'validate.py'
SCHEMA_CLI = ROOT / 'cli' / 'validate_schema.py'


def run_cli(state, cwd, *extra):
    return subprocess.run(
        [sys.executable, str(CLI), '--state', str(ROOT / state), *extra],
        cwd=cwd, capture_output=True, text=True
    )


class IntegrationTests(unittest.TestCase):
    def test_current_state_cli_nonzero_and_deterministic_across_cwds(self):
        a = run_cli('state/current_assignment_state.json', ROOT)
        b = run_cli('state/current_assignment_state.json', tempfile.gettempdir())
        self.assertEqual(a.returncode, 1)
        self.assertEqual(b.returncode, 1)
        self.assertEqual(a.stdout, b.stdout)
        self.assertEqual(a.stderr, b.stderr)
        self.assertIn('Blocking errors: 5', a.stdout)
        self.assertIn('E-APPOINTMENT-MISSING', a.stdout)

    def test_valid_four_person_cli_exit_zero(self):
        p = run_cli('fixtures/valid_four_person.json', ROOT)
        self.assertEqual(p.returncode, 0)
        self.assertIn('Valid: YES', p.stdout)
        self.assertIn('Blocking errors: 0', p.stdout)

    def test_json_result_is_machine_readable(self):
        out = ROOT / 'reports' / 'test_result.json'
        p = run_cli('fixtures/valid_four_person.json', ROOT, '--json-out', str(out), '--json-only')
        self.assertEqual(p.returncode, 0)
        data = json.loads(p.stdout)
        self.assertTrue(data['valid'])
        self.assertEqual(data['blocking_error_count'], 0)
        self.assertTrue(out.exists())

    def test_schema_cli_accepts_all_fixtures(self):
        fixtures = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'fixtures').glob('*.json'))
        args = [sys.executable, str(SCHEMA_CLI)]
        for fixture in fixtures:
            args.extend(['--state', fixture])
        p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(p.stdout.count('PASS'), len(fixtures))


if __name__ == '__main__':
    unittest.main()
