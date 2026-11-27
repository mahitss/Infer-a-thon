#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compact auditor reproduction: V2 vulnerable vs V2.1 rejected. Read-only."""
import copy, importlib.util, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
V2 = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2')
V21 = Path(r'C:\Users\pc\AppData\Local\Temp\opencode\M001_TEAM_ASSIGNMENT_ENGINE_V2_1')


def load(name, root):
    spec = importlib.util.spec_from_file_location(name, root / 'engine' / 'validator.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def run(m, st, schema=None):
    p = m.load_policy(); s = schema or m.load_schema()
    try:
        r = m.validate_state(st, p, s)
        return {'ready': r.stage_b_role_ready,
                'codes': sorted(set(i.code for i in r.issues))}
    except Exception as exc:
        return {'exception': '%s: %s' % (type(exc).__name__, str(exc).splitlines()[0])}


old, new = load('v2_cmp', V2), load('v21_cmp', V21)
base_old = old.load_json_strict(V2 / 'tests' / 'fixtures' / 'valid_four_person.json')
base_new = new.load_json_strict(V21 / 'tests' / 'fixtures' / 'valid_four_person.json')
rows = []

# N-01/N-02: whitespace basis/rationale.
for label, key, path, value in (
    ('N-01 basis', 'roles', ('RESEARCH_OWNER', 'approval', 'basis'), ' \t\n '),
    ('N-02 rationale', 'combination_approvals', (0, 'rationale'), ' \t\n '),
):
    for tag, mod, base in (('V2', old, base_old), ('V2.1', new, base_new)):
        st = copy.deepcopy(base)
        node = st
        if key == 'roles':
            node = st['roles']
            for part in path[:-1]:
                node = node[part]
            node[path[-1]] = value
        else:
            node = st[key][path[0]]
            node[path[1]] = value
        rows.append({'finding': label, 'version': tag, **run(mod, st)})

# N-03: shared acceptance evidence (V2 style: point both roles to one record).
for tag, mod, base, eid in (
    ('V2', old, base_old, 'e-acc-C-P1'),
    ('V2.1', new, base_new, 'e-acc-C-P1-RESEARCH_OWNER'),
):
    st = copy.deepcopy(base)
    st['roles']['CONTINUE_STOP_OWNER']['acceptance']['evidence_id'] = eid
    rows.append({'finding': 'N-03 shared acceptance', 'version': tag, **run(mod, st)})

# N-15: governance null.
for tag, mod, base in (('V2', old, base_old), ('V2.1', new, base_new)):
    st = copy.deepcopy(base); st['governance'] = None
    rows.append({'finding': 'N-15 governance null', 'version': tag, **run(mod, st)})

# N-15: unresolvable ref schema.
bad_schema_old = json.loads((V2 / 'schemas' / 'team_assignment.schema.json').read_text(encoding='utf-8'))
bad_schema_old['properties']['candidates']['additionalProperties'] = {'$ref': '#/$defs/NOPE'}
bad_schema_new = json.loads(bad_schema_old.__class__ and json.dumps(bad_schema_old))
for tag, mod, base, schema in (
    ('V2', old, base_old, bad_schema_old), ('V2.1', new, base_new, bad_schema_new),
):
    rows.append({'finding': 'N-15 unresolvable ref', 'version': tag,
                 **run(mod, copy.deepcopy(base), schema)})

out = {'comparison': rows}
(HERE / 'tests' / 'results' / 'quick_comparison_results.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
for r in rows:
    print('%-24s %-5s %s' % (r['finding'], r['version'], r.get('exception') or ('ready=%s %s' % (r['ready'], r['codes'][:4]))))
