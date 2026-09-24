import os
import glob
import json
import pandas as pd
import numpy as np

# Canonical 53 Physical Telemetry Parameters
CANONICAL_PHYSICAL_PARAMS = [
    "env.oat",
    "env.wind_vector",
    "flight.airspeed_ktas",
    "flight.barometric_altitude",
    "flight.elevator_angle",
    "flight.elevator_load",
    "flight.rudder_angle",
    "flight.rudder_load",
    "flight.aileron_angle",
    "flight.aileron_load",
    "flight.flap_position",
    "flight.landing_gear_status",
    "flight.weight_on_wheels",
    "nav.gps_lat",
    "nav.gps_lon",
    "nav.ground_speed",
    "nav.heading",
    "engine.rpm",
    "propeller.rpm",
    "engine.map",
    "engine.cht_1",
    "engine.cht_2",
    "engine.cht_3",
    "engine.cht_4",
    "engine.egt_1",
    "engine.egt_2",
    "engine.egt_3",
    "engine.egt_4",
    "engine.oil_pressure",
    "engine.oil_temp",
    "engine.coolant_pressure",
    "engine.coolant_temp",
    "sensor.vibration_engine_mount_x",
    "sensor.vibration_engine_mount_y",
    "sensor.vibration_engine_mount_z",
    "sensor.vibration_gearbox",
    "sensor.magnetic_chip_detector_mcd",
    "fuel.flow_rate",
    "fuel.total_fuel",
    "fuel.injector_pulse_width",
    "fuel.pump_primary_status",
    "fuel.pump_secondary_status",
    "ignition.coil_voltage",
    "ignition.spark_misfire_flags",
    "engine.oil_scavenge_pump_rate",
    "engine.water_pump_speed",
    "electrical.main_bus_voltage",
    "electrical.main_bus_current",
    "electrical.alternator_1_current",
    "electrical.alternator_2_current",
    "electrical.ecu_lane_a_status",
    "electrical.ecu_lane_b_status",
    "electrical.sensor_reference_5v"
]

ANOMALY_SCORE_PARAMS = [
    "anomaly_score_thermal",
    "anomaly_score_mechanical",
    "anomaly_score_electrical"
]

FLIGHT_PHASES = [
    "STARTUP",
    "WARMUP",
    "TAKEOFF",
    "CLIMB",
    "CRUISE",
    "DESCENT",
    "LANDING"
]

# The exact 63 feature names in canonical order
ONE_HOT_PHASE_PARAMS = [f"flight.phase_{p}" for p in FLIGHT_PHASES]
CANONICAL_63_FEATURES = CANONICAL_PHYSICAL_PARAMS + ANOMALY_SCORE_PARAMS + ONE_HOT_PHASE_PARAMS

assert len(CANONICAL_PHYSICAL_PARAMS) == 53
assert len(ANOMALY_SCORE_PARAMS) == 3
assert len(FLIGHT_PHASES) == 7
assert len(CANONICAL_63_FEATURES) == 63


def load_and_preprocess_dataset(dataset_root=None):
    """
    Recursively loads all 63 CSVs, standardizes schemas,
    generates canonical 63-feature matrix and extracts target labels.
    """
    if dataset_root is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        dataset_root = os.path.join(base_dir, "data", "diagnostic_dataset")
        
    csv_files = sorted(glob.glob(os.path.join(dataset_root, "**", "*.csv"), recursive=True))
    if len(csv_files) != 63:
        raise ValueError(f"Expected exactly 63 CSV files, found {len(csv_files)}")
        
    dfs = []
    flight_manifest = []
    
    for file_path in csv_files:
        fname = os.path.basename(file_path)
        folder = os.path.basename(os.path.dirname(file_path))
        raw_df = pd.read_csv(file_path)
        
        # Standardize column names
        if "flags" in raw_df.columns:
            raw_df = raw_df.rename(columns={"flags": "flight.phase"})
            
        # Verify mandatory columns
        if "flight.phase" not in raw_df.columns:
            raise KeyError(f"Missing 'flight.phase' in {fname}")
        if "fault_label" not in raw_df.columns:
            raise KeyError(f"Missing 'fault_label' in {fname}")
            
        for param in CANONICAL_PHYSICAL_PARAMS + ANOMALY_SCORE_PARAMS:
            if param not in raw_df.columns:
                raise KeyError(f"Missing feature '{param}' in {fname}")
                
        # Reorder to canonical 53 + 3 + 1 + 1 columns
        ordered_df = raw_df[CANONICAL_PHYSICAL_PARAMS + ANOMALY_SCORE_PARAMS + ["flight.phase", "fault_label"]].copy()
        
        # Flight ID identifier for splitting
        ordered_df["flight_file"] = fname
        ordered_df["flight_folder"] = folder
        
        dfs.append(ordered_df)
        flight_manifest.append({
            "file": fname,
            "folder": folder,
            "rows": len(ordered_df),
            "unique_faults": ordered_df["fault_label"].unique().tolist()
        })
        
    full_df = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(csv_files)} files, Total Rows: {len(full_df):,}")
    
    # Target strings
    y_raw = full_df["fault_label"].copy()
    
    # Metadata for flight splitting
    flight_files = full_df["flight_file"].copy()
    
    # One-hot encode flight.phase strictly with 7 categorical levels
    full_df["flight.phase"] = pd.Categorical(full_df["flight.phase"], categories=FLIGHT_PHASES)
    phase_dummies = pd.get_dummies(full_df["flight.phase"], prefix="flight.phase", dtype=float)
    
    # Verify exact one-hot column names
    for col in ONE_HOT_PHASE_PARAMS:
        if col not in phase_dummies.columns:
            phase_dummies[col] = 0.0
    phase_dummies = phase_dummies[ONE_HOT_PHASE_PARAMS]
    
    # Construct final 63-feature matrix X
    X_physical = full_df[CANONICAL_PHYSICAL_PARAMS].astype(np.float32)
    X_anomaly = full_df[ANOMALY_SCORE_PARAMS].astype(np.float32)
    X_phase = phase_dummies.astype(np.float32)
    
    X = pd.concat([X_physical, X_anomaly, X_phase], axis=1)
    
    # Verify final column names and ordering
    if list(X.columns) != CANONICAL_63_FEATURES:
        raise ValueError("X columns do not match CANONICAL_63_FEATURES exactly!")
        
    return X, y_raw, flight_files, full_df


def create_flight_level_split(flight_files, full_df):
    """
    Splits dataset at the flight file level so no flight is shared between train and test.
    Returns boolean masks: train_mask, test_mask.
    """
    unique_files = sorted(flight_files.unique())
    train_files = []
    test_files = []
    
    # Group nominal files (15 files: 12 train, 3 test)
    nominal_files = [f for f in unique_files if "nominal" in f]
    train_files.extend(nominal_files[:12])
    test_files.extend(nominal_files[12:])
    
    # Group base fault files (17 pairs: flight_0XX -> train, flight_0XY -> test)
    base_fault_files = [f for f in unique_files if f.startswith("flight_") and "nominal" not in f]
    # Group by base prefix / fault type
    # File naming: flight_016_minor_overheat.csv, flight_017_minor_overheat.csv
    # Each fault has 2 files consecutively numbered
    base_fault_files.sort()
    for i in range(0, len(base_fault_files), 2):
        pair = base_fault_files[i:i+2]
        if len(pair) == 2:
            train_files.append(pair[0])
            test_files.append(pair[1])
        else:
            train_files.append(pair[0])
            
    # Group cascade files (7 pairs: _v1 -> train, _v2 -> test)
    cascade_files = [f for f in unique_files if not f.startswith("flight_")]
    cascade_files.sort()
    for f in cascade_files:
        if "_v1" in f:
            train_files.append(f)
        elif "_v2" in f:
            test_files.append(f)
        else:
            train_files.append(f)
            
    train_mask = flight_files.isin(train_files)
    test_mask = flight_files.isin(test_files)
    
    print(f"\nFlight-Level Split Summary:")
    print(f"  Total Flights: {len(unique_files)}")
    print(f"  Train Flights: {len(train_files)} ({train_mask.sum():,} rows, {train_mask.mean()*100:.2f}%)")
    print(f"  Test Flights:  {len(test_files)} ({test_mask.sum():,} rows, {test_mask.mean()*100:.2f}%)")
    
    return train_mask, test_mask, train_files, test_files


if __name__ == "__main__":
    X, y, flight_files, df = load_and_preprocess_dataset()
    print("X shape:", X.shape)
    print("y unique classes:", len(y.unique()))
    train_mask, test_mask, tr_f, te_f = create_flight_level_split(flight_files, df)
