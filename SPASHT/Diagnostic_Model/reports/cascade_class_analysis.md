# SPASHT Diagnostic Model: Cascade Dataset & Target Class Analysis

**Investigation Focus:** Resolution of the 18/19 Base Classes vs. 25 Full Classes Architectural Decision  
**Target Dataset Examined:** [`data/diagnostic_dataset/spasht_official_cascades_58col/`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/data/diagnostic_dataset/spasht_official_cascades_58col)  
**Status:** Audit & Analysis Complete — No training or artifact generation performed.

---

## 1. Cascade File Inventory

The cascade dataset contains **14 CSV files** (7 distinct compound failure types evaluated across 2 independent simulation flights each, `_v1` and `_v2`):

| File Name | Rows | Fault Class Injected | Primary Subsystem 1 | Primary Subsystem 2 / Type |
|---|---|---|---|---|
| `01_CASCADE_THERMAL_MECHANICAL_v1.csv` | 9,000 | `CASCADE_THERMAL_MECHANICAL` | Thermal (Overheat) | Mechanical (Vibrations) |
| `01_CASCADE_THERMAL_MECHANICAL_v2.csv` | 9,000 | `CASCADE_THERMAL_MECHANICAL` | Thermal (Overheat) | Mechanical (Vibrations) |
| `02_CASCADE_MECHANICAL_FLUID_v1.csv` | 9,000 | `CASCADE_MECHANICAL_FLUID` | Mechanical (Bearing/Vib) | Fluid (Oil pressure drop) |
| `02_CASCADE_MECHANICAL_FLUID_v2.csv` | 9,000 | `CASCADE_MECHANICAL_FLUID` | Mechanical (Bearing/Vib) | Fluid (Oil pressure drop) |
| `03_CASCADE_FLUID_THERMAL_v1.csv` | 9,000 | `CASCADE_FLUID_THERMAL` | Fluid (Coolant/Oil) | Thermal (CHT elevation) |
| `03_CASCADE_FLUID_THERMAL_v2.csv` | 9,000 | `CASCADE_FLUID_THERMAL` | Fluid (Coolant/Oil) | Thermal (CHT elevation) |
| `04_SENSOR_GHOSTING_v1.csv` | 9,000 | `SENSOR_GHOSTING` | Avionics / Electrical | Erratic sensor reads |
| `04_SENSOR_GHOSTING_v2.csv` | 9,000 | `SENSOR_GHOSTING` | Avionics / Electrical | Erratic sensor reads |
| `05_TOTAL_SYSTEM_FAILURE_v1.csv` | 9,000 | `TOTAL_SYSTEM_FAILURE` | Powerplant / Electrical / Fluid | Full Catastrophic Loss |
| `05_TOTAL_SYSTEM_FAILURE_v2.csv` | 9,000 | `TOTAL_SYSTEM_FAILURE` | Powerplant / Electrical / Fluid | Full Catastrophic Loss |
| `06_SIMULTANEOUS_THERMAL_ELECTRICAL_v1.csv` | 9,000 | `SIMULTANEOUS_THERMAL_ELECTRICAL` | Thermal (Overheat) | Electrical (Bus/Alternator) |
| `06_SIMULTANEOUS_THERMAL_ELECTRICAL_v2.csv` | 9,000 | `SIMULTANEOUS_THERMAL_ELECTRICAL` | Thermal (Overheat) | Electrical (Bus/Alternator) |
| `07_SIMULTANEOUS_MECHANICAL_FLUID_v1.csv` | 9,000 | `SIMULTANEOUS_MECHANICAL_FLUID` | Mechanical (Vibrations) | Fluid (Fuel/Oil system) |
| `07_SIMULTANEOUS_MECHANICAL_FLUID_v2.csv` | 9,000 | `SIMULTANEOUS_MECHANICAL_FLUID` | Mechanical (Vibrations) | Fluid (Fuel/Oil system) |

* Total Cascade Rows: `126,000` (14 files × 9,000 rows).
* All pairs (`_v1` vs `_v2`) are non-identical flights with independent stochastic flight telemetry across 44 parameters.

---

## 2. Class Distributions & Fault-Transition Timing

Every cascade flight models a continuous 2.5-hour mission (9,000 sequential 1-second steps) starting from standard nominal conditions and transitioning to the injected compound fault:

| Injected Fault Label | Pre-Fault Rows (`NORMAL_OPERATIONS`) | Post-Fault Rows | Transition Time | Flight Phase at Transition |
|---|---|---|---|---|
| `CASCADE_THERMAL_MECHANICAL` | 3,000 (33.3%) | 6,000 (66.7%) | t = 3,000 s (50.0 min) | `CRUISE` |
| `CASCADE_MECHANICAL_FLUID` | 2,000 (22.2%) | 7,000 (77.8%) | t = 2,000 s (33.3 min) | `CRUISE` |
| `CASCADE_FLUID_THERMAL` | 4,000 (44.4%) | 5,000 (55.6%) | t = 4,000 s (66.7 min) | `CRUISE` |
| `SENSOR_GHOSTING` | 1,000 (11.1%) | 8,000 (88.9%) | t = 1,000 s (16.7 min) | `CLIMB` |
| `TOTAL_SYSTEM_FAILURE` | 500 (5.6%) | 8,500 (94.4%) | t = 500 s (8.3 min) | `TAKEOFF` |
| `SIMULTANEOUS_THERMAL_ELECTRICAL` | 4,001 (44.5%) | 4,999 (55.5%) | t = 4,001 s (66.7 min) | `CRUISE` |
| `SIMULTANEOUS_MECHANICAL_FLUID` | 4,001 (44.5%) | 4,999 (55.5%) | t = 4,001 s (66.7 min) | `CRUISE` |

* **Cumulative Cascade Samples:**
  * Active Compound Fault Samples: `89,002` rows
  * Pre-Transition `NORMAL_OPERATIONS` Samples: `36,998` rows

---

## 3. Telemetry & Anomaly-Score Dynamics

### A. Anomaly Score Transitions (Pre- vs. Post-Fault)

In the nominal pre-fault segments, all 3 Health Engine anomaly scores are uniformly `0.000`. Upon fault injection, the anomaly scores exhibit sharp, physically consistent cross-subsystem responses:

| Fault Scenario | Thermal Score ($S_T$) | Mechanical Score ($S_M$) | Electrical Score ($S_E$) | Observed Anomaly Profile |
|---|---|---|---|---|
| Nominal Baseline | 0.000 | 0.000 | 0.000 | Clear nominal baseline |
| `CASCADE_THERMAL_MECHANICAL` | **0.792** | **0.300** | 0.000 | Thermal runaway driving secondary mechanical vibration |
| `CASCADE_MECHANICAL_FLUID` | **0.268** | **0.990** | 0.000 | Severe mechanical bearing damage triggering fluid system pressure loss |
| `CASCADE_FLUID_THERMAL` | **0.396** | **0.560** | 0.000 | Fluid restriction inducing thermal climb |
| `SENSOR_GHOSTING` | 0.100 | 0.100 | **0.990** | Severe electrical/sensor reference corruption |
| `TOTAL_SYSTEM_FAILURE` | **0.990** | **0.990** | **0.990** | Universal critical trip across all 3 Health subsystems |
| `SIMULTANEOUS_THERMAL_ELECTRICAL` | **0.980** | 0.000 | **0.950** | Dual independent failures in thermal and electrical domains |
| `SIMULTANEOUS_MECHANICAL_FLUID` | **0.920** | **0.990** | 0.000 | Dual independent failures in mechanical and fluid domains |

### B. Physical Telemetry Verification

* **`TOTAL_SYSTEM_FAILURE`:** `electrical.main_bus_voltage` collapses from 28.2 V to **0.0 V**, `engine.oil_pressure` drops from 3.9 bar to **0.0 bar**, and CHT temperature rises to **250.0 °C**.
* **`CASCADE_MECHANICAL_FLUID`:** Mount vibration accelerates from 1.54 g to **9.42 g**, and oil pressure drops from 5.3 bar to **1.6 bar**.
* **`CASCADE_THERMAL_MECHANICAL`:** CHT increases from 87.8 °C to **135.8 °C**, accompanied by mount vibration elevating from 1.59 g to **3.79 g**.
* **`SENSOR_GHOSTING`:** Main bus voltage drops/oscillates from 28.2 V to **17.5 V**, with inconsistent CHT spikes to **231.4 °C** under cruise engine loads.

---

## 4. Relationship Between Cascade Classes and Base Faults

1. **Genuinely Distinct Compound Signatures:**
   * In single-fault files, only one subsystem diverges (e.g., `flight_018_critical_overheat` only triggers $S_T \approx 0.95$, with $S_M=0, S_E=0$).
   * In cascade files, multiple subsystems deviate concurrently in physical telemetry and Health anomaly scores.
2. **Classification Role:**
   * These 7 cascade labels are **genuine multi-fault/systemic operational states**, not synthetic noise or duplicate single faults.
   * If a compound failure occurs in flight, an 18-class model forced to predict a single fault would suffer from ambiguity (e.g., arbitrarily picking between `CRITICAL_OVERHEAT` and `SEVERE_VIBRATION` when both are active). A 25-class model cleanly resolves compound states.

---

## 5. Documentation Evidence

* **`docs/Diagnostic_Step1_Data_Prep.md` (Line 15):**
  > *"You will have dozens of CSV files (51+ base faults, plus all the cascading and total failure datasets you are currently generating)."*
  * **Evidence:** The documentation explicitly planned and authorized the ingestion of cascading and total failure datasets alongside base faults.
* **`docs/Diagnostic_Model_Guide.md` (Line 31):**
  > *"...covering all 18 fault types in the Sanjeevani matrix."*
* **`docs/Diagnostic_Step2_XGBoost_Training.md` (Line 31) & `docs/diagnostic_xgboost_training.md` (Line 27):**
  > *"relate to each of the 19 possible fault classes."* / `num_class=19, # 0 to 18`
  * **Context:** The initial reference to 19 classes (`num_class=19`) was drafted prior to completing the generation of the cascade and multi-fault datasets mentioned in Step 1.

---

## 6. Runtime Contract & I/O Compatibility

Review of [`docs/2_Diagnostic_IO_Mapping.md`](file:///c:/Users/Atharva/OneDrive/Desktop/Diagonstic-model/docs/2_Diagnostic_IO_Mapping.md):

```text
1. The AI Boundary (ONNX File):
   - INPUTS: 63 Nodes (53 physical + 3 anomaly scores + 7 one-hot phase flags)
   - OUTPUTS: 1 Integer representing the predicted class

2. The Runtime Boundary (Python Code):
   - Python grabs the integer from ONNX output.
   - Python uses fault_label_encoder.pkl to translate the integer into the string label.
```

* **No Hardcoded Class Limitation in Runtime:**
  * The input tensor size is strictly fixed at `63`. Both base (49 files) and cascade (14 files) datasets produce exactly **63 features** after one-hot encoding flight phase.
  * The output is a dynamic integer decoded by `fault_label_encoder.pkl`. The runtime architecture does not constrain the number of classes: `LabelEncoder` seamlessly encodes and decodes `0..18` (19 classes) or `0..24` (25 classes).

---

## 7. Comparative Assessment: 19-Class vs. 25-Class Model

| Dimension | 19-Class Model (Base Only) | 25-Class Model (Base + Cascades) |
|---|---|---|
| **Training Scope** | 49 CSV files (441,000 rows) | 63 CSV files (567,000 rows) |
| **Fault Coverage** | 18 Single faults + Nominal | 18 Single faults + 7 Compound/Cascade/Systemic faults + Nominal |
| **Input Feature Shape** | 63 Features (`[None, 63]`) | 63 Features (`[None, 63]`) |
| **ONNX Runtime Contract** | Fully Compatible | Fully Compatible |
| **Step 1 Docs Compliance** | Ignores generated cascade files | Fulfills Step 1 requirement (*"plus all cascading/total failure datasets"*) |
| **Step 2 Docs Reference** | Matches literal `num_class=19` snippet | Requires updating `num_class=25` |
| **Cascade File Preparation** | None needed | Standardize `flags` → `flight.phase` and align column order |
| **Real-World Diagnostic Capability** | Cannot classify compound/cascading failures | Disambiguates single vs compound failures |

---

## 8. Final Recommendation

**Recommendation:** Train the Diagnostic Model on **all 25 classes (63 CSV files, 567,000 rows)**.

**Rationale:**
1. **Documented Intent:** `Diagnostic_Step1_Data_Prep.md` explicitly calls for ingesting the cascade and total failure datasets.
2. **Physical Validity:** The 14 cascade files represent physically distinct multi-subsystem failure signatures with synchronized multi-anomaly score elevations ($S_T, S_M, S_E$) and telemetry collapses.
3. **Runtime Decoupling:** `2_Diagnostic_IO_Mapping.md` relies on `fault_label_encoder.pkl` for string translation, allowing seamless extension to 25 classes without altering the 63-feature ONNX I/O contract.
4. **Data Preparation Requirement:** When loading `spasht_official_cascades_58col`, the data preparation script will rename `flags` to `flight.phase` and align column ordering with the standard 58-column schema before one-hot encoding.

---

**Next Action:** Awaiting confirmation to proceed with Step 1 Data Preparation and Model Training.
