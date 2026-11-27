#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V2 CLI with safe input-error handling and deterministic output."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.validator import (  # noqa: E402
    DuplicateKeyError, Issue, ValidationResult, human_report, json_result,
    load_json_strict, load_policy, load_schema, validate_state
)


def error_result(code, message, source):
    issue = Issue('ERROR', code, 'input', '', '', message)
    result = ValidationResult(
        dimensions={'input':'FAIL'}, issues=[issue], stage_b_role_ready=False)
    text = human_report(result, source)
    payload = json_result(result, source)
    return text, payload


def main(argv=None):
    ap = argparse.ArgumentParser(description='Validate M001 V2 team assignment state')
    ap.add_argument('--state', required=True)
    ap.add_argument('--json-out')
    ap.add_argument('--json-only', action='store_true')
    args = ap.parse_args(argv)

    state_path = Path(args.state)
    if not state_path.is_absolute():
        state_path = ROOT / state_path
    source = state_path.name

    try:
        state = load_json_strict(state_path)
        policy = load_policy()
        schema = load_schema()
        result = validate_state(state, policy, schema)
        text = human_report(result, source)
        payload = json_result(result, source)
        exit_code = 0 if result.stage_b_role_ready else 1
    except (DuplicateKeyError, ValueError) as exc:
        code = str(exc).split(':', 1)[0] if ':' in str(exc) else 'E-INPUT-INVALID'
        text, payload = error_result(code, str(exc), source)
        exit_code = 2

    if args.json_out:
        out = Path(args.json_out)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + '\n', encoding='utf-8')
    print(payload if args.json_only else text)
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
