"""M001-TEAM-006: 22 required adversarial regressions for the four HIGH findings."""
import json, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engine.validator import (  # noqa: E402
    load_json_strict, load_policy, load_schema, structural_schema_errors, validate_state
)
F = ROOT / 'tests' / 'fixtures'
P, S = load_policy(), load_schema()
CLI = ROOT / 'cli' / 'validate.py'


def codes(r):
    return sorted(set(i.code for i in r.issues))


def v(name):
    return validate_state(load_json_strict(F / name), P, S)


class V21HighFindings(unittest.TestCase):
    def test_01_empty_approval_basis(self):
        r = v('basis_empty.json')
        self.assertIn('E-DECISION-EVIDENCE-EMPTY', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_02_ascii_whitespace_approval_basis(self):
        r = v('basis_ascii_ws.json')
        self.assertIn('E-DECISION-EVIDENCE-EMPTY', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_03_unicode_whitespace_approval_basis(self):
        r = v('basis_unicode_ws.json')
        self.assertIn('E-DECISION-EVIDENCE-EMPTY', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_04_missing_approval_basis(self):
        r = v('basis_missing.json')
        self.assertIn('E-DECISION-EVIDENCE-EMPTY', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_05_null_approval_basis(self):
        r = v('basis_null.json')
        self.assertIn('E-DECISION-EVIDENCE-EMPTY', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_06_non_string_approval_basis(self):
        r = v('basis_nonstring.json')
        self.assertTrue({'E-DECISION-EVIDENCE-EMPTY', 'E-SCHEMA'}.intersection(codes(r)))
        self.assertFalse(r.stage_b_role_ready)

    def test_07_empty_rationale(self):
        r = v('rationale_empty.json')
        self.assertIn('E-COMBINATION-RATIONALE', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_08_whitespace_only_rationale(self):
        r = v('rationale_ws.json')
        self.assertIn('E-COMBINATION-RATIONALE', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_09_unicode_whitespace_rationale(self):
        r = v('rationale_unicode_ws.json')
        self.assertIn('E-COMBINATION-RATIONALE', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_10_missing_rationale(self):
        r = v('rationale_missing.json')
        self.assertTrue({'E-COMBINATION-RATIONALE', 'E-SCHEMA'}.intersection(codes(r)))
        self.assertFalse(r.stage_b_role_ready)

    def test_11_acceptance_evidence_wrong_role(self):
        r = v('acceptance_wrong_role.json')
        self.assertTrue({'E-EVIDENCE-SUBJECT', 'E-ACCEPTANCE-ROLE', 'E-ACCEPTANCE-APPOINTMENT'}.intersection(codes(r)))
        self.assertFalse(r.stage_b_role_ready)

    def test_12_acceptance_evidence_wrong_candidate(self):
        r = v('acceptance_wrong_candidate.json')
        self.assertTrue({'E-EVIDENCE-SUBJECT', 'E-ACCEPTANCE-ROLE'}.intersection(codes(r)))
        self.assertFalse(r.stage_b_role_ready)

    def test_13_acceptance_evidence_another_appointment(self):
        r = v('acceptance_other_appointment.json')
        self.assertIn('E-ACCEPTANCE-APPOINTMENT', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_14_reused_acceptance_subject_mismatch(self):
        r = v('acceptance_subject_mismatch.json')
        self.assertTrue({'E-EVIDENCE-SUBJECT', 'E-ACCEPTANCE-DECISION-REUSED'}.intersection(codes(r)))
        self.assertFalse(r.stage_b_role_ready)

    def test_15_unverified_acceptance_evidence(self):
        r = v('acceptance_unverified.json')
        self.assertIn('E-EVIDENCE-UNVERIFIED', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_16_revoked_acceptance_evidence(self):
        r = v('acceptance_revoked.json')
        self.assertIn('E-EVIDENCE-REVOKED', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_17_missing_acceptance_evidence(self):
        r = v('acceptance_missing.json')
        self.assertIn('E-EVIDENCE-MISSING', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_18_invalid_schema_structure(self):
        schema = load_schema(F / 'invalid_schema.json')
        instance = load_json_strict(F / 'valid_four_person.json')
        errs = structural_schema_errors(instance, schema)
        self.assertTrue(any(e.startswith('E-SCHEMA-') for e in errs))
        r = validate_state(instance, P, schema)
        self.assertFalse(r.stage_b_role_ready)
        self.assertTrue(all(d == 'FAIL' for d in r.dimensions.values()))

    def test_19_unresolvable_schema_reference(self):
        schema = load_schema(F / 'unresolvable_ref_schema.json')
        instance = load_json_strict(F / 'valid_four_person.json')
        errs = structural_schema_errors(instance, schema)
        self.assertTrue(any('E-SCHEMA-REFERENCE' in e for e in errs))
        self.assertTrue(all(len(e) < 250 for e in errs))
        r = validate_state(instance, P, schema)
        self.assertFalse(r.stage_b_role_ready)

    def test_20_assignment_blocked_after_schema_failure(self):
        r = v('schema_invalid_assignment.json')
        self.assertFalse(r.stage_b_role_ready)
        self.assertIn('E-SCHEMA', codes(r))
        self.assertTrue(all(d == 'FAIL' for d in r.dimensions.values()))
        self.assertNotIn('E-APPOINTMENT-MISSING', codes(r))

    def test_21_stable_cli_errors_without_tracebacks(self):
        for name in ('schema_invalid_assignment.json', 'invalid_utf8.bin',
                     'duplicate_json_key.json', 'malformed.json', 'does_not_exist.json'):
            with self.subTest(name=name):
                p = subprocess.run([sys.executable, str(CLI), '--state', str(F / name)],
                                   cwd=str(ROOT), capture_output=True, text=True)
                self.assertIn(p.returncode, (1, 2))
                self.assertNotIn('Traceback', p.stderr)
                self.assertEqual(p.stderr, '')
                self.assertIn('Stage B role readiness: NO', p.stdout)

    def test_22_valid_matching_evidence_passes(self):
        r = v('valid_four_person.json')
        self.assertTrue(r.stage_b_role_ready)
        self.assertEqual(r.errors, [])
        self.assertEqual(r.dimensions['human_candidate_acceptance'], 'PASS')
        self.assertEqual(r.dimensions['evidence_integrity'], 'PASS')


if __name__ == '__main__':
    unittest.main()
