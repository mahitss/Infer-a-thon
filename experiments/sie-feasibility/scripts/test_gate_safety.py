#!/usr/bin/env python3
"""Gate-safety and extraction-status tests (M001.3.2).

Uses stub command runners; never pulls an image, starts Docker or runs inference.
"""
import json
import math
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml  # noqa: E402
import gate_check as gate  # noqa: E402
import smoke_gate  # noqa: E402
import compose_policy  # noqa: E402
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


class TestFiniteValueRejection(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)

    def assert_gate_bad(self, **overrides):
        ok, errors = gate.validate_gate(valid_gate(self.now, **overrides), now=self.now)
        self.assertFalse(ok, errors)
        return errors

    def test_nan_threshold(self):
        self.assertTrue(any("finite" in e for e in self.assert_gate_bad(memory_safety_threshold_gb=float("nan"))))

    def test_nan_available_ram(self):
        self.assertTrue(any("finite" in e for e in self.assert_gate_bad(**{gate.RAM_FIELD: float("nan")})))

    def test_positive_infinity_threshold_and_ram(self):
        self.assertTrue(any("finite" in e for e in self.assert_gate_bad(memory_safety_threshold_gb=float("inf"))))
        self.assertTrue(any("finite" in e for e in self.assert_gate_bad(**{gate.RAM_FIELD: float("inf")})))

    def test_negative_infinity_threshold_and_ram(self):
        self.assertTrue(any("finite" in e for e in self.assert_gate_bad(memory_safety_threshold_gb=float("-inf"))))
        self.assertTrue(any("finite" in e for e in self.assert_gate_bad(**{gate.RAM_FIELD: float("-inf")})))

    def test_boolean_ram_rejected(self):
        self.assertTrue(any("finite" in e for e in self.assert_gate_bad(**{gate.RAM_FIELD: True})))

    def test_non_finite_live_diagnostic_is_finite_checked(self):
        self.assertFalse(gate.is_finite_number(float("nan")))
        self.assertFalse(gate.is_finite_number(float("inf")))
        self.assertFalse(gate.is_finite_number(float("-inf")))
        self.assertFalse(gate.is_finite_number(True))
        self.assertTrue(gate.is_finite_number(8.0))

    def test_malformed_diagnostic_string_raises(self):
        with self.assertRaises(RuntimeError):
            gate._finite_gb("nan", 1024.0, "RAM")
        with self.assertRaises(RuntimeError):
            gate._finite_gb("Infinity", 1024.0, "RAM")


class TestEffectiveThreshold(unittest.TestCase):
    def gate_file(self, **overrides):
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(valid_gate(**overrides), handle)
        handle.close()
        return handle.name

    def test_recorded_threshold_above_minimum(self):
        self.assertEqual(gate.recorded_threshold({"memory_safety_threshold_gb": 12}), 12)

    def test_recorded_threshold_below_minimum_rejected(self):
        with self.assertRaises(ValueError):
            gate.recorded_threshold({"memory_safety_threshold_gb": 7})

    def test_live_ram_below_recorded_threshold(self):
        path = self.gate_file(memory_safety_threshold_gb=10, **{gate.RAM_FIELD: 12.0})
        try:
            ok, observed, message = gate.second_ram_check(path, runner=lambda a: stub_runner(a, ram_mb=9 * 1024))
            self.assertFalse(ok)
            self.assertIn("below effective threshold 10", message)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_live_ram_equal_to_threshold(self):
        path = self.gate_file(memory_safety_threshold_gb=8, **{gate.RAM_FIELD: 8.0})
        try:
            ok, observed, message = gate.second_ram_check(path, runner=lambda a: stub_runner(a, ram_mb=8 * 1024))
            self.assertTrue(ok, message)
            self.assertEqual(observed, 8.0)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_second_ram_check_failure_message(self):
        with self.assertRaises(ValueError):
            gate.recorded_threshold({"memory_safety_threshold_gb": float("nan")})

    def test_shell_second_check_precedes_startup(self):
        script = Path(__file__).resolve().parent.joinpath("run_smoke_test.sh").read_text(encoding="utf-8")
        self.assertIn("--live-check", script)
        self.assertLess(script.index("--live-check"), script.index("up -d"))


class TestVolumeLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config_path = Path(__file__).resolve().parents[1] / "config" / "sie-cpu.yml"
        cls.config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        cls.script = (Path(__file__).resolve().parent / "run_smoke_test.sh").read_text(encoding="utf-8")

    def test_stable_cache_volume_across_projects(self):
        first = compose_policy.cache_volume_name(self.config, "project-A")
        second = compose_policy.cache_volume_name(self.config, "project-B")
        self.assertEqual(first, "sie-hf-cache")
        self.assertEqual(first, second)

    def test_teardown_keeps_cache_and_is_isolated(self):
        lines = [line.strip() for line in self.script.splitlines() if "compose" in line and "down" in line]
        self.assertTrue(lines)
        for line in lines:
            self.assertFalse(compose_policy.teardown_deletes_volumes(line), line)
        self.assertTrue(any(compose_policy.cleanup_is_isolated(line, "sie-m001-smoke-$$-$(date +%s)")
                            for line in lines) or all("-p" in line for line in lines))

    def test_volume_policy_helpers_reject_bad_input(self):
        with self.assertRaises(ValueError):
            compose_policy.cache_volume_name({}, "project")
        with self.assertRaises(ValueError):
            compose_policy.teardown_deletes_volumes(None)


class TestBenchmarkExitCodes(unittest.TestCase):
    def test_distinct_exit_codes(self):
        codes = {ext.exit_code_for(s) for s in ("EXECUTED", "PARTIAL", "FAILED")}
        self.assertEqual(len(codes), 3)
        self.assertEqual(ext.exit_code_for("EXECUTED"), 0)
        self.assertNotEqual(ext.exit_code_for("PARTIAL"), 0)
        self.assertNotEqual(ext.exit_code_for("FAILED"), 0)
        self.assertNotIn(ext.EXIT_INVALID_DATASET, codes)
        self.assertNotIn(ext.EXIT_SDK_UNAVAILABLE, codes)

    def test_failed_inference_is_not_executed(self):
        self.assertEqual(ext.execution_status(3, 0, 3), "FAILED")
        self.assertEqual(ext.exit_code_for(ext.execution_status(3, 0, 3)), ext.EXIT_FAILED)


if __name__ == "__main__":
    unittest.main()
