from pathlib import Path
r = Path(__file__).resolve().parent
old = r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2'
new = r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1'
for rel in ('tests/independent/independent_adversarial_v21.py',
            'tests/independent/refined_cases_v21.py'):
    p = r / rel
    s = p.read_text(encoding='utf-8')
    s = s.replace(old, new)
    s = s.replace('REAUDIT = Path(__file__).resolve().parents[1]',
                  'REAUDIT = Path(__file__).resolve().parents[2]')
    p.write_text(s, encoding='utf-8')
print('independent suites adapted to V2.1')
