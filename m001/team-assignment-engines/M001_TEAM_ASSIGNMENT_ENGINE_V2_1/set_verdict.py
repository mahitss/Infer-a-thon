from pathlib import Path
r = Path(__file__).resolve().parent
verdict = 'FOUR HIGH DEFECTS REMEDIATED' + chr(0x2014) + ' READY FOR INDEPENDENT FOLLOW-UP'
p = r / 'M001_V2_1_AUDIT.md'
s = p.read_text(encoding='utf-8').replace('VERDICT_PLACEHOLDER', verdict)
p.write_text(s, encoding='utf-8')
print('verdict written:', [hex(ord(c)) for c in verdict if not c.isalnum() and c != ' '])
