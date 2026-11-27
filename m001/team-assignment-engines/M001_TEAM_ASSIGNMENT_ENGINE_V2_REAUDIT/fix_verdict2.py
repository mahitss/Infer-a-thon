from pathlib import Path
import json
r = Path(__file__).resolve().parent
dash = chr(0x2014)
target = 'FAIL ' + dash + ' CRITICAL OR HIGH DEFECTS FOUND'
p = r / 'M001_V2_INDEPENDENT_REAUDIT.md'
s = p.read_text(encoding='utf-8')
# Replace any corrupted variant and the hyphen variant.
import re
s = re.sub(r'FAIL [\ufffd\-] CRITICAL OR HIGH DEFECTS FOUND', target, s)
p.write_text(s, encoding='utf-8')
q = r / 'M001_FINAL_DEFECT_REGISTER.json'
d = json.loads(q.read_text(encoding='utf-8'))
d['verdict'] = target
q.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('verdict set via chr(0x2014)')
