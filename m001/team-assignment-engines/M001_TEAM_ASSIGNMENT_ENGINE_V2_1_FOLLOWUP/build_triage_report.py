#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Render the lower-severity triage JSON into the required report."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
d = json.loads((ROOT / 'analysis' / 'lower_severity_triage.json').read_text(encoding='utf-8'))
lines = [
    '# M001 V2.1 — Lower-Severity Risk Triage',
    '',
    '**Mission:** M001-TEAM-007  ',
    '**Source:** unchanged `V2_REAUDIT/M001_FINAL_DEFECT_REGISTER.json`  ',
    '**Evidence:** `analysis/lower_severity_triage.json`, `reports/TRIAGE_AGENT_NOTES.md`',
    '',
    'All 24 carried-forward findings (17 MEDIUM, 7 LOW) were examined. Original severities were',
    'preserved; no finding was automatically closed. Only S-03 was independently verified closed',
    '(incidentally by the N-15 fix); it remains listed at its original severity.',
    '',
    '## Classification summary',
    '',
    '| Class | Meaning | Count | IDs |',
    '|---|---|---|---|',
]
for cls, meaning in (
    ('A', 'Must fix before Stage B readiness'),
    ('B', 'Must fix before recruitment authorization'),
    ('C', 'Must fix before field validation'),
    ('D', 'Acceptable residual with documented rationale'),
    ('E', 'Still requires investigation'),
):
    ids = [f['finding_id'] for f in d['findings'] if f['classification'] == cls]
    lines.append('| %s | %s | %d | %s |' % (cls, meaning, len(ids), ', '.join(ids) or '—'))

lines += ['', '## Complete finding mapping', '',
          '| ID | Sev | Component | V2.1 behaviour | Reproduced | Stage B? | Confidentiality/authorization? | Class | Blocks ops? |',
          '|---|---|---|---|---|---|---|---|---|']
for f in d['findings']:
    def cell(v, n=150):
        s = str(v).replace('|', '/').replace('\n', ' ')
        return s[:n] + ('…' if len(s) > n else '')
    lines.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
        f['finding_id'], f['original_severity'], cell(f.get('affected_component'), 90),
        cell(f.get('v21_behaviour')), cell(f.get('reproduction_status'), 60),
        cell(f.get('affects_stage_b_readiness'), 110),
        cell(f.get('affects_participant_confidentiality_or_authorization_integrity'), 110),
        f['classification'], cell(f.get('blocks_eventual_operational_use'), 30)))

lines += ['', '## A-class findings (block Stage B readiness)', '']
for f in d['findings']:
    if f['classification'] == 'A':
        lines += ['### %s — %s' % (f['finding_id'], f['title']), '',
                  '- Severity: %s (unchanged)' % f['original_severity'],
                  '- Component: %s' % f.get('affected_component'),
                  '- Reproduction: %s' % f.get('reproduction_status'),
                  '- Stage B impact: %s' % f.get('affects_stage_b_readiness'),
                  '- Recommended resolution: %s' % f.get('recommended_resolution'),
                  '']

lines += ['## Verified closure / incidental improvements', '',
          '- Verified closed: %s' % ', '.join(d['verification_summary'].get('independently_verified_closed', [])),
          '- Incidental partial improvements (not closure): %s' %
          ', '.join(d['verification_summary'].get('incidental_partial_improvements_observed', [])),
          '- All findings kept open except S-03: %s' % d['verification_summary'].get('all_findings_kept_open_except_S03'),
          '',
          '## New follow-up finding', '',
          '- F-007 (MEDIUM, class A): invisible Unicode format characters (U+200B, U+200E, U+2060)',
          '  satisfy `meaningful_text()` because `str.strip()` does not remove them. Independently',
          '  reproduced on V2.1: approval basis of repeated U+200B yields Stage B YES with zero issues.',
          '  Recommended: require at least one visible/alphanumeric character (reject Unicode categories',
          '  Cc/Cf/Zs/Zl/Zp-only strings) in `meaningful_text()` and combine with `strip()`.',
          '']
(ROOT / 'M001_LOWER_SEVERITY_RISK_TRIAGE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('wrote triage report with', len(d['findings']), 'findings')
