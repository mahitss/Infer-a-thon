#!/usr/bin/env python3
"""Pure resource-gate validation helpers (M001.3.2).

No Docker start, no image pull, no inference. All helpers are testable with an
injected command runner so tests never execute real commands.

Internal safety policy (NOT an official SIE minimum requirement):
  * minimum memory threshold: 8 GB
  * gate freshness window: 10 minutes (fixed; not user-configurable)
"""
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


def is_number(value):
    """Numeric but explicitly not bool (bool is a subclass of int in Python)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


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


def read_available_ram_gb(runner=default_runner):
    """Observe current host RAM availability in GB (read-only)."""
    if platform.system() == "Windows":
        result = runner([
            "powershell", "-NoProfile", "-Command",
            "(Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory).AvailableMBytes",
        ])
        if result.returncode != 0:
            raise RuntimeError(f"RAM diagnostic failed: {result.stderr.strip()}")
        megabytes = float(result.stdout.strip().splitlines()[-1].strip())
        return round(megabytes / 1024.0, 2)
    try:
        with open("/proc/meminfo", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemAvailable:"):
                    return round(int(line.split()[1]) / 1024.0 / 1024.0, 2)
    except OSError:
        pass
    result = runner(["bash", "-lc", "awk '/MemAvailable/ {print $2}' /proc/meminfo"])
    if result.returncode != 0:
        raise RuntimeError("RAM diagnostic unavailable")
    return round(float(result.stdout.strip().splitlines()[-1]) / 1024.0 / 1024.0, 2)


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
    if not is_number(threshold):
        errors.append("memory_safety_threshold_gb must be numeric (not bool)")
    elif threshold < INTERNAL_MIN_THRESHOLD_GB:
        errors.append(f"memory_safety_threshold_gb {threshold} is below internal minimum {INTERNAL_MIN_THRESHOLD_GB} GB")

    available = gate.get(RAM_FIELD)
    if not is_number(available):
        errors.append(f"{RAM_FIELD} must be numeric (not bool)")
    elif is_number(threshold) and available < threshold:
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
    import json
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise ValueError(f"gate file unreadable/invalid JSON: {type(exc).__name__}: {exc}") from exc


def disk_free_gb(path="."):
    usage = shutil.disk_usage(path)
    return round(usage.free / 1024.0 / 1024.0 / 1024.0, 2)
