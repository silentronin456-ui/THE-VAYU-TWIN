# SPASHT Diagnostic Engine: Runtime Integration Guide

**Module:** `src/diagnostic_runtime.py`  
**Model Artifact:** `artifacts/diagnostic_xgboost_v1.onnx`  
**Label Mapping:** `artifacts/fault_label_encoder.pkl`  
**Authoritative Feature Order:** `artifacts/feature_schema.json`  

---

## 1. Runtime Architecture Overview

The SPASHT Diagnostic Engine is designed for sub-millisecond, low-overhead execution on cockpit avionics and edge telemetry gateways. It classifies 1 Hz snapshots of aircraft telemetry and Health Engine anomaly scores into **25 discrete operational states** (1 nominal condition and 24 fault types).

```text
+-----------------------------------------------------------------------------------+
|                            VayuTwin Ingestion Layer                               |
|   1. 53 Physical Telemetry Parameters (Sensors / FDR / Simulator)                 |
|   2. 3 Health Engine Anomaly Scores (Thermal, Mechanical, Electrical)             |
|   3. 1 Flight Phase Tag ('STARTUP' .. 'LANDING')                                  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        DiagnosticEngine Preprocessor                              |
|   - Input Validation (numeric types, NaN/Inf checks, phase domain verification)  |
|   - Phase One-Hot Encoding (7 binary flags)                                       |
|   - Canonical 63-Feature Ordering via artifacts/feature_schema.json               |
|   - Shape Assertion: [batch_size, 63] Float32 Tensor                              |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        ONNX Runtime Inference Session                             |
|   Model: artifacts/diagnostic_xgboost_v1.onnx (opset 12)                          |
|   Input:  'float_input' [batch_size, 63] (FLOAT)                                  |
|   Output: 'label' [batch_size] (INT64)                                            |
|           'probabilities' [batch_size, 25] (FLOAT)                                |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                       Label Decoder & Output Structuring                          |
|   - Decode integer prediction via artifacts/fault_label_encoder.pkl               |
|   - Map top softmax score as confidence                                           |
|   - Construct structured DiagnosticResult object                                  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                       Optional Alert Stabilizer Layer                             |
|   - Temporal Debouncer (K-frame consecutive verification, default K=3)            |
|   - Filters transient transition boundary jitter                                  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                     Sanjeevani UI / GCS Cockpit Alerting                          |
+-----------------------------------------------------------------------------------+
```

---

## 2. Input Contract

A single telemetry snapshot must be passed as a dictionary containing **57 required fields**:

1. **53 Physical Parameters:**
   * **Atmospheric:** `env.oat`, `env.wind_vector`
   * **Aerodynamic & Flight Dynamics:** `flight.airspeed_ktas`, `flight.barometric_altitude`, `flight.elevator_angle`, `flight.elevator_load`, `flight.rudder_angle`, `flight.rudder_load`, `flight.aileron_angle`, `flight.aileron_load`, `flight.flap_position`, `flight.landing_gear_status`, `flight.weight_on_wheels`
   * **Navigation:** `nav.gps_lat`, `nav.gps_lon`, `nav.ground_speed`, `nav.heading`
   * **Propulsion & Thermal:** `engine.rpm`, `propeller.rpm`, `engine.map`, `engine.cht_1`..`4`, `engine.egt_1`..`4`, `engine.oil_pressure`, `engine.oil_temp`, `engine.coolant_pressure`, `engine.coolant_temp`, `engine.oil_scavenge_pump_rate`, `engine.water_pump_speed`
   * **Vibration & Structural:** `sensor.vibration_engine_mount_x`..`z`, `sensor.vibration_gearbox`, `sensor.magnetic_chip_detector_mcd`
   * **Fuel & Ignition:** `fuel.flow_rate`, `fuel.total_fuel`, `fuel.injector_pulse_width`, `fuel.pump_primary_status`, `fuel.pump_secondary_status`, `ignition.coil_voltage`, `ignition.spark_misfire_flags`
   * **Electrical & Avionics:** `electrical.main_bus_voltage`, `electrical.main_bus_current`, `electrical.alternator_1_current`, `electrical.alternator_2_current`, `electrical.ecu_lane_a_status`, `electrical.ecu_lane_b_status`, `electrical.sensor_reference_5v`
2. **3 Health Engine Anomaly Scores:**
   * `anomaly_score_thermal` (Float $\in [0.0, 1.0]$)
   * `anomaly_score_mechanical` (Float $\in [0.0, 1.0]$)
   * `anomaly_score_electrical` (Float $\in [0.0, 1.0]$)
3. **Flight Phase:**
   * `flight.phase` (or legacy `flags`) string $\in$ `{"STARTUP", "WARMUP", "TAKEOFF", "CLIMB", "CRUISE", "DESCENT", "LANDING"}`

---

## 3. Python API Quickstart

### A. Single Snapshot Inference (1 Hz Live Stream)

```python
from diagnostic_runtime import DiagnosticEngine

# 1. Initialize engine (loads ONNX model and LabelEncoder)
engine = DiagnosticEngine()

# 2. Ingest 1 Hz telemetry dictionary
snapshot = {
    "env.oat": 15.2,
    "env.wind_vector": 3.4,
    "flight.airspeed_ktas": 142.0,
    "flight.barometric_altitude": 5500.0,
    # ... all other 50 physical parameters ...
    "anomaly_score_thermal": 0.85,
    "anomaly_score_mechanical": 0.0,
    "anomaly_score_electrical": 0.0,
    "flight.phase": "CRUISE"
}

# 3. Execute diagnosis
result = engine.diagnose_snapshot(snapshot, timestamp="2026-09-25T14:32:01Z")

print(f"Status:     {result.status}")
print(f"Prediction: {result.predicted_fault_label}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Is Fault:   {result.is_fault}")
```

### B. Batch Inference (Historical / Replay Analytics)

```python
import pandas as pd
from diagnostic_runtime import DiagnosticEngine

engine = DiagnosticEngine()

# Load batch dataframe
df = pd.read_csv("flight_recording.csv")

# Run batch diagnosis
results = engine.diagnose_batch(df)

for r in results[:5]:
    print(r.timestamp, r.predicted_fault_label, r.confidence)
```

### C. Debounced Cockpit Alerting (Sanjeevani UI Integration)

```python
from diagnostic_runtime import DiagnosticEngine, DiagnosticAlertStabilizer

engine = DiagnosticEngine()
stabilizer = DiagnosticAlertStabilizer(engine, debounce_threshold=3)

# Stream sequential 1-second frames
for frame in telemetry_stream:
    alert_status = stabilizer.process_snapshot(frame)
    if alert_status.is_alert_active:
        print(f"CRITICAL ALERT: {alert_status.confirmed_fault_label}")
```

---

## 4. Structured Output Format

The `DiagnosticResult.to_dict()` method serializes the prediction to standard JSON:

```json
{
  "predicted_class_id": 6,
  "predicted_fault_label": "CRITICAL_OVERHEAT",
  "confidence": 0.9842,
  "probabilities": {
    "ALTERNATOR_1_FAILURE": 0.0001,
    "CRITICAL_OVERHEAT": 0.9842,
    "MINOR_OVERHEAT": 0.0152,
    "NORMAL_OPERATIONS": 0.0002
  },
  "flight_phase": "CRUISE",
  "timestamp": "2026-09-25T14:32:01Z",
  "is_fault": true,
  "status": "FAULT_DETECTED"
}
```

---

## 5. Error Handling & Validation Rules

`DiagnosticEngine` enforces strict validation before calling ONNX Runtime:

| Error Condition | Exception Raised | Description |
|---|---|---|
| Missing Telemetry Field | `DiagnosticValidationError` | Identifies the exact missing feature key. |
| Non-Numeric Type | `DiagnosticValidationError` | Rejects non-numeric values (e.g. strings in numeric fields). |
| Non-Finite Values (`NaN`, `Inf`) | `DiagnosticValidationError` | Rejects `NaN`, `+Inf`, `-Inf`. |
| Invalid Flight Phase | `DiagnosticValidationError` | Rejects phase strings outside the 7 standard phases. |
| Missing Artifact File | `DiagnosticRuntimeError` | Raised at initialization if any production artifact is absent. |
| Bad Tensor Shape | `DiagnosticValidationError` | Rejects tensors not matching `[N, 63]`. |

---

## 6. Integration Points with VayuTwin

1. **Upstream Health Engine:** The Health Engine calculates rolling anomaly scores ($S_T, S_M, S_E$) from reconstruction errors. These are merged into the telemetry dictionary under keys `anomaly_score_thermal`, `anomaly_score_mechanical`, and `anomaly_score_electrical`.
2. **Upstream Flight Director / FMS:** Supplies the current flight phase tag (`flight.phase`).
3. **Downstream Sanjeevani UI:** Consumes the `DiagnosticResult` or `AlertStatus` object over ZeroMQ / WebSocket / IPC to render pilot alert banners and checklists.

---

## 7. Known Limitations

1. **Snapshot Nature:** The classifier evaluates each 1 Hz snapshot independently. Temporal consistency is handled by the optional `DiagnosticAlertStabilizer` debouncing layer.
2. **Transition Seconds:** During the initial 1–2 seconds of fault onset before sensor readings diverge past ambient noise, individual snapshots may oscillate before stabilizing.
