"""
SPASHT AI - Diagnostic Runtime Integration & Verification Test Suite
===================================================================
Comprehensive tests for DiagnosticEngine, DiagnosticResult, and DiagnosticAlertStabilizer.
Ensures zero-loss parity, robust error rejection, artifact protection, and seamless API usage.
"""

import os
import sys
import hashlib
import time
import unittest
import numpy as np
import pandas as pd
import joblib

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from diagnostic_runtime import (
    DiagnosticEngine,
    DiagnosticResult,
    DiagnosticAlertStabilizer,
    DiagnosticValidationError,
    DiagnosticRuntimeError
)
from prepare_data import load_and_preprocess_dataset, create_flight_level_split


class TestDiagnosticRuntimeIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.artifacts_dir = os.path.join(cls.base_dir, "artifacts")
        cls.onnx_path = os.path.join(cls.artifacts_dir, "diagnostic_xgboost_v1.onnx")
        
        # Compute SHA256 of ONNX model before tests to verify immutability
        with open(cls.onnx_path, "rb") as f:
            cls.onnx_sha256_before = hashlib.sha256(f.read()).hexdigest()
            
        cls.engine = DiagnosticEngine(cls.artifacts_dir)
        
        # Load sample raw datasets for realistic testing
        cls.sample_nominal_csv = os.path.join(
            cls.base_dir, "data", "diagnostic_dataset", "nominal_diagnostic_dataset", "flight_001_nominal.csv"
        )
        cls.sample_fault_csv = os.path.join(
            cls.base_dir, "data", "diagnostic_dataset", "Thermal Anomalies", "flight_018_critical_overheat.csv"
        )
        cls.sample_cascade_csv = os.path.join(
            cls.base_dir, "data", "diagnostic_dataset", "spasht_official_cascades_58col", "05_TOTAL_SYSTEM_FAILURE_v1.csv"
        )

    def test_01_artifacts_immutability(self):
        """Verify that initializing and running DiagnosticEngine does not alter the ONNX artifact."""
        with open(self.onnx_path, "rb") as f:
            current_sha256 = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(
            self.onnx_sha256_before, 
            current_sha256, 
            "CRITICAL: ONNX artifact was modified or corrupted!"
        )

    def test_02_single_nominal_snapshot(self):
        """Test inference on a real nominal telemetry snapshot."""
        df_nom = pd.read_csv(self.sample_nominal_csv)
        row_dict = df_nom.iloc[100].to_dict()
        
        result = self.engine.diagnose_snapshot(row_dict, timestamp="2026-09-25T12:00:00Z")
        
        self.assertIsInstance(result, DiagnosticResult)
        self.assertEqual(result.predicted_fault_label, "NORMAL_OPERATIONS")
        self.assertEqual(result.is_fault, False)
        self.assertEqual(result.status, "NOMINAL")
        self.assertEqual(result.flight_phase, row_dict["flight.phase"])
        self.assertGreater(result.confidence, 0.5)
        self.assertEqual(len(result.probabilities), 25)
        self.assertIn("NORMAL_OPERATIONS", result.probabilities)

    def test_03_single_fault_snapshot(self):
        """Test inference on a real critical overheat snapshot."""
        df_fault = pd.read_csv(self.sample_fault_csv)
        # Row 8000 is well within the fault injection window
        row_dict = df_fault.iloc[8000].to_dict()
        
        result = self.engine.diagnose_snapshot(row_dict, timestamp=8000)
        
        self.assertIsInstance(result, DiagnosticResult)
        self.assertEqual(result.predicted_fault_label, "CRITICAL_OVERHEAT")
        self.assertEqual(result.is_fault, True)
        self.assertEqual(result.status, "FAULT_DETECTED")
        self.assertGreater(result.confidence, 0.9)
        self.assertEqual(result.timestamp, 8000)

    def test_04_cascade_snapshot_with_flags_column(self):
        """Test inference on a cascade file with 'flags' column name."""
        df_cas = pd.read_csv(self.sample_cascade_csv)
        row_dict = df_cas.iloc[8000].to_dict()
        
        # Verify 'flags' is in dict instead of 'flight.phase'
        self.assertIn("flags", row_dict)
        
        result = self.engine.diagnose_snapshot(row_dict)
        self.assertEqual(result.predicted_fault_label, "TOTAL_SYSTEM_FAILURE")
        self.assertEqual(result.is_fault, True)
        self.assertGreater(result.confidence, 0.9)

    def test_05_batch_inference(self):
        """Test batch inference on multiple snapshots across different phases."""
        df_fault = pd.read_csv(self.sample_fault_csv)
        sample_batch = df_fault.iloc[0:100] # First 100 seconds
        
        results = self.engine.diagnose_batch(sample_batch)
        
        self.assertEqual(len(results), 100)
        for res in results:
            self.assertIsInstance(res, DiagnosticResult)
            self.assertIn(res.predicted_fault_label, self.engine.classes)

    def test_06_validation_missing_feature(self):
        """Verify that omitting a required telemetry field raises DiagnosticValidationError."""
        df_nom = pd.read_csv(self.sample_nominal_csv)
        row_dict = df_nom.iloc[0].to_dict()
        
        # Remove an important physical parameter
        del row_dict["engine.oil_pressure"]
        
        with self.assertRaises(DiagnosticValidationError) as ctx:
            self.engine.diagnose_snapshot(row_dict)
        self.assertIn("Missing required telemetry feature: 'engine.oil_pressure'", str(ctx.exception))

    def test_07_validation_missing_anomaly_score(self):
        """Verify that omitting an anomaly score raises DiagnosticValidationError."""
        df_nom = pd.read_csv(self.sample_nominal_csv)
        row_dict = df_nom.iloc[0].to_dict()
        
        del row_dict["anomaly_score_thermal"]
        
        with self.assertRaises(DiagnosticValidationError) as ctx:
            self.engine.diagnose_snapshot(row_dict)
        self.assertIn("Missing required telemetry feature: 'anomaly_score_thermal'", str(ctx.exception))

    def test_08_validation_nan_and_inf(self):
        """Verify that NaN or infinite numerical values are strictly rejected."""
        df_nom = pd.read_csv(self.sample_nominal_csv)
        
        # Test NaN
        row_nan = df_nom.iloc[0].to_dict()
        row_nan["engine.cht_1"] = float("nan")
        with self.assertRaises(DiagnosticValidationError) as ctx:
            self.engine.diagnose_snapshot(row_nan)
        self.assertIn("Non-finite value detected", str(ctx.exception))
        
        # Test Inf
        row_inf = df_nom.iloc[0].to_dict()
        row_inf["electrical.main_bus_voltage"] = float("inf")
        with self.assertRaises(DiagnosticValidationError) as ctx:
            self.engine.diagnose_snapshot(row_inf)
        self.assertIn("Non-finite value detected", str(ctx.exception))

    def test_09_validation_invalid_flight_phase(self):
        """Verify that unsupported flight phase strings are rejected."""
        df_nom = pd.read_csv(self.sample_nominal_csv)
        row_dict = df_nom.iloc[0].to_dict()
        
        row_dict["flight.phase"] = "SUPERCRUISE_INVALID"
        
        with self.assertRaises(DiagnosticValidationError) as ctx:
            self.engine.diagnose_snapshot(row_dict)
        self.assertIn("Invalid flight phase", str(ctx.exception))

    def test_10_parity_with_held_out_dataset(self):
        """
        Verify 100% agreement on a representative batch of 1,000 held-out samples
        comparing DiagnosticEngine against native XGBoost checkpoint.
        """
        native_model_path = os.path.join(self.artifacts_dir, "diagnostic_xgboost_model.joblib")
        native_model = joblib.load(native_model_path)
        
        X, y_raw, flight_files, full_df = load_and_preprocess_dataset()
        _, test_mask, _, _ = create_flight_level_split(flight_files, full_df)
        
        X_test_sample = X[test_mask].iloc[:1000].values.astype(np.float32)
        native_preds = native_model.predict(X_test_sample)
        
        runtime_results = self.engine.diagnose_raw_tensor(X_test_sample)
        runtime_preds = np.array([r.predicted_class_id for r in runtime_results])
        
        matches = (native_preds == runtime_preds).sum()
        self.assertEqual(matches, 1000, "Parity mismatch detected between native model and runtime wrapper!")

    def test_11_alert_stabilizer_debouncing(self):
        """Verify that DiagnosticAlertStabilizer debounces transient single-frame spikes."""
        stabilizer = DiagnosticAlertStabilizer(self.engine, debounce_threshold=3)
        stabilizer.reset()
        
        df_nom = pd.read_csv(self.sample_nominal_csv)
        nom_dict = df_nom.iloc[0].to_dict()
        
        df_fault = pd.read_csv(self.sample_fault_csv)
        fault_dict = df_fault.iloc[8000].to_dict()
        
        # Frame 1: Nominal
        s1 = stabilizer.process_snapshot(nom_dict)
        self.assertEqual(s1.confirmed_fault_label, "NORMAL_OPERATIONS")
        self.assertEqual(s1.is_alert_active, False)
        
        # Frame 2: First fault frame (consecutive = 1 < threshold 3 -> alert remains false)
        s2 = stabilizer.process_snapshot(fault_dict)
        self.assertEqual(s2.raw_result.predicted_fault_label, "CRITICAL_OVERHEAT")
        self.assertEqual(s2.consecutive_fault_count, 1)
        self.assertEqual(s2.is_alert_active, False) # Still debouncing
        
        # Frame 3: Second fault frame (consecutive = 2 < 3 -> alert remains false)
        s3 = stabilizer.process_snapshot(fault_dict)
        self.assertEqual(s3.consecutive_fault_count, 2)
        self.assertEqual(s3.is_alert_active, False)
        
        # Frame 4: Third fault frame (consecutive = 3 == threshold -> alert trips!)
        s4 = stabilizer.process_snapshot(fault_dict)
        self.assertEqual(s4.consecutive_fault_count, 3)
        self.assertEqual(s4.confirmed_fault_label, "CRITICAL_OVERHEAT")
        self.assertEqual(s4.is_alert_active, True)
        
        # Frame 5: Return to nominal immediately clears the alert
        s5 = stabilizer.process_snapshot(nom_dict)
        self.assertEqual(s5.confirmed_fault_label, "NORMAL_OPERATIONS")
        self.assertEqual(s5.is_alert_active, False)
        self.assertEqual(s5.consecutive_fault_count, 0)


def run_integration_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDiagnosticRuntimeIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    return res.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
