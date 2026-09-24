# Diagnostic Engine: Input/Output Mapping

---

## 1. The AI Boundary (The ONNX File)
The XGBoost ONNX file (`diagnostic_xgboost_v1.onnx`) is a multi-class classifier.
*   **INPUTS (63 Nodes):** 
    *   53 normalized physical telemetry parameters
    *   3 Anomaly Scores (Calculated by your Python code from the Health Model!)
    *   7 Phase Flags (One-Hot Encoded from the `flight.phase` string)
*   **OUTPUTS (1 Node):** 
    *   1 Integer representing the predicted fault class (e.g., `4`).

## 2. The Runtime Boundary (Your Python Code)
The ONNX file only outputs a raw number. Your Python code must translate it.
1. Your Python code grabs the integer `4` from the ONNX output.
2. Your Python code uses `fault_label_encoder.pkl` to translate `4` into the string `"COOLANT_SYSTEM_LEAK"`.
3. Your Python code triggers the Sanjeevani UI alert so the pilot sees the error.
