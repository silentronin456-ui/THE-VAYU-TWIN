# SPASHT Diagnostic Engine: Final Model & Evaluation Report

**Project:** VayuTwin / SPASHT AI Architecture  
**Model Name:** `SPASHT-Diagnostic-Engine` (XGBoost v1.0)  
**Execution Date:** 2026-09-25  
**Final Status:** Validated, Verified & Exported to Production ONNX  

---

## 1. Executive Summary

The SPASHT Diagnostic Engine has been trained, rigorously evaluated on independent held-out flights, exported to standard ONNX format, and verified with 100% mathematical parity in ONNX Runtime.

* **Dataset Scope:** All **63 CSV files** (`567,000` total samples at 1 Hz across 7 subdirectories).
* **Fault Classes:** Full **25-class multi-class taxonomy** (1 nominal baseline + 17 base single faults + 7 compound/cascade/systemic faults).
* **Feature Signature:** Exactly **63 Float32 inputs** (53 canonical physical parameters + 3 Health Engine anomaly scores + 7 one-hot flight phases).
* **Held-Out Test Performance (27 Independent Flights, 243,000 Samples):**
  * **Overall Accuracy:** **99.64%** (vs. 50.75% Majority-Class Baseline)
  * **Macro F1-Score:** **0.9944**
  * **Weighted F1-Score:** **0.9964**
* **ONNX Runtime Parity:** **100.0000%** exact agreement on 243,000 held-out samples (`243,000 / 243,000`).

---

## 2. Complete 25-Class Taxonomy

The `LabelEncoder` was fitted across all 567,000 samples, establishing the following integer-to-string mapping:

| Class Index | `fault_label` String | Category | Support (Train) | Support (Test) | Total Samples |
|---|---|---|---|---|---|
| `0` | `ALTERNATOR_1_FAILURE` | Electrical Single Fault | 4,168 | 4,915 | 9,083 |
| `1` | `BLOCKED_FUEL_FILTER` | Fuel/Fluid Single Fault | 3,770 | 4,122 | 7,892 |
| `2` | `CASCADE_FLUID_THERMAL` | Compound Cascade | 5,000 | 5,000 | 10,000 |
| `3` | `CASCADE_MECHANICAL_FLUID` | Compound Cascade | 7,000 | 7,000 | 14,000 |
| `4` | `CASCADE_THERMAL_MECHANICAL` | Compound Cascade | 6,000 | 6,000 | 12,000 |
| `5` | `COOLANT_SYSTEM_LEAK` | Thermal Single Fault | 5,038 | 3,778 | 8,816 |
| `6` | `CRITICAL_OVERHEAT` | Thermal Single Fault | 4,399 | 4,352 | 8,751 |
| `7` | `ECU_LANE_A_FAILURE` | Electrical Single Fault | 4,431 | 4,504 | 8,935 |
| `8` | `ELEVATOR_BINDING` | Aero/Control Single Fault | 4,858 | 5,295 | 10,153 |
| `9` | `FUEL_PUMP_FAILURE` | Fuel/Fluid Single Fault | 3,650 | 3,766 | 7,416 |
| `10` | `MAIN_BUS_SHORT_CIRCUIT` | Electrical Single Fault | 4,332 | 4,454 | 8,786 |
| `11` | `MINOR_OVERHEAT` | Thermal Single Fault | 5,386 | 4,456 | 9,842 |
| `12` | `MINOR_VIBRATION` | Mechanical Single Fault | 5,252 | 3,653 | 8,905 |
| `13` | `NORMAL_OPERATIONS` | Nominal Baseline | 204,340 | 123,326 | 327,666 |
| `14` | `OAT_SENSOR_FAILURE` | Sensor Single Fault | 4,718 | 4,820 | 9,538 |
| `15` | `OIL_LEAK` | Fluid Single Fault | 3,820 | 4,847 | 8,667 |
| `16` | `PITOT_TUBE_BLOCKAGE` | Sensor Single Fault | 4,918 | 4,491 | 9,409 |
| `17` | `RADIATOR_BLOCKAGE` | Thermal Single Fault | 3,771 | 5,024 | 8,795 |
| `18` | `SENSOR_GHOSTING` | Avionics Systemic Fault | 8,000 | 8,000 | 16,000 |
| `19` | `SEVERE_VIBRATION` | Mechanical Single Fault | 4,521 | 5,351 | 9,872 |
| `20` | `SIMULTANEOUS_MECHANICAL_FLUID` | Multi-Fault Simultaneous | 4,999 | 4,999 | 9,998 |
| `21` | `SIMULTANEOUS_THERMAL_ELECTRICAL` | Multi-Fault Simultaneous | 4,999 | 4,999 | 9,998 |
| `22` | `STUCK_CONTROL_SURFACE` | Aero/Control Single Fault | 4,058 | 3,640 | 7,698 |
| `23` | `TOTAL_SYSTEM_FAILURE` | Full Catastrophic Failure | 8,500 | 8,500 | 17,000 |
| `24` | `VIBRATION_GEARBOX_BEARING` | Mechanical Single Fault | 4,072 | 3,708 | 7,780 |

---

## 3. Canonical 63-Feature Runtime Schema

The canonical schema is strictly ordered as follows in [`artifacts/feature_schema.json`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/artifacts/feature_schema.json):

1. **53 Physical Telemetry Parameters:**
   * `env.oat`, `env.wind_vector`
   * `flight.airspeed_ktas`, `flight.barometric_altitude`, `flight.elevator_angle`, `flight.elevator_load`, `flight.rudder_angle`, `flight.rudder_load`, `flight.aileron_angle`, `flight.aileron_load`, `flight.flap_position`, `flight.landing_gear_status`, `flight.weight_on_wheels`
   * `nav.gps_lat`, `nav.gps_lon`, `nav.ground_speed`, `nav.heading`
   * `engine.rpm`, `propeller.rpm`, `engine.map`
   * `engine.cht_1`, `engine.cht_2`, `engine.cht_3`, `engine.cht_4`
   * `engine.egt_1`, `engine.egt_2`, `engine.egt_3`, `engine.egt_4`
   * `engine.oil_pressure`, `engine.oil_temp`, `engine.coolant_pressure`, `engine.coolant_temp`
   * `sensor.vibration_engine_mount_x`, `sensor.vibration_engine_mount_y`, `sensor.vibration_engine_mount_z`, `sensor.vibration_gearbox`, `sensor.magnetic_chip_detector_mcd`
   * `fuel.flow_rate`, `fuel.total_fuel`, `fuel.injector_pulse_width`, `fuel.pump_primary_status`, `fuel.pump_secondary_status`
   * `ignition.coil_voltage`, `ignition.spark_misfire_flags`
   * `engine.oil_scavenge_pump_rate`, `engine.water_pump_speed`
   * `electrical.main_bus_voltage`, `electrical.main_bus_current`, `electrical.alternator_1_current`, `electrical.alternator_2_current`, `electrical.ecu_lane_a_status`, `electrical.ecu_lane_b_status`, `electrical.sensor_reference_5v`
2. **3 Health Engine Anomaly Scores:**
   * `anomaly_score_thermal`, `anomaly_score_mechanical`, `anomaly_score_electrical`
3. **7 One-Hot Encoded Flight Phase Flags:**
   * `flight.phase_STARTUP`, `flight.phase_WARMUP`, `flight.phase_TAKEOFF`, `flight.phase_CLIMB`, `flight.phase_CRUISE`, `flight.phase_DESCENT`, `flight.phase_LANDING`

---

## 4. Preprocessing & Flight-Level Splitting

* **Pre-processing:**
  1. For the 14 cascade CSV files, the column header `flags` is systematically mapped to `flight.phase`.
  2. The 53 physical parameters in cascade files (where CHT/EGT were interleaved) are programmatically re-ordered to the exact canonical sequence matching the base files.
  3. `pd.Categorical(df['flight.phase'], categories=FLIGHT_PHASES)` guarantees consistent 7-column binary one-hot generation across all flights.
* **Flight-Level Partitioning Strategy:**
  * **Train Set:** **36 flights** (`324,000` samples / 57.14%)
    * 12 nominal flights (`flight_001` through `flight_012`)
    * 17 base fault flights (first flight of each pair: `flight_016`, `flight_018`, `flight_020`, `flight_022`, `flight_024`, `flight_026`, `flight_028`, `flight_030`, `flight_032`, `flight_034`, `flight_036`, `flight_038`, `flight_040`, `flight_042`, `flight_044`, `flight_046`, `flight_048`)
    * 7 cascade flights (`_v1` files: `01_v1` through `07_v1`)
  * **Held-Out Test Set:** **27 flights** (`243,000` samples / 42.86%)
    * 3 nominal flights (`flight_013`, `flight_014`, `flight_015`)
    * 17 base fault flights (second flight of each pair: `flight_017`, `flight_019`, `flight_021`, `flight_023`, `flight_025`, `flight_027`, `flight_029`, `flight_031`, `flight_033`, `flight_035`, `flight_037`, `flight_039`, `flight_041`, `flight_043`, `flight_045`, `flight_047`, `flight_049`)
    * 7 cascade flights (`_v2` files: `01_v2` through `07_v2`)
* **Leakage Guarantee:** Zero row-level cross-contamination. Test samples originate exclusively from separate flight simulation runs.

---

## 5. Model Architecture & Hyperparameters

```python
xgb.XGBClassifier(
    objective='multi:softprob',
    num_class=25,
    max_depth=6,
    learning_rate=0.1,
    n_estimators=100,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    tree_method='hist',
    device='cpu'
)
```

---

## 6. Held-Out Evaluation Metrics

```text
================================================================================
HELD-OUT TEST EVALUATION (27 Independent Flights, 243,000 Samples)
================================================================================
  Overall Accuracy:             99.64% (Train Accuracy: 100.00%)
  Majority Class Baseline:      50.75% (Predicting NORMAL_OPERATIONS)
  Macro Precision:              0.9962
  Macro Recall:                 0.9929
  Macro F1-Score:               0.9944
  Weighted Precision:           0.9965
  Weighted Recall:              0.9964
  Weighted F1-Score:            0.9964
================================================================================
```

### Detailed Per-Class Classification Report

| Class Label | Precision | Recall | F1-Score | Support (Samples) |
|---|---|---|---|---|
| `ALTERNATOR_1_FAILURE` | 0.9980 | 0.9998 | 0.9989 | 4,915 |
| `BLOCKED_FUEL_FILTER` | 0.9998 | 0.9719 | 0.9856 | 4,122 |
| `CASCADE_FLUID_THERMAL` | 1.0000 | 0.9998 | 0.9999 | 5,000 |
| `CASCADE_MECHANICAL_FLUID` | 1.0000 | 1.0000 | 1.0000 | 7,000 |
| `CASCADE_THERMAL_MECHANICAL` | 1.0000 | 0.9825 | 0.9912 | 6,000 |
| `COOLANT_SYSTEM_LEAK` | 0.9995 | 0.9979 | 0.9987 | 3,778 |
| `CRITICAL_OVERHEAT` | 0.9635 | 0.9995 | 0.9812 | 4,352 |
| `ECU_LANE_A_FAILURE` | 1.0000 | 1.0000 | 1.0000 | 4,504 |
| `ELEVATOR_BINDING` | 0.9796 | 0.9994 | 0.9894 | 5,295 |
| `FUEL_PUMP_FAILURE` | 1.0000 | 1.0000 | 1.0000 | 3,766 |
| `MAIN_BUS_SHORT_CIRCUIT` | 1.0000 | 1.0000 | 1.0000 | 4,454 |
| `MINOR_OVERHEAT` | 0.9704 | 1.0000 | 0.9850 | 4,456 |
| `MINOR_VIBRATION` | 1.0000 | 1.0000 | 1.0000 | 3,653 |
| `NORMAL_OPERATIONS` | 0.9965 | 1.0000 | 0.9982 | 123,326 |
| `OAT_SENSOR_FAILURE` | 0.9998 | 1.0000 | 0.9999 | 4,820 |
| `OIL_LEAK` | 0.9983 | 0.9608 | 0.9792 | 4,847 |
| `PITOT_TUBE_BLOCKAGE` | 0.9998 | 0.9978 | 0.9988 | 4,491 |
| `RADIATOR_BLOCKAGE` | 0.9996 | 0.9136 | 0.9547 | 5,024 |
| `SENSOR_GHOSTING` | 1.0000 | 1.0000 | 1.0000 | 8,000 |
| `SEVERE_VIBRATION` | 1.0000 | 1.0000 | 1.0000 | 5,351 |
| `SIMULTANEOUS_MECHANICAL_FLUID` | 1.0000 | 1.0000 | 1.0000 | 4,999 |
| `SIMULTANEOUS_THERMAL_ELECTRICAL` | 1.0000 | 1.0000 | 1.0000 | 4,999 |
| `STUCK_CONTROL_SURFACE` | 0.9995 | 1.0000 | 0.9997 | 3,640 |
| `TOTAL_SYSTEM_FAILURE` | 1.0000 | 1.0000 | 1.0000 | 8,500 |
| `VIBRATION_GEARBOX_BEARING` | 1.0000 | 1.0000 | 1.0000 | 3,708 |

---

## 7. Feature Importance & Interpretability

Top 15 most informative features by average information gain:

1. `anomaly_score_mechanical` (Primary cross-subsystem mechanical trip indicator)
2. `anomaly_score_electrical` (Primary electrical/avionics trip indicator)
3. `electrical.alternator_1_current` (Isolates alternator failures)
4. `sensor.vibration_gearbox` (Isolates gearbox bearing anomalies)
5. `engine.coolant_temp` (Discriminates minor vs. critical thermal events)
6. `electrical.ecu_lane_a_status` (Isolates lane A digital failure)
7. `sensor.vibration_engine_mount_x` (Separates minor vs. severe vibration)
8. `electrical.main_bus_voltage` (Isolates bus short circuits and total failures)
9. `anomaly_score_thermal` (Primary thermal trip indicator)
10. `fuel.flow_rate` (Detects fuel pump & filter flow anomalies)
11. `engine.oil_pressure` (Detects oil leaks and mechanical fluid collapses)
12. `flight.elevator_load` (Isolates elevator binding)
13. `flight.airspeed_ktas` (Detects pitot tube blockages)
14. `env.oat` (Detects OAT sensor drift/failure)
15. `flight.phase_CRUISE` (Contextualizes phase-dependent nominal envelope)

* **Physical Validity:** The model heavily leverages the 3 Health Engine anomaly scores for macro triage while utilizing specific physical sensors for fine-grained root-cause isolation.

---

## 8. Artifacts Inventory

All required production artifacts have been verified in [`artifacts/`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/artifacts):

1. [`artifacts/diagnostic_xgboost_v1.onnx`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/artifacts/diagnostic_xgboost_v1.onnx) (`916,755` bytes) — Standard ONNX neural computation graph expecting `[None, 63]` float tensor.
2. [`artifacts/fault_label_encoder.pkl`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/artifacts/fault_label_encoder.pkl) — Scikit-Learn `LabelEncoder` object with all 25 classes.
3. [`artifacts/feature_schema.json`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/artifacts/feature_schema.json) — Ordered JSON list of 63 input feature names.
4. [`artifacts/manifest.json`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/artifacts/manifest.json) — Model metadata, framework version, opset 12, I/O signature.

---

## 9. Limitations & Deployment Recommendations

1. **Flight Sample Diversity:** Each fault type is represented by 2 independent flights (1 in train, 1 in test). While the model achieves 99.64% accuracy across the 27 held-out flights, expanding future training sets to 10+ simulation runs per fault mode with variable turbulence and atmospheric conditions is recommended.
2. **Sequential Inference:** In the live Python backend, pass 1 Hz snapshots preprocessed to the canonical 63-feature order. Feed the tensor into `diagnostic_xgboost_v1.onnx` and decode the integer output with `fault_label_encoder.pkl`.

---

**Report complete.**
