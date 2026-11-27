from pathlib import Path
r = Path(__file__).resolve().parent
p = r / 'tests' / 'independent' / 'independent_adversarial_v21.py'
s = p.read_text(encoding='utf-8')
replacements = [
    ("'BLOCK_IF_ROLE_BOUND', ['E-EVIDENCE-ROLE']",
     "'BLOCK_IF_ROLE_BOUND', ['E-ACCEPTANCE-ROLE', 'E-EVIDENCE-SUBJECT']"),
    ("'BLOCK', ['E-SCHEMA'])\ncase('EVID-06'", "'BLOCK', ['E-SCHEMA', 'E-EVIDENCE-REVOKED'])\ncase('EVID-06'"),
    ("'BLOCK', ['E-AUTHORIZATION-STATE'])", "'BLOCK', ['E-AUTHORIZATION-STATE', 'E-SCHEMA'])"),
]
for old, new in replacements:
    s = s.replace(old, new)
p.write_text(s, encoding='utf-8')
print('updated auditor expectations for V2.1 stable codes')
