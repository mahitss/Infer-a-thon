#!/usr/bin/env python3
"""Gate-safety and extraction-status tests (M001.3.2).

Uses stub command runners; never pulls an image, starts Docker or runs inference.
"""
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_check as gate  # noqa: E402
import smoke_gate  # noqa: E402
import benchmark_extract as ext  # noqa: E402


def stub_runner(argv, ram_mb=16384, docker_ready=True):
    """Return a stub CommandResult for RAM/Docker diagnostics only."""
    joined = " ".join(argv)
    if "AvailableMBytes" in joined or "MemAvailable" in joined:
        return gate.CommandResult(0, f"{ram_mb}\n")
    if argv and argv[0] == "docker" and "version" in joined:
        return gate.CommandResult(0, "29.9.3") if docker_ready else gate.CommandResult(1, "", "engine down")
    raise AssertionError(f"unexpected command in safety test: {argv}")


def valid_gate(now=None, **overrides):
    reference = now or datetime.now(timezone.utc)
    data = {
        "status": "PASS",
        "checked_at": reference.isoformat().replace("+00:00", "Z"),
        "memory_safety_threshold_gb": 8,
        gate.RAM_FIELD: 16.0,
        "docker_engine_ready": True,
    }
    data.update(overrides)
    return data


class TestGateValidation(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)

    def assert_invalid(self, data, fragment):
        ok, errors = gate.validate_gate(data, now=self.now)
        self.assertFalse(ok)
        self.assertTrue(any(fragment in e for e in errors), errors)

    def test_threshold_below_8(self):
        self.assert_invalid(valid_gate(self.now, memory_safety_threshold_gb=7.9), "below internal minimum")

    def test_threshold_one_rejected(self):
        self.assert_invalid(valid_gate(self.now, memory_safety_threshold_gb=1), "below internal minimum")

    def test_threshold_bool_true_rejected(self):
        self.assert_invalid(valid_gate(self.now, memory_safety_threshold_gb=True), "not bool")

    def test_threshold_bool_false_rejected(self):
        self.assert_invalid(valid_gate(self.now, memory_safety_threshold_gb=False), "not bool")

    def test_available_ram_bool_rejected(self):
        self.assert_invalid(valid_gate(self.now, **{gate.RAM_FIELD: True}), "not bool")

    def test_insufficient_ram(self):
        self.assert_invalid(valid_gate(self.now, **{gate.RAM_FIELD: 7.9}), "below threshold")

    def test_stale_timestamp(self):
        stale = (self.now - timedelta(seconds=gate.MAX_GATE_AGE_SECONDS + 1))
        self.assert_invalid(valid_gate(stale), "stale")

    def test_future_timestamp(self):
        future = self.now + timedelta(seconds=60)
        self.assert_invalid(valid_gate(future), "future")

    def test_docker_readiness_false(self):
        self.assert_invalid(valid_gate(self.now, docker_engine_ready=False), "boolean true")

    def test_valid_gate(self):
        ok, errors = gate.validate_gate(valid_gate(self.now), now=self.now)
        self.assertTrue(ok, errors)

    def test_invalid_gate_json(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            handle.write("{not json")
            path = handle.name
        try:
            with self.assertRaises(ValueError):
                gate.load_gate(path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_fixed_freshness_window(self):
        self.assertEqual(gate.MAX_GATE_AGE_SECONDS, 600)
        self.assertFalse(hasattr(gate, "SIE_GATE_MAX_AGE_SECONDS"))


class TestSmokePreflight(unittest.TestCase):
    def test_refuses_before_docker_when_gate_blocked(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            handle.write('{"status": "BLOCKED"}')
            path = handle.name
        try:
            calls = []
            def runner(argv):
                calls.append(argv)
                return gate.CommandResult(0, "")
            ok, reasons = smoke_gate.preflight(path, env={"SIE_IMAGE_PULL_AUTHORIZED": "1"},
                                               runner=runner)
            self.assertFalse(ok)
            self.assertTrue(any("status" in r for r in reasons), reasons)
            self.assertEqual(calls, [], "no command should run for a rejected gate")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_refuses_on_live_low_ram(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            import json
            json.dump(valid_gate(), handle)
            path = handle.name
        try:
            ok, reasons = smoke_gate.preflight(
                path, env={"SIE_IMAGE_PULL_AUTHORIZED": "1"},
                runner=lambda argv: stub_runner(argv, ram_mb=2048),
            )
            self.assertFalse(ok)
            self.assertTrue(any("live available RAM" in r for r in reasons), reasons)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_accepts_valid_gate_with_stubs(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            import json
            json.dump(valid_gate(), handle)
            path = handle.name
        try:
            ok, reasons = smoke_gate.preflight(
                path, env={"SIE_IMAGE_PULL_AUTHORIZED": "1"},
                runner=lambda argv: stub_runner(argv, ram_mb=16384),
            )
            self.assertTrue(ok, reasons)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_shell_precedes_compose_startup(self):
        script = Path(__file__).resolve().parent.joinpath("run_smoke_test.sh").read_text(encoding="utf-8")
        preflight_at = script.index("smoke_gate.py")
        startup_at = script.index("up -d")
        self.assertLess(preflight_at, startup_at)
        self.assertNotIn("SIE_GATE_MAX_AGE_SECONDS", script)
        command_lines = [line for line in script.splitlines()
                         if line.strip().startswith("docker compose")]
        self.assertTrue(any("down" in line for line in command_lines))
        self.assertTrue(all("-v" not in line for line in command_lines))


class TestExtractionStatuses(unittest.TestCase):
    def test_status_values(self):
        self.assertEqual(ext.execution_status(10, 10, 0), "EXECUTED")
        self.assertEqual(ext.execution_status(10, 8, 2), "PARTIAL")
        self.assertEqual(ext.execution_status(10, 0, 10), "FAILED")
        self.assertEqual(ext.execution_status(0, 0, 0), "FAILED")

    def test_wrong_extracted_value_metrics(self):
        samples = [{"id": "x", "ground_truth": {"unit_price": "240 rupees per carton"}}]
        predictions = {"x": [{"label": "unit_price", "text": "999 rupees per carton"}]}
        metrics = ext.evaluate(samples, predictions)
        self.assertEqual(metrics["field_presence"]["tp"], 1)
        self.assertEqual(metrics["field_value_normalized_exact"]["tp"], 0)
        self.assertEqual(metrics["field_value_normalized_exact"]["fn"], 1)
        self.assertEqual(metrics["field_value_normalized_exact"]["fp"], 1)

    def test_failed_samples_excluded_from_metric_counts(self):
        samples = [
            {"id": "ok", "ground_truth": {"currency": "INR"}},
            {"id": "bad", "ground_truth": {"currency": "INR"}},
        ]
        predictions = {"ok": [{"label": "currency", "text": "INR"}]}
        metrics = ext.evaluate(samples, predictions)
        self.assertEqual(metrics["field_presence"]["fn"], 0)
        self.assertEqual(metrics["field_value_normalized_exact"]["tp"], 1)


if __name__ == "__main__":
    unittest.main()
