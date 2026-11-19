#!/usr/bin/env python3
"""Reproducible SIE GLiNER extraction benchmark (M001.3). NOT executed yet.

Compares extracted spans to manually labelled ground truth for quantity,
product, unit price, currency, payment terms, delivery commitment, buyer and
supplier. Reports micro precision/recall over field labels.

Extraction of named entities is NOT agreement detection. Negations and
ambiguous acknowledgements are labelled explicitly in the dataset.

Usage: python benchmark_extract.py --model urchade/gliner_multi-v2.1 \
           --data ../data/extraction_samples.jsonl --out ../results/
"""
import argparse
import json
from pathlib import Path

from sie_sdk import SIEClient
from sie_sdk.types import Item

LABELS = ["buyer", "supplier", "product", "quantity", "unit_price",
          "currency", "payment_terms", "delivery_commitment"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="urchade/gliner_multi-v2.1")
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="../results")
    args = ap.parse_args()

    samples = []
    with open(args.data, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                samples.append(json.loads(line))

    client = SIEClient("http://127.0.0.1:8080")
    tp = fp = fn = failures = 0
    per_sample = []
    for s in samples:
        try:
            res = client.extract(args.model, Item(text=s["text"]), labels=LABELS)
            predicted = {e["label"] for e in res["entities"] if e.get("label") in LABELS}
        except Exception as exc:
            failures += 1
            print(f"sample {s['id']} failed: {type(exc).__name__}: {exc}")
            continue
        truth = {k for k, v in s["ground_truth"].items()
                 if k in LABELS and v is not None}
        tp += len(predicted & truth)
        fp += len(predicted - truth)
        fn += len(truth - predicted)
        per_sample.append({"id": s["id"], "predicted": sorted(predicted),
                           "expected": sorted(truth)})

    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    result = {
        "model": args.model,
        "samples": len(samples),
        "successful": len(samples) - failures,
        "micro_precision": round(precision, 3) if precision is not None else None,
        "micro_recall": round(recall, 3) if recall is not None else None,
        "failures": failures,
        "per_sample": per_sample,
        "caveat": "Field-label overlap only; does not measure agreement detection or factual correctness.",
    }
    out = Path(args.out) / "extract-results.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
