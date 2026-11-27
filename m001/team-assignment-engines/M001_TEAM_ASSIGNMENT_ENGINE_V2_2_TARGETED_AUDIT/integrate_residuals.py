#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Integrate newly found residuals and per-case corpus classifications."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent

triage = json.loads((ROOT/'analysis'/'remaining_findings.json').read_text(encoding='utf-8'))
reg = json.loads((ROOT/'tests'/'results'/'regression_results.json').read_text(encoding='utf-8'))

# Reclassify corpus entries using the regression stream's individual analysis.
classification = {c['id']: c['classification'] for c in reg['open_corpus_cases']}
for f in triage['findings']:
    if f['finding_id'].startswith('CORPUS-'):
        cid = f['finding_id'].replace('CORPUS-', '')
        cls = classification.get(cid, 'inconclusive')
        genuine = cls == 'genuine residual'
        f['classification'] = 'A' if genuine else ('E' if cls == 'inconclusive' else 'D')
        f['corpus_classification'] = cls
        f['still_reproducible'] = genuine or cls == 'inconclusive'
        f['remediate_before_stage_b'] = genuine
        f['residual_with_rationale'] = cls == 'expectation artifact'
        f['requires_investigation'] = cls == 'inconclusive'

# New residual defects found by the targeted audit.
new = [
    {'finding_id':'D-02','severity':'MEDIUM','title':'Non-base Unicode characters satisfy meaningful_text()',
     'component':'engine/validator.py meaningful_text()','canonical_match':'F-007 boundary variant',
     'still_reproducible':True,
     'observed_codes':[],
     'affects_identity_or_evidence_integrity':False,
     'affects_confidentiality':False,
     'affects_operational_readiness':True,
     'remediate_before_stage_b':True,'residual_with_rationale':False,'requires_investigation':False,
     'classification':'A','status':'open',
     'recommended_resolution':'Require at least one base/letter/number character (not only Mn/Mc/Me/Co/Cn/Cs/FE0F) for decision-text fields, without rejecting legitimate marked or ZWJ text.'},
    {'finding_id':'D-03','severity':'MEDIUM','title':'Duplicate-evidence signature bypass via unchecked role on non-acceptance evidence',
     'component':'engine/validator.py evidence signature (9-field)','canonical_match':'N-08 bypass variant',
     'still_reproducible':True,'observed_codes':[],
     'affects_identity_or_evidence_integrity':True,
     'affects_confidentiality':False,
     'affects_operational_readiness':True,
     'remediate_before_stage_b':True,'residual_with_rationale':False,'requires_investigation':False,
     'classification':'A','status':'open',
     'recommended_resolution':'Use canonical 6-field signature from the canonical finding, or validate role/appointment_ref/decision_ref for all evidence types.'},
]
existing = {f['finding_id'] for f in triage['findings']}
for f in new:
    if f['finding_id'] not in existing:
        triage['findings'].append(f)
triage['counts'] = {'total':len(triage['findings']),
                    'open':sum(1 for f in triage['findings'] if f['status']=='open'),
                    'verified_closed':sum(1 for f in triage['findings'] if f['status']=='verified_closed'),
                    'remediate_before_stage_b':sum(1 for f in triage['findings'] if f['remediate_before_stage_b'])}
triage['note'] = ('N-04, N-08, N-11, N-12 and F-007 canonical reproductions independently verified fixed. '
                  'D-01, D-02 and D-03 are new MEDIUM residuals found during this verification. '
                  'No severity downgraded; no silent closure.')
(ROOT/'analysis'/'remaining_findings.json').write_text(json.dumps(triage,indent=2)+'\n',encoding='utf-8')
print(triage['counts'])

regjson = json.loads((ROOT/'M001_TARGETED_DEFECT_REGISTER.json').read_text(encoding='utf-8'))
regjson['new_findings'] += [
    {'id':'D-02','severity':'MEDIUM','status':'OPEN','classification':'A',
     'title':'Non-base Unicode characters satisfy meaningful_text()',
     'evidence':'Mn/Mc/Me-only, U+FE0F-only, private-use, unassigned and escaped-surrogate basis strings yield Stage B YES with zero issues',
     'affects_identity_or_evidence_integrity':False,'affects_operational_readiness':True},
    {'id':'D-03','severity':'MEDIUM','status':'OPEN','classification':'A',
     'title':'Duplicate-evidence signature bypass via unchecked role on non-acceptance evidence',
     'evidence':'3 variants (PO approval, formal appointment, onboarding): clone evidence, change unvalidated role field, readiness YES with zero issues',
     'affects_identity_or_evidence_integrity':True,'affects_operational_readiness':True},
]
regjson['remaining_findings'] = triage['counts']
regjson['scope_note'] = ('Canonical reproductions of all five remediations verified fixed. D-01, D-02 and D-03 '
                         'are new MEDIUM residuals requiring further engineering before Stage B reliance. '
                         'Formal staffing, operational safeguards, recruitment and field validation remain unachieved.')
regjson['verdict'] = 'CONDITIONAL PASS — FIVE REMEDIATIONS VERIFIED, RESIDUAL FINDINGS REMAIN'
(ROOT/'M001_TARGETED_DEFECT_REGISTER.json').write_text(json.dumps(regjson,indent=2)+'\n',encoding='utf-8')
print('defect register updated')
