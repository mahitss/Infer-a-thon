#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Standard-library JSON Schema subset validation for assignment states."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.validator import load_json, load_schema, validate_schema  # noqa: E402


def resolve(path, root):
    p = Path(path)
    return p if p.is_absolute() else root / p


def main(argv=None):
    ap = argparse.ArgumentParser(description='Validate assignment state JSON structure')
    ap.add_argument('--state', action='append', required=True)
    ap.add_argument('--schema', default='schemas/team_assignment.schema.json')
    args = ap.parse_args(argv)
    schema = load_schema(resolve(args.schema, ROOT))
    failed = False
    for raw in args.state:
        path = resolve(raw, ROOT)
        errors = validate_schema(load_json(path), schema, '$')
        status = 'PASS' if not errors else 'FAIL'
        print('%s %s errors=%d' % (status, path.name, len(errors)))
        for e in errors:
            print('  %s' % e)
        if errors:
            failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
