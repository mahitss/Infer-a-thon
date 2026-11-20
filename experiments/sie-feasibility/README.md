# SIE feasibility experiment kit (M001.3 / corrected M001.3.1)

Status: **BLOCKED at resource gate — no experiment, registry pull, model download or inference executed.**

This directory contains scripts, synthetic data and result placeholders for the
SIE feasibility study. It contains **no application code, model weights,
caches, credentials or Docker images**.

## Contents

- `environment-report.md` — observed hardware/OS/Docker/Python/Ollama diagnostics.
- `model-support-matrix.md` — documented model capabilities; untested items marked as such.
- `config/sie-cpu.yml` — intended server configuration (localhost-only, telemetry off, persistent HF cache).
- `config/versions.json` — observed model revisions, bundle SHA, and unrecorded version blockers.
- `data/multilingual_corpus.jsonl` — 24-record **pilot smoke corpus** (EN/HI/Hinglish) with labels.
- `data/extraction_samples.jsonl` — 10 synthetic extraction examples with ground truth.
- `scripts/env_audit.ps1` — re-run the Phase 1 environment audit (no secrets printed).
- `scripts/gate_check.py` — pure gate validation (8 GB internal minimum, fixed 10-minute freshness).
- `scripts/generate_resource_gate.py` — writes `resource-gate.json` from real read-only diagnostics; PASS/BLOCKED automatic.
- `scripts/smoke_gate.py` — pre-startup refusal checks, including a LIVE RAM recheck; mocked in tests.
- `scripts/run_smoke_test.sh` — gated local smoke test; refuses before Compose startup; isolated project + cleanup.
- `scripts/benchmark_encode.py` — encode/retrieval benchmark (p95 via linear interpolation).
- `scripts/benchmark_score.py` — reranker benchmark.
- `scripts/benchmark_extract.py` — separate field-presence and field-value exact-match metrics.
- `scripts/test_metric_helpers.py` — unit tests for pure metric/validation helpers (no SDK needed).
- `results/resource-gate.json` — machine-readable gate decision (BLOCKED, with correction notes).
- `results/benchmark-results.json` — placeholders; every measurement `null`.
- `results/blocked-log.md` — blocker record with sensitive information removed.

## How to unblock (requires approval)

1. Start Docker Desktop manually, without changing resource allocations. This script does **not** start it.
2. Generate the gate from live diagnostics: `python experiments/sie-feasibility/scripts/generate_resource_gate.py --out experiments/sie-feasibility/results/resource-gate.json`. Do **not** hand-edit a JSON file to manufacture PASS.
3. The **8 GB** figure is our **internal conservative safety policy for this experiment**, not an official SIE minimum requirement. The freshness window is fixed at **10 minutes** and cannot be widened with an environment variable.
4. Explicitly authorize any image pull: `SIE_IMAGE_PULL_AUTHORIZED=1 bash scripts/run_smoke_test.sh`. The script rechecks **live host RAM** immediately before startup; a previously PASS gate cannot substitute.
5. Run the benchmark scripts from the repository root (paths documented in `docs/m001-sie-feasibility.md`).
6. Never report a measurement that was not actually produced by these scripts.

## Safety rules

- Bind the service to `127.0.0.1` only; never publish port 8080 publicly.
- Set `DO_NOT_TRACK=1` and `SIE_TELEMETRY_DISABLED=1`.
- Use a named Docker volume for the Hugging Face cache; never commit it.
- Use synthetic data only; no real commercial evidence.
- `run_smoke_test.sh` refuses execution when the gate is stale, not PASS, below the threshold, missing engine readiness, or missing explicit pull authorization; it performs a live RAM recheck, uses an isolated Compose project per invocation, installs cleanup before startup, and preserves the named model-cache volume (never `down -v`).

## Reproducibility status

- Image tag `ghcr.io/superlinked/sie-server:latest-cpu-default` is **mutable**; digest not recorded because no pull/manifest inspection occurred.
- `sie-sdk` is not version-pinned; no release number was observed.
- Model `sie_id`s, observed `hf_revision`s and the `default` bundle SHA are in `config/versions.json`.
- These pinning gaps remain a blocker for exact reproduction; no value was invented.

## Corrections recorded in M001.3.1

- RAM: 2.27 GB bge-m3 artifact exceeds the 2.23 GB sample but is below 2.83 GB; overhead unknown; headroom unverified.
- Network: `ghcr.io/v2/` 405 to HEAD = reachability only; registry pull UNVERIFIED.
- Extraction: separate presence and normalized value metrics; no translation/guessing.
- Encoding: valid linear-interpolation p95; iterations ≥ 1; pilot-corpus caveat.
- Smoke test: fresh gate + timestamp + internal 8 GB policy + engine check + explicit pull authorization + cleanup.

## Corrections recorded in M001.3.2

- Gate validation now rejects thresholds below 8 GB, boolean thresholds/RAM, stale or future timestamps, false Docker readiness, and non-PASS status; freshness is fixed at 10 minutes.
- A generator script now produces the gate from real diagnostics; hand-edited gates are never sufficient because the smoke test rechecks live RAM.
- Cleanup is installed before startup, covers partial starts/readiness/SDK/inference failures and interrupts, uses an isolated Compose project, and never deletes the cache volume.
- GLiNER's 1.16 GB artifact is smaller than both RAM samples; its blocker was the overall gate/engine, not its own size. CPU inference remains untested.
- Extraction results now report attempted/successful/failed samples and EXECUTED/PARTIAL/FAILED status; metrics are conditional on inference success.
