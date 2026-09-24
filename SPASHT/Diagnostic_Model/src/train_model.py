import os
import json
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

from prepare_data import load_and_preprocess_dataset, create_flight_level_split, CANONICAL_63_FEATURES

def train():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    artifacts_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    
    print("=" * 70)
    print("SPASHT DIAGNOSTIC MODEL: TRAINING PIPELINE (25 CLASSES)")
    print("=" * 70)
    
    # 1. Load Data
    t0 = time.time()
    X, y_raw, flight_files, full_df = load_and_preprocess_dataset()
    print(f"Data loading & canonical feature alignment completed in {time.time()-t0:.2f}s")
    
    # 2. Label Encoding
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    num_classes = len(le.classes_)
    print(f"Fitted LabelEncoder across {len(y):,} samples.")
    print(f"Verified Class Count: {num_classes}")
    
    if num_classes != 25:
        raise ValueError(f"Expected 25 classes, but LabelEncoder found {num_classes} classes!")
        
    print("\nClass Mapping (Integer -> String):")
    for idx, cls_name in enumerate(le.classes_):
        print(f"  {idx:2d} -> {cls_name}")
        
    # Save fault_label_encoder.pkl
    encoder_path = os.path.join(artifacts_dir, "fault_label_encoder.pkl")
    joblib.dump(le, encoder_path)
    print(f"\nSaved LabelEncoder to: {encoder_path}")
    
    # Save feature_schema.json
    schema_path = os.path.join(artifacts_dir, "feature_schema.json")
    with open(schema_path, "w") as f:
        json.dump(CANONICAL_63_FEATURES, f, indent=2)
    print(f"Saved Canonical Feature Schema (63 features) to: {schema_path}")
    
    # 3. Flight-Level Split
    train_mask, test_mask, train_files, test_files = create_flight_level_split(flight_files, full_df)
    
    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    
    print(f"\nDataset Partitions:")
    print(f"  Training Set:   {X_train.shape[0]:,} samples across {len(train_files)} flights")
    print(f"  Held-out Test:  {X_test.shape[0]:,} samples across {len(test_files)} flights")
    
    # Verify both partitions contain all 25 classes
    train_classes = set(y_train)
    test_classes = set(y_test)
    print(f"  Classes in Train: {len(train_classes)} / 25")
    print(f"  Classes in Test:  {len(test_classes)} / 25")
    
    # 4. Initialize XGBoost
    # Check GPU availability
    device = "cpu"
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            print("CUDA GPU detected. Setting device='cuda'.")
        else:
            print("No CUDA GPU detected. Using CPU histogram boosting.")
    except Exception:
        print("Using CPU histogram boosting.")
        
    xgb_params = {
        "objective": "multi:softprob",
        "num_class": num_classes,
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 100,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "tree_method": "hist",
        "device": device
    }
    
    print("\nModel Hyperparameters:")
    for k, v in xgb_params.items():
        print(f"  {k}: {v}")
        
    model = xgb.XGBClassifier(**xgb_params)
    
    # 5. Fit Model
    print("\nTraining XGBClassifier on 324,000 samples...")
    t_train_start = time.time()
    # Fit using numpy array to maintain f0..f62 indexing required by ONNX converter
    model.fit(X_train.values, y_train)
    t_train_end = time.time()
    print(f"Training completed successfully in {t_train_end - t_train_start:.2f}s!")
    
    # 6. Save model checkpoint
    model_save_path = os.path.join(artifacts_dir, "diagnostic_xgboost_model.joblib")
    joblib.dump(model, model_save_path)
    print(f"Saved native model checkpoint to: {model_save_path}")
    
    return model, le, X_train, y_train, X_test, y_test, train_files, test_files

if __name__ == "__main__":
    train()
