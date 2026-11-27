"""The 20 explicit remediation scenarios required by M001-TEAM-004.

All candidate data referenced here is SYNTHETIC_TEST_DATA and is confined to
tests/fixtures. The real state file is never modified.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engine.validator import (  # noqa: E402
    DuplicateKeyError, load_json_strict, load_policy, load_schema, validate_state
)

F = ROOT / 'tests' / 'fixtures'
P = load_policy()
S = load_schema()


def load(name):
    return load_json_strict(F / name)


def v(name):
    return validate_state(load(name), P, S)


def codes(result):
    return [i.code for i in result.issues]


class ExplicitScenarios(unittest.TestCase):
    def test_01_multi_role_without_po_combination_approval(self):
        r = v('multi_role_no_approval.json')
        self.assertIn('E-COMBINATION-APPROVAL-MISSING', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_02_approval_for_different_combination(self):
        r = v('approval_different_combination.json')
        self.assertIn('E-COMBINATION-APPROVAL-MISSING', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_03_proposed_treated_as_appointed(self):
        r = v('proposed_treated_as_appointed.json')
        self.assertTrue(any(i.code == 'E-APPOINTMENT-MISSING' and i.role == 'MODERATOR'
                            for i in r.issues))
        self.assertFalse(r.stage_b_role_ready)

    def test_04_accepted_conversation_not_formal(self):
        r = v('accepted_conversation_formal.json')
        self.assertTrue(any(i.code == 'E-APPOINTMENT-MISSING' and i.role == 'MODERATOR'
                            for i in r.issues))
        self.assertFalse(r.stage_b_role_ready)

    def test_05_boolean_evidence_without_reference(self):
        r = v('boolean_evidence_without_ref.json')
        self.assertTrue(any(c.startswith('E-EVIDENCE-MISSING') for c in codes(r)))

    def test_06_forged_evidence_identifier(self):
        r = v('forged_evidence_id.json')
        self.assertIn('E-EVIDENCE-UNKNOWN', codes(r))

    def test_07_duplicate_candidate_identities(self):
        r = v('duplicate_candidate_identity.json')
        self.assertIn('E-CANDIDATE-DUPLICATE', codes(r))

    def test_08_unknown_candidate_identity(self):
        r = v('unknown_candidate_identity.json')
        self.assertIn('E-CANDIDATE-UNKNOWN', codes(r))

    def test_09_formally_appointed_with_missing_formal_approval(self):
        r1 = v('po_approval_missing.json')
        self.assertIn('E-PO-APPROVAL', codes(r1))
        r2 = v('formal_missing_formal_approval.json')
        self.assertIn('E-FORMAL-APPROVAL-MISMATCH', codes(r2))

    def test_10_empty_approval_basis(self):
        r = v('empty_approval_basis.json')
        self.assertIn('E-DECISION-EVIDENCE-EMPTY', codes(r))

    def test_11_discouraged_combination_without_po_review(self):
        r = v('discouraged_no_review.json')
        self.assertIn('E-DISCOURAGED-RO-MODERATOR', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_12_missing_timestamps(self):
        r = v('missing_timestamps.json')
        self.assertIn('E-TIMESTAMP-MISSING', codes(r))

    def test_13_duplicate_json_keys(self):
        with self.assertRaises(DuplicateKeyError):
            load('duplicate_json_key.json')

    def test_14_unapproved_topology_not_stage_b_ready(self):
        r = v('topology_unapproved_stage_b.json')
        self.assertIn('E-TOPOLOGY-UNAPPROVED', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_15_rejected_candidate_not_active(self):
        r = v('rejected_active_appointment.json')
        self.assertTrue('E-UNAPPROVED-APPOINTMENT' in codes(r) or
                        'E-APPOINTMENT-MISSING' in codes(r))

    def test_16_missing_onboarding(self):
        r = v('missing_onboarding.json')
        self.assertIn('E-ONBOARDING', codes(r))

    def test_17_malformed_json(self):
        with self.assertRaises(ValueError) as cm:
            load('malformed.json')
        self.assertIn('E-JSON-INVALID', str(cm.exception))

    def test_18_invalid_utf8(self):
        with self.assertRaises(ValueError) as cm:
            load('invalid_utf8.bin')
        self.assertIn('E-ENCODING-INVALID', str(cm.exception))

    def test_19_missing_state_file(self):
        with self.assertRaises(ValueError) as cm:
            load_json_strict(F / 'does_not_exist.json')
        self.assertIn('E-FILE-NOT-FOUND', str(cm.exception))

    def test_20_no_authorization_from_passing_topology(self):
        r1 = v('recruitment_inferred.json')
        self.assertIn('E-AUTHORIZATION-STATE', codes(r1))
        self.assertFalse(r1.recruitment_authorized)
        self.assertFalse(r1.field_validation_authorized)
        r2 = v('valid_four_person.json')
        self.assertTrue(r2.stage_b_role_ready)
        self.assertFalse(r2.recruitment_authorized)
        self.assertFalse(r2.field_validation_authorized)


if __name__ == '__main__':
    unittest.main()
