# SPASHT Diagnostic Model: Comprehensive Dataset & Documentation Audit Report

## 1. Project & Inventory Overview

- **Total CSV Files Discovered:** 63
- **Total Samples (Rows):** 567,000 (all 63 files contain exactly 9,000 rows each)
- **Missing / Null Values:** 0
- **Infinite Values:** 0
- **Duplicate Rows:** 0
- **AWS / DynamoDB Datasets / Files:** None found in workspace (`[]`)

## 2. Folder-by-Folder Breakdown

| Folder / Dataset | File Count | Total Rows | Columns | Schema Group | Unique Fault Classes | Flight Phases |
|---|---|---|---|---|---|---|
| `Thermal Anomalies` | 8 | 72,000 | 58 | Schema 1 (`flight.phase`) | 5 | 7 |
| `aerodynamics_sensor_anomalies` | 6 | 54,000 | 58 | Schema 1 (`flight.phase`) | 4 | 7 |
| `electrical_anomalies` | 6 | 54,000 | 58 | Schema 1 (`flight.phase`) | 4 | 7 |
| `fluid_fuel_anomalies` | 6 | 54,000 | 58 | Schema 1 (`flight.phase`) | 4 | 7 |
| `mechanical_anomalies` | 8 | 72,000 | 58 | Schema 1 (`flight.phase`) | 5 | 7 |
| `nominal_diagnostic_dataset` | 15 | 135,000 | 58 | Schema 1 (`flight.phase`) | 1 | 7 |
| `spasht_official_cascades_58col` | 14 | 126,000 | 58 | Schema 2 (`flags`) | 8 | 7 |

## 3. Detailed File Inventory & Flight Allocation

| File Name | Folder | Rows | Fault Classes Present | Phase Counts |
|---|---|---|---|---|
| `flight_016_minor_overheat.csv` | `Thermal Anomalies` | 9,000 | MINOR_OVERHEAT: 5386, NORMAL_OPERATIONS: 3614 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_017_minor_overheat.csv` | `Thermal Anomalies` | 9,000 | NORMAL_OPERATIONS: 4544, MINOR_OVERHEAT: 4456 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_018_critical_overheat.csv` | `Thermal Anomalies` | 9,000 | NORMAL_OPERATIONS: 4601, CRITICAL_OVERHEAT: 4399 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_019_critical_overheat.csv` | `Thermal Anomalies` | 9,000 | NORMAL_OPERATIONS: 4648, CRITICAL_OVERHEAT: 4352 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_020_coolant_leak.csv` | `Thermal Anomalies` | 9,000 | COOLANT_SYSTEM_LEAK: 5038, NORMAL_OPERATIONS: 3962 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_021_coolant_leak.csv` | `Thermal Anomalies` | 9,000 | NORMAL_OPERATIONS: 5222, COOLANT_SYSTEM_LEAK: 3778 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_022_radiator_blockage.csv` | `Thermal Anomalies` | 9,000 | NORMAL_OPERATIONS: 5229, RADIATOR_BLOCKAGE: 3771 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_023_radiator_blockage.csv` | `Thermal Anomalies` | 9,000 | RADIATOR_BLOCKAGE: 5024, NORMAL_OPERATIONS: 3976 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_044_pitot_blockage.csv` | `aerodynamics_sensor_anomalies` | 9,000 | PITOT_TUBE_BLOCKAGE: 4918, NORMAL_OPERATIONS: 4082 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_045_pitot_blockage.csv` | `aerodynamics_sensor_anomalies` | 9,000 | NORMAL_OPERATIONS: 4509, PITOT_TUBE_BLOCKAGE: 4491 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_046_elevator_binding.csv` | `aerodynamics_sensor_anomalies` | 9,000 | ELEVATOR_BINDING: 4858, NORMAL_OPERATIONS: 4142 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_047_elevator_binding.csv` | `aerodynamics_sensor_anomalies` | 9,000 | ELEVATOR_BINDING: 5295, NORMAL_OPERATIONS: 3705 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_048_oat_sensor_fail.csv` | `aerodynamics_sensor_anomalies` | 9,000 | OAT_SENSOR_FAILURE: 4718, NORMAL_OPERATIONS: 4282 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_049_oat_sensor_fail.csv` | `aerodynamics_sensor_anomalies` | 9,000 | OAT_SENSOR_FAILURE: 4820, NORMAL_OPERATIONS: 4180 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_038_alt1_failure.csv` | `electrical_anomalies` | 9,000 | NORMAL_OPERATIONS: 4832, ALTERNATOR_1_FAILURE: 4168 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_039_alt1_failure.csv` | `electrical_anomalies` | 9,000 | ALTERNATOR_1_FAILURE: 4915, NORMAL_OPERATIONS: 4085 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_040_ecu_lane_a_fail.csv` | `electrical_anomalies` | 9,000 | NORMAL_OPERATIONS: 4569, ECU_LANE_A_FAILURE: 4431 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_041_ecu_lane_a_fail.csv` | `electrical_anomalies` | 9,000 | ECU_LANE_A_FAILURE: 4504, NORMAL_OPERATIONS: 4496 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_042_main_bus_short.csv` | `electrical_anomalies` | 9,000 | NORMAL_OPERATIONS: 4668, MAIN_BUS_SHORT_CIRCUIT: 4332 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_043_main_bus_short.csv` | `electrical_anomalies` | 9,000 | NORMAL_OPERATIONS: 4546, MAIN_BUS_SHORT_CIRCUIT: 4454 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_032_fuel_pump_fail.csv` | `fluid_fuel_anomalies` | 9,000 | NORMAL_OPERATIONS: 5350, FUEL_PUMP_FAILURE: 3650 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_033_fuel_pump_fail.csv` | `fluid_fuel_anomalies` | 9,000 | NORMAL_OPERATIONS: 5234, FUEL_PUMP_FAILURE: 3766 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_034_blocked_fuel_filter.csv` | `fluid_fuel_anomalies` | 9,000 | NORMAL_OPERATIONS: 5230, BLOCKED_FUEL_FILTER: 3770 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_035_blocked_fuel_filter.csv` | `fluid_fuel_anomalies` | 9,000 | NORMAL_OPERATIONS: 4878, BLOCKED_FUEL_FILTER: 4122 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_036_oil_leak.csv` | `fluid_fuel_anomalies` | 9,000 | NORMAL_OPERATIONS: 5180, OIL_LEAK: 3820 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_037_oil_leak.csv` | `fluid_fuel_anomalies` | 9,000 | OIL_LEAK: 4847, NORMAL_OPERATIONS: 4153 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_024_minor_vib.csv` | `mechanical_anomalies` | 9,000 | MINOR_VIBRATION: 5252, NORMAL_OPERATIONS: 3748 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_025_minor_vib.csv` | `mechanical_anomalies` | 9,000 | NORMAL_OPERATIONS: 5347, MINOR_VIBRATION: 3653 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_026_severe_vib.csv` | `mechanical_anomalies` | 9,000 | SEVERE_VIBRATION: 4521, NORMAL_OPERATIONS: 4479 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_027_severe_vib.csv` | `mechanical_anomalies` | 9,000 | SEVERE_VIBRATION: 5351, NORMAL_OPERATIONS: 3649 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_028_gearbox_bearing.csv` | `mechanical_anomalies` | 9,000 | NORMAL_OPERATIONS: 4928, VIBRATION_GEARBOX_BEARING: 4072 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_029_gearbox_bearing.csv` | `mechanical_anomalies` | 9,000 | NORMAL_OPERATIONS: 5292, VIBRATION_GEARBOX_BEARING: 3708 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_030_stuck_surface.csv` | `mechanical_anomalies` | 9,000 | NORMAL_OPERATIONS: 4942, STUCK_CONTROL_SURFACE: 4058 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_031_stuck_surface.csv` | `mechanical_anomalies` | 9,000 | NORMAL_OPERATIONS: 5360, STUCK_CONTROL_SURFACE: 3640 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_001_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_002_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_003_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_004_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_005_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_006_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_007_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_008_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_009_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_010_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_011_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_012_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_013_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_014_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `flight_015_nominal.csv` | `nominal_diagnostic_dataset` | 9,000 | NORMAL_OPERATIONS: 9000 | CRUISE: 5910, CLIMB: 1200, DESCENT: 1200, WARMUP: 390, LANDING: 240, STARTUP: 30, TAKEOFF: 30 |
| `01_CASCADE_THERMAL_MECHANICAL_v1.csv` | `spasht_official_cascades_58col` | 9,000 | CASCADE_THERMAL_MECHANICAL: 6000, NORMAL_OPERATIONS: 3000 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `01_CASCADE_THERMAL_MECHANICAL_v2.csv` | `spasht_official_cascades_58col` | 9,000 | CASCADE_THERMAL_MECHANICAL: 6000, NORMAL_OPERATIONS: 3000 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `02_CASCADE_MECHANICAL_FLUID_v1.csv` | `spasht_official_cascades_58col` | 9,000 | CASCADE_MECHANICAL_FLUID: 7000, NORMAL_OPERATIONS: 2000 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `02_CASCADE_MECHANICAL_FLUID_v2.csv` | `spasht_official_cascades_58col` | 9,000 | CASCADE_MECHANICAL_FLUID: 7000, NORMAL_OPERATIONS: 2000 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `03_CASCADE_FLUID_THERMAL_v1.csv` | `spasht_official_cascades_58col` | 9,000 | CASCADE_FLUID_THERMAL: 5000, NORMAL_OPERATIONS: 4000 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `03_CASCADE_FLUID_THERMAL_v2.csv` | `spasht_official_cascades_58col` | 9,000 | CASCADE_FLUID_THERMAL: 5000, NORMAL_OPERATIONS: 4000 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `04_SENSOR_GHOSTING_v1.csv` | `spasht_official_cascades_58col` | 9,000 | SENSOR_GHOSTING: 8000, NORMAL_OPERATIONS: 1000 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `04_SENSOR_GHOSTING_v2.csv` | `spasht_official_cascades_58col` | 9,000 | SENSOR_GHOSTING: 8000, NORMAL_OPERATIONS: 1000 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `05_TOTAL_SYSTEM_FAILURE_v1.csv` | `spasht_official_cascades_58col` | 9,000 | TOTAL_SYSTEM_FAILURE: 8500, NORMAL_OPERATIONS: 500 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `05_TOTAL_SYSTEM_FAILURE_v2.csv` | `spasht_official_cascades_58col` | 9,000 | TOTAL_SYSTEM_FAILURE: 8500, NORMAL_OPERATIONS: 500 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `06_SIMULTANEOUS_THERMAL_ELECTRICAL_v1.csv` | `spasht_official_cascades_58col` | 9,000 | SIMULTANEOUS_THERMAL_ELECTRICAL: 4999, NORMAL_OPERATIONS: 4001 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `06_SIMULTANEOUS_THERMAL_ELECTRICAL_v2.csv` | `spasht_official_cascades_58col` | 9,000 | SIMULTANEOUS_THERMAL_ELECTRICAL: 4999, NORMAL_OPERATIONS: 4001 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `07_SIMULTANEOUS_MECHANICAL_FLUID_v1.csv` | `spasht_official_cascades_58col` | 9,000 | SIMULTANEOUS_MECHANICAL_FLUID: 4999, NORMAL_OPERATIONS: 4001 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |
| `07_SIMULTANEOUS_MECHANICAL_FLUID_v2.csv` | `spasht_official_cascades_58col` | 9,000 | SIMULTANEOUS_MECHANICAL_FLUID: 4999, NORMAL_OPERATIONS: 4001 | CRUISE: 6660, DESCENT: 720, CLIMB: 600, LANDING: 480, WARMUP: 300, STARTUP: 180, TAKEOFF: 60 |

## 4. Feature Architecture & Column Breakdown

### A. 53 Physical Telemetry Parameters (Documented: 53, Actual: 53)

1. `env.oat` (dtype: `float64`, min: -40.16409696307621, max: 25.615393056138625)
2. `env.wind_vector` (dtype: `float64`, min: 4.771560655456215, max: 25.40852404971291)
3. `flight.airspeed_ktas` (dtype: `float64`, min: -6.323290303212032, max: 126.48000759630442)
4. `flight.barometric_altitude` (dtype: `float64`, min: -5.453448173517627, max: 30006.300102966303)
5. `flight.elevator_angle` (dtype: `float64`, min: -4.420352545000977, max: 5.20053389008173)
6. `flight.elevator_load` (dtype: `float64`, min: -3.635698954002885, max: 319.61457198945607)
7. `flight.rudder_angle` (dtype: `float64`, min: -1.1221078285079356, max: 1.1209232004495042)
8. `flight.rudder_load` (dtype: `float64`, min: -2.451450983639605, max: 33.15787385076888)
9. `flight.aileron_angle` (dtype: `float64`, min: -1.49545182564487, max: 1.6106458726990796)
10. `flight.aileron_load` (dtype: `float64`, min: -3.0243457369351794, max: 44.93096384670399)
11. `flight.flap_position` (dtype: `float64`, min: 0.0, max: 30.0)
12. `flight.landing_gear_status` (dtype: `int64`, min: 0.0, max: 1.0)
13. `flight.weight_on_wheels` (dtype: `int64`, min: 0.0, max: 1.0)
14. `nav.gps_lat` (dtype: `float64`, min: 31.99952133177593, max: 38.16844116749477)
15. `nav.gps_lon` (dtype: `float64`, min: -122.4194, max: 34.0004680858965)
16. `nav.ground_speed` (dtype: `float64`, min: -6.955619333533235, max: 139.12800835593487)
17. `nav.heading` (dtype: `float64`, min: 265.0881830713066, max: 274.7932807051571)
18. `engine.rpm` (dtype: `float64`, min: -1038.734401312388, max: 15000.0)
19. `propeller.rpm` (dtype: `float64`, min: 0.0, max: 2393.172675930683)
20. `engine.map` (dtype: `float64`, min: 14.068225642813134, max: 51.39501986211212)
21. `engine.cht_1` (dtype: `float64`, min: -150.0, max: 250.0)
22. `engine.cht_2` (dtype: `float64`, min: 21.77019638391302, max: 900.0)
23. `engine.cht_3` (dtype: `float64`, min: 19.50280827450481, max: 250.0)
24. `engine.cht_4` (dtype: `float64`, min: 20.900755869718928, max: 250.0)
25. `engine.egt_1` (dtype: `float64`, min: 147.359911320054, max: 887.3186260044127)
26. `engine.egt_2` (dtype: `float64`, min: 147.13047789868548, max: 886.375568352715)
27. `engine.egt_3` (dtype: `float64`, min: 148.56158159334777, max: 890.707634219965)
28. `engine.egt_4` (dtype: `float64`, min: 147.27848695597183, max: 891.7350150375289)
29. `engine.oil_pressure` (dtype: `float64`, min: -0.2941868466525111, max: 6.230261605150746)
30. `engine.oil_temp` (dtype: `float64`, min: 9.990265946775178, max: 129.02444891166533)
31. `engine.coolant_pressure` (dtype: `float64`, min: -0.1343013709671435, max: 2.351877866941812)
32. `engine.coolant_temp` (dtype: `float64`, min: 17.463127548799804, max: 133.02438314786895)
33. `sensor.vibration_engine_mount_x` (dtype: `float64`, min: -1.0501179129899292, max: 16.077340086121243)
34. `sensor.vibration_engine_mount_y` (dtype: `float64`, min: -1.3521700372700098, max: 16.212290265989505)
35. `sensor.vibration_engine_mount_z` (dtype: `float64`, min: -0.5477222256906167, max: 16.099875496015354)
36. `sensor.vibration_gearbox` (dtype: `float64`, min: -0.2869083702376547, max: 35.0)
37. `sensor.magnetic_chip_detector_mcd` (dtype: `int64`, min: 0.0, max: 1.0)
38. `fuel.flow_rate` (dtype: `float64`, min: -2.234254275447741, max: 45.51599136133263)
39. `fuel.total_fuel` (dtype: `float64`, min: 65.4294900192671, max: 200.0)
40. `fuel.injector_pulse_width` (dtype: `float64`, min: -0.3170850031999768, max: 14.260243315654996)
41. `fuel.pump_primary_status` (dtype: `int64`, min: 0.0, max: 1.0)
42. `fuel.pump_secondary_status` (dtype: `int64`, min: 0.0, max: 1.0)
43. `ignition.coil_voltage` (dtype: `float64`, min: 0.0, max: 14.681484852679034)
44. `ignition.spark_misfire_flags` (dtype: `int64`, min: 0.0, max: 0.0)
45. `engine.oil_scavenge_pump_rate` (dtype: `float64`, min: 0.0, max: 4640.0)
46. `engine.water_pump_speed` (dtype: `float64`, min: 0.0, max: 5220.0)
47. `electrical.main_bus_voltage` (dtype: `float64`, min: 0.0, max: 28.896910572814797)
48. `electrical.main_bus_current` (dtype: `float64`, min: 6.545418488490144, max: 112.1369043937113)
49. `electrical.alternator_1_current` (dtype: `float64`, min: -1.3809447650851432, max: 29.88001659640005)
50. `electrical.alternator_2_current` (dtype: `float64`, min: -1.517372465995142, max: 24.17875304302716)
51. `electrical.ecu_lane_a_status` (dtype: `int64`, min: 0.0, max: 1.0)
52. `electrical.ecu_lane_b_status` (dtype: `int64`, min: 1.0, max: 1.0)
53. `electrical.sensor_reference_5v` (dtype: `float64`, min: 3.2, max: 5.047061261092431)

### B. 3 Anomaly Score Features (Documented: 3, Actual: 3)

1. `anomaly_score_thermal` (dtype: `float64`, min: 0.0, max: 0.99)
2. `anomaly_score_mechanical` (dtype: `float64`, min: 0.0, max: 0.99)
3. `anomaly_score_electrical` (dtype: `float64`, min: 0.0, max: 0.99)

### C. Flight Phase Categorical Field & One-Hot Encoding

- **Base Files Column Name:** `flight.phase`
- **Cascade Files Column Name:** `flags` (Contains same string values as `flight.phase`)
- **Unique Phase Values (7 documented vs 7 actual):**
  - `CRUISE`: 382,830 samples (67.52%)
  - `DESCENT`: 68,880 samples (12.15%)
  - `CLIMB`: 67,200 samples (11.85%)
  - `WARMUP`: 23,310 samples (4.11%)
  - `LANDING`: 18,480 samples (3.26%)
  - `STARTUP`: 3,990 samples (0.70%)
  - `TAKEOFF`: 2,310 samples (0.41%)

- **One-Hot Encoding Expansion:** 53 (Physical) + 3 (Anomaly Scores) + 7 (One-hot Phase flags) = **63 Features** (Exactly matches documented ONNX input shape).

## 5. Target / Class Distribution (Documented vs Actual)

- **Documented Target Classes:** 19 (18 specific faults + `NORMAL_OPERATIONS`)
- **Actual Unique Target Classes in Data:** 25 (18 base classes + 7 cascade/complex failure classes)

| Class # | Fault Label | Sample Count | % of Dataset | Source Folders |
|---|---|---|---|---|
| 1 | `NORMAL_OPERATIONS` | 327,666 | 57.79% | Thermal Anomalies, aerodynamics_sensor_anomalies, electrical_anomalies, fluid_fuel_anomalies, mechanical_anomalies, nominal_diagnostic_dataset, spasht_official_cascades_58col |
| 2 | `TOTAL_SYSTEM_FAILURE` | 17,000 | 3.00% | spasht_official_cascades_58col |
| 3 | `SENSOR_GHOSTING` | 16,000 | 2.82% | spasht_official_cascades_58col |
| 4 | `CASCADE_MECHANICAL_FLUID` | 14,000 | 2.47% | spasht_official_cascades_58col |
| 5 | `CASCADE_THERMAL_MECHANICAL` | 12,000 | 2.12% | spasht_official_cascades_58col |
| 6 | `ELEVATOR_BINDING` | 10,153 | 1.79% | aerodynamics_sensor_anomalies |
| 7 | `CASCADE_FLUID_THERMAL` | 10,000 | 1.76% | spasht_official_cascades_58col |
| 8 | `SIMULTANEOUS_THERMAL_ELECTRICAL` | 9,998 | 1.76% | spasht_official_cascades_58col |
| 9 | `SIMULTANEOUS_MECHANICAL_FLUID` | 9,998 | 1.76% | spasht_official_cascades_58col |
| 10 | `SEVERE_VIBRATION` | 9,872 | 1.74% | mechanical_anomalies |
| 11 | `MINOR_OVERHEAT` | 9,842 | 1.74% | Thermal Anomalies |
| 12 | `OAT_SENSOR_FAILURE` | 9,538 | 1.68% | aerodynamics_sensor_anomalies |
| 13 | `PITOT_TUBE_BLOCKAGE` | 9,409 | 1.66% | aerodynamics_sensor_anomalies |
| 14 | `ALTERNATOR_1_FAILURE` | 9,083 | 1.60% | electrical_anomalies |
| 15 | `ECU_LANE_A_FAILURE` | 8,935 | 1.58% | electrical_anomalies |
| 16 | `MINOR_VIBRATION` | 8,905 | 1.57% | mechanical_anomalies |
| 17 | `COOLANT_SYSTEM_LEAK` | 8,816 | 1.55% | Thermal Anomalies |
| 18 | `RADIATOR_BLOCKAGE` | 8,795 | 1.55% | Thermal Anomalies |
| 19 | `MAIN_BUS_SHORT_CIRCUIT` | 8,786 | 1.55% | electrical_anomalies |
| 20 | `CRITICAL_OVERHEAT` | 8,751 | 1.54% | Thermal Anomalies |
| 21 | `OIL_LEAK` | 8,667 | 1.53% | fluid_fuel_anomalies |
| 22 | `BLOCKED_FUEL_FILTER` | 7,892 | 1.39% | fluid_fuel_anomalies |
| 23 | `VIBRATION_GEARBOX_BEARING` | 7,780 | 1.37% | mechanical_anomalies |
| 24 | `STUCK_CONTROL_SURFACE` | 7,698 | 1.36% | mechanical_anomalies |
| 25 | `FUEL_PUMP_FAILURE` | 7,416 | 1.31% | fluid_fuel_anomalies |

## 6. Schema Comparison & Compatibility Audit

### Schema Group 1: Base Fault & Nominal Datasets (49 Files, 441,000 Rows)
- **Status:** Fully Compatible with documented pipeline.
- **Columns (58):** Starts with `flight.phase`, CHT block followed by EGT block, ends with 3 anomaly scores + `fault_label`.

### Schema Group 2: Cascading / Complex Anomalies (14 Files, 126,000 Rows)
- **Status:** Potentially Compatible after documented preprocessing / standardization.
- **Discrepancies identified:**
  1. Column `flags` contains the flight phase strings instead of column name `flight.phase`.
  2. Interleaved CHT/EGT order (`engine.cht_1, engine.egt_1, engine.cht_2, engine.egt_2...`) instead of grouped (`engine.cht_1..4, engine.egt_1..4`).
  3. Contains 7 additional complex cascade fault classes not present in the 18 single-fault matrix.

## 7. Temporal & Flight Transition Structure

- Each CSV represents a single continuous flight simulation of exactly **9,000 seconds (2.5 hours)** sampled at **1 Hz**.
- All 15 nominal files contain 100% `NORMAL_OPERATIONS`.
- All 48 fault/cascade files start with `NORMAL_OPERATIONS` during early phases (Startup/Warmup/Takeoff/early Climb or Cruise), and transition to the injected fault at a specific timestamp during Cruise/Descent/Landing.
- **Critical Train/Val/Test Split Consideration:** Because rows within a single flight CSV are sequential 1 Hz continuous time-series, a random row-wise train_test_split would cause massive data leakage (adjacent seconds appearing in train and test). Splits should be partitioned **flight-by-flight** (e.g. Flight v1 in train, Flight v2 in test).

## 8. Documentation vs Dataset Comparison Matrix

| Item | Documentation Specification | Actual Dataset Evidence | Status / Discrepancy |
|---|---|---|---|
| Physical Features | 53 | 53 | **MATCH** |
| Anomaly Scores | 3 | 3 | **MATCH** (`anomaly_score_thermal`, `anomaly_score_mechanical`, `anomaly_score_electrical`) |
| Flight Phase Column | `flight.phase` | `flight.phase` (49 files) / `flags` (14 files) | **DISCREPANCY** (Column naming in cascades) |
| Flight Phase Values | 7 (`STARTUP` to `LANDING`) | 7 exact matching values | **MATCH** |
| Final One-Hot Input Features | 63 | 53 + 3 + 7 = 63 | **MATCH** |
| Base Fault Files Count | 51 files (documented) | 49 base + 14 cascades = 63 files | **DISCREPANCY** (Base has 49 files; Flights 050-051 missing from base series) |
| Fault Classes Count | 19 classes (18 faults + nominal) | 25 classes (18 base + 7 cascades) | **DISCREPANCY** (18 base classes in 49 files; 25 classes if cascades included) |
| Target Column | `fault_label` | `fault_label` (all 63 files) | **MATCH** |
| Model Architecture | XGBoost (`XGBClassifier`) | Supervised multi-class | **MATCH** |
| ONNX Input Shape | `[None, 63]` | `[None, 63]` | **MATCH** |
| AWS / DynamoDB Data | Mentioned in audit scope | None present in workspace | **CONFIRMED ABSENT** |

