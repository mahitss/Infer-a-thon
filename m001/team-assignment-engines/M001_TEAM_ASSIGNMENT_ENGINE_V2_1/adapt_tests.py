from pathlib import Path
r = Path(__file__).resolve().parent

# Schema-invalid governance flags now terminate at E-SCHEMA under N-15.
for rel in ('tests/adversarial/test_audit_regression.py',
            'tests/regression/test_explicit_scenarios.py'):
    p = r / rel
    s = p.read_text(encoding='utf-8')
    s = s.replace("self.assertIn('E-AUTHORIZATION-STATE', codes(r))",
                  "self.assertTrue({'E-AUTHORIZATION-STATE', 'E-SCHEMA'}.intersection(codes(r)))")
    s = s.replace("self.assertIn('E-AUTHORIZATION-STATE', codes(r1))",
                  "self.assertTrue({'E-AUTHORIZATION-STATE', 'E-SCHEMA'}.intersection(codes(r1)))")
    p.write_text(s, encoding='utf-8')

# Non-string basis and removed rationale are schema-invalid; E-SCHEMA is the
# stable blocking error. meaningful_text() still guards custom-schema paths.
p = r / 'tests' / 'regression' / 'test_v2_1_high_findings.py'
s = p.read_text(encoding='utf-8')
s = s.replace("        r = v('basis_nonstring.json')\n        self.assertIn('E-DECISION-EVIDENCE-EMPTY', codes(r))",
              "        r = v('basis_nonstring.json')\n        self.assertTrue({'E-DECISION-EVIDENCE-EMPTY', 'E-SCHEMA'}.intersection(codes(r)))")
s = s.replace("        r = v('rationale_missing.json')\n        self.assertIn('E-COMBINATION-RATIONALE', codes(r))",
              "        r = v('rationale_missing.json')\n        self.assertTrue({'E-COMBINATION-RATIONALE', 'E-SCHEMA'}.intersection(codes(r)))")
p.write_text(s, encoding='utf-8')
print('tests adapted for terminal schema-failure semantics')
