#!/usr/bin/env python3
"""Reproducible SIE encode/retrieval benchmark (M001.3). NOT executed yet.

Measures: first-load duration, warm latency, embedding dimensions, top-1
accuracy and top-3 recall on a synthetic EN/HI/Hinglish corpus.

Usage: python benchmark_encode.py --model sentence-transformers/all-MiniLM-L6-v2 \
           --corpus ../data/multilingual_corpus.jsonl --iterations 5 --out ../results/

This measures retrieval relevance only. Semantic similarity is NOT factual correctness.
Capture peak container memory separately with `docker stats --no-stream`.
"""
import argparse
import json
import statistics
import time
from pathlib import Path

from sie_sdk import SIEClient
from sie_sdk.types import Item


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

    docs, queries = load_corpus(args.corpus)
    client = SIEClient("http://127.0.0.1:8080")

    t0 = time.perf_counter()
    first = client.encode(args.model, Item(text=docs[0]["text"]))
    first_load_s = time.perf_counter() - t0
    dim = len(first["dense"].tolist() if hasattr(first["dense"], "tolist") else first["dense"])

    latencies = []
    for _ in range(args.iterations):
        t = time.perf_counter()
        client.encode(args.model, Item(text="warm timing probe"))
        latencies.append((time.perf_counter() - t) * 1000)

    doc_vecs = [client.encode(args.model, Item(text=d["text"]))["dense"] for d in docs]
    doc_vecs = [v.tolist() if hasattr(v, "tolist") else list(v) for v in doc_vecs]

    top1, top3, failures = 0, 0, 0
    for q in queries:
        try:
            qv = client.encode(args.model, Item(text=q["text"]))["dense"]
            qv = qv.tolist() if hasattr(qv, "tolist") else list(qv)
            scored = sorted(
                zip([d["id"] for d in docs], [cosine(qv, dv) for dv in doc_vecs]),
                key=lambda p: p[1], reverse=True,
            )
            ranked_ids = [i for i, _ in scored]
            expected = set(q["relevant_doc_ids"])
            if ranked_ids[0] in expected:
                top1 += 1
            if expected.intersection(ranked_ids[:3]):
                top3 += 1
        except Exception as exc:  # record failures accurately
            failures += 1
            print(f"query {q['id']} failed: {type(exc).__name__}: {exc}")

    result = {
        "model": args.model,
        "successful_inference_count": len(docs) + len(queries) + args.iterations + 1 - failures,
        "first_load_seconds": round(first_load_s, 3),
        "warm_latency_ms_mean": round(statistics.mean(latencies), 2),
        "warm_latency_ms_p95": round(sorted(latencies)[int(0.95 * (len(latencies) - 1))], 2),
        "embedding_dimensions": dim,
        "queries": len(queries),
        "top1_accuracy": round(top1 / max(len(queries) - failures, 1), 3),
        "top3_recall": round(top3 / max(len(queries) - failures, 1), 3),
        "failures": failures,
        "note": "Retrieval relevance only; not factual correctness.",
    }
    out = Path(args.out) / "encode-results.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
