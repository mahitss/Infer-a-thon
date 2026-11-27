from pathlib import Path
import json
r = Path(__file__).resolve().parent
p = r / 'M001_V2_INDEPENDENT_REAUDIT.md'
s = p.read_text(encoding='utf-8').replace('FAIL - CRITICAL OR HIGH DEFECTS FOUND',
                                          'FAIL — CRITICAL OR HIGH DEFECTS FOUND')
p.write_text(s, encoding='utf-8')
q = r / 'M001_FINAL_DEFECT_REGISTER.json'
d = json.loads(q.read_text(encoding='utf-8'))
d['verdict'] = 'FAIL — CRITICAL OR HIGH DEFECTS FOUND'
q.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('verdict strings updated')
