from pathlib import Path
p = Path(__file__).resolve().parent / 'tests' / 'independent' / 'independent_adversarial_v21.py'
s = p.read_text(encoding='utf-8')
s = s.replace("'BLOCK_STALE', ['E-COMBINATION-APPROVAL-STALE']",
              "'BLOCK_STALE', ['E-COMBINATION-APPROVAL-STALE', 'E-COMBINATION-APPROVAL-TIMESTAMP-ORDER']")
p.write_text(s, encoding='utf-8')
print('corpus expectation updated for N-11 stable code')
