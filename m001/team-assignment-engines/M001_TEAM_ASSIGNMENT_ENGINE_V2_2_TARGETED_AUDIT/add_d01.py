#!/usr/bin/env python
import json
from pathlib import Path
p = Path(__file__).resolve().parent / 'analysis' / 'remaining_findings.json'
d = json.loads(p.read_text(encoding='utf-8'))
d['findings'].append({
    'finding_id': 'D-01', 'severity': 'MEDIUM',
    'title': 'Appointment candidate_ref is not bound to the formal role record candidate_ref',
    'component': 'engine/validator.py appointments loop (lines 515-538)',
    'canonical_match': 'adjacent to N-12',
    'still_reproducible': True,
    'observed_codes': [],
    'affects_identity_or_evidence_integrity': True,
    'affects_confidentiality': False,
    'affects_operational_readiness': True,
    'remediate_before_stage_b': True,
    'residual_with_rationale': False,
    'requires_investigation': False,
    'classification': 'A', 'status': 'open',
    'recommended_resolution': 'Require appointment.candidate_ref == role_records[role].candidate_ref and emit E-APPOINTMENT-RECORD or a dedicated binding code on mismatch.',
    'source': 'M001-TEAM-009 independent targeted audit'
})
d['counts'] = {'total': len(d['findings']),
               'open': sum(1 for f in d['findings'] if f['status']=='open'),
               'verified_closed': sum(1 for f in d['findings'] if f['status']=='verified_closed'),
               'remediate_before_stage_b': sum(1 for f in d['findings'] if f['remediate_before_stage_b'])}
p.write_text(json.dumps(d, indent=2) + '\n', encoding='utf-8')
print(d['counts'])
