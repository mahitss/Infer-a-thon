#!/usr/bin/env bash
# Intended local SIE CPU smoke test. NOT executed in M001.3 (resource gate failed).
# Safety: localhost-only, telemetry off, synthetic data only.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$ROOT/config/sie-cpu.yml"

echo "[1/5] checking Docker Linux engine"
docker version --format '{{.Server.Version}}' >/dev/null || { echo "BLOCKED: Docker daemon not running"; exit 2; }

echo "[2/5] starting SIE on 127.0.0.1:8080 with telemetry disabled"
docker compose -f "$CONFIG" up -d

echo "[3/5] waiting for readiness"
for i in $(seq 1 60); do
  if [ "$(curl -fsS http://127.0.0.1:8080/readyz 2>/dev/null || true)" = "ok" ]; then
    echo "ready after ${i}s"; break
  fi
  sleep 1
done
curl -fsS http://127.0.0.1:8080/readyz || { echo "BLOCKED: readiness check failed"; exit 3; }

echo "[4/5] SDK connectivity and first small model"
python - "$@" <<'PY'
from sie_sdk import SIEClient
from sie_sdk.types import Item
c = SIEClient("http://127.0.0.1:8080")
r = c.encode("sentence-transformers/all-MiniLM-L6-v2", Item(text="synthetic benchmark text"))
print("dense_shape:", r["dense"].shape)
PY

echo "[5/5] container memory snapshot (capture manually for results)"
docker stats --no-stream --format '{{.Name}} {{.MemUsage}}'

echo "Smoke test complete. Stop with: docker compose -f '$CONFIG' down"
