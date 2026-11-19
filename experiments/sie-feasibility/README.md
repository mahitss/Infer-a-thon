# SIE feasibility experiment kit (M001.3)

Status: **BLOCKED at resource gate — no experiment executed.**

This directory contains reproducible scripts, synthetic data and result
placeholders for the SIE feasibility study. It contains **no application
code, model weights, caches, credentials or Docker images**.

## Contents

- `environment-report.md` — observed hardware/OS/Docker/Python/Ollama diagnostics.
- `model-support-matrix.md` — documented model capabilities; untested items marked as such.
- `config/sie-cpu.yml` — intended server configuration (localhost-only, telemetry off, persistent HF cache).
- `data/multilingual_corpus.jsonl` — synthetic EN/HI/Hinglish retrieval corpus with labels.
- `data/extraction_samples.jsonl` — synthetic extraction examples with manually labelled ground truth.
- `scripts/env_audit.ps1` — re-run the Phase 1 environment audit (no secrets printed).
- `scripts/run_smoke_test.sh` — start the documented CPU image locally with telemetry disabled.
- `scripts/benchmark_encode.py` — encode/retrieval benchmark (MiniLM, bge-m3).
- `scripts/benchmark_score.py` — reranker benchmark.
- `scripts/benchmark_extract.py` — GLiNER extraction precision/recall.
- `results/resource-gate.json` — machine-readable gate decision.
- `results/benchmark-results.json` — placeholders; every measurement is `null` because nothing ran.
- `results/blocked-log.md` — failure/blocked record with sensitive information removed.

## How to unblock (requires approval)

1. Start Docker Desktop (no change to its resource allocations) and confirm `GET /readyz` path is reachable only on localhost.
2. Re-run `powershell -File scripts/env_audit.ps1` at a time when at least 8 GB RAM is available.
3. If the gate passes, run `bash scripts/run_smoke_test.sh`, then the three benchmark scripts, writing raw results into `results/`.
4. Never report a measurement that was not actually produced by these scripts.

## Safety rules used throughout

- Bind the service to `127.0.0.1` only; never publish port 8080 publicly.
- Set `DO_NOT_TRACK=1` and `SIE_TELEMETRY_DISABLED=1`.
- Use a named Docker volume for the Hugging Face cache; never commit it.
- Use synthetic data only; no real commercial evidence.
