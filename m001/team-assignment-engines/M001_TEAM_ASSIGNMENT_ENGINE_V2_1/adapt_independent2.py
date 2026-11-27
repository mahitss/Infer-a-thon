from pathlib import Path
r = Path(__file__).resolve().parent
p = r / 'tests' / 'independent' / 'independent_adversarial_v21.py'
s = p.read_text(encoding='utf-8')
# Map legacy evidence IDs used by auditor cases to V2.1 role-bound IDs.
for prefix in ('e-acc', 'e-po', 'e-form', 'e-onb'):
    old = "'%s-C-P1'" % prefix
    new = "'%s-C-P1-RESEARCH_OWNER'" % prefix
    s = s.replace(old, new)
p.write_text(s, encoding='utf-8')
print('mapped auditor evidence IDs to V2.1 role-bound IDs')
