#!/usr/bin/env python3
"""SIE GLiNER extraction benchmark (M001.3.1). NOT executed yet.

Reports TWO separate metric families:

1. Field-presence: was the expected field label extracted at all?
2. Field-value normalized exact match: did an extracted span equal the
   manually labelled value after the documented normalization rules?

Neither metric measures agreement detection, negation handling, legal
enforceability or factual correctness. The SDK is imported lazily so pure
helpers can be unit-tested without sie-sdk installed.

Usage (from repository root, after an authorized smoke test):
  python experiments/sie-feasibility/scripts/benchmark_extract.py \
      --model urchade/gliner_multi-v2.1 \
      --data experiments/sie-feasibility/data/extraction_samples.jsonl \
      --out experiments/sie-feasibility/results
"""
import argparse
import json
import re
from pathlib import Path

LABELS = ["buyer", "supplier", "product", "quantity", "unit_price",
          "currency", "payment_terms", "delivery_commitment"]

# Transparent, documented normalization rules only. No translation, no guessing.
PUNCTUATION_TO_STRIP = ".,!?;:'\"()[]{}—–|/\\"
CURRENCY_ALIASES = {"rs": "inr", "rupees": "inr", "rupee": "inr", "₹": "inr"}
NORMALIZATION_RULES = [
    "trim leading/trailing whitespace",
    "collapse internal whitespace runs to one space",
    "casefold (Unicode-aware lowercase)",
    "remove documented punctuation characters: " + PUNCTUATION_TO_STRIP,
    "for the currency field only, map explicit aliases rs/rupees/rupee/₹ to inr",
    "no translation and no inferred or guessed values",
]


def normalize_value(value, label=None):
    """Normalize a span or ground-truth value using only documented rules."""
    if value is None:
        return None
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    text = text.casefold()
    text = "".join(ch for ch in text if ch not in PUNCTUATION_TO_STRIP).strip()
    if label == "currency" and text in CURRENCY_ALIASES:
        text = CURRENCY_ALIASES[text]
    return text


def prf(tp, fp, fn):
    """Precision, recall and F1 from counts; None when undefined."""
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    if precision is not None and recall is not None and (precision + recall):
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = None
    return {
        "precision": round(precision, 3) if precision is not None else None,
        "recall": round(recall, 3) if recall is not None else None,
        "f1": round(f1, 3) if f1 is not None else None,
        "tp": tp, "fp": fp, "fn": fn,
    }


def _entities(predictions, sample_id, label=None):
    """Extract entity dicts for one sample, optionally filtered by label."""
    rows = predictions.get(sample_id, []) or []
    return [e for e in rows if e.get("label") in LABELS and (label is None or e.get("label") == label)]


def field_presence_counts(samples, predictions):
    """TP/FP/FN over field labels (does not inspect extracted values)."""
    tp = fp = fn = 0
    for s in samples:
        truth = {k for k, v in s["ground_truth"].items()
                 if k in LABELS and v is not None}
        pred = {e["label"] for e in _entities(predictions, s["id"]) if e.get("label")}
        tp += len(truth & pred)
        fp += len(pred - truth)
        fn += len(truth - pred)
    return tp, fp, fn


def field_value_counts(samples, predictions):
    """TP/FP/FN over normalized extracted values against ground truth."""
    tp = fp = fn = 0
    for s in samples:
        for label in LABELS:
            truth = s["ground_truth"].get(label)
            spans = [e.get("text") for e in _entities(predictions, s["id"], label)
                     if e.get("text") is not None]
            if truth is None:
                # A value predicted where the label says none belongs: false positive.
                fp += len(spans)
                continue
            expected = normalize_value(truth, label)
            matched = any(normalize_value(span, label) == expected for span in spans)
            tp += 1 if matched else 0
            fn += 0 if matched else 1
            fp += sum(1 for span in spans if normalize_value(span, label) != expected)
    return tp, fp, fn


def evaluate(samples, predictions):
    """Pure evaluation function used by both the CLI and unit tests.

    Only samples with a successful inference result are in `predictions`.
    Failed samples are excluded from the metric counts; see execution_status
    and METRICS_SCOPE_NOTE for how that affects end-to-end interpretation.
    """
    evaluated = [s for s in samples if s["id"] in predictions]
    return {
        "field_presence": prf(*field_presence_counts(evaluated, predictions)),
        "field_value_normalized_exact": prf(*field_value_counts(evaluated, predictions)),
    }


def execution_status(attempted, successful, failures):
    """EXECUTED / PARTIAL / FAILED from inference outcomes."""
    if attempted <= 0 or successful <= 0:
        return "FAILED"
    if failures > 0:
        return "PARTIAL"
    return "EXECUTED"


METRICS_SCOPE_NOTE = (
    "Metrics are computed only over samples with successful inference. "
    "Failed samples are excluded from precision/recall/F1 counts but are "
    "reported separately; therefore these metrics are conditional on inference "
    "success and are NOT end-to-end accuracy. Always read them together with "
    "attempted/successful/failed counts and execution_status. "
    "Neither metric measures agreement detection or factual correctness."
)


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

    try:
        from sie_sdk import SIEClient
        from sie_sdk.types import Item
    except ImportError as exc:
        print(f"BLOCKED: sie-sdk unavailable ({exc}). No inference was run.")
        return 2

    if not samples:
        print("FAILED: dataset contains no samples")
        return 2

    client = SIEClient("http://127.0.0.1:8080")
    predictions, failures, per_sample = {}, 0, []
    for s in samples:
        try:
            res = client.extract(args.model, Item(text=s["text"]), labels=LABELS)
            entities = res.get("entities", []) or []
            predictions[s["id"]] = entities
            per_sample.append({
                "id": s["id"],
                "status": "SUCCESS",
                "predicted_labels": sorted({e.get("label") for e in entities if e.get("label") in LABELS}),
                "expected_labels": sorted({k for k, v in s["ground_truth"].items()
                                           if k in LABELS and v is not None}),
            })
        except Exception as exc:
            failures += 1
            detail = f"{type(exc).__name__}: {exc}"
            per_sample.append({"id": s["id"], "status": "FAILED", "error": detail})
            print(f"sample {s['id']} failed: {detail}")

    successful = len(samples) - failures
    result = {
        "status": execution_status(len(samples), successful, failures),
        "model": args.model,
        "attempted_samples": len(samples),
        "successful_inference_samples": successful,
        "failed_inference_samples": failures,
        "metrics": evaluate(samples, predictions),
        "metrics_scope_note": METRICS_SCOPE_NOTE,
        "normalization_rules": NORMALIZATION_RULES,
        "per_sample": per_sample,
        "caveat": "Field presence and normalized value correctness are NOT agreement-detection accuracy, "
                  "negation handling, or factual correctness. No translation is performed.",
    }
    out = Path(args.out) / "extract-results.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
