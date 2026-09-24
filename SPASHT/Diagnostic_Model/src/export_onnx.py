import os
import json
import joblib
import numpy as np
import onnxmltools
from onnxmltools.convert.common.data_types import FloatTensorType

from prepare_data import CANONICAL_63_FEATURES

def export():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    artifacts_dir = os.path.join(base_dir, "artifacts")
    
    print("=" * 70)
    print("SPASHT DIAGNOSTIC MODEL: ONNX EXPORT PIPELINE")
    print("=" * 70)
    
    # 1. Load trained model and encoder
    model_path = os.path.join(artifacts_dir, "diagnostic_xgboost_model.joblib")
    encoder_path = os.path.join(artifacts_dir, "fault_label_encoder.pkl")
    
    if not os.path.exists(model_path) or not os.path.exists(encoder_path):
        raise FileNotFoundError("Trained model or encoder not found. Run train_model.py first.")
        
    model = joblib.load(model_path)
    le = joblib.load(encoder_path)
    
    print(f"Loaded trained XGBoost model ({len(le.classes_)} classes).")
    
    # 2. Define ONNX input signature: FloatTensorType with shape [None, 63]
    initial_type = [('float_input', FloatTensorType([None, 63]))]
    
    print("Exporting XGBoost Classifier to ONNX format (opset 12)...")
    onnx_model = onnxmltools.convert_xgboost(
        model,
        initial_types=initial_type,
        target_opset=12
    )
    
    # 3. Save ONNX binary
    onnx_file_path = os.path.join(artifacts_dir, "diagnostic_xgboost_v1.onnx")
    with open(onnx_file_path, "wb") as f:
        f.write(onnx_model.SerializeToString())
    print(f"Successfully saved ONNX model to: {onnx_file_path}")
    print(f"ONNX Model File Size: {os.path.getsize(onnx_file_path):,} bytes")
    
    # 4. Generate manifest.json
    manifest_data = {
        "model_name": "SPASHT-Diagnostic-Engine",
        "version": "1.0",
        "framework": "ONNX",
        "opset": 12,
        "input_signature": {
            "name": "float_input",
            "shape": [None, 63],
            "dtype": "FLOAT"
        },
        "output_signature": {
            "label": {
                "name": "label",
                "dtype": "INT64",
                "description": "Predicted fault class index (0 to 24)"
            },
            "probabilities": {
                "name": "probabilities",
                "dtype": "MAP(INT64, FLOAT)",
                "description": "Softmax probability distribution across 25 classes"
            }
        },
        "classes_count": len(le.classes_),
        "classes": list(le.classes_),
        "input_features_count": len(CANONICAL_63_FEATURES),
        "input_features": CANONICAL_63_FEATURES,
        "timestamp": "2026-09-25",
        "hardware_target": "Edge / Cockpit Runtime & Cloud Telemetry Stream"
    }
    
    manifest_path = os.path.join(artifacts_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Successfully created runtime manifest: {manifest_path}")
    
    return onnx_file_path

if __name__ == "__main__":
    export()
