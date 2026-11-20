#!/usr/bin/env bash
# Local SIE CPU smoke test (M001.3.2). NOT executed in this repository.
#
# ALL refusal checks run in smoke_gate.py BEFORE any Compose command that can
# create containers. The gate freshness window is fixed at 10 minutes inside
# gate_check.py and cannot be widened with an environment variable.
#
# Safety properties:
#   - no Docker Desktop auto-start; no Windows/WSL setting changes
#   - localhost-only binding and telemetry opt-out come from config/sie-cpu.yml
#   - explicit isolated Compose project name per invocation
#   - cleanup trap installed before startup; only this project is torn down
#   - named model-cache volume is NEVER deleted (no `down -v`)
#   - explicit authorization required: SIE_IMAGE_PULL_AUTHORIZED=1
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$ROOT/config/sie-cpu.yml"
GATE_FILE="${SIE_GATE_FILE:-$ROOT/results/resource-gate.json}"
PYTHON_BIN="${PYTHON_BIN:-python}"
PROJECT="sie-m001-smoke-$$-$(date +%s)"

# Install cleanup BEFORE any container can be created. STARTED is set to 1
# immediately before `up`, so a partial/failed start is also cleaned up.
STARTED=0
cleanup() {
  if [ "$STARTED" -eq 1 ]; then
    echo "[cleanup] stopping isolated project '$PROJECT' (volume preserved)"
    docker compose -p "$PROJECT" -f "$CONFIG" down --remove-orphans >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT
trap 'echo "[interrupt] cleaning up"; cleanup; exit 130' INT TERM

echo "[gate] pre-startup safety checks (includes LIVE RAM recheck)"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "BLOCKED: python not available for gate validation"; exit 2
fi
"$PYTHON_BIN" "$ROOT/scripts/smoke_gate.py" --gate "$GATE_FILE" || {
  echo "BLOCKED: smoke test refused before Docker startup"; exit 2
}

echo "[gate] compose config validation (no containers created)"
docker compose -p "$PROJECT" -f "$CONFIG" config >/dev/null || { echo "BLOCKED: invalid compose config"; exit 2; }

echo "[gate] image presence / authorized pull"
IMAGE="$(docker compose -p "$PROJECT" -f "$CONFIG" config --images | head -n 1)"
if [ -z "$IMAGE" ]; then
  echo "BLOCKED: could not resolve image from compose config"; exit 2
fi
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "NOTICE: image $IMAGE is not present locally; authorized pull may occur"
fi

echo "[run] starting isolated project '$PROJECT' on 127.0.0.1:8080"
STARTED=1
docker compose -p "$PROJECT" -f "$CONFIG" up -d

echo "[run] waiting for readiness"
READY=0
for i in $(seq 1 60); do
  if [ "$(curl -fsS http://127.0.0.1:8080/readyz 2>/dev/null || true)" = "ok" ]; then
    echo "ready after ${i}s"; READY=1; break
  fi
  sleep 1
done
if [ "$READY" -ne 1 ]; then
  echo "BLOCKED: readiness timed out"; exit 3
fi
curl -fsS http://127.0.0.1:8080/readyz || { echo "BLOCKED: readiness check failed"; exit 3; }

echo "[run] SDK connectivity and first small model"
"$PYTHON_BIN" - <<'PY' || { echo "BLOCKED: SDK/inference check failed"; exit 4; }
from sie_sdk import SIEClient
from sie_sdk.types import Item
client = SIEClient("http://127.0.0.1:8080")
result = client.encode("sentence-transformers/all-MiniLM-L6-v2", Item(text="synthetic benchmark text"))
print("dense_shape:", result["dense"].shape)
PY

echo "[run] container memory snapshot"
docker stats --no-stream --format '{{.Name}} {{.MemUsage}}'

echo "Smoke test complete; cleanup will stop only project '$PROJECT'."
