#!/usr/bin/env python3
"""Generate resource-gate.json from real, read-only host diagnostics (M001.3.2).

Does NOT start Docker Desktop, modify WSL/Windows settings, pull images or run
inference. Writes PASS or BLOCKED automatically from observed values.

Usage:
  python experiments/sie-feasibility/scripts/generate_resource_gate.py \
      --out experiments/sie-feasibility/results/resource-gate.json
"""
import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_check as gate  # noqa: E402

GENERATOR_VERSION = "1.0"


def build_gate(runner=gate.default_runner, now=None):
    """Collect diagnostics and build a gate dict with an automatic verdict."""
    observed_at = now or datetime.now(timezone.utc)
    errors = []
    try:
        ram = gate.read_available_ram_gb(runner)
        if not gate.is_number(ram):
            errors.append("RAM diagnostic did not return a number")
            ram = None
    except Exception as exc:  # noqa: BLE001
        errors.append(f"RAM diagnostic failed: {type(exc).__name__}: {exc}")
        ram = None

    engine_ready, engine_detail = gate.check_docker_engine(runner)
    if not engine_ready:
        errors.append(f"Docker Linux engine unavailable: {engine_detail}")

    if ram is not None and ram < gate.INTERNAL_MIN_THRESHOLD_GB:
        errors.append(
            f"available RAM {ram} GB is below internal policy minimum "
            f"{gate.INTERNAL_MIN_THRESHOLD_GB} GB"
        )

    status = "PASS" if not errors else "BLOCKED"
    return {
        "check_id": "M001.3.2-generated-resource-gate",
        "checked_at": observed_at.isoformat().replace("+00:00", "Z"),
        "generated_by": "generate_resource_gate.py",
        "generator_version": GENERATOR_VERSION,
        "freshness_window_seconds": gate.MAX_GATE_AGE_SECONDS,
        "branch": "research/m001-sie-feasibility",
        "memory_safety_threshold_gb": gate.INTERNAL_MIN_THRESHOLD_GB,
        "memory_safety_threshold_note": gate.POLICY_NOTE,
        "status": status,
        "observed": {
            "cpu": platform.processor() or platform.machine(),
            "os": f"{platform.system()} {platform.release()}",
            "python": platform.python_version(),
            "ram_available_gb": ram,
            "docker_engine_ready": engine_ready,
            "docker_engine_detail": engine_detail,
            "disk_free_gb": gate.disk_free_gb(),
        },
        gate.RAM_FIELD: ram,
        "docker_engine_ready": engine_ready,
        "criteria": {
            "physical_memory_headroom": "PASS" if ram is not None and ram >= gate.INTERNAL_MIN_THRESHOLD_GB else "FAIL",
            "linux_docker_engine_ready": "PASS" if engine_ready else "FAIL",
        },
        "reason": ("Observed values satisfy the internal safety policy." if not errors
                   else "; ".join(errors)),
        "downloads_attempted": False,
        "inference_executed": False,
        "note": "Generated from live diagnostics; a gate alone is not proof of current availability. "
                "The smoke test performs an independent live RAM recheck.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    gate_data = build_gate()
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(gate_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"GATE {gate_data['status']}: {gate_data['reason']}")
    print(f"written: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
