#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CLI for M001 team assignment validation."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.validator import (  # noqa: E402
    human_report, json_result, load_json, load_policy, load_schema, validate_state
)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Validate M001 team assignment state')
    ap.add_argument('--state', required=True, help='Path to assignment state JSON')
    ap.add_argument('--json-out', help='Path for machine-readable JSON result')
    ap.add_argument('--json-only', action='store_true',
                    help='Print only the machine-readable JSON result')
    args = ap.parse_args(argv)

    state_path = Path(args.state)
    if not state_path.is_absolute():
        state_path = ROOT / state_path

    state = load_json(state_path)
    result = validate_state(state, load_policy(), load_schema())
    source = state_path.name

    if args.json_out:
        out = Path(args.json_out)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json_result(result, source) + '\n', encoding='utf-8')

    if args.json_only:
        print(json_result(result, source))
    else:
        print(human_report(result, source))
    return 1 if result.errors else 0


if __name__ == '__main__':
    sys.exit(main())
