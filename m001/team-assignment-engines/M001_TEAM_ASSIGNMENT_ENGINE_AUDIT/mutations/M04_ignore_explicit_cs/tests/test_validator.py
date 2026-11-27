import copy
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.validator import (  # noqa: E402
    load_json, load_policy, load_schema, validate_schema, validate_state
)

FIX = ROOT / 'fixtures'


def fixture(name):
    return load_json(FIX / name)


def codes(result, severity=None):
    return [i.code for i in result.issues if severity is None or i.severity == severity]


class SchemaTests(unittest.TestCase):
    def test_current_state_conforms_to_schema(self):
        errors = validate_schema(fixture('ro_accepted_others_unassigned.json'), load_schema())
        self.assertEqual(errors, [])

    def test_missing_required_section_rejected(self):
        bad = fixture('valid_four_person.json')
        del bad['roles']
        errors = validate_schema(bad, load_schema())
        self.assertTrue(any('missing required field roles' in e for e in errors))


class CurrentStateTests(unittest.TestCase):
    def test_current_state_missing_appointments(self):
        result = validate_state(fixture('ro_accepted_others_unassigned.json'), load_policy(), load_schema())
        missing = [i for i in result.errors if i.code == 'E-APPOINTMENT-MISSING']
        self.assertEqual(len(missing), 5)
        self.assertEqual(sorted(i.role for i in missing), sorted([
            'MODERATOR', 'NOTE_TAKER', 'DATA_CUSTODIAN', 'ANALYST', 'CONTINUE_STOP_OWNER']))

    def test_research_owner_not_promoted(self):
        result = validate_state(fixture('ro_accepted_others_unassigned.json'), load_policy(), load_schema())
        self.assertIn('I-RO-NOT-FORMAL', codes(result, 'INFO'))
        self.assertNotIn('E-STATE-INVALID', codes(result))
        state = fixture('ro_accepted_others_unassigned.json')
        self.assertEqual(state['roles']['RESEARCH_OWNER']['state'], 'ACCEPTED_IN_CONVERSATION')
        self.assertFalse(state['roles']['RESEARCH_OWNER']['approval']['formal'])

    def test_topology_warning(self):
        result = validate_state(fixture('ro_accepted_others_unassigned.json'), load_policy(), load_schema())
        self.assertIn('W-TOPOLOGY-PROPOSED', codes(result, 'WARNING'))


class StaffingModelTests(unittest.TestCase):
    def test_valid_models_have_no_blocking_errors(self):
        for name in ('valid_four_person.json', 'valid_five_person.json', 'valid_six_person.json'):
            with self.subTest(name=name):
                result = validate_state(fixture(name), load_policy(), load_schema())
                self.assertEqual(result.errors, [])

    def test_invalid_three_person_has_hard_incompatibility(self):
        result = validate_state(fixture('invalid_three_person.json'), load_policy(), load_schema())
        self.assertIn('E-HARD-MODERATOR-ANALYST', codes(result, 'ERROR'))

    def test_hard_incompatibilities(self):
        cases = {
            'hard_moderator_analyst.json': 'E-HARD-MODERATOR-ANALYST',
            'hard_moderator_custodian.json': 'E-HARD-MODERATOR-CUSTODIAN'
        }
        for name, code in cases.items():
            with self.subTest(name=name):
                result = validate_state(fixture(name), load_policy(), load_schema())
                self.assertIn(code, codes(result, 'ERROR'))

    def test_discouraged_combinations_are_warnings(self):
        cases = {
            'discouraged_ro_moderator.json': 'W-DISCOURAGED-RO-MODERATOR',
            'discouraged_custodian_analyst.json': 'W-DISCOURAGED-CUSTODIAN-ANALYST'
        }
        for name, code in cases.items():
            with self.subTest(name=name):
                result = validate_state(fixture(name), load_policy(), load_schema())
                self.assertIn(code, codes(result, 'WARNING'))
                self.assertNotIn(code.replace('W-', 'E-'), codes(result, 'ERROR'))

    def test_conditional_evidence(self):
        cases = {
            'missing_evidence_separation.json': 'E-COND-EVIDENCE-SEPARATION',
            'missing_explicit_cs.json': 'E-COND-EXPLICIT-CS'
        }
        for name, code in cases.items():
            with self.subTest(name=name):
                result = validate_state(fixture(name), load_policy(), load_schema())
                self.assertIn(code, codes(result, 'ERROR'))


class CompletenessTests(unittest.TestCase):
    def test_missing_candidate_acceptance(self):
        result = validate_state(fixture('missing_candidate_acceptance.json'), load_policy(), load_schema())
        self.assertIn('E-CANDIDATE-ACCEPTANCE', codes(result, 'ERROR'))

    def test_missing_product_owner_approval(self):
        result = validate_state(fixture('missing_po_approval.json'), load_policy(), load_schema())
        self.assertIn('E-PO-APPROVAL', codes(result, 'ERROR'))

    def test_missing_onboarding(self):
        result = validate_state(fixture('missing_onboarding.json'), load_policy(), load_schema())
        self.assertIn('E-ONBOARDING', codes(result, 'ERROR'))

    def test_other_state_requirements(self):
        checks = [
            ('availability', 'E-AVAILABILITY', lambda r: r['availability'].update({'confirmed': False})),
            ('conflict', 'E-CONFLICT-DISCLOSURE', lambda r: r['conflict_disclosure'].update({'provided': False})),
            ('confidentiality', 'E-CONFIDENTIALITY', lambda r: r['confidentiality'].update({'acknowledged': False})),
            ('escalation', 'E-ESCALATION-CONTACT', lambda r: r['escalation'].update({'contact': None}))
        ]
        for label, code, mutate in checks:
            with self.subTest(label=label):
                bad = fixture('valid_four_person.json')
                mutate(bad['roles']['MODERATOR'])
                result = validate_state(bad, load_policy(), load_schema())
                self.assertIn(code, codes(result, 'ERROR'))

    def test_duplicate_and_unknown_roles(self):
        dup = fixture('valid_four_person.json')
        dup['assignments'][1]['roles'].append('RESEARCH_OWNER')
        result = validate_state(dup, load_policy(), load_schema())
        self.assertIn('E-ROLE-DUPLICATE', codes(result, 'ERROR'))

        unknown = fixture('valid_four_person.json')
        unknown['assignments'][0]['roles'].append('UNKNOWN_ROLE')
        result = validate_state(unknown, load_policy(), load_schema())
        self.assertIn('E-ROLE-UNKNOWN', codes(result, 'ERROR'))


class DeterminismTests(unittest.TestCase):
    def test_repeated_validation_identical(self):
        state = fixture('deterministic_state.json')
        a = validate_state(state, load_policy(), load_schema()).to_dict()
        b = validate_state(copy.deepcopy(state), load_policy(), load_schema()).to_dict()
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
