import os
import json
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

from prepare_data import load_and_preprocess_dataset, create_flight_level_split, CANONICAL_63_FEATURES

def evaluate():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    artifacts_dir = os.path.join(base_dir, "artifacts")
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    print("=" * 70)
    print("SPASHT DIAGNOSTIC MODEL: EVALUATION & SANITY CHECKS")
    print("=" * 70)
    
    # 1. Load artifacts and data
    encoder_path = os.path.join(artifacts_dir, "fault_label_encoder.pkl")
    model_path = os.path.join(artifacts_dir, "diagnostic_xgboost_model.joblib")
    
    if not os.path.exists(encoder_path) or not os.path.exists(model_path):
        raise FileNotFoundError("Missing artifacts. Please run train_model.py first.")
        
    le = joblib.load(encoder_path)
    model = joblib.load(model_path)
    
    X, y_raw, flight_files, full_df = load_and_preprocess_dataset()
    y = le.transform(y_raw)
    train_mask, test_mask, train_files, test_files = create_flight_level_split(flight_files, full_df)
    
    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    
    print("\nRunning Model Predictions...")
    t0 = time.time()
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    print(f"Predictions generated in {time.time()-t0:.2f}s")
    
    # 2. Compute Performance Metrics
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    # Majority class baseline
    # Find integer corresponding to 'NORMAL_OPERATIONS'
    norm_idx = int(le.transform(['NORMAL_OPERATIONS'])[0])
    majority_pred = np.full_like(y_test, norm_idx)
    majority_acc = accuracy_score(y_test, majority_pred)
    
    test_macro_p = precision_score(y_test, y_test_pred, average='macro', zero_division=0)
    test_macro_r = recall_score(y_test, y_test_pred, average='macro', zero_division=0)
    test_macro_f1 = f1_score(y_test, y_test_pred, average='macro', zero_division=0)
    
    test_weighted_p = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
    test_weighted_r = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
    test_weighted_f1 = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
    
    print("\n" + "=" * 50)
    print("HELD-OUT TEST SET EVALUATION (27 Independent Flights)")
    print("=" * 50)
    print(f"  Accuracy:             {test_acc*100:.2f}% (Train Accuracy: {train_acc*100:.2f}%)")
    print(f"  Majority Baseline:    {majority_acc*100:.2f}% (Predicting NORMAL_OPERATIONS)")
    print(f"  Macro Precision:      {test_macro_p:.4f}")
    print(f"  Macro Recall:         {test_macro_r:.4f}")
    print(f"  Macro F1-Score:       {test_macro_f1:.4f}")
    print(f"  Weighted Precision:   {test_weighted_p:.4f}")
    print(f"  Weighted Recall:      {test_weighted_r:.4f}")
    print(f"  Weighted F1-Score:    {test_weighted_f1:.4f}")
    
    # Detailed Classification Report
    cls_report = classification_report(
        y_test, y_test_pred,
        target_names=le.classes_,
        digits=4,
        zero_division=0
    )
    print("\nDetailed Per-Class Performance:")
    print(cls_report)
    
    # 3. Save Evaluation Report TXT
    report_txt_path = os.path.join(reports_dir, "evaluation_report.txt")
    with open(report_txt_path, "w") as f:
        f.write("SPASHT DIAGNOSTIC XGBOOST MODEL EVALUATION REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Dataset: 63 CSV files (567,000 samples)\n")
        f.write(f"Class Count: 25 Unique Fault Classes\n")
        f.write(f"Input Features: 63 Canonical Parameters\n\n")
        f.write(f"Flight Split: 36 Train Flights ({len(y_train):,} rows) / 27 Held-out Test Flights ({len(y_test):,} rows)\n\n")
        f.write(f"Overall Metrics:\n")
        f.write(f"  Train Accuracy:       {train_acc*100:.2f}%\n")
        f.write(f"  Test Accuracy:        {test_acc*100:.2f}%\n")
        f.write(f"  Majority Baseline:    {majority_acc*100:.2f}%\n")
        f.write(f"  Macro Precision:      {test_macro_p:.4f}\n")
        f.write(f"  Macro Recall:         {test_macro_r:.4f}\n")
        f.write(f"  Macro F1-Score:       {test_macro_f1:.4f}\n")
        f.write(f"  Weighted Precision:   {test_weighted_p:.4f}\n")
        f.write(f"  Weighted Recall:      {test_weighted_r:.4f}\n")
        f.write(f"  Weighted F1-Score:    {test_weighted_f1:.4f}\n\n")
        f.write("Per-Class Detailed Classification Report:\n")
        f.write(cls_report + "\n")
    print(f"Saved evaluation text report to: {report_txt_path}")
    
    # 4. Confusion Matrix Plot
    cm = confusion_matrix(y_test, y_test_pred)
    plt.figure(figsize=(18, 14))
    sns.heatmap(
        cm, annot=False, cmap="Blues", fmt="d",
        xticklabels=le.classes_, yticklabels=le.classes_
    )
    plt.title("SPASHT Diagnostic Model: Confusion Matrix (25 Classes - Held-Out Test Flights)", fontsize=14, pad=15)
    plt.xlabel("Predicted Class", fontsize=12)
    plt.ylabel("True Class", fontsize=12)
    plt.xticks(rotation=90, fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    cm_path = os.path.join(reports_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"Saved confusion matrix plot to: {cm_path}")
    
    # 5. Feature Importance Analysis
    booster = model.get_booster()
    importance_gain = booster.get_score(importance_type="gain")
    # Map feature names
    feature_names = CANONICAL_63_FEATURES
    feat_scores = []
    for f_idx, col_name in enumerate(feature_names):
        # XGBoost hist might use f0, f1... or column names
        score = importance_gain.get(col_name, importance_gain.get(f"f{f_idx}", 0.0))
        feat_scores.append((col_name, score))
        
    feat_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Plot top 25 features
    top_feats = feat_scores[:25]
    plt.figure(figsize=(12, 10))
    y_pos = np.arange(len(top_feats))
    plt.barh(y_pos, [s[1] for s in top_feats][::-1], align='center', color='navy')
    plt.yticks(y_pos, [s[0] for s in top_feats][::-1], fontsize=10)
    plt.xlabel("Average Gain (Information Gain per Split)", fontsize=12)
    plt.title("Top 25 Most Informative Features in Diagnostic Engine", fontsize=14, pad=15)
    plt.tight_layout()
    fi_path = os.path.join(reports_dir, "feature_importance.png")
    plt.savefig(fi_path, dpi=300)
    plt.close()
    print(f"Saved feature importance plot to: {fi_path}")
    
    # 6. Leakage & Sanity Check Report
    # Check flight overlap
    overlap = set(train_files).intersection(set(test_files))
    print(f"\nLeakage Check: Flight overlap count between Train and Test: {len(overlap)}")
    assert len(overlap) == 0, f"Critical Leakage: Overlapping flights found: {overlap}"
    
    return {
        "train_accuracy": train_acc,
        "test_accuracy": test_acc,
        "majority_baseline": majority_acc,
        "macro_f1": test_macro_f1,
        "weighted_f1": test_weighted_f1,
        "top_features": feat_scores[:10],
        "cls_report": cls_report
    }

if __name__ == "__main__":
    evaluate()
