import copy, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engine.validator import load_json_strict, load_policy, load_schema, validate_state  # noqa: E402
F = ROOT / 'tests' / 'fixtures'
P = load_policy(); S = load_schema()

def v(name): return validate_state(load_json_strict(F / name), P, S)
def load(name): return load_json_strict(F / name)
def codes(r): return [i.code for i in r.issues]

class Regression(unittest.TestCase):
    def test_valid_four_five_six_stage_b_ready(self):
        for name in ('valid_four_person.json','valid_five_person.json','valid_six_person.json'):
            with self.subTest(name=name):
                r = v(name)
                self.assertTrue(r.stage_b_role_ready)
                self.assertEqual(r.errors, [])
                self.assertTrue(r.recruitment_authorized is False)
                self.assertTrue(r.field_validation_authorized is False)

    def test_current_state_remains_blocked(self):
        r = v('current_assignment_state.json')
        self.assertFalse(r.stage_b_role_ready)
        self.assertEqual(len([i for i in r.errors if i.code=='E-APPOINTMENT-MISSING']), 6)
        self.assertEqual(r.dimensions['role_compatibility'], 'PASS')

    def test_hard_incompatibility_not_overridable(self):
        r = v('hard_incompatibility_approved.json')
        self.assertIn('E-HARD-MODERATOR-ANALYST', codes(r))
        self.assertFalse(r.stage_b_role_ready)

    def test_discouraged_with_exact_approval_passes(self):
        s = load('discouraged_no_review.json')
        cand = 'C-P1'; roles = sorted(['RESEARCH_OWNER','MODERATOR']); key='+'.join(roles)
        ev='e-combo-review-allowed'
        from hashlib import sha256
        s['evidence'][ev]={'evidence_id':ev,'evidence_type':'COMBINATION_REVIEW',
            'source_ref':'synthetic://allowed','content_hash':sha256(ev.encode()).hexdigest(),
            'recording_authority':'SYNTHETIC_TEST_DATA','timestamp':'2026-11-27T01:00:00+00:00',
            'verification_status':'VERIFIED','subject':cand+':'+key}
        s['combination_approvals'].append({'candidate_ref':cand,'roles':roles,'outcome':'APPROVED',
            'rationale':'SYNTHETIC_TEST_DATA documented PO review',
            'evidence_id':ev,'product_owner_approved':True,
            'decision_timestamp':'2026-11-27T01:00:00+00:00'})
        r = validate_state(s, P, S)
        self.assertNotIn('E-DISCOURAGED-RO-MODERATOR', codes(r))
        self.assertTrue(r.stage_b_role_ready)

    def test_naive_timestamp_rejected(self):
        s = load('valid_four_person.json')
        s['roles']['ANALYST']['formal']['formal_appointed_at'] = '2026-11-27T02:00:00'
        r = validate_state(s, P, S)
        self.assertIn('E-TIMESTAMP-MISSING', codes(r))

    def test_separate_dimensions_present(self):
        r = v('valid_four_person.json').to_dict()
        expected = {'structural_topology_validity','role_assignment_completeness',
                    'human_candidate_acceptance','formal_appointment_validity',
                    'product_owner_combination_approval','evidence_integrity',
                    'role_compatibility','onboarding_readiness'}
        self.assertTrue(expected.issubset(set(r['dimensions'])))
        self.assertFalse(r['recruitment_authorized'])
        self.assertFalse(r['field_validation_authorized'])

if __name__ == '__main__': unittest.main()
