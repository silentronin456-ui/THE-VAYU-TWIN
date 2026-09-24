"""
SPASHT AI — Simulated Live Feed Test Suite
==========================================
Deterministic tests for SimulatedLiveFeed and related helpers.

All tests operate in FAST mode (no real-time delays).
Only a configurable small number of rows is processed per test to keep
the suite fast even on large CSVs (9,000 rows each).

Tests verify:
  1.  Nominal CSV can be streamed end-to-end.
  2.  Fault CSV can be streamed and produces fault predictions.
  3.  Cascade CSV (uses 'flags' column) can be streamed.
  4.  Every processed row produces a valid FeedResult.
  5.  The 63-feature contract is respected (no ValidationError for real rows).
  6.  The ONNX artifact is byte-for-byte unchanged after the simulation.
  7.  Raw CSV files are not modified.
  8.  FAST mode operates without measurable real-time delay.
  9.  REALTIME mode is importable and configurable (not exercised for speed).
  10. FeedResult.to_dict() serialises cleanly to JSON.
  11. Alert stabilizer resets correctly between different scenarios.
"""

import os
import sys
import json
import time
import hashlib
import unittest
import tempfile

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.abspath(os.path.join(_SRC_DIR, ".."))
sys.path.insert(0, _SRC_DIR)

from simulate_live_feed import SimulatedLiveFeed, SCENARIOS, FeedResult
from diagnostic_runtime import DiagnosticValidationError

# ---------------------------------------------------------------------------
# Test configuration
# ---------------------------------------------------------------------------
# Number of rows to process per test.  Keep small to stay fast.
TEST_ROWS = 50          # covers nominal phase at start of each flight
FAULT_WINDOW_ROWS = 30      # rows to process at the fault window boundary

# FAULT_WINDOW_START is determined dynamically from the actual CSV (see test_12)

_ARTIFACTS_DIR = os.path.join(_BASE_DIR, "artifacts")
_ONNX_PATH = os.path.join(_ARTIFACTS_DIR, "diagnostic_xgboost_v1.onnx")


def _sha256(path: str) -> str:
    """Compute SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class TestSimulatedLiveFeed(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Shared setup: single engine initialisation + ONNX baseline checksum."""
        cls.onnx_sha256_before = _sha256(_ONNX_PATH)

        # Shared feed instance (FAST mode, verbose=False for clean test output)
        cls.feed = SimulatedLiveFeed(
            artifacts_dir=_ARTIFACTS_DIR,
            debounce_threshold=3,
            realtime=False,
            verbose=False,
        )

        cls.nominal_csv   = SCENARIOS["nominal"]
        cls.fault_csv     = SCENARIOS["fault"]
        cls.cascade_csv   = SCENARIOS["cascade"]

    # ------------------------------------------------------------------
    # Test 1: Nominal CSV streams successfully
    # ------------------------------------------------------------------
    def test_01_nominal_csv_streams(self):
        """Nominal CSV produces TEST_ROWS FeedResult objects without error."""
        results = self.feed.run(
            csv_path=self.nominal_csv,
            scenario_label="nominal",
            max_rows=TEST_ROWS,
        )
        self.assertEqual(len(results), TEST_ROWS)

    # ------------------------------------------------------------------
    # Test 2: Fault CSV streams successfully
    # ------------------------------------------------------------------
    def test_02_fault_csv_streams(self):
        """Fault CSV processes TEST_ROWS rows without error."""
        results = self.feed.run(
            csv_path=self.fault_csv,
            scenario_label="fault",
            max_rows=TEST_ROWS,
        )
        self.assertEqual(len(results), TEST_ROWS)

    # ------------------------------------------------------------------
    # Test 3: Cascade CSV (flags column) streams successfully
    # ------------------------------------------------------------------
    def test_03_cascade_csv_streams(self):
        """Cascade CSV ('flags' column) streams without KeyError or ValidationError."""
        results = self.feed.run(
            csv_path=self.cascade_csv,
            scenario_label="cascade",
            max_rows=TEST_ROWS,
        )
        self.assertEqual(len(results), TEST_ROWS)

    # ------------------------------------------------------------------
    # Test 4: Every row produces a valid FeedResult
    # ------------------------------------------------------------------
    def test_04_every_row_produces_valid_result(self):
        """All returned objects are FeedResult with populated DiagnosticResult."""
        results = self.feed.run(
            csv_path=self.nominal_csv,
            scenario_label="nominal",
            max_rows=TEST_ROWS,
        )
        for idx, r in enumerate(results):
            self.assertIsInstance(r, FeedResult, f"Row {idx} is not a FeedResult")
            self.assertIn(
                r.raw_result.predicted_fault_label,
                self.feed.engine.classes,
                f"Row {idx} predicted label not in 25-class taxonomy",
            )
            self.assertGreater(r.raw_result.confidence, 0.0, f"Row {idx} confidence is zero")
            self.assertEqual(
                len(r.raw_result.probabilities), 25,
                f"Row {idx} probability dict does not have 25 entries",
            )

    # ------------------------------------------------------------------
    # Test 5: 63-feature contract verified (no ValidationError for real rows)
    # ------------------------------------------------------------------
    def test_05_feature_contract_intact(self):
        """
        Streaming real CSV rows through preprocess_snapshot() triggers no
        DiagnosticValidationError — confirms the 63-feature contract is met.
        """
        import pandas as pd

        for csv_path in [self.nominal_csv, self.fault_csv, self.cascade_csv]:
            df = pd.read_csv(csv_path)
            if "flags" in df.columns and "flight.phase" not in df.columns:
                df = df.rename(columns={"flags": "flight.phase"})

            for i in range(min(5, len(df))):
                row_dict = df.iloc[i].to_dict()
                try:
                    tensor, phase = self.feed.engine.preprocess_snapshot(row_dict)
                    self.assertEqual(tensor.shape, (1, 63), f"Shape mismatch at row {i} of {csv_path}")
                    self.assertIn(phase, self.feed.engine.VALID_PHASES)
                except DiagnosticValidationError as exc:
                    self.fail(f"ValidationError on real CSV row: {exc}")

    # ------------------------------------------------------------------
    # Test 6: ONNX artifact unchanged after simulation
    # ------------------------------------------------------------------
    def test_06_onnx_artifact_unchanged(self):
        """ONNX model artifact byte-hash is identical before and after simulation."""
        # Run a simulation to exercise the ONNX session
        self.feed.run(
            csv_path=self.fault_csv,
            scenario_label="fault",
            max_rows=10,
        )
        onnx_sha256_after = _sha256(_ONNX_PATH)
        self.assertEqual(
            self.onnx_sha256_before,
            onnx_sha256_after,
            "CRITICAL: ONNX artifact was modified during simulation!",
        )

    # ------------------------------------------------------------------
    # Test 7: Raw CSV files are not modified
    # ------------------------------------------------------------------
    def test_07_raw_csv_files_unchanged(self):
        """Streaming does not modify the source CSV files."""
        sha_before = {
            "nominal" : _sha256(self.nominal_csv),
            "fault"   : _sha256(self.fault_csv),
            "cascade" : _sha256(self.cascade_csv),
        }

        for label, csv_path in SCENARIOS.items():
            self.feed.run(csv_path=csv_path, scenario_label=label, max_rows=5)

        for label, csv_path in SCENARIOS.items():
            sha_after = _sha256(csv_path)
            self.assertEqual(
                sha_before[label],
                sha_after,
                f"CSV file was modified during simulation: {csv_path}",
            )

    # ------------------------------------------------------------------
    # Test 8: FAST mode has negligible real-time delay
    # ------------------------------------------------------------------
    def test_08_fast_mode_no_delay(self):
        """FAST mode processes 20 rows in under 10 seconds (no sleep)."""
        feed_fast = SimulatedLiveFeed(
            artifacts_dir=_ARTIFACTS_DIR,
            realtime=False,
            verbose=False,
        )
        t0 = time.monotonic()
        feed_fast.run(csv_path=self.nominal_csv, scenario_label="nominal", max_rows=20)
        elapsed = time.monotonic() - t0
        self.assertLess(
            elapsed, 10.0,
            f"FAST mode took {elapsed:.2f}s for 20 rows — this is too slow.",
        )

    # ------------------------------------------------------------------
    # Test 9: REALTIME mode is importable and configurable (not exercised)
    # ------------------------------------------------------------------
    def test_09_realtime_mode_importable(self):
        """REALTIME mode can be instantiated; attribute is set correctly."""
        feed_rt = SimulatedLiveFeed(
            artifacts_dir=_ARTIFACTS_DIR,
            realtime=True,
            verbose=False,
        )
        self.assertTrue(feed_rt.realtime)
        # We do NOT call .run() here — REALTIME sleep is not for automated tests.

    # ------------------------------------------------------------------
    # Test 10: FeedResult.to_dict() serialises to valid JSON
    # ------------------------------------------------------------------
    def test_10_feed_result_json_serialisable(self):
        """FeedResult.to_dict() produces a JSON-serialisable structure."""
        results = self.feed.run(
            csv_path=self.fault_csv,
            scenario_label="fault",
            max_rows=5,
        )
        for r in results:
            d = r.to_dict()
            try:
                json_str = json.dumps(d)
            except (TypeError, ValueError) as exc:
                self.fail(f"FeedResult.to_dict() produced non-serialisable dict: {exc}")
            # Round-trip parse
            parsed = json.loads(json_str)
            self.assertIn("elapsed_s", parsed)
            self.assertIn("raw", parsed)
            self.assertIn("stabilized", parsed)
            self.assertIn("predicted_fault_label", parsed["raw"])
            self.assertIn("is_alert_active", parsed["stabilized"])

    # ------------------------------------------------------------------
    # Test 11: Alert stabilizer resets between runs
    # ------------------------------------------------------------------
    def test_11_stabilizer_resets_between_scenarios(self):
        """
        Running a fault scenario followed by a nominal scenario must not
        carry over the confirmed_fault state from the fault run.
        """
        # Run fault scenario first — process enough rows to be well past fault onset
        self.feed.run(
            csv_path=self.fault_csv,
            scenario_label="fault",
            max_rows=5000,
        )

        # Now run nominal — stabilizer.reset() is called at the start of run()
        nominal_results = self.feed.run(
            csv_path=self.nominal_csv,
            scenario_label="nominal",
            max_rows=TEST_ROWS,
        )

        # All nominal rows should have no active alert (they are pre-fault rows)
        for r in nominal_results:
            self.assertEqual(
                r.alert_status.confirmed_fault_label,
                "NORMAL_OPERATIONS",
                "Stabilizer carried fault state across scenarios — reset failed.",
            )

    # ------------------------------------------------------------------
    # Test 12: Fault CSV produces fault predictions inside fault window
    # ------------------------------------------------------------------
    def test_12_fault_window_produces_fault_predictions(self):
        """Rows from the fault injection window should produce non-nominal predictions."""
        import pandas as pd

        df = pd.read_csv(self.fault_csv)

        # Dynamically locate the actual fault onset row in the CSV
        non_nominal_mask = df["fault_label"] != "NORMAL_OPERATIONS"
        self.assertTrue(
            non_nominal_mask.any(),
            "Fault CSV contains no non-nominal rows — wrong file?",
        )
        fault_onset_row = int(non_nominal_mask.idxmax())  # first True index
        # Sample 30 rows starting from the fault onset (well inside fault region)
        start = fault_onset_row
        end = min(start + FAULT_WINDOW_ROWS, len(df))

        # Build snapshot dicts and run through engine
        fault_labels_seen = set()
        for i in range(start, end):
            row_dict = df.iloc[i].to_dict()
            result = self.feed.engine.diagnose_snapshot(row_dict)
            fault_labels_seen.add(result.predicted_fault_label)

        # At least some predictions in this window should be non-nominal
        non_nominal = fault_labels_seen - {"NORMAL_OPERATIONS"}
        self.assertGreater(
            len(non_nominal), 0,
            f"No fault predictions in window [{start}:{end}]. "
            f"Labels seen: {fault_labels_seen}",
        )

    # ------------------------------------------------------------------
    # Test 13: Cascade CSV produces cascade predictions inside fault window
    # ------------------------------------------------------------------
    def test_13_cascade_window_produces_cascade_predictions(self):
        """Rows from the cascade fault window should predict a cascade class."""
        import pandas as pd

        df = pd.read_csv(self.cascade_csv)
        if "flags" in df.columns:
            df = df.rename(columns={"flags": "flight.phase"})

        # Dynamically locate cascade fault onset
        non_nominal_mask = df["fault_label"] != "NORMAL_OPERATIONS"
        self.assertTrue(
            non_nominal_mask.any(),
            "Cascade CSV contains no non-nominal rows — wrong file?",
        )
        start = int(non_nominal_mask.idxmax())
        end = min(start + FAULT_WINDOW_ROWS, len(df))

        cascade_labels = set()
        for i in range(start, end):
            row_dict = df.iloc[i].to_dict()
            result = self.feed.engine.diagnose_snapshot(row_dict)
            cascade_labels.add(result.predicted_fault_label)

        non_nominal = cascade_labels - {"NORMAL_OPERATIONS"}
        self.assertGreater(
            len(non_nominal), 0,
            f"No non-nominal predictions in cascade window [{start}:{end}]. Labels: {cascade_labels}",
        )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def run_simulator_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimulatedLiveFeed)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_simulator_tests()
    sys.exit(0 if success else 1)
