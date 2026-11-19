#!/usr/bin/env python3
"""Reproducible SIE score/rerank benchmark (M001.3). NOT executed yet.

Uses the documented CPU reranker cross-encoder/ms-marco-MiniLM-L-6-v2.
Reports top-1 accuracy, original dataset rank vs reranked position, warm
latency and failures. Do not use a model identifier that is not in the
official catalog.

Usage: python benchmark_score.py --model cross-encoder/ms-marco-MiniLM-L-6-v2 \
           --corpus ../data/multilingual_corpus.jsonl --out ../results/
"""
import argparse
import json
import statistics
import time
from pathlib import Path

from sie_sdk import SIEClient
from sie_sdk.types import Item


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="cross-encoder/ms-marco-MiniLM-L-6-v2")
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", default="../results")
    args = ap.parse_args()

    docs, queries = [], []
    with open(args.corpus, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            (docs if row["type"] == "doc" else queries).append(row)

    client = SIEClient("http://127.0.0.1:8080")
    items = [Item(id=d["id"], text=d["text"]) for d in docs]
    original_rank = {d["id"]: i for i, d in enumerate(docs)}

    latencies, top1, failures, movements = [], 0, 0, []
    for q in queries:
        try:
            t = time.perf_counter()
            res = client.score(args.model, Item(text=q["text"]), items)
            latencies.append((time.perf_counter() - t) * 1000)
            ranked = [e["item_id"] for e in sorted(res["scores"], key=lambda e: e["rank"])]
            expected = set(q["relevant_doc_ids"])
            if ranked and ranked[0] in expected:
                top1 += 1
            for rel in expected:
                movements.append({
                    "query": q["id"], "doc": rel,
                    "original_rank": original_rank.get(rel),
                    "reranked_position": ranked.index(rel) if rel in ranked else None,
                })
        except Exception as exc:
            failures += 1
            print(f"query {q['id']} failed: {type(exc).__name__}: {exc}")

    result = {
        "model": args.model,
        "queries": len(queries),
        "successful": len(queries) - failures,
        "top1_accuracy": round(top1 / max(len(queries) - failures, 1), 3),
        "warm_latency_ms_mean": round(statistics.mean(latencies), 2) if latencies else None,
        "failures": failures,
        "rank_movements": movements,
        "multilingual_note": "ms-marco-MiniLM-L-6-v2 is English-oriented; HI/Hinglish results are diagnostic, not quality claims.",
    }
    out = Path(args.out) / "score-results.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
