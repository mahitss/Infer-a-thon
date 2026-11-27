"""M001-TEAM-008: regression tests for N-04, N-08, N-11, N-12 and F-007."""
import copy, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engine.validator import load_json_strict, load_policy, load_schema, validate_state  # noqa: E402

F = ROOT / 'tests' / 'fixtures'
P, S = load_policy(), load_schema()


def v(name):
    r = validate_state(load_json_strict(F / name), P, S)
    return r, sorted(set(i.code for i in r.issues))


class V22Blockers(unittest.TestCase):
    # F-007
    def test_01_invisible_basis_chars(self):
        for tag in ('zwsp', 'lrm', 'wj', 'bom'):
            with self.subTest(tag=tag):
                r, codes = v('basis_invisible_%s.json' % tag)
                self.assertFalse(r.stage_b_role_ready)
                self.assertIn('E-DECISION-EVIDENCE-EMPTY', codes)

    def test_02_invisible_rationale_chars(self):
        for tag in ('zwsp', 'lrm', 'wj', 'bom'):
            with self.subTest(tag=tag):
                r, codes = v('rationale_invisible_%s.json' % tag)
                self.assertFalse(r.stage_b_role_ready)
                self.assertIn('E-COMBINATION-RATIONALE', codes)

    def test_03_mixed_whitespace_invisible(self):
        for name, code in (('basis_invisible_mixed.json', 'E-DECISION-EVIDENCE-EMPTY'),
                           ('rationale_invisible_mixed.json', 'E-COMBINATION-RATIONALE')):
            with self.subTest(name=name):
                r, codes = v(name)
                self.assertFalse(r.stage_b_role_ready)
                self.assertIn(code, codes)

    def test_04_ascii_and_unicode_whitespace(self):
        for name, code in (('basis_ascii_ws.json', 'E-DECISION-EVIDENCE-EMPTY'),
                           ('basis_unicode_ws.json', 'E-DECISION-EVIDENCE-EMPTY'),
                           ('rationale_ws.json', 'E-COMBINATION-RATIONALE'),
                           ('rationale_unicode_ws.json', 'E-COMBINATION-RATIONALE')):
            with self.subTest(name=name):
                r, codes = v(name)
                self.assertFalse(r.stage_b_role_ready)
                self.assertIn(code, codes)

    def test_05_meaningful_unicode_content(self):
        for tag in ('english', 'accented', 'indic', 'rtl', 'emoji_zwj'):
            for prefix, field in (('basis', 'basis'), ('rationale', 'rationale')):
                with self.subTest(tag=tag, prefix=prefix):
                    r, codes = v('%s_valid_%s.json' % (prefix, tag))
                    self.assertTrue(r.stage_b_role_ready, (tag, codes))
                    self.assertEqual(codes, [])

    def test_06_non_string_and_null(self):
        for name in ('basis_null.json', 'basis_nonstring.json', 'rationale_null.json',
                     'rationale_nonstring.json'):
            with self.subTest(name=name):
                r, codes = v(name)
                self.assertFalse(r.stage_b_role_ready)
                self.assertTrue({'E-SCHEMA', 'E-DECISION-EVIDENCE-EMPTY',
                                 'E-COMBINATION-RATIONALE'}.intersection(codes))

    def test_07_no_fabrication(self):
        state = load_json_strict(F / 'basis_invisible_zwsp.json')
        before = state['roles']['RESEARCH_OWNER']['approval']['basis']
        r = validate_state(state, P, S)
        after = state['roles']['RESEARCH_OWNER']['approval']['basis']
        self.assertEqual(before, after)
        self.assertEqual(before, '\u200b' * 6)
        self.assertFalse(r.stage_b_role_ready)

    # N-04
    def test_08_escalation_contact(self):
        for name in ('escalation_ws.json', 'escalation_invisible.json'):
            with self.subTest(name=name):
                r, codes = v(name)
                self.assertFalse(r.stage_b_role_ready)
                self.assertIn('E-ESCALATION-CONTACT', codes)

    # N-08
    def test_09_duplicate_evidence(self):
        r, codes = v('evidence_duplicate.json')
        self.assertFalse(r.stage_b_role_ready)
        self.assertIn('E-EVIDENCE-DUPLICATE', codes)

    # N-11
    def test_10_combination_before_acceptance(self):
        r, codes = v('combination_before_acceptance.json')
        self.assertFalse(r.stage_b_role_ready)
        self.assertIn('E-COMBINATION-APPROVAL-TIMESTAMP-ORDER', codes)

    def test_11_valid_ordering_still_passes(self):
        r, codes = v('valid_four_person.json')
        self.assertTrue(r.stage_b_role_ready)
        self.assertEqual(codes, [])

    # N-12
    def test_12_whitespace_candidate_reference(self):
        r, codes = v('candidate_whitespace_ref.json')
        self.assertFalse(r.stage_b_role_ready)
        self.assertIn('E-CANDIDATE-REF-INVALID', codes)

    # Determinism
    def test_13_deterministic_repeated_execution(self):
        a = v('valid_four_person.json')[0].to_dict()
        b = v('valid_four_person.json')[0].to_dict()
        c = v('basis_invisible_zwsp.json')[0].to_dict()
        d = v('basis_invisible_zwsp.json')[0].to_dict()
        self.assertEqual(a, b)
        self.assertEqual(c, d)


if __name__ == '__main__':
    unittest.main()
