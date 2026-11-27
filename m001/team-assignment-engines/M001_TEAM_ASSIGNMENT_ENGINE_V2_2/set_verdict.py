from pathlib import Path
p = Path(__file__).resolve().parent / 'M001_V2_2_ENGINE_AUDIT.md'
verdict = 'FIVE STAGE B BLOCKERS REMEDIATED' + chr(0x2014) + ' READY FOR TARGETED INDEPENDENT VERIFICATION'
s = p.read_text(encoding='utf-8').replace('VERDICT_PLACEHOLDER', verdict)
p.write_text(s, encoding='utf-8')
print('verdict set with em dash codepoint', hex(ord(chr(0x2014))))
