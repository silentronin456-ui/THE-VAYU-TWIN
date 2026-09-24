import os
import json
import joblib
import numpy as np
import pandas as pd
import onnxruntime as ort
import xgboost as xgb

from prepare_data import load_and_preprocess_dataset, create_flight_level_split, CANONICAL_63_FEATURES

def validate():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    artifacts_dir = os.path.join(base_dir, "artifacts")
    
    print("=" * 70)
    print("SPASHT DIAGNOSTIC MODEL: ONNX RUNTIME VALIDATION")
    print("=" * 70)
    
    onnx_path = os.path.join(artifacts_dir, "diagnostic_xgboost_v1.onnx")
    encoder_path = os.path.join(artifacts_dir, "fault_label_encoder.pkl")
    schema_path = os.path.join(artifacts_dir, "feature_schema.json")
    model_path = os.path.join(artifacts_dir, "diagnostic_xgboost_model.joblib")
    
    for p in [onnx_path, encoder_path, schema_path, model_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing artifact: {p}")
            
    le = joblib.load(encoder_path)
    model = joblib.load(model_path)
    
    with open(schema_path, "r") as f:
        schema = json.load(f)
        
    # 1. Initialize ONNX Runtime Session
    session = ort.InferenceSession(onnx_path)
    
    inputs = session.get_inputs()
    outputs = session.get_outputs()
    
    print("\nONNX Model Inspection:")
    for i, inp in enumerate(inputs):
        print(f"  Input {i}: Name='{inp.name}', Type={inp.type}, Shape={inp.shape}")
    for i, out in enumerate(outputs):
        print(f"  Output {i}: Name='{out.name}', Type={out.type}, Shape={out.shape}")
        
    assert len(inputs) == 1, "Expected exactly 1 input node"
    assert inputs[0].name == "float_input", f"Input name mismatch: {inputs[0].name}"
    assert inputs[0].shape[1] == 63, f"Expected 63 input features, got {inputs[0].shape[1]}"
    
    # 2. Load held-out test data
    X, y_raw, flight_files, full_df = load_and_preprocess_dataset()
    y = le.transform(y_raw)
    _, test_mask, _, test_files = create_flight_level_split(flight_files, full_df)
    
    X_test = X[test_mask].values.astype(np.float32)
    y_test = y[test_mask]
    
    print(f"\nRunning comparative validation on {len(X_test):,} held-out test samples...")
    
    # Run test in batches of 10,000 for efficiency
    batch_size = 10000
    native_preds = []
    onnx_preds = []
    
    for start_idx in range(0, len(X_test), batch_size):
        end_idx = min(start_idx + batch_size, len(X_test))
        batch_X = X_test[start_idx:end_idx]
        
        # Native XGBoost inference
        n_pred = model.predict(batch_X)
        native_preds.extend(n_pred)
        
        # ONNX Runtime inference
        ort_out = session.run(None, {inputs[0].name: batch_X})
        # ort_out[0] contains class labels
        onnx_preds.extend(ort_out[0])
        
    native_preds = np.array(native_preds)
    onnx_preds = np.array(onnx_preds)
    
    # 3. Check exact agreement
    matches = (native_preds == onnx_preds).sum()
    match_rate = matches / len(X_test) * 100.0
    print(f"\nComparative Prediction Agreement:")
    print(f"  Total Validated Samples: {len(X_test):,}")
    print(f"  Exact Prediction Matches: {matches:,} / {len(X_test):,} ({match_rate:.4f}%)")
    
    if match_rate < 99.99:
        raise ValueError(f"ONNX vs Native mismatch rate too high: {100-match_rate:.4f}% mismatches!")
        
    # 4. Test Single-Row Live Inference Pipeline
    sample_row = X_test[0:1] # shape [1, 63]
    ort_res = session.run(None, {"float_input": sample_row})
    pred_int = int(ort_res[0][0])
    pred_label = le.inverse_transform([pred_int])[0]
    
    print(f"\nSingle-Row Live Telemetry Snapshot Inference Simulation:")
    print(f"  Input Tensor Shape:   {sample_row.shape}")
    print(f"  ONNX Output Integer:  {pred_int}")
    print(f"  Decoded String Label: '{pred_label}'")
    print(f"  Ground Truth Label:   '{le.inverse_transform([y_test[0]])[0]}'")
    
    print("\n" + "=" * 70)
    print("ALL ONNX RUNTIME VALIDATION CHECKS PASSED PERFECTLY!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    validate()
