#!/usr/bin/env python3
"""Dataset-validation and real CLI-outcome tests (M001.3.4).

The SDK is mocked only at the test boundary. These tests verify exit codes and
artifact contents; they do NOT demonstrate real SIE functionality.
"""
import contextlib
import io
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import benchmark_extract as ext  # noqa: E402


SAMPLES = [
    {"id": "a", "text": "Buyer Alpha confirmed 240 rupees.", "ground_truth": {"buyer": "Alpha"}},
    {"id": "b", "text": "Supplier Beta offered 30 days.", "ground_truth": {"supplier": "Beta"}},
    {"id": "c", "text": "Delivery on 12 December.", "ground_truth": {"delivery_commitment": "12 December"}},
]


def fake_sdk(responses, tracker):
    class FakeItem:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeClient:
        def __init__(self):
            self.index = 0

        def extract(self, model, item, labels):
            response = responses[self.index]
            self.index += 1
            tracker["extract_calls"] += 1
            if isinstance(response, Exception):
                raise response
            return response

    sdk = types.ModuleType("sie_sdk")
    sdk_types = types.ModuleType("sie_sdk.types")
    sdk_types.Item = FakeItem

    def client_factory(url):
        tracker["client_created"] = True
        return FakeClient()

    sdk.SIEClient = client_factory
    return {"sie_sdk": sdk, "sie_sdk.types": sdk_types}


def good(label, text):
    return {"entities": [{"label": label, "text": text, "score": 0.9, "start": 0, "end": len(text)}]}


def run_cli(data_path, out_dir):
    with mock.patch.object(sys, "argv", ["benchmark_extract.py", "--data", str(data_path), "--out", str(out_dir)]):
        with contextlib.redirect_stdout(io.StringIO()):
            return ext.main()


class TestDatasetValidation(unittest.TestCase):
    def test_valid_dataset(self):
        samples, error = ext.validate_dataset(SAMPLES)
        self.assertIsNone(error)
        self.assertEqual(len(samples), 3)

    def test_duplicate_ids_rejected(self):
        rows = SAMPLES + [dict(SAMPLES[0])]
        samples, error = ext.validate_dataset(rows)
        self.assertIsNone(samples)
        self.assertIn("duplicate id", error)

    def test_non_object_row_rejected(self):
        _, error = ext.validate_dataset(["not an object"])
        self.assertIn("not a JSON object", error)

    def test_empty_id_and_text_rejected(self):
        _, error = ext.validate_dataset([{"id": "", "text": "x", "ground_truth": {}}])
        self.assertIn("id", error)
        _, error = ext.validate_dataset([{"id": "x", "text": "  ", "ground_truth": {}}])
        self.assertIn("text", error)

    def test_invalid_ground_truth_rejected(self):
        for gt in (None, [], "text", {"unknown_label": "x"},
                   {"buyer": 42}, {"buyer": ""}, {"note": 5}):
            row = {"id": "x", "text": "text", "ground_truth": gt}
            _, error = ext.validate_dataset([row])
            self.assertIsNotNone(error, gt)

    def test_empty_dataset_rejected(self):
        _, error = ext.validate_dataset([])
        self.assertIn("no samples", error)


class TestCLIOutcomes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = self.root / "samples.jsonl"
        self.data.write_text("\n".join(json.dumps(s) for s in SAMPLES) + "\n", encoding="utf-8")
        self.out = self.root / "results"

    def install_sdk(self, responses):
        tracker = {"client_created": False, "extract_calls": 0}
        modules = fake_sdk(responses, tracker)
        old = {name: sys.modules.get(name) for name in modules}
        sys.modules.update(modules)
        self.addCleanup(self.restore_modules, old, modules)
        return tracker

    @staticmethod
    def restore_modules(old, modules):
        for name in modules:
            if old[name] is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old[name]

    def artifact(self):
        return json.loads((self.out / "extract-results.json").read_text(encoding="utf-8"))

    def test_executed_exit_zero_and_artifact(self):
        responses = [good("buyer", "Alpha"), good("supplier", "Beta"),
                     good("delivery_commitment", "12 December")]
        tracker = self.install_sdk(responses)
        code = run_cli(self.data, self.out)
        self.assertEqual(code, ext.EXIT_EXECUTED)
        self.assertEqual(code, 0)
        artifact = self.artifact()
        self.assertEqual(artifact["status"], "EXECUTED")
        self.assertEqual(artifact["attempted_samples"], 3)
        self.assertEqual(artifact["successful_inference_samples"], 3)
        self.assertEqual(artifact["failed_inference_samples"], 0)
        self.assertTrue(tracker["client_created"])

    def test_partial_exit_three_and_artifact(self):
        responses = [good("buyer", "Alpha"), RuntimeError("boom"), good("supplier", "Beta")]
        self.install_sdk(responses)
        code = run_cli(self.data, self.out)
        self.assertEqual(code, ext.EXIT_PARTIAL)
        self.assertNotEqual(code, 0)
        artifact = self.artifact()
        self.assertEqual(artifact["status"], "PARTIAL")
        self.assertEqual(artifact["successful_inference_samples"], 2)
        self.assertEqual(artifact["failed_inference_samples"], 1)

    def test_failed_exit_four_and_artifact(self):
        self.install_sdk([RuntimeError("boom") for _ in SAMPLES])
        code = run_cli(self.data, self.out)
        self.assertEqual(code, ext.EXIT_FAILED)
        artifact = self.artifact()
        self.assertEqual(artifact["status"], "FAILED")
        self.assertEqual(artifact["successful_inference_samples"], 0)
        self.assertEqual(artifact["failed_inference_samples"], 3)

    def test_invalid_jsonl_exit_two(self):
        self.data.write_text("{invalid json\n", encoding="utf-8")
        tracker = self.install_sdk([])
        code = run_cli(self.data, self.out)
        self.assertEqual(code, ext.EXIT_INVALID_DATASET)
        self.assertEqual(code, 2)
        self.assertFalse(tracker["client_created"])
        artifact = self.artifact()
        self.assertEqual(artifact["status"], "FAILED")
        self.assertEqual(artifact["attempted_samples"], 0)
        self.assertIn("invalid dataset", artifact["reason"])

    def test_invalid_row_schema_rejected_before_sdk(self):
        bad = [dict(SAMPLES[0]), dict(SAMPLES[0])]  # duplicate id
        self.data.write_text("\n".join(json.dumps(s) for s in bad) + "\n", encoding="utf-8")
        tracker = self.install_sdk([])
        code = run_cli(self.data, self.out)
        self.assertEqual(code, ext.EXIT_INVALID_DATASET)
        self.assertFalse(tracker["client_created"])
        self.assertEqual(tracker["extract_calls"], 0)
        self.assertIn("duplicate id", self.artifact()["reason"])

    def test_sdk_unavailable_exit_five(self):
        old = sys.modules.get("sie_sdk")
        sys.modules["sie_sdk"] = None
        self.addCleanup(self.restore_single, old)
        code = run_cli(self.data, self.out)
        self.assertEqual(code, ext.EXIT_SDK_UNAVAILABLE)
        self.assertEqual(code, 5)
        artifact = self.artifact()
        self.assertEqual(artifact["status"], "FAILED")
        self.assertIn("sie-sdk unavailable", artifact["reason"])

    @staticmethod
    def restore_single(old):
        if old is None:
            sys.modules.pop("sie_sdk", None)
        else:
            sys.modules["sie_sdk"] = old


if __name__ == "__main__":
    unittest.main()
