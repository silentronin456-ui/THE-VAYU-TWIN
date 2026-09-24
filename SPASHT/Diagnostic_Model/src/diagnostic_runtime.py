"""
SPASHT AI - Diagnostic Engine Runtime Integration Module
========================================================
Production-grade, reusable runtime wrapper for the 25-class SPASHT Diagnostic Model.
Ingests 1 Hz multi-sensor aircraft telemetry snapshots + Health Engine anomaly scores,
assembles the canonical 63-feature Float32 tensor, executes ONNX Runtime inference,
and decodes predicted fault classes for Sanjeevani UI alerting.
"""

import os
import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import joblib
import onnxruntime as ort


class DiagnosticValidationError(ValueError):
    """Raised when input telemetry data fails validation checks."""
    pass


class DiagnosticRuntimeError(RuntimeError):
    """Raised when ONNX inference or artifact loading fails."""
    pass


@dataclass
class DiagnosticResult:
    """Structured diagnostic prediction result for a single telemetry snapshot."""
    predicted_class_id: int
    predicted_fault_label: str
    confidence: float
    probabilities: Dict[str, float]
    flight_phase: str
    timestamp: Optional[Any] = None
    is_fault: bool = field(init=False)
    status: str = field(init=False)
    
    def __post_init__(self):
        self.is_fault = (self.predicted_fault_label != "NORMAL_OPERATIONS")
        self.status = "FAULT_DETECTED" if self.is_fault else "NOMINAL"

    def to_dict(self) -> Dict[str, Any]:
        """Convert diagnostic result to JSON-serializable dictionary."""
        return {
            "predicted_class_id": int(self.predicted_class_id),
            "predicted_fault_label": str(self.predicted_fault_label),
            "confidence": float(self.confidence),
            "probabilities": {k: float(v) for k, v in self.probabilities.items()},
            "flight_phase": str(self.flight_phase),
            "timestamp": self.timestamp,
            "is_fault": bool(self.is_fault),
            "status": str(self.status)
        }


@dataclass
class AlertStatus:
    """Debounced / stabilized alert state for Sanjeevani UI."""
    raw_result: DiagnosticResult
    confirmed_fault_label: str
    is_alert_active: bool
    consecutive_fault_count: int
    debounce_threshold: int


class DiagnosticEngine:
    """
    Authoritative Diagnostic Engine Runtime Wrapper.
    
    Manages ONNX Runtime sessions, dynamic LabelEncoder decoding,
    and strict feature ordering as specified in feature_schema.json.
    """
    
    VALID_PHASES = ("STARTUP", "WARMUP", "TAKEOFF", "CLIMB", "CRUISE", "DESCENT", "LANDING")
    
    def __init__(self, artifacts_dir: Optional[str] = None):
        """
        Initialize the Diagnostic Engine and load all validated production artifacts.
        
        Args:
            artifacts_dir: Optional path to artifacts directory. Defaults to ../artifacts.
        """
        if artifacts_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            artifacts_dir = os.path.join(base_dir, "artifacts")
            
        self.artifacts_dir = os.path.abspath(artifacts_dir)
        self.onnx_path = os.path.join(self.artifacts_dir, "diagnostic_xgboost_v1.onnx")
        self.encoder_path = os.path.join(self.artifacts_dir, "fault_label_encoder.pkl")
        self.schema_path = os.path.join(self.artifacts_dir, "feature_schema.json")
        self.manifest_path = os.path.join(self.artifacts_dir, "manifest.json")
        
        self._load_and_validate_artifacts()
        self._initialize_onnx_session()

    def _load_and_validate_artifacts(self):
        """Verify that all required artifacts exist and load schemas."""
        for path, name in [
            (self.onnx_path, "ONNX Model"),
            (self.encoder_path, "Label Encoder"),
            (self.schema_path, "Feature Schema"),
            (self.manifest_path, "Manifest")
        ]:
            if not os.path.isfile(path):
                raise DiagnosticRuntimeError(f"Missing required artifact '{name}': {path}")
                
        # Load canonical feature schema (authoritative single source of truth for ordering)
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.canonical_features: List[str] = json.load(f)
            
        if len(self.canonical_features) != 63:
            raise DiagnosticRuntimeError(
                f"Feature schema must contain exactly 63 features, found {len(self.canonical_features)}"
            )
            
        # Parse physical features, anomaly score features, and one-hot phase features
        self.physical_params = [
            c for c in self.canonical_features 
            if not c.startswith("anomaly_score_") and not c.startswith("flight.phase_")
        ]
        self.anomaly_params = [
            c for c in self.canonical_features 
            if c.startswith("anomaly_score_")
        ]
        self.phase_flag_params = [
            c for c in self.canonical_features 
            if c.startswith("flight.phase_")
        ]
        
        if len(self.physical_params) != 53 or len(self.anomaly_params) != 3 or len(self.phase_flag_params) != 7:
            raise DiagnosticRuntimeError(
                f"Invalid schema composition: {len(self.physical_params)} physical, "
                f"{len(self.anomaly_params)} anomaly, {len(self.phase_flag_params)} phase flags."
            )
            
        # Load LabelEncoder
        try:
            self.label_encoder = joblib.load(self.encoder_path)
            self.classes: List[str] = list(self.label_encoder.classes_)
        except Exception as e:
            raise DiagnosticRuntimeError(f"Failed to load LabelEncoder from {self.encoder_path}: {e}")
            
        if len(self.classes) != 25:
            raise DiagnosticRuntimeError(
                f"Expected 25 classes in LabelEncoder, found {len(self.classes)}"
            )

    def _initialize_onnx_session(self):
        """Initialize ONNX Runtime inference session and verify I/O contract."""
        try:
            # Set minimal thread configuration for deterministic, low-latency execution
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 1
            opts.inter_op_num_threads = 1
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            
            self.session = ort.InferenceSession(self.onnx_path, sess_options=opts)
        except Exception as e:
            raise DiagnosticRuntimeError(f"Failed to initialize ONNX Runtime session: {e}")
            
        inputs = self.session.get_inputs()
        outputs = self.session.get_outputs()
        
        if len(inputs) != 1:
            raise DiagnosticRuntimeError(f"Expected exactly 1 input node, found {len(inputs)}")
            
        self.input_name = inputs[0].name
        expected_feature_dim = inputs[0].shape[1]
        
        if expected_feature_dim != 63:
            raise DiagnosticRuntimeError(
                f"ONNX model expects {expected_feature_dim} features, but schema defines 63."
            )
            
        self.output_label_name = outputs[0].name
        self.output_prob_name = outputs[1].name if len(outputs) > 1 else None

    def preprocess_snapshot(self, snapshot: Dict[str, Any]) -> Tuple[np.ndarray, str]:
        """
        Validate and assemble a single telemetry dictionary into a canonical 63-feature Float32 tensor.
        
        Args:
            snapshot: Dictionary containing:
                - 53 physical telemetry keys
                - 3 anomaly scores ('anomaly_score_thermal', 'anomaly_score_mechanical', 'anomaly_score_electrical')
                - 'flight.phase' string (e.g. 'CRUISE') OR 'flags' string.
        
        Returns:
            Tuple of (1x63 float32 numpy array, normalized flight phase string).
        
        Raises:
            DiagnosticValidationError: If fields are missing, invalid, NaN, or non-finite.
        """
        if not isinstance(snapshot, dict):
            raise DiagnosticValidationError(f"Snapshot must be a dictionary, got {type(snapshot)}")
            
        # Extract and validate flight phase
        phase_raw = snapshot.get("flight.phase", snapshot.get("flags", snapshot.get("flight_phase", None)))
        if phase_raw is None:
            raise DiagnosticValidationError("Missing mandatory field 'flight.phase' (or 'flags').")
            
        phase_str = str(phase_raw).strip().upper()
        if phase_str not in self.VALID_PHASES:
            raise DiagnosticValidationError(
                f"Invalid flight phase '{phase_raw}'. Must be one of: {self.VALID_PHASES}"
            )
            
        # Extract and validate numeric features
        vector = np.empty(63, dtype=np.float32)
        
        for idx, feat_name in enumerate(self.canonical_features):
            if feat_name.startswith("flight.phase_"):
                # One-hot encoded phase flag
                target_phase = feat_name.replace("flight.phase_", "")
                vector[idx] = 1.0 if phase_str == target_phase else 0.0
            else:
                # Telemetry parameter or anomaly score
                if feat_name not in snapshot:
                    raise DiagnosticValidationError(f"Missing required telemetry feature: '{feat_name}'")
                    
                val = snapshot[feat_name]
                if val is None or isinstance(val, (str, bool)):
                    raise DiagnosticValidationError(
                        f"Feature '{feat_name}' must be numeric (int/float), got {type(val)}: {val}"
                    )
                    
                try:
                    num_val = float(val)
                except (ValueError, TypeError):
                    raise DiagnosticValidationError(
                        f"Could not convert feature '{feat_name}' with value '{val}' to float."
                    )
                    
                if math.isnan(num_val) or math.isinf(num_val):
                    raise DiagnosticValidationError(
                        f"Non-finite value detected for feature '{feat_name}': {num_val}"
                    )
                    
                vector[idx] = num_val
                
        # Reshape to [1, 63]
        return vector.reshape(1, 63), phase_str

    def preprocess_batch(self, snapshots: Union[List[Dict[str, Any]], Any]) -> Tuple[np.ndarray, List[str]]:
        """
        Preprocess a sequence / batch of telemetry snapshots.
        
        Args:
            snapshots: List of snapshot dictionaries or pandas DataFrame.
            
        Returns:
            Tuple of (Nx63 Float32 numpy array, list of N phase strings).
        """
        if hasattr(snapshots, "to_dict") and callable(getattr(snapshots, "to_dict")):
            # Convert pandas DataFrame to list of dicts
            snapshots_list = snapshots.to_dict(orient="records")
        elif isinstance(snapshots, (list, tuple)):
            snapshots_list = snapshots
        else:
            raise DiagnosticValidationError(f"Unsupported batch input type: {type(snapshots)}")
            
        if len(snapshots_list) == 0:
            raise DiagnosticValidationError("Cannot preprocess an empty batch.")
            
        batch_vectors = []
        phase_list = []
        
        for i, snap in enumerate(snapshots_list):
            try:
                vec, ph = self.preprocess_snapshot(snap)
                batch_vectors.append(vec[0])
                phase_list.append(ph)
            except DiagnosticValidationError as e:
                raise DiagnosticValidationError(f"Validation failed at batch index {i}: {e}")
                
        batch_tensor = np.array(batch_vectors, dtype=np.float32)
        return batch_tensor, phase_list

    def diagnose_snapshot(self, snapshot: Dict[str, Any], timestamp: Optional[Any] = None) -> DiagnosticResult:
        """
        Run real-time diagnostic inference on a single 1 Hz telemetry snapshot.
        
        Args:
            snapshot: Dictionary of raw telemetry.
            timestamp: Optional telemetry timestamp.
            
        Returns:
            DiagnosticResult containing predicted class, confidence, and full probability distribution.
        """
        tensor, phase_str = self.preprocess_snapshot(snapshot)
        return self._run_inference_tensor(tensor, [phase_str], [timestamp])[0]

    def diagnose_batch(
        self, 
        snapshots: Union[List[Dict[str, Any]], Any], 
        timestamps: Optional[List[Any]] = None
    ) -> List[DiagnosticResult]:
        """
        Run batch diagnostic inference across multiple telemetry snapshots.
        
        Args:
            snapshots: List of snapshot dicts or pandas DataFrame.
            timestamps: Optional list of timestamps matching snapshots.
            
        Returns:
            List of DiagnosticResult objects.
        """
        tensor, phases = self.preprocess_batch(snapshots)
        return self._run_inference_tensor(tensor, phases, timestamps)

    def diagnose_raw_tensor(
        self, 
        tensor: np.ndarray, 
        phases: Optional[List[str]] = None,
        timestamps: Optional[List[Any]] = None
    ) -> List[DiagnosticResult]:
        """
        Run diagnostic inference directly on a pre-validated [N, 63] Float32 tensor.
        
        Args:
            tensor: 2D numpy array of shape [N, 63].
            phases: Optional list of phase strings. Defaults to 'UNKNOWN'.
            timestamps: Optional list of timestamps.
        """
        if not isinstance(tensor, np.ndarray):
            raise DiagnosticValidationError(f"Expected numpy ndarray, got {type(tensor)}")
        if tensor.ndim != 2 or tensor.shape[1] != 63:
            raise DiagnosticValidationError(
                f"Input tensor must have shape [N, 63], got {tensor.shape}"
            )
        if tensor.dtype != np.float32:
            tensor = tensor.astype(np.float32)
            
        n_samples = tensor.shape[0]
        if phases is None:
            phases = ["UNKNOWN"] * n_samples
        elif len(phases) != n_samples:
            raise DiagnosticValidationError("Length of phases list must match tensor row count.")
            
        return self._run_inference_tensor(tensor, phases, timestamps)

    def _run_inference_tensor(
        self, 
        tensor: np.ndarray, 
        phases: List[str], 
        timestamps: Optional[List[Any]]
    ) -> List[DiagnosticResult]:
        """Internal execution engine for ONNX inference and label decoding."""
        n_samples = tensor.shape[0]
        if timestamps is None:
            ts_list = [None] * n_samples
        else:
            if len(timestamps) != n_samples:
                raise DiagnosticValidationError("Timestamps length must match tensor sample count.")
            ts_list = timestamps

        # Execute ONNX Runtime Session
        try:
            ort_outputs = self.session.run(None, {self.input_name: tensor})
        except Exception as e:
            raise DiagnosticRuntimeError(f"ONNX inference execution failed: {e}")
            
        pred_label_indices = ort_outputs[0] # Shape [N]
        prob_matrix = ort_outputs[1] if len(ort_outputs) > 1 else None # Shape [N, 25]
        
        # Decode string labels using LabelEncoder
        decoded_labels = self.label_encoder.inverse_transform(pred_label_indices)
        
        results: List[DiagnosticResult] = []
        for i in range(n_samples):
            cls_id = int(pred_label_indices[i])
            label_str = str(decoded_labels[i])
            
            if prob_matrix is not None:
                probs_row = prob_matrix[i]
                confidence = float(np.max(probs_row))
                prob_dict = {
                    self.classes[c_idx]: float(probs_row[c_idx])
                    for c_idx in range(len(self.classes))
                }
            else:
                confidence = 1.0
                prob_dict = {label_str: 1.0}
                
            res = DiagnosticResult(
                predicted_class_id=cls_id,
                predicted_fault_label=label_str,
                confidence=confidence,
                probabilities=prob_dict,
                flight_phase=phases[i],
                timestamp=ts_list[i]
            )
            results.append(res)
            
        return results


class DiagnosticAlertStabilizer:
    """
    Optional alert debouncer / temporal smoothing layer for Cockpit / Sanjeevani UI.
    
    Prevents fleeting single-second transient classifications at transition boundaries
    by requiring K consecutive identical fault diagnoses before tripping a formal confirmed alert.
    """
    
    def __init__(self, engine: DiagnosticEngine, debounce_threshold: int = 3):
        """
        Args:
            engine: Configured DiagnosticEngine instance.
            debounce_threshold: Number of consecutive identical fault frames required.
        """
        if debounce_threshold < 1:
            raise ValueError("Debounce threshold must be at least 1.")
            
        self.engine = engine
        self.debounce_threshold = debounce_threshold
        self.current_candidate_fault: Optional[str] = None
        self.consecutive_count: int = 0
        self.confirmed_fault: str = "NORMAL_OPERATIONS"

    def reset(self):
        """Reset stabilizer state (e.g. at the start of a new flight)."""
        self.current_candidate_fault = None
        self.consecutive_count = 0
        self.confirmed_fault = "NORMAL_OPERATIONS"

    def process_snapshot(self, snapshot: Dict[str, Any], timestamp: Optional[Any] = None) -> AlertStatus:
        """
        Process a telemetry snapshot through the diagnostic engine and update debounced alert state.
        
        Returns:
            AlertStatus object containing raw result and confirmed alert state.
        """
        raw_result = self.engine.diagnose_snapshot(snapshot, timestamp=timestamp)
        predicted_fault = raw_result.predicted_fault_label
        
        if predicted_fault == "NORMAL_OPERATIONS":
            self.consecutive_count = 0
            self.current_candidate_fault = None
            self.confirmed_fault = "NORMAL_OPERATIONS"
        else:
            if predicted_fault == self.current_candidate_fault:
                self.consecutive_count += 1
            else:
                self.current_candidate_fault = predicted_fault
                self.consecutive_count = 1
                
            if self.consecutive_count >= self.debounce_threshold:
                self.confirmed_fault = self.current_candidate_fault
                
        is_alert_active = (self.confirmed_fault != "NORMAL_OPERATIONS")
        
        return AlertStatus(
            raw_result=raw_result,
            confirmed_fault_label=self.confirmed_fault,
            is_alert_active=is_alert_active,
            consecutive_fault_count=self.consecutive_count,
            debounce_threshold=self.debounce_threshold
        )
