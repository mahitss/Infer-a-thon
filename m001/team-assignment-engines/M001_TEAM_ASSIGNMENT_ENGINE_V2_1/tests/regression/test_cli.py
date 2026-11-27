import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = ROOT / 'cli' / 'validate.py'
F = ROOT / 'tests' / 'fixtures'

def run(state, cwd=ROOT, *extra):
    return subprocess.run([sys.executable, str(CLI_PATH), '--state', str(state), *extra],
                          cwd=cwd, capture_output=True, text=True)

class CLI(unittest.TestCase):
    def test_valid_four_exit_zero(self):
        p = run(F / 'valid_four_person.json')
        self.assertEqual(p.returncode, 0)
        self.assertIn('Stage B role readiness: YES', p.stdout)
        self.assertNotIn('Recruitment authorized: YES', p.stdout)

    def test_current_exit_one(self):
        p = run(ROOT / 'state' / 'current_assignment_state.json')
        self.assertEqual(p.returncode, 1)
        self.assertIn('Stage B role readiness: NO', p.stdout)
        self.assertIn('E-APPOINTMENT-MISSING', p.stdout)

    def test_safe_input_errors_no_traceback(self):
        cases = [(F/'malformed.json','E-JSON-INVALID'),
                 (F/'invalid_utf8.bin','E-ENCODING-INVALID'),
                 (F/'duplicate_json_key.json','E-DUPLICATE-JSON-KEY'),
                 (F/'does_not_exist.json','E-FILE-NOT-FOUND')]
        for path, code in cases:
            with self.subTest(code=code):
                p = run(path)
                self.assertEqual(p.returncode, 2)
                self.assertIn(code, p.stdout)
                self.assertNotIn('Traceback', p.stderr)

    def test_json_only_machine_readable(self):
        p = run(F/'valid_four_person.json', ROOT, '--json-only')
        self.assertEqual(p.returncode, 0)
        data = json.loads(p.stdout)
        self.assertTrue(data['stage_b_role_ready'])
        self.assertEqual(data['blocking_error_count'], 0)

    def test_determinism_two_directories(self):
        a = run(ROOT/'state'/'current_assignment_state.json', ROOT)
        b = run(ROOT/'state'/'current_assignment_state.json', tempfile.gettempdir())
        self.assertEqual(a.stdout, b.stdout)
        self.assertEqual(a.stderr, b.stderr)
        self.assertEqual(a.returncode, b.returncode)

if __name__ == '__main__': unittest.main()
