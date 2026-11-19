# Model support matrix (documented, not tested)

Legend: **Documented** = stated in official docs/config; **Untested** = not run
in this milestone; **Blocked** = cannot run on this machine/config.

Model identifiers are copied from SIE's `packages/sie_server/models/*.yaml` and
the official docs. No identifier was invented.

| sie_id | Primitive | Input | Key config | Approx. largest weight artifact (HF API, 2026-11-19) | Bundle / image | CPU status here |
|---|---|---|---|---|---|---|
| `sentence-transformers/all-MiniLM-L6-v2` | encode | text, max_seq 256 | dense dim 384, mean pooling, normalized | 90.9 MB | `default` / `latest-cpu-default`, `sentence_transformer` adapter | Documented; **Untested** |
| `BAAI/bge-m3` | encode + score | text, max_seq 8192 | dense 1024, sparse 250002, multivector 1024 | 2.27 GB | `default` / `latest-cpu-default`, `bge_m3_flash` / `bge_m3_flag` | Documented; **Blocked** — size exceeds available RAM |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | score | text, max_seq 512 | `bert_flash_cross_encoder` | 91.0 MB | `default` / `latest-cpu-default` | Documented; **Untested** |
| `urchade/gliner_multi-v2.1` | extract (NER) | text, max_seq 384 | `gliner` adapter, zero-shot labels | 1.16 GB | `default` / `latest-cpu-default` | Documented; **Blocked by gate** (size vs RAM) |
| `openai/whisper-large-v3-turbo` | extract (audio) | audio | `whisper.adapter`, float16 | 1.62 GB | listed in `default` bundle | Documented; **Untested**, CPU feasibility unknown |
| `docling` (`superlinked/docling-artifacts`) | extract (document) | document/images | profiles `default` (embedded text) and `ocr` (rasterize + OCR); max 100 pages, 16 MB, 90 s timeout | not measured | `default` / `latest-cpu-default`, `docling.adapter` | Born-digital parsing documented; **Untested**; OCR profile untested |
| `microsoft/Florence-2-base` | extract (vision/OCR) | images | `<OCR>` / `<OCR_WITH_REGION>` | not measured | `default` bundle lists `florence2` | Flat-text image OCR documented; **Untested** |
| `zai-org/GLM-OCR`, `lightonai/LightOnOCR-2-1B`, `PaddlePaddle/PaddleOCR-VL-1.5`, `opendatalab/MinerU2.5-Pro-2604-1.2B` | extract (OCR VLM) | images | dedicated OCR models | not measured | documented on `latest-cuda12-sglang-vision-extract` / `latest-cuda12-transformers5` | **Blocked** — require non-CPU bundles; no NVIDIA GPU |
| `Qwen/Qwen3-Reranker-4B` | score | text, max_seq 32768 | `qwen2_flash_cross_encoder`, fused Triton kernels, CUDA graphs | 4.06 GB | GPU-oriented profile | **Blocked** — GPU techniques and size |
| `Qwen/Qwen3-0.6B` via `generate` | generate | text | SGLang | not measured | `latest-cuda12-sglang` | **Blocked** — requires NVIDIA GPU |

## Multilingual notes

- `BAAI/bge-m3`: documented multilingual flagship (dense + sparse).
- `urchade/gliner_multi-v2.1`: documented multilingual NER (100+ languages).
- `sentence-transformers/all-MiniLM-L6-v2` and `cross-encoder/ms-marco-MiniLM-L-6-v2`: English-oriented; Hindi/Hinglish quality untested.
- `convaiinnovations/laya-multilingual`, `knowledgator/gliclass-multilang-mini`, `fastino/GLiNER2.5-multi-Decide` exist with multilingual claims in the repo/config but were not part of this milestone's test plan and are untested.

## Telemetry/privacy configuration (documented)

- From SIE 0.13.0 telemetry is off by default; opt-out: `DO_NOT_TRACK=1` or `SIE_TELEMETRY_DISABLED=1`.
- Experiment config sets both opt-outs, binds to localhost, and uses a named HF cache volume.
