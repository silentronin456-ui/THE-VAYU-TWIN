# SPASHT Diagnostic Model - Project State

## 1. Project Purpose
The SPASHT Diagnostic Engine is a high-speed, lightweight multi-class classification system for the VayuTwin project. It processes 1 Hz multi-sensor aircraft telemetry snapshots combined with Health Model anomaly scores and flight phase flags to classify the aircraft's operational state into 25 distinct categories (1 nominal condition and 24 specific single, compound, or cascading fault modes).

---

## 2. Current Architecture
The end-to-end inference and diagnostic pipeline operates as follows:

```text
Raw Telemetry Stream (1 Hz) 
  → DiagnosticEngine Preprocessing & Column Alignment (53 physical sensors)
  → Health Engine Integration (3 anomaly scores: thermal, mechanical, electrical)
  → One-Hot Phase Categorization (7 binary flags: STARTUP to LANDING)
  → Canonical 63-Feature Float32 Tensor [batch_size, 63]
  → 25-Class XGBoost Classifier (diagnostic_xgboost_v1.onnx via ONNX Runtime)
  → Dynamic Integer Output [0..24] + Softmax Probabilities [batch_size, 25]
  → Label Decoder (fault_label_encoder.pkl)
  → DiagnosticResult / Optional DiagnosticAlertStabilizer (Debounced Alert)
  → Sanjeevani UI Cockpit Alert Layer
```

Key architectural choices:
* **Model Family:** XGBoost `XGBClassifier` with histogram-based tree boosting (`tree_method='hist'`) for sub-millisecond inference.
* **Universal Deployment Target:** Exported via ONNX (opset 12) expecting a strict `[None, 63]` float tensor.
* **Decoupled Decoding:** String translation is decoupled from the ONNX graph via `fault_label_encoder.pkl`, enabling flexible multi-class expansion without ONNX graph re-architecting.
* **Authoritative Schema Contract:** `artifacts/feature_schema.json` is the dynamic single source of truth for runtime feature ordering.
* **Separated Alert Debouncing:** Optional `DiagnosticAlertStabilizer` provides temporal smoothing without altering the pure snapshot classifier.

---

## 3. Dataset Facts
* **Total Files:** 63 CSV files (9,000 continuous 1 Hz rows each, representing 2.5-hour flight missions).
* **Total Samples:** 567,000 rows.
* **Data Quality:** 0 missing values, 0 infinite values, 0 duplicate rows.
* **Folder Hierarchy:** 7 subdirectories:
  1. `nominal_diagnostic_dataset/` (15 files, 135,000 rows, 100% nominal)
  2. `Thermal Anomalies/` (8 files, 72,000 rows, 4 fault pairs)
  3. `mechanical_anomalies/` (8 files, 72,000 rows, 4 fault pairs)
  4. `fluid_fuel_anomalies/` (6 files, 54,000 rows, 3 fault pairs)
  5. `electrical_anomalies/` (6 files, 54,000 rows, 3 fault pairs)
  6. `aerodynamics_sensor_anomalies/` (6 files, 54,000 rows, 3 fault pairs)
  7. `spasht_official_cascades_58col/` (14 files, 126,000 rows, 7 cascade pairs)
* **Classes:** 25 unique labels (`NORMAL_OPERATIONS` + 17 base single faults + 7 compound/cascade faults).
* **Feature Composition (63 Total):**
  * 53 Physical Telemetry Parameters (aerodynamic, propulsion, thermal, electrical, navigation, vibration, fuel, ignition).
  * 3 Health Anomaly Scores (`anomaly_score_thermal`, `anomaly_score_mechanical`, `anomaly_score_electrical`).
  * 7 One-Hot Flight Phases (`STARTUP`, `WARMUP`, `TAKEOFF`, `CLIMB`, `CRUISE`, `DESCENT`, `LANDING`).
* **Schema Handling:** Cascade files had `flags` mapped to `flight.phase`, and interleaved CHT/EGT columns were aligned to canonical physical parameter ordering.

---

## 4. Source Files

### Source Code (`src/`)
* [`src/diagnostic_runtime.py`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/src/diagnostic_runtime.py): Production runtime wrapper (`DiagnosticEngine`, `DiagnosticResult`, `DiagnosticAlertStabilizer`) supporting single-snapshot and batch inference with strict validation.
* [`src/test_runtime_integration.py`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/src/test_runtime_integration.py): 11-test integration suite verifying parity, validation rejection, debouncing, and artifact immutability.
* [`src/prepare_data.py`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/src/prepare_data.py): Canonical 63-feature standardization, cascade schema alignment, and flight-level partition masks.
* [`src/train_model.py`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/src/train_model.py): Fits 25-class `LabelEncoder` and trains histogram XGBoost model.
* [`src/evaluate_model.py`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/src/evaluate_model.py): Flight-level holdout evaluation, classification metrics, confusion matrix, and feature gain analysis.
* [`src/export_onnx.py`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/src/export_onnx.py): Serializes trained model to ONNX opset 12 with shape `[None, 63]` and builds manifest.
* [`src/validate_onnx.py`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/src/validate_onnx.py): Verifies 100% mathematical parity between native XGBoost and ONNX Runtime across all held-out test flights.
* [`src/audit_dataset.py`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/src/audit_dataset.py): Automated recursive dataset auditing script.

### Production Artifacts (`artifacts/`)
* [`artifacts/diagnostic_xgboost_v1.onnx`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/artifacts/diagnostic_xgboost_v1.onnx): Universal ONNX computation graph (916 KB).
* [`artifacts/fault_label_encoder.pkl`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/artifacts/fault_label_encoder.pkl): Scikit-Learn `LabelEncoder` containing the 25 class mappings.
* [`artifacts/feature_schema.json`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/artifacts/feature_schema.json): Canonical ordered list of 63 input feature names.
* [`artifacts/manifest.json`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/artifacts/manifest.json): Deployment metadata and I/O signature specifications.
* [`artifacts/diagnostic_xgboost_model.joblib`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/artifacts/diagnostic_xgboost_model.joblib): Native XGBoost model checkpoint (2.6 MB).

### Documentation & Reports (`reports/` & `docs/`)
* [`docs/Diagnostic_Runtime_Integration.md`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/docs/Diagnostic_Runtime_Integration.md): Comprehensive developer guide for runtime integration, input contracts, and Sanjeevani UI alerting.
* [`reports/final_diagnostic_report.md`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/reports/final_diagnostic_report.md): Comprehensive model evaluation and benchmarking report.
* [`reports/dataset_audit.md`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/reports/dataset_audit.md) / [`dataset_audit.json`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/reports/dataset_audit.json): Exhaustive initial dataset inventory and discrepancy audit.
* [`reports/cascade_class_analysis.md`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/reports/cascade_class_analysis.md): Deep-dive into compound cascade signatures and 18 vs. 25 class justification.
* [`reports/confusion_matrix.png`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/reports/confusion_matrix.png): 25x25 held-out confusion matrix heatmap.
* [`reports/feature_importance.png`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/reports/feature_importance.png): Information gain bar chart for top 25 features.

---

## 5. Model Configuration
* **Classifier:** `xgboost.XGBClassifier`
* **Objective:** `multi:softprob`
* **Number of Classes (`num_class`):** `25` (dynamically derived from `LabelEncoder`)
* **Number of Estimators (`n_estimators`):** `100`
* **Maximum Tree Depth (`max_depth`):** `6`
* **Learning Rate (`learning_rate`):** `0.1`
* **Subsample Ratio (`subsample`):** `0.8`
* **Column Subsample by Tree (`colsample_bytree`):** `0.8`
* **Tree Method (`tree_method`):** `hist` (CPU histogram-based boosting)
* **Random Seed (`random_state`):** `42`

---

## 6. Verified Results
All metrics verified on **27 independent held-out flight files (243,000 samples)** with zero row/flight overlap:

* **Held-Out Test Accuracy:** **99.64%** (Train Accuracy: 100.00%)
* **Majority-Class Baseline:** **50.75%** (Predicting `NORMAL_OPERATIONS`)
* **Macro Precision / Recall / F1:** `0.9962` / `0.9929` / `0.9944`
* **Weighted Precision / Recall / F1:** `0.9965` / `0.9964` / `0.9964`
* **Top Information Gain Breakdown:**
  * Physical Telemetry Parameters: **76.62%**
  * Flight Phase Flags: **16.14%**
  * Health Anomaly Scores: **7.25%**
* **ONNX Runtime Parity:** **100.0000%** (`243,000 / 243,000` exact matches between Native XGBoost and ONNX Runtime).
* **Integration Test Suite:** **11 / 11 PASS** in `src/test_runtime_integration.py` (immutability, validation rejection, batch inference, debouncing).

---

## 7. Important Decisions
1. **Full 25-Class Scope:** Ingested all 63 files (including 14 cascade files) because cascade signatures represent distinct physical compound failure states explicitly planned in `Diagnostic_Step1_Data_Prep.md`.
2. **Flight-Level Splitting:** Split at the flight/file level (36 train flights / 27 test flights) because sequential 1 Hz time series within a flight would cause massive data leakage under random row splitting.
3. **Explicit Canonical Column Alignment:** Preprocessing indexes columns by explicit names (`CANONICAL_PHYSICAL_PARAMS`) rather than positional order, eliminating schema drift between base files and interleaved cascade files.
4. **Authoritative Runtime Schema:** `DiagnosticEngine` loads `artifacts/feature_schema.json` directly to construct the 63-feature tensor, ensuring runtime inference cannot diverge from training order.
5. **Separated Alert Debouncing:** Built `DiagnosticAlertStabilizer` as an independent temporal wrapper on top of the snapshot classifier, keeping ML inference stateless and clean.
6. **Dynamic Class Count Ingestion:** Model derives `num_class` dynamically from `LabelEncoder.classes_` (25) rather than hardcoding legacy 19 classes.
7. **ONNX Export via Standard Ops:** Serialized using `onnxmltools` with float tensor input `[None, 63]` and opset 12 for maximum cross-platform compatibility.

---

## 8. Known Limitations / Risks
1. **Limited Independent Flight Diversity:** Each specific fault type is represented by 2 simulation flights (1 in train, 1 in test). While test accuracy is 99.64%, statistical confidence regarding arbitrary turbulence and flight profiles is constrained by the simulation sample diversity.
2. **Synthetic Data Origin:** Telemetry is generated from flight dynamics simulations rather than real-world flight data recorders (FDR).
3. **External Dependencies:** Live telemetry streaming ingestion, GCS transport, and the frontend Sanjeevani UI live outside this repository; `DiagnosticEngine` provides the clean Python API boundary to connect with them.
4. **Transition Boundary Dynamics:** The 0.36% test error occurs almost exclusively at the exact 1–2 second transition window where nominal operation converts into a fault.

---

## 9. Current Status
* **DATASET:** COMPLETE (63 files, 567,000 rows, audited & verified)
* **PREPROCESSING:** COMPLETE (Canonical 63-feature pipeline verified)
* **TRAINING:** COMPLETE (25-class XGBoost model trained in 32.75s)
* **EVALUATION:** COMPLETE (99.64% held-out test accuracy, full reports generated)
* **ONNX:** COMPLETE (`artifacts/diagnostic_xgboost_v1.onnx` validated at 100% parity)
* **INTEGRATION:** COMPLETE (`src/diagnostic_runtime.py` implemented; final runtime suite: 11/11 PASS)
* **SIMULATOR:** COMPLETE (`src/simulate_live_feed.py` is an ASCII-safe simulation/test harness; 13/13 tests PASS)
* **FINAL VERIFICATION:** COMPLETE (syntax/import checks; deterministic nominal, known-fault, and cascade demonstrations passed)
* **ARTIFACT INTEGRITY:** VERIFIED (SHA-256 unchanged: ONNX `36EE418A16ED9DF769C087E708B2B6DB7CEAE5D9C848C52373A107935006C17F`; encoder `7C367433E6FF82774DEAADF3EF0B912EF811DEA56127C82737A9C5A14E1F6BFE`; schema `DB934ED71B5E875B911287121F6422491A3AD8C5DCC96671DEA8AEF4513BE46F`; manifest `F1CA2E1CB4D48E52040C6152EEDCE283AECFC79D16029E5F9171C31317FFB630`)
* **DOCUMENTATION:** UP TO DATE (`docs/Diagnostic_Runtime_Integration.md` & `PROJECT_STATE.md` synchronized)
* **INTEGRATION DISCOVERY:** COMPLETE (repository inspection confirmed external dependencies are absent)
* **READINESS:** **FROZEN FOR SUBMISSION**

---

## 10. Current Next Step

**Exact next step for VayuTwin:** Obtain stable contracts for (a) the Health Engine's three anomaly scores, (b) GCS telemetry field names, units, and flight-phase payload, and (c) Sanjeevani UI transport. Build the live adapter only in the owning integration repository after those contracts are supplied; do not alter this frozen diagnostic component.

**Hard blockers for live integration (external, not fixable in this repo):**
* SPASHT Health Engine (anomaly scores) — not present
* GCS / telemetry ingestion — not present
* Sanjeevani UI transport — not present

---

## 11. Changelog
* `2026-09-25 | DATASET AUDIT & CASCADE ANALYSIS | Verified 63 CSVs, 567,000 rows, 25 classes; identified schema variations in cascades; generated reports/dataset_audit.md and reports/cascade_class_analysis.md`
* `2026-09-25 | TRAINING PIPELINE IMPLEMENTATION | Built canonical 63-feature data pipeline (prepare_data.py); implemented flight-level train/test split (36/27 flights)`
* `2026-09-25 | MODEL TRAINING & EVALUATION | Trained 25-class histogram XGBoost model (train_model.py); evaluated held-out test set achieving 99.64% accuracy (evaluate_model.py)`
* `2026-09-25 | ONNX EXPORT & RUNTIME VALIDATION | Exported diagnostic_xgboost_v1.onnx (export_onnx.py); confirmed 100% parity on 243,000 test samples (validate_onnx.py); generated manifest.json`
* `2026-09-25 | RUNTIME INTEGRATION & VERIFICATION | Built diagnostic_runtime.py (DiagnosticEngine, AlertStabilizer); created test_runtime_integration.py (11/11 tests pass); created docs/Diagnostic_Runtime_Integration.md; updated PROJECT_STATE.md`
* `2026-09-25 | INTEGRATION DISCOVERY | Full repo audit completed. Confirmed: DiagnosticEngine API boundary is complete. Confirmed absent: Health Engine (anomaly scores), GCS telemetry feed, flight phase tagger, Sanjeevani UI transport. Report: integration_discovery_report.md`
* `2026-09-25 | FINAL VERIFICATION & FREEZE | Removed remaining Unicode from simulator console output; runtime tests 11/11 PASS; simulator tests 13/13 PASS; nominal, CRITICAL_OVERHEAT, and TOTAL_SYSTEM_FAILURE demonstrations passed; four production artifact hashes verified unchanged; component frozen for submission.`
