#!/usr/bin/env bash
# Local SIE CPU smoke test (M001.3.1). NOT executed in M001.3/M001.3.1.
#
# This script REFUSES to run unless ALL of the following are true:
#   1. A resource-gate JSON result exists with status PASS.
#   2. Its checked_at timestamp is recent (default max age: 24 hours).
#   3. It records the documented internal memory safety threshold (8 GB) and
#      an available-RAM sample at or above that threshold.
#      NOTE: 8 GB is our internal conservative safety policy, NOT an official
#      SIE minimum requirement.
#   4. It records docker_engine_ready = true, and the engine is reachable now.
#   5. The user explicitly authorizes the image pull:
#        SIE_IMAGE_PULL_AUTHORIZED=1 ./run_smoke_test.sh
#
# It does NOT start Docker Desktop, does NOT modify Windows/WSL settings, and
# does NOT publish port 8080 publicly. Telemetry opt-out stays in the config.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$ROOT/config/sie-cpu.yml"
GATE_FILE="${SIE_GATE_FILE:-$ROOT/results/resource-gate.json}"
MAX_AGE_SECONDS="${SIE_GATE_MAX_AGE_SECONDS:-86400}"
PYTHON_BIN="${PYTHON_BIN:-python}"
STARTED=0

cleanup() {
  if [ "$STARTED" -eq 1 ]; then
    echo "[cleanup] stopping SIE container"
    docker compose -f "$CONFIG" down --remove-orphans >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

echo "[gate 1/5] validating fresh resource gate: $GATE_FILE"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "BLOCKED: python not available for gate validation"; exit 2
fi
if ! GATE_MSG=$("$PYTHON_BIN" - "$GATE_FILE" "$MAX_AGE_SECONDS" <<'PY'
import json, sys
from datetime import datetime, timezone

path, max_age = sys.argv[1], int(sys.argv[2])

def fail(msg):
    print(msg)
    sys.exit(1)

try:
    with open(path, encoding="utf-8") as fh:
        gate = json.load(fh)
except Exception as exc:
    fail("gate file unreadable: %s" % exc)

if gate.get("status") != "PASS":
    fail("gate status is %r, expected PASS" % gate.get("status"))

raw = gate.get("checked_at")
if not isinstance(raw, str):
    fail("gate has no checked_at timestamp")
try:
    checked = datetime.fromisoformat(raw.replace("Z", "+00:00"))
except ValueError:
    fail("checked_at is not ISO-8601: %r" % raw)
if checked.tzinfo is None:
    checked = checked.replace(tzinfo=timezone.utc)
age = (datetime.now(timezone.utc) - checked).total_seconds()
if age < 0 or age > max_age:
    fail("gate is stale or in the future: age=%.0fs, max=%ds" % (age, max_age))

threshold = gate.get("memory_safety_threshold_gb")
if not isinstance(threshold, (int, float)) or threshold <= 0:
    fail("memory_safety_threshold_gb missing or invalid (internal policy, 8 GB)")
available = gate.get("ram_available_gb_max")
if not isinstance(available, (int, float)) or available < threshold:
    fail("available RAM %r is below internal safety threshold %r" % (available, threshold))

if gate.get("docker_engine_ready") is not True:
    fail("gate records docker_engine_ready != true")

print("PASS")
PY
); then
  echo "BLOCKED: $GATE_MSG"
  exit 2
fi
echo "gate result: $GATE_MSG"

echo "[gate 2/5] explicit image-pull authorization"
if [ "${SIE_IMAGE_PULL_AUTHORIZED:-0}" != "1" ]; then
  echo "BLOCKED: set SIE_IMAGE_PULL_AUTHORIZED=1 to authorize any image pull"
  exit 2
fi

echo "[gate 3/5] Docker Linux engine availability (no auto-start)"
if ! command -v docker >/dev/null 2>&1; then
  echo "BLOCKED: docker CLI not found"; exit 2
fi
if ! docker version --format '{{.Server.Version}}' >/dev/null 2>&1; then
  echo "BLOCKED: Docker Linux engine not running (will not start Docker Desktop)"; exit 2
fi

echo "[gate 4/5] compose configuration validation"
docker compose -f "$CONFIG" config >/dev/null || { echo "BLOCKED: invalid compose config"; exit 2; }

echo "[gate 5/5] image presence / authorized pull"
IMAGE="$(docker compose -f "$CONFIG" config --images | head -n 1)"
if [ -z "$IMAGE" ]; then
  echo "BLOCKED: could not resolve image from compose config"; exit 2
fi
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "NOTICE: image $IMAGE is not present locally; authorized pull will occur"
fi

echo "[run] starting SIE on 127.0.0.1:8080 with telemetry disabled"
docker compose -f "$CONFIG" up -d
STARTED=1

echo "[run] waiting for readiness"
for i in $(seq 1 60); do
  if [ "$(curl -fsS http://127.0.0.1:8080/readyz 2>/dev/null || true)" = "ok" ]; then
    echo "ready after ${i}s"; break
  fi
  sleep 1
done
curl -fsS http://127.0.0.1:8080/readyz || { echo "BLOCKED: readiness check failed"; exit 3; }

echo "[run] SDK connectivity and first small model"
python - <<'PY'
from sie_sdk import SIEClient
from sie_sdk.types import Item
client = SIEClient("http://127.0.0.1:8080")
result = client.encode("sentence-transformers/all-MiniLM-L6-v2", Item(text="synthetic benchmark text"))
print("dense_shape:", result["dense"].shape)
PY

echo "[run] container memory snapshot"
docker stats --no-stream --format '{{.Name}} {{.MemUsage}}'

echo "Smoke test complete. Container will be stopped by cleanup on exit."
