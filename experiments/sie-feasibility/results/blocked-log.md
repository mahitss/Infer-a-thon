# Blocked / failure log — M001.3

No credentials, customer documents, private transaction data or raw logs with
sensitive content are included. Only diagnostic error text is recorded.

## Resource gate stop (2026-11-19)

- `docker version` exit 1: `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.`
- `docker info` exit 1: same error.
- `docker images` exit 1: same error.
- `docker ps -a` exit 1: same error.
- `wsl.exe --list --verbose`: `docker-desktop` state `Stopped`.
- Available RAM samples: 2,285 MB and 2,898 MB.

**Action taken:** stopped before any `docker pull`, model download or inference
call. No image was pulled; no model weight was downloaded; no container was
started.

## Why this is BLOCKED and not a failed benchmark

A failed benchmark would require a running server and an executed call that
errored. Neither happened. Reporting zero latencies or zero accuracies would
be fabrication. All numeric fields in `benchmark-results.json` are `null`.

## Exact blockers by phase

- Phase 4 smoke test: Docker Linux engine not running.
- Phase 5 encode: no server; `BAAI/bge-m3` ~2.27 GB exceeds the 2.23 GB lower sample but is below the 2.83 GB upper sample; overhead unknown, so verified headroom is insufficient. Docker engine unavailability is an independent blocker.
- Phase 6 score: no server; multilingual `Qwen/Qwen3-Reranker-4B` ~4.06 GB and GPU-oriented profile.
- Phase 7 extract: no server; GLiNER model ~1.16 GB vs ~2.5 GB available.
- Phase 8 OCR/audio: no server; dedicated OCR VLMs require non-CPU image bundles; no NVIDIA GPU.
- Phase 9 generate: SIE Generate requires `latest-cuda12-sglang`; no NVIDIA GPU.

## Potential ₹0 alternatives (untested)

- Start Docker Desktop with existing allocations and re-check against the **internal conservative 8 GB safety policy** (not an official SIE minimum requirement).
- Use only ~90 MB models first (MiniLM encode, ms-marco-MiniLM reranker).
- Use `docling` default profile for born-digital PDFs; defer scanned-document OCR.
- Use already-installed Ollama 4B models as a *separate* reasoning layer; never label it SIE Generate.
- Before any pull, a fresh gate result with status PASS, timestamp, threshold and engine readiness must exist, and `SIE_IMAGE_PULL_AUTHORIZED=1` must be set.

## Corrections recorded in M001.3.1

- RAM claim corrected: 2.27 GB exceeds the lower 2.23 GB sample, is below the 2.83 GB sample; overhead unknown.
- Network claim corrected: `ghcr.io/v2/` HTTP 405 to HEAD is endpoint reachability only; no manifest, layer or blob download was tested; registry pull status UNVERIFIED.
- No Docker, registry pull, model download or inference was performed in M001.3.1.
