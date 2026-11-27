#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build remaining-finding triage preserving IDs and severities."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
src = json.loads(Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1_FOLLOWUP\analysis\lower_severity_triage.json').read_text(encoding='utf-8'))
corpus = json.loads(Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_2\tests\results\independent_adversarial_results.json').read_text(encoding='utf-8'))
CLOSED_IN_V22 = {'N-04', 'N-08', 'N-11', 'N-12'}
rows = []
for f in src['findings']:
    cls = f['classification']
    if f['finding_id'] in CLOSED_IN_V22:
        cls = 'D'
    rows.append({
        'finding_id': f['finding_id'], 'severity': f['original_severity'],
        'title': f['title'], 'component': f.get('affected_component'),
        'still_reproducible': (f.get('reproduction_status', '').lower().startswith('reproduced')
                               and f['finding_id'] not in CLOSED_IN_V22),
        'affects_identity_or_evidence_integrity': ('evidence' in str(f.get('affected_component','')).lower()
            or 'candidate' in str(f.get('affected_component','')).lower()
            or f['finding_id'] in ('N-08','N-12','N-13','S-05','S-07')),
        'affects_confidentiality': False,
        'affects_operational_readiness': cls == 'A',
        'remediate_before_stage_b': cls == 'A',
        'residual_with_rationale': cls == 'D',
        'requires_investigation': cls == 'E',
        'classification': cls,
        'status': ('verified_closed' if f['finding_id'] in ({'S-03'} | CLOSED_IN_V22) else 'open'),
        'verification_note': ('independently verified closed in V2.2 targeted audit'
                              if f['finding_id'] in CLOSED_IN_V22 else
                              ('incidentally closed by N-15 fix in V2.1' if f['finding_id'] == 'S-03' else '')),
        'recommended_resolution': f.get('recommended_resolution'),
        'source': 'V2 re-audit register / follow-up triage',
    })
# Corpus residuals, mapped to canonical IDs where applicable.
mapping = {
    'COMB-03': ('N-05', 'MEDIUM'), 'COMB-12': (None, 'MEDIUM'),
    'EVID-03': ('N-07/S-02', 'MEDIUM'), 'EVID-06': ('N-09', 'MEDIUM'),
    'ST-02': ('N-10', 'MEDIUM'), 'ID-02': ('N-13', 'MEDIUM'),
    'ID-07': ('N-13', 'MEDIUM'),
}
for c in corpus['cases']:
    if c['verdict'] != 'DEFECT':
        continue
    canonical, sev = mapping.get(c['id'], (None, 'MEDIUM'))
    rows.append({
        'finding_id': 'CORPUS-' + c['id'], 'severity': sev,
        'title': c['description'], 'component': 'engine/validator.py',
        'canonical_match': canonical,
        'still_reproducible': True,
        'observed_codes': c['observed']['codes'],
        'affects_identity_or_evidence_integrity': c['id'] in ('EVID-03','EVID-06','ID-02','ID-07'),
        'affects_confidentiality': False,
        'affects_operational_readiness': c['id'] in ('EVID-03','EVID-06','ST-02','ID-02','ID-07'),
        'remediate_before_stage_b': c['id'] in ('EVID-03','EVID-06','ST-02','ID-02','ID-07'),
        'residual_with_rationale': c['id'] in ('COMB-03','COMB-12'),
        'requires_investigation': c['id'] in ('EVID-03','EVID-06','ST-02','ID-02','ID-07'),
        'classification': 'A' if c['id'] in ('EVID-03','EVID-06','ST-02','ID-02','ID-07') else 'D',
        'status': 'open',
        'source': 'independent 50-case corpus V2.2 run',
    })
out = {'mission':'M001-TEAM-009','date':'2026-11-28',
       'note':'N-04, N-08, N-11 and F-007 are independently verified closed in V2.2; N-12 is verified closed; S-03 was previously closed by N-15. All other findings retain original IDs and severities.',
       'findings': rows,
       'counts': {'total': len(rows), 'open': sum(1 for r in rows if r['status']=='open'),
                  'verified_closed': sum(1 for r in rows if r['status']=='verified_closed'),
                  'remediate_before_stage_b': sum(1 for r in rows if r['remediate_before_stage_b'])}}
(HERE/'analysis'/'remaining_findings.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print('triaged',len(rows),'findings;',out['counts'])
