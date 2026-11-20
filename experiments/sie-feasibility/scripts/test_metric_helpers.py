#!/usr/bin/env python3
"""Pure-helper unit tests for the SIE feasibility harness (M001.3.1).

These tests import only standard-library code; sie-sdk is not required and
no inference is performed.

Run from repository root:
  python -m unittest discover -s experiments/sie-feasibility/scripts -p 'test_*.py' -v
"""
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import benchmark_encode as enc  # noqa: E402
import benchmark_extract as ext  # noqa: E402


class TestNormalization(unittest.TestCase):
    def test_whitespace_case_punctuation(self):
        self.assertEqual(ext.normalize_value("  240  Rupees  per  Carton.  "),
                         "240 rupees per carton")

    def test_currency_alias_only_for_currency_field(self):
        self.assertEqual(ext.normalize_value("RS.", "currency"), "inr")
        self.assertEqual(ext.normalize_value("₹", "currency"), "inr")
        self.assertEqual(ext.normalize_value("240 Rs", "unit_price"), "240 rs")
        self.assertEqual(ext.normalize_value("240 Rs", "currency"), "240 rs")

    def test_no_translation(self):
        self.assertEqual(ext.normalize_value("240 रुपये प्रति कार्टन"),
                         "240 रुपये प्रति कार्टन")

    def test_none(self):
        self.assertIsNone(ext.normalize_value(None))


class TestPRF(unittest.TestCase):
    def test_known(self):
        self.assertEqual(ext.prf(4, 2, 4), {
            "precision": 0.667, "recall": 0.5, "f1": 0.571,
            "tp": 4, "fp": 2, "fn": 4,
        })

    def test_undefined(self):
        r = ext.prf(0, 0, 0)
        self.assertIsNone(r["precision"])
        self.assertIsNone(r["f1"])


class TestExtractionMetrics(unittest.TestCase):
    samples = [
        {"id": "s1", "ground_truth": {"buyer": "Metro Traders",
                                       "unit_price": "240 rupees per carton",
                                       "currency": "INR", "supplier": None}},
        {"id": "s2", "ground_truth": {"buyer": None, "supplier": "Shree Agro",
                                       "unit_price": None, "currency": None}},
    ]

    def test_presence_and_value_are_separate(self):
        predictions = {
            "s1": [
                {"label": "buyer", "text": "wrong buyer"},
                {"label": "unit_price", "text": "240  RUPEES per carton."},
                {"label": "currency", "text": "RS."},
            ],
            "s2": [{"label": "supplier", "text": "Shree Agro"}],
        }
        m = ext.evaluate(self.samples, predictions)
        self.assertEqual(m["field_presence"]["tp"], 4)
        self.assertEqual(m["field_presence"]["fp"], 0)
        self.assertEqual(m["field_presence"]["fn"], 0)
        # buyer present but wrong value -> presence TP, value FN + FP
        self.assertEqual(m["field_value_normalized_exact"]["tp"], 3)
        self.assertEqual(m["field_value_normalized_exact"]["fn"], 1)
        self.assertEqual(m["field_value_normalized_exact"]["fp"], 1)

    def test_false_positive_when_no_truth(self):
        predictions = {"s1": [], "s2": [{"label": "buyer", "text": "nobody"}]}
        m = ext.evaluate(self.samples, predictions)
        self.assertEqual(m["field_presence"]["fp"], 1)
        self.assertEqual(m["field_value_normalized_exact"]["fp"], 1)


class TestEncodeHelpers(unittest.TestCase):
    def test_percentile_linear(self):
        self.assertAlmostEqual(enc.percentile([1, 2, 3, 4], 0.95), 3.85)
        self.assertAlmostEqual(enc.percentile([10, 20, 30, 40, 50], 0.95), 48.0)

    def test_percentile_single_and_invalid(self):
        self.assertEqual(enc.percentile([7], 0.95), 7)
        with self.assertRaises(ValueError):
            enc.percentile([], 0.95)
        with self.assertRaises(ValueError):
            enc.percentile([1, 2], 1.5)

    def test_iterations_validation(self):
        self.assertEqual(enc.validate_iterations(1), 1)
        for bad in (0, -1, 1.5, True, "5"):
            with self.assertRaises(ValueError):
                enc.validate_iterations(bad)


if __name__ == "__main__":
    unittest.main()
