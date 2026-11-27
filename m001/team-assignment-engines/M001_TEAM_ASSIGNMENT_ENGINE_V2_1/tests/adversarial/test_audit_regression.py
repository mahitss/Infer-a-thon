import sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engine.validator import (  # noqa: E402
    DuplicateKeyError, load_json_strict, load_policy, load_schema, validate_state
)
F = ROOT / 'tests' / 'fixtures'
POLICY = load_policy(); SCHEMA = load_schema()

def load(name): return load_json_strict(F / name)
def v(name): return validate_state(load(name), POLICY, SCHEMA)
def codes(r, sev='ERROR'): return [i.code for i in r.issues if i.severity == sev]

class AuditRegression(unittest.TestCase):
    def test_adv01_hard_moderator_analyst(self):
        # Derived from valid four by creating an approved hard conflict in memory.
        s = load('valid_four_person.json')
        s['roles']['MODERATOR']['candidate_ref'] = 'C-P4'
        s['appointments'] = [a for a in s['appointments'] if a['role'] != 'MODERATOR']
        s['appointments'].append({'candidate_ref':'C-P4','role':'MODERATOR','state':'FORMALLY_APPOINTED'})
        r = validate_state(s, POLICY, SCHEMA)
        self.assertIn('E-HARD-MODERATOR-ANALYST', codes(r))

    def test_adv02_hard_moderator_custodian(self):
        s = load('valid_four_person.json')
        s['roles']['MODERATOR']['candidate_ref'] = 'C-P3'
        s['appointments'] = [a for a in s['appointments'] if a['role'] != 'MODERATOR']
        s['appointments'].append({'candidate_ref':'C-P3','role':'MODERATOR','state':'FORMALLY_APPOINTED'})
        r = validate_state(s, POLICY, SCHEMA)
        self.assertIn('E-HARD-MODERATOR-CUSTODIAN', codes(r))

    def test_adv03_discouraged_ro_moderator(self):
        r = v('discouraged_no_review.json')
        self.assertIn('E-DISCOURAGED-RO-MODERATOR', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_adv04_discouraged_custodian_analyst(self):
        s = load('valid_four_person.json')
        s['roles']['DATA_CUSTODIAN']['candidate_ref'] = 'C-P4'
        s['appointments'] = [a for a in s['appointments'] if a['role'] != 'DATA_CUSTODIAN']
        s['appointments'].append({'candidate_ref':'C-P4','role':'DATA_CUSTODIAN','state':'FORMALLY_APPOINTED'})
        r = validate_state(s, POLICY, SCHEMA)
        self.assertIn('E-DISCOURAGED-CUSTODIAN-ANALYST', codes(r))

    def test_adv05_boolean_evidence_without_reference(self):
        r = v('boolean_evidence_without_ref.json')
        self.assertTrue(any(c.startswith('E-EVIDENCE-MISSING') for c in codes(r)))

    def test_adv06_forged_evidence_reference(self):
        r = v('forged_evidence_id.json')
        self.assertIn('E-EVIDENCE-UNKNOWN', codes(r))

    def test_adv07_duplicate_candidate_identity(self):
        r = v('duplicate_candidate_identity.json')
        self.assertIn('E-CANDIDATE-DUPLICATE', codes(r))

    def test_adv08_unknown_candidate_identity(self):
        r = v('unknown_candidate_identity.json')
        self.assertIn('E-CANDIDATE-UNKNOWN', codes(r))

    def test_adv09_proposed_not_appointed(self):
        r = v('proposed_treated_as_appointed.json')
        self.assertIn('E-APPOINTMENT-MISSING', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_adv10_accepted_conversation_not_formal(self):
        r = v('accepted_conversation_formal.json')
        self.assertIn('E-APPOINTMENT-MISSING', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_adv11_formal_state_formal_false(self):
        r = v('formal_missing_formal_approval.json')
        self.assertIn('E-FORMAL-APPROVAL-MISMATCH', codes(r))

    def test_adv12_empty_approval_basis(self):
        r = v('empty_approval_basis.json')
        self.assertIn('E-DECISION-EVIDENCE-EMPTY', codes(r))

    def test_adv13_discouraged_without_review(self):
        r = v('discouraged_no_review.json')
        self.assertIn('E-DISCOURAGED-RO-MODERATOR', codes(r))

    def test_adv14_missing_timestamps(self):
        r = v('missing_timestamps.json')
        self.assertIn('E-TIMESTAMP-MISSING', codes(r))

    def test_adv15_duplicate_json_keys(self):
        with self.assertRaises(DuplicateKeyError):
            load('duplicate_json_key.json')

    def test_adv16_topology_unapproved_blocks_stage_b(self):
        r = v('topology_unapproved_stage_b.json')
        self.assertIn('E-TOPOLOGY-UNAPPROVED', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_adv17_rejected_candidate_not_active(self):
        r = v('rejected_active_appointment.json')
        self.assertTrue('E-UNAPPROVED-APPOINTMENT' in codes(r) or 'E-APPOINTMENT-MISSING' in codes(r))

    def test_adv18_missing_onboarding(self):
        r = v('missing_onboarding.json')
        self.assertIn('E-ONBOARDING', codes(r))

    def test_adv19_malformed_json(self):
        with self.assertRaises(ValueError) as cm:
            load('malformed.json')
        self.assertIn('E-JSON-INVALID', str(cm.exception))

    def test_adv20_invalid_utf8(self):
        with self.assertRaises(ValueError) as cm:
            load('invalid_utf8.bin')
        self.assertIn('E-ENCODING-INVALID', str(cm.exception))

    def test_adv21_missing_file(self):
        with self.assertRaises(ValueError) as cm:
            load_json_strict(F / 'does_not_exist.json')
        self.assertIn('E-FILE-NOT-FOUND', str(cm.exception))

    def test_adv22_no_authorization_inference(self):
        r = v('recruitment_inferred.json')
        self.assertTrue({'E-AUTHORIZATION-STATE', 'E-SCHEMA'}.intersection(codes(r)))
        self.assertFalse(r.recruitment_authorized)
        self.assertFalse(r.field_validation_authorized)

    def test_adv23_different_combination_approval(self):
        r = v('approval_different_combination.json')
        self.assertTrue(any(c.startswith('E-COMBINATION-APPROVAL-MISSING') for c in codes(r)))

    def test_adv24_deterministic(self):
        a = v('valid_four_person.json').to_dict()
        b = v('valid_four_person.json').to_dict()
        self.assertEqual(a, b)

if __name__ == '__main__': unittest.main()
