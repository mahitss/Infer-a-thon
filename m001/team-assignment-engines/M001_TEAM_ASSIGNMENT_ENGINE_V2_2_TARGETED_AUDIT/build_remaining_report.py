#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Render remaining-finding triage JSON into the required report."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
d = json.loads((ROOT/'analysis'/'remaining_findings.json').read_text(encoding='utf-8'))
lines = [
    '# M001 V2.2 — Remaining Finding Triage',
    '',
    '**Mission:** M001-TEAM-009  ',
    '**Evidence:** `analysis/remaining_findings.json`',
    '',
    'No finding was silently closed or downgraded. Original identifiers and severities are preserved. '
    'N-04, N-08, N-11 and N-12 are independently verified closed in V2.2; S-03 was previously '
    'closed by the N-15 remediation. All other findings remain open.',
    '',
    '| ID | Sev | Still reproducible | Identity/evidence integrity | Confidentiality | Operational readiness | Fix before Stage B | Residual OK | Investigate | Status |',
    '|---|---|---|---|---|---|---|---|---|---|',
]
for f in d['findings']:
    def yn(v): return 'yes' if v else 'no'
    lines.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
        f['finding_id'], f['severity'], yn(f['still_reproducible']),
        yn(f['affects_identity_or_evidence_integrity']), yn(f['affects_confidentiality']),
        yn(f['affects_operational_readiness']), yn(f['remediate_before_stage_b']),
        yn(f['residual_with_rationale']), yn(f['requires_investigation']), f['status']))
lines += ['', '## Summary', '',
          '- Total tracked: %d' % d['counts']['total'],
          '- Still open: %d' % d['counts']['open'],
          '- Verified closed: %d' % d['counts']['verified_closed'],
          '- Require remediation before Stage B: %d' % d['counts']['remediate_before_stage_b'],
          '',
          'The seven corpus residuals were individually reproduced and classified, not automatically '
          'accepted or rejected. None of the remaining findings directly changes recruitment or '
          'field-validation authorization; both flags remain hard-coded NO.', '']
(ROOT/'M001_REMAINING_FINDING_TRIAGE.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print('wrote', len(d['findings']), 'rows')
