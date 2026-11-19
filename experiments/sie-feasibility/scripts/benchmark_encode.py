#!/usr/bin/env python3
"""SIE encode/retrieval benchmark (M001.3.1). NOT executed yet.

Measures first-load duration, warm latency (mean and linearly interpolated
p95), embedding dimensions, top-1 accuracy and top-3 recall.

PILOT CORPUS CAVEAT: the committed 24-record corpus is a pilot smoke corpus,
NOT sufficient evidence for general multilingual quality. It covers a narrow
slice of English, Hindi and Hinglish business messages and lacks hard
negatives, paraphrases and conflicting-evidence pairs. Any result from it is
diagnostic only.

This measures retrieval relevance. Semantic similarity is NOT factual
correctness. Capture peak container memory separately with `docker stats`.

Usage (from repository root, after an authorized smoke test):
  python experiments/sie-feasibility/scripts/benchmark_encode.py \
      --model sentence-transformers/all-MiniLM-L6-v2 \
      --corpus experiments/sie-feasibility/data/multilingual_corpus.jsonl \
      --iterations 5 --out experiments/sie-feasibility/results
"""
import argparse
import json
import math
import statistics
import time
from pathlib import Path

PILOT_CORPUS_CAVEAT = (
    "Pilot smoke corpus of 24 synthetic records: limited EN/HI/Hinglish coverage; "
    "no hard negatives, paraphrases or conflicting-evidence examples. "
    "Not sufficient evidence for general multilingual quality."
)


def validate_iterations(value):
    """Accept only integers >= 1; reject zero, negatives and non-integers."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("iterations must be an integer >= 1")
    if value < 1:
        raise ValueError("iterations must be >= 1 (zero or negative rejected)")
    return value


def percentile(values, q):
    """Linear-interpolation percentile (numpy 'linear' method), q in [0,1]."""
    if not values:
        raise ValueError("percentile requires at least one value")
    if not 0 <= q <= 1:
        raise ValueError("q must be between 0 and 1")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def load_corpus(path):
    docs, queries = [], []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            (docs if row["type"] == "doc" else queries).append(row)
    return docs, queries


def as_list(vector):
    return vector.tolist() if hasattr(vector, "tolist") else list(vector)


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--iterations", type=int, default=5)
    ap.add_argument("--out", default="../results")
    args = ap.parse_args()

    try:
        iterations = validate_iterations(args.iterations)
    except ValueError as exc:
        print(f"INVALID INPUT: {exc}")
        return 2

    docs, queries = load_corpus(args.corpus)
    if not docs or not queries:
        print("INVALID CORPUS: expected at least one doc and one query")
        return 2

    try:
        from sie_sdk import SIEClient
        from sie_sdk.types import Item
    except ImportError as exc:
        print(f"BLOCKED: sie-sdk unavailable ({exc}). No inference was run.")
        return 2

    client = SIEClient("http://127.0.0.1:8080")

    t0 = time.perf_counter()
    first = client.encode(args.model, Item(text=docs[0]["text"]))
    first_load_s = time.perf_counter() - t0
    dim = len(as_list(first["dense"]))

    latencies = []
    for _ in range(iterations):
        t = time.perf_counter()
        client.encode(args.model, Item(text="warm timing probe"))
        latencies.append((time.perf_counter() - t) * 1000)

    doc_vecs = [as_list(client.encode(args.model, Item(text=d["text"]))["dense"]) for d in docs]

    top1, top3, failures = 0, 0, 0
    for q in queries:
        try:
            qv = as_list(client.encode(args.model, Item(text=q["text"]))["dense"])
            scored = sorted(
                zip([d["id"] for d in docs], [cosine(qv, dv) for dv in doc_vecs]),
                key=lambda pair: pair[1], reverse=True,
            )
            ranked_ids = [doc_id for doc_id, _ in scored]
            expected = set(q["relevant_doc_ids"])
            if ranked_ids[0] in expected:
                top1 += 1
            if expected.intersection(ranked_ids[:3]):
                top3 += 1
        except Exception as exc:
            failures += 1
            print(f"query {q['id']} failed: {type(exc).__name__}: {exc}")

    result = {
        "status": "EXECUTED",
        "model": args.model,
        "corpus": {"path": args.corpus, "records": len(docs) + len(queries),
                   "caveat": PILOT_CORPUS_CAVEAT},
        "iterations": iterations,
        "successful_inference_count": len(docs) + len(queries) + iterations + 1 - failures,
        "first_load_seconds": round(first_load_s, 3),
        "warm_latency_ms_mean": round(statistics.mean(latencies), 2),
        "warm_latency_ms_p95": round(percentile(latencies, 0.95), 2),
        "p95_method": "linear interpolation over sorted samples: (n-1)*0.95",
        "embedding_dimensions": dim,
        "queries": len(queries),
        "top1_accuracy": round(top1 / max(len(queries) - failures, 1), 3),
        "top3_recall": round(top3 / max(len(queries) - failures, 1), 3),
        "failures": failures,
        "note": "Retrieval relevance only; not factual correctness.",
    }
    out = Path(args.out) / "encode-results.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
