#!/usr/bin/env python3
"""Pure resource-gate validation helpers (M001.3.2).

No Docker start, no image pull, no inference. All helpers are testable with an
injected command runner so tests never execute real commands.

Internal safety policy (NOT an official SIE minimum requirement):
  * minimum memory threshold: 8 GB
  * gate freshness window: 10 minutes (fixed; not user-configurable)
"""
import json
import math
import platform
import shutil
import subprocess
from datetime import datetime, timezone

INTERNAL_MIN_THRESHOLD_GB = 8.0
MAX_GATE_AGE_SECONDS = 600  # fixed 10-minute freshness window
RAM_FIELD = "ram_available_gb"
POLICY_NOTE = (
    "Internal conservative safety policy for this experiment, "
    "not an official SIE minimum requirement."
)


class CommandResult:
    __slots__ = ("returncode", "stdout", "stderr")

    def __init__(self, returncode, stdout, stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def default_runner(argv, timeout=30):
    """Run a read-only diagnostic command. Never starts Docker Desktop."""
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


NON_FINITE_ERROR = "must be a finite numeric value (not bool, NaN or infinity)"


def is_number(value):
    """Numeric but explicitly not bool (bool is a subclass of int in Python)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_finite_number(value):
    """Finite numeric only: rejects bool, NaN, +/-inf and huge ints.

    math.isfinite() converts its argument to float, which raises OverflowError
    for very large integers and TypeError/ValueError for other malformed
    values. Any such failure means the value is not a usable measurement, so
    return False rather than propagating an exception.
    """
    try:
        return is_number(value) and math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


def parse_timestamp(raw):
    """Parse an ISO-8601 UTC timestamp; return a timezone-aware datetime."""
    if not isinstance(raw, str):
        raise ValueError("checked_at must be an ISO-8601 string")
    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"checked_at is not ISO-8601: {raw!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _finite_gb(raw_value, divisor, label):
    """Convert a diagnostic value to GB, rejecting any malformed result."""
    try:
        value = float(raw_value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(f"{label} diagnostic is not numeric: {raw_value!r}") from exc
    if not is_finite_number(value):
        raise RuntimeError(f"{label} diagnostic is not finite: {raw_value!r}")
    gigabytes = round(value / divisor, 2)
    if not is_finite_number(gigabytes):
        raise RuntimeError(f"{label} conversion produced a non-finite value")
    return gigabytes


def read_available_ram_gb(runner=default_runner):
    """Observe current host RAM availability in GB (read-only)."""
    if platform.system() == "Windows":
        result = runner([
            "powershell", "-NoProfile", "-Command",
            "(Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory).AvailableMBytes",
        ])
        if result.returncode != 0:
            raise RuntimeError(f"RAM diagnostic failed: {result.stderr.strip()}")
        return _finite_gb(result.stdout.strip().splitlines()[-1].strip(), 1024.0, "available RAM (MB)")
    try:
        with open("/proc/meminfo", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemAvailable:"):
                    return _finite_gb(line.split()[1], 1024.0 * 1024.0, "available RAM (kB)")
    except OSError:
        pass
    result = runner(["bash", "-lc", "awk '/MemAvailable/ {print $2}' /proc/meminfo"])
    if result.returncode != 0:
        raise RuntimeError("RAM diagnostic unavailable")
    return _finite_gb(result.stdout.strip().splitlines()[-1], 1024.0 * 1024.0, "available RAM (kB)")


def check_docker_engine(runner=default_runner):
    """Return (ready, detail) from a read-only `docker version` probe."""
    try:
        result = runner(["docker", "version", "--format", "{{.Server.Version}}"])
    except Exception as exc:  # noqa: BLE001 - record any command failure
        return False, f"docker probe failed: {type(exc).__name__}: {exc}"
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip() or "docker engine not reachable"
    return True, result.stdout.strip()


def validate_gate(gate, now=None, max_age_seconds=MAX_GATE_AGE_SECONDS):
    """Validate a gate dict. Return (ok, errors). Rejects bools everywhere."""
    errors = []
    if not isinstance(gate, dict):
        return False, ["gate must be a JSON object"]

    if gate.get("status") != "PASS":
        errors.append(f"status is {gate.get('status')!r}, expected 'PASS'")

    threshold = gate.get("memory_safety_threshold_gb")
    if not is_finite_number(threshold):
        errors.append(f"memory_safety_threshold_gb {NON_FINITE_ERROR}")
    elif threshold < INTERNAL_MIN_THRESHOLD_GB:
        errors.append(f"memory_safety_threshold_gb {threshold} is below internal minimum {INTERNAL_MIN_THRESHOLD_GB} GB")

    available = gate.get(RAM_FIELD)
    if not is_finite_number(available):
        errors.append(f"{RAM_FIELD} {NON_FINITE_ERROR}")
    elif is_finite_number(threshold) and available < threshold:
        errors.append(f"available RAM {available} GB is below threshold {threshold} GB")

    if gate.get("docker_engine_ready") is not True:
        errors.append("docker_engine_ready must be boolean true")

    try:
        checked = parse_timestamp(gate.get("checked_at"))
    except ValueError as exc:
        errors.append(str(exc))
    else:
        reference = now or datetime.now(timezone.utc)
        age = (reference - checked).total_seconds()
        if age < 0:
            errors.append("checked_at is in the future")
        elif age > max_age_seconds:
            errors.append(f"checked_at is stale: age={age:.0f}s, max={max_age_seconds}s")

    return not errors, errors


def load_gate(path):
    """Load and JSON-parse a gate file; raise ValueError with a clear reason."""
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise ValueError(f"gate file unreadable/invalid JSON: {type(exc).__name__}: {exc}") from exc


def disk_free_gb(path="."):
    usage = shutil.disk_usage(path)
    return round(usage.free / 1024.0 / 1024.0 / 1024.0, 2)


def recorded_threshold(data):
    """Return max(8 GB, recorded threshold); reject malformed recorded values."""
    if not isinstance(data, dict):
        raise ValueError("gate must be a JSON object")
    value = data.get("memory_safety_threshold_gb")
    if not is_finite_number(value):
        raise ValueError(f"recorded threshold {NON_FINITE_ERROR}")
    if value < INTERNAL_MIN_THRESHOLD_GB:
        raise ValueError(f"recorded threshold {value} is below internal minimum {INTERNAL_MIN_THRESHOLD_GB} GB")
    return max(INTERNAL_MIN_THRESHOLD_GB, value)


def check_live_ram_against(threshold_gb, runner=default_runner):
    """Return (ok, observed_gb, message) for a fresh RAM diagnostic."""
    if not is_finite_number(threshold_gb) or threshold_gb < INTERNAL_MIN_THRESHOLD_GB:
        return False, None, f"effective threshold is invalid: {threshold_gb!r}"
    try:
        observed = read_available_ram_gb(runner)
    except Exception as exc:  # noqa: BLE001
        return False, None, f"live RAM diagnostic failed: {type(exc).__name__}: {exc}"
    if not is_finite_number(observed):
        return False, observed, f"live RAM diagnostic {observed!r} {NON_FINITE_ERROR}"
    if observed < threshold_gb:
        return False, observed, f"live RAM {observed} GB is below effective threshold {threshold_gb} GB"
    return True, observed, f"live RAM {observed} GB meets effective threshold {threshold_gb} GB"


def second_ram_check(gate_path, runner=default_runner):
    """Live recheck using the gate's recorded threshold (never trusts the gate)."""
    try:
        data = load_gate(gate_path)
        threshold = recorded_threshold(data)
    except ValueError as exc:
        return False, None, str(exc)
    return check_live_ram_against(threshold, runner)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-check", action="store_true",
                        help="perform a fresh live RAM recheck using the gate's recorded threshold")
    parser.add_argument("--gate", required=True)
    args = parser.parse_args()
    if not args.live_check:
        parser.error("only --live-check is supported")
    ok, observed, message = second_ram_check(args.gate)
    print(f"LIVE RAM {'PASS' if ok else 'BLOCKED'}: {message}")
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
