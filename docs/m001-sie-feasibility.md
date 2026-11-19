# M001.3 — SIE Feasibility & Multilingual Benchmark

**Status:** **BLOCKED at Phase 3 (resource gate). No SIE smoke test or benchmark was executed.**
**Date:** 2026-11-19
**Branch:** `research/m001-sie-feasibility`
**Baseline commit:** `8d7f506424a01c7d66fedf980e1a73752f1f05a5`

> This is a research/experimentation deliverable, not application code. Every
> result below is either **observed** (environment diagnostics, official
> documentation) or **not tested**. No inference numbers are reported because
> no inference was run. Model names and capabilities are taken from official
> SIE documentation and repository configuration — none were invented.

## Phase 1 — Environment report (observed)

| Item | Observed value |
|------|----------------|
| CPU | AMD Ryzen 5 7520U with Radeon Graphics, 4 physical cores / 8 logical processors |
| Physical RAM | 16,023,164 KB ≈ **15.28 GB** |
| Available RAM | 2,285 MB → 2,898 MB across two samples ≈ **2.23–2.83 GB available** |
| GPU | AMD Radeon(TM) Graphics (integrated), driver 32.0.21045.16010, AdapterRAM reported 512 MB (shared memory). **No NVIDIA/CUDA GPU.** |
| Windows | Windows 11 Home Single Language, 10.0.26200 (build 26200), 64-bit |
| WSL2 | Installed. Default version 2. Distribution `docker-desktop` present, **State: Stopped** |
| Docker Desktop CLI | Client 29.9.3, API 1.56, Compose v5.7.0, context `desktop-linux` |
| Docker Linux engine | **NOT READY** — `docker version` / `info` / `images` / `ps -a` all fail: `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine ... The system cannot find the file specified.` No Docker Desktop process running. |
| Disk (C:) | 475.3 GB total, **154.85 GB free** |
| Docker inventory | Unavailable (daemon not running) |
| Port 8080 | **No listener** — free |
| Python | 3.13.5 at `C:\Users\pc\AppData\Local\Programs\Python\Python313\python.exe`; `py` launcher also lists CPython 3.14.4 and 3.12.13; `python -m venv` available; pip available |
| Ollama | Installed, v0.40.16. Local models: `gemma4:31b-cloud` (cloud, no local size), `gemma3:4b` (3.4 GB), `qwen3.5:4b` (3.3 GB) |
| `.wslconfig` | Absent (no custom WSL memory allocation) |

No environment variables were printed. No Windows settings, WSL installation, drivers, or Docker resource allocations were changed.

## Phase 2 — Official SIE investigation (documented findings)

Sources: [quickstart](https://superlinked.com/docs/quickstart), [extract](https://superlinked.com/docs/extract), [OCR](https://superlinked.com/docs/extract/ocr), [model catalog](https://superlinked.com/models), [superlinked/sie](https://github.com/superlinked/sie), `bundles/default.yaml`, and per-model YAML configs in `packages/sie_server/models/`.

### Image/bundle facts
- CPU image: `ghcr.io/superlinked/sie-server:latest-cpu-default`; readiness endpoint `GET /readyz` → `ok`; server default port 8080; models load on first request.
- `bundles/default.yaml` (the default bundle used by the CPU image) lists adapters including `sentence_transformer`, `bge_m3_flash`, `bge_m3_flag`, `bert_flash_cross_encoder`, `gliner`, `gliner2`, `glirel`, `gliclass`, `gliformer`, `laya`, `whisper.adapter`, `docling.adapter`, `florence2`, `paddleocr_vl`, `mineru_vl`, `colbert`, `splade_flash`, `siglip`.
- **Bundle presence ≠ runnable on CPU.** The README states Docker images are bundle-specific so incompatible model families stay isolated; the `default` image intentionally does not advertise the `sglang-vision-extract` / `transformers5` families. Qwen3-Reranker-4B's default profile uses fused Triton kernels and CUDA graphs (GPU-only techniques). Generation requires `ghcr.io/superlinked/sie-server:latest-cuda12-sglang`, which needs NVIDIA GPUs.
- SDK compatibility: Python `pip install sie-sdk`, `SIEClient("http://localhost:8080")`; TypeScript `@superlinked/sie-sdk`. `encode`, `score`, `extract`, `generate` methods documented. `sie-server[local]` native install requires Python 3.12 (host has 3.13.5; the repo's `py` launcher offers 3.12.13).

### Model identifiers, inputs and first-load sizes
Sizes are the largest weight artifact reported by the Hugging Face model API on 2026-11-19; approximate, not measured locally.

| sie_id / hf_id | Task | Input | Dimensions / output | Approx. first-load artifact |
|---|---|---|---|---|
| `sentence-transformers/all-MiniLM-L6-v2` | encode | text, max seq 256 | dense 384 | ~90.9 MB (docs: ~90 MB) |
| `BAAI/bge-m3` | encode + score | text, max seq 8192 | dense 1024, sparse 250002, multivector 1024 | ~2.27 GB (docs: ~2.3 GB) |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | score | text, max seq 512 | cross-encoder logits | ~91.0 MB |
| `urchade/gliner_multi-v2.1` | extract (zero-shot NER) | text, max seq 384 | entities with label, text, score, start, end | ~1.16 GB |
| `openai/whisper-large-v3-turbo` | extract (transcription) | audio | `data` with transcription | ~1.62 GB |
| `docling` (`superlinked/docling-artifacts`) | extract (document) | document (PDF/DOCX/HTML...), images | `data.markdown`, `data.document`; profiles `default` and `ocr` | artifact size not measured |
| `Qwen/Qwen3-Reranker-4B` | score | text, max seq 32768 | rerank scores | ~4.06 GB; GPU-oriented profile |

- Multilingual retrieval: `BAAI/bge-m3` is the documented multilingual flagship (dense + sparse). `all-MiniLM-L6-v2` is an English sentence embedder. `urchade/gliner_multi-v2.1` is documented as multilingual NER across 100+ languages.
- Speech-to-text: Whisper adapter is listed in the default bundle, but **not tested**. `whisper-large-v3-turbo` requires ~1.62 GB and audio input; feasibility on this CPU-only laptop is unverified.
- OCR: dedicated OCR models (GLM-OCR, LightOnOCR-2, PaddleOCR-VL-1.5, MinerU2.5) are documented for **other image bundles** (`latest-cuda12-sglang-vision-extract` / `latest-cuda12-transformers5`). `docling` is in the default bundle: `default` profile parses born-digital PDFs using embedded text (no OCR); `ocr` profile rasterizes and runs OCR. Both are untested.
- Generate: requires the CUDA SGLang image; **not available** on this machine. It is not the same as an Ollama process and must not be described as SIE Generate.

### Telemetry / privacy (documented)
- From SIE 0.13.0 telemetry is off unless `SIE_TELEMETRY_ENABLED=1`; earlier releases default to on. Opt-out: `SIE_TELEMETRY_DISABLED=1` or `DO_NOT_TRACK=1` (always win), or `SIE_TELEMETRY_ENABLED=0`. Endpoint `https://telemetry.superlinked.com/api/telemetry`, overridable via `SIE_TELEMETRY_URL`.
- Event fields: random `worker_id`, timestamp, event type, version, variant, OS/arch, GPU names, deployment env. No request data, hostnames, or file paths; receiver derives coarse location from source IP and does not store the address.
- Planned experiment configuration sets `DO_NOT_TRACK=1` and `SIE_TELEMETRY_DISABLED=1`, binds to `127.0.0.1:8080:8080`, uses a named volume for the HF cache, and uses synthetic data only.

## Phase 3 — Resource gate (observed → FAILED)

| Gate criterion | Requirement | Observed | Verdict |
|---|---|---|---|
| Physical memory | Enough headroom for container + model | 15.28 GB total, only 2.23–2.83 GB available | **FAIL** |
| Docker/WSL memory | Engine running with usable memory | WSL distro `docker-desktop` stopped; daemon unreachable; no `.wslconfig` | **FAIL** |
| Host disk | Space for image + model cache | 154.85 GB free | PASS |
| Network | Docs/registry reachable | superlinked.com HTTP 200, github.com HTTP 200, ghcr.io/v2 responded (405 to HEAD, expected for a registry) | PASS |
| Linux Docker engine | Ready | `npipe:////./pipe/dockerDesktopLinuxEngine` missing | **FAIL** |

**Decision: STOP before pulling any image or model.** The largest required model for the multilingual benchmark (`BAAI/bge-m3`, ~2.27 GB) alone exceeds currently available RAM; the Docker engine is not running. No downloads, container starts, or inference calls were made.

## Phases 4–9 — BLOCKED (not executed)

| Phase | Intended test | Status | Exact blocker |
|---|---|---|---|
| 4 — Smoke test | `/readyz`, SDK connect, model metadata, inference | **BLOCKED** | Docker Linux engine unavailable; resource gate failed |
| 5 — Encode | MiniLM then bge-m3; EN/HI/Hinglish retrieval | **BLOCKED** | No SIE server; bge-m3 ~2.27 GB > available RAM |
| 6 — Score | `cross-encoder/ms-marco-MiniLM-L-6-v2` rerank | **BLOCKED** | No SIE server; multilingual Qwen3 reranker is GPU-oriented (~4.06 GB) |
| 7 — Extract | `urchade/gliner_multi-v2.1` GLiNER fields | **BLOCKED** | No SIE server; model ~1.16 GB vs ~2.5 GB available |
| 8 — OCR/audio | docling default/ocr, whisper | **BLOCKED** | No SIE server; dedicated OCR VLMs require non-CPU image bundles; no NVIDIA GPU |
| 9 — Generate | SIE Generate vs Ollama | **BLOCKED (documented)** | SIE Generate requires CUDA SGLang image; no NVIDIA GPU. Ollama is installed with 4B models but was not used for this milestone |

No success metrics, latencies, accuracies, or memory measurements are reported. See [results/blocked-log.md](../experiments/sie-feasibility/results/blocked-log.md) for the failure record and [results/resource-gate.json](../experiments/sie-feasibility/results/resource-gate.json) for machine-readable gate data.

## Phase 10 — Artifacts

- [Experiment index](../experiments/sie-feasibility/README.md)
- [Environment report](../experiments/sie-feasibility/environment-report.md)
- [Model support matrix](../experiments/sie-feasibility/model-support-matrix.md)
- [Run configuration (localhost, telemetry off)](../experiments/sie-feasibility/config/sie-cpu.yml)
- [Synthetic multilingual corpus](../experiments/sie-feasibility/data/multilingual_corpus.jsonl)
- [Synthetic extraction examples with ground truth](../experiments/sie-feasibility/data/extraction_samples.jsonl)
- Reproducible scripts: `env_audit.ps1`, `run_smoke_test.sh`, `benchmark_encode.py`, `benchmark_score.py`, `benchmark_extract.py`
- Raw results: `results/resource-gate.json`, `results/benchmark-results.json` (all measurements `null` — not tested), `results/blocked-log.md`

No weights, caches, credentials, or Docker images are committed.

## Phase 11 — Technical recommendation (evidence-based, provisional)

Answers are conditioned on the resource gate failing; they are **documentation-based hypotheses**, not measured conclusions.

1. **Can SIE run locally on our hardware?** Not demonstrated. The CPU image is documented for x86 Linux and should be technically compatible with this x86 laptop under Docker Desktop/WSL2, but the engine is not running and available RAM is too low. Evidence: Phase 1/3. **Verdict: UNVERIFIED / currently BLOCKED.**
2. **Which primitives work locally?** Docs indicate `encode`, `score`, `extract` are in the CPU default bundle; `generate` requires the CUDA image. Actual local support is untested. Evidence: `bundles/default.yaml`, quickstart.
3. **Best multilingual model?** `BAAI/bge-m3` is the documented multilingual flagship with dense+sparse output; untested here. `all-MiniLM-L6-v2` is English-oriented. Evidence: model configs and docs. **No measured winner.**
4. **Is reranking affordable on CPU?** Unknown. The small `ms-marco-MiniLM-L-6-v2` reranker (~91 MB) is the only CPU-plausible candidate; the multilingual `Qwen/Qwen3-Reranker-4B` (~4.06 GB, CUDA-graph/Triton profile) is not. Evidence: model configs, HF sizes.
5. **OCR/transcription without GPU?** Born-digital document parsing via `docling` `default` profile is a plausible CPU path; scanned/image OCR via dedicated VLM models is documented on GPU/vision bundles only; Whisper transcription is in the default bundle but its CPU feasibility is untested. Evidence: OCR docs, bundle list, model config.
6. **Does generation need a separate runtime?** SIE Generate requires a CUDA SGLang image, so it cannot run here. Ollama (v0.40.16) is already installed with `gemma3:4b` and `qwen3.5:4b`; it could be a separate local reasoning layer, but model loading was not tested. It must be labelled Ollama, not SIE Generate.
7. **Can the system remain ₹0?** Self-hosted SIE is open source; no spend is required if CPU models suffice and Ollama is used for generation. However, GPU-only OCR/generation would require either hardware we lack or a paid service. **₹0 is plausible but unproven for the full workflow.**
8. **What must be simplified/replaced?** Likely: drop dedicated VLM OCR (use docling default + manual review for scans), use small English/Hinglish embeddings instead of bge-m3 if RAM stays low, use the small cross-encoder reranker or skip reranking, and use Ollama for agent reasoning.
9. **Architecture decisions to change?** The M001 architecture already says "verify SIE model/hosting path before implementation." This milestone confirms that gate remains **open**. ADR-001's modular monolith and repository-interface abstraction for semantic search remain sound; do not hard-code SIE or any model ID into application code until benchmarks exist. Consider adding an ADR for a local-generation fallback (Ollama) and a CPU-only capability matrix.

## Phase 12 — Verification

- Inspected all modified/new files before commit.
- Environment diagnostics executed with exit codes recorded in `environment-report.md`.
- No experiment was run, so no benchmark reproducibility claim is made; scripts are provided for a future unblocked run.
- Secret scan: no credentials/API keys/customer data committed.
- Link validation, `git diff --check`, and commit inspection are recorded in the delivery report to the Product Owner.
- **Result: BLOCKED, not failed silently.** Nothing was presented as tested when it was not.

## Outstanding work / next gates

- Approval to start Docker Desktop (without changing resource allocations) and re-run the resource gate at a time when ≥8 GB RAM is available.
- Approval to pull `ghcr.io/superlinked/sie-server:latest-cpu-default` and download only the ~90 MB MiniLM model first.
- Actual EN/HI/Hinglish encode, score and GLiNER extract benchmarks.
- Official 2026-12-05 brief fit review and Product Owner approval remain open from M001.
