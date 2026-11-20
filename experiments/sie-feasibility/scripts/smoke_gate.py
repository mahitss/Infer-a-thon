#!/usr/bin/env python3
"""Pre-startup safety gate for the SIE smoke test (M001.3.2).

This module performs ALL refusal checks before any Docker Compose command can
create containers. It is invoked by run_smoke_test.sh and is unit-tested with
mocked command runners; no image pull or inference occurs here.

Checks, in order:
  1. Gate JSON parses, status PASS, fixed 10-minute freshness window.
  2. Threshold is numeric, not bool, and >= 8 GB (internal policy).
  3. Recorded available RAM is numeric, not bool, and >= threshold.
  4. Recorded docker_engine_ready is boolean true.
  5. LIVE host RAM recheck >= 8 GB (a stale gate cannot substitute).
  6. Explicit authorization: SIE_IMAGE_PULL_AUTHORIZED=1.
  7. Docker Linux engine reachable now (read-only probe; no auto-start).
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_check as gate  # noqa: E402


def preflight(gate_path, env=None, runner=gate.default_runner, now=None):
    """Return (ok, reasons). Never starts containers or pulls images."""
    env = os.environ if env is None else env
    reasons = []

    try:
        data = gate.load_gate(gate_path)
    except ValueError as exc:
        return False, [str(exc)]

    valid, errors = gate.validate_gate(data, now=now)
    if not valid:
        # Short-circuit: an invalid gate must not trigger any command probe.
        return False, errors

    try:
        live_ram = gate.read_available_ram_gb(runner)
    except Exception as exc:  # noqa: BLE001
        reasons.append(f"live RAM check failed: {type(exc).__name__}: {exc}")
        live_ram = None
    if gate.is_number(live_ram):
        if live_ram < gate.INTERNAL_MIN_THRESHOLD_GB:
            reasons.append(
                f"live available RAM {live_ram} GB is below internal minimum "
                f"{gate.INTERNAL_MIN_THRESHOLD_GB} GB"
            )
    else:
        reasons.append("live available RAM is not numeric")

    if env.get("SIE_IMAGE_PULL_AUTHORIZED") != "1":
        reasons.append("SIE_IMAGE_PULL_AUTHORIZED=1 not set")

    engine_ready, detail = gate.check_docker_engine(runner)
    if not engine_ready:
        reasons.append(f"Docker Linux engine unavailable: {detail}")

    return not reasons, reasons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", required=True)
    args = ap.parse_args()

    ok, reasons = preflight(args.gate)
    if ok:
        print("GATE PASS: all pre-startup safety checks satisfied")
        return 0
    for reason in reasons:
        print(f"BLOCKED: {reason}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
