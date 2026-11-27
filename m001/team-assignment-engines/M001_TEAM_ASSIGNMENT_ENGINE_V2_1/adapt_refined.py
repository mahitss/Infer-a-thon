from pathlib import Path
r = Path(__file__).resolve().parent
p = r / 'tests' / 'independent' / 'refined_cases_v21.py'
s = p.read_text(encoding='utf-8')
for prefix in ('e-acc', 'e-po', 'e-form', 'e-onb'):
    s = s.replace("'%s-C-P1'" % prefix, "'%s-C-P1-RESEARCH_OWNER'" % prefix)
p.write_text(s, encoding='utf-8')
print('refined cases mapped to V2.1 evidence IDs')
