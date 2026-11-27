#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Consolidate all independent audit result files into one evidence index."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FILES = [
    'tests/results/independent_adversarial_results.json',
    'tests/results/refined_case_results.json',
    'tests/results/current_state_boundary_results.json',
    'tests/results/cli_robustness_results.json',
    'tests/results/finding_closure_results.json',
    'schema/schema_results.json',
    'mutation/results/independent_mutation_results.json',
]
out = {}
for rel in FILES:
    p = ROOT / rel
    if p.is_file():
        try:
            out[rel] = {'status': 'present', 'data': json.loads(p.read_text(encoding='utf-8'))}
        except Exception as exc:
            out[rel] = {'status': 'invalid', 'error': str(exc)}
    else:
        out[rel] = {'status': 'missing'}
path = ROOT / 'evidence' / 'consolidated_evidence.json'
path.write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
print('consolidated', len(out), 'files;', sum(1 for v in out.values() if v['status'] == 'present'), 'present')
