# AeroTwin-HUMS: Exhaustive Technical Audit

**Audit Date:** October 2026  
**Repository:** `Aerotwin-HUMS-main.zip` (106 files, ~753 KB)  
**Auditor Classification:** Senior Aerospace PHM Researcher & Software Auditor  
**Evidence Hierarchy:** Executable code → Raw data → Metadata → Documentation → Presentation claims

---

## 1. Executive Summary

AeroTwin-HUMS is a physics-informed digital twin framework for UAV piston engine health monitoring. The delivered repository implements a vendored Python physics package (`aerotwin_physics`), a FastAPI backend integration layer, and a React 18 frontend dashboard. The physics engine is functional and passes all executable validation checks (6/6). The ML model artifacts are Git LFS pointer stubs and cannot be deserialized in the test environment. All performance claims require qualification against the evidence hierarchy.

### Critical Findings

| Finding | Severity | Impact |
|---------|----------|--------|
| `.joblib` model files are Git LFS pointers (133 bytes), not binary models | **HIGH** | Model 4 and Model 5 cannot execute inference; system falls back to heuristic paths |
| Model 5 original metadata reports R²=0.9998 with target leakage | **HIGH** | Documented and corrected in `final_config.json`; clean R²=0.760 |
| Model 4 `_build_feature_row()` generates 106 of 184 expected features | **HIGH** | 78 features zero-padded; inference quality degraded even if model loads |
| CAN and MQTT adapters are unwired stubs | **MEDIUM** | WebSocket is the only active ingestion path |
| Redis integration is completely unused | **LOW** | Alert deduplication is process-local only |
| `sensor_4` and `sensor_11` have no confirmed physical identity | **MEDIUM** | Down-weighted to 0.5 in diagnostic calculations |

---

## 2. Repository Structure

```
Aerotwin-HUMS-main/
├── integrated/
│   ├── INTEGRATION.md
│   ├── backend/
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   ├── app/
│   │   │   ├── main.py                    # FastAPI application entry
│   │   │   ├── core/config.py             # Environment settings
│   │   │   ├── core/audit.py              # HTTP audit middleware
│   │   │   ├── api/routes_predictions.py  # POST /api/v1/predict
│   │   │   ├── api/routes_ingestion.py    # POST /api/v1/ingest
│   │   │   ├── api/routes_ws.py           # WS /ws/ingest, /ws/telemetry
│   │   │   ├── models_serving/
│   │   │   │   ├── aerotwin_adapter.py    # Real physics twin adapter
│   │   │   │   ├── physics_models.py      # Heuristic stub
│   │   │   │   ├── ml_models.py           # Mock ML fallbacks
│   │   │   │   └── registry.py            # Model registry
│   │   │   ├── orchestration/
│   │   │   │   ├── router.py              # Rule-based model routing
│   │   │   │   └── rules.py               # Routing rule definitions
│   │   │   ├── realtime/
│   │   │   │   ├── bridge.py              # A/B → 4-cylinder mapping
│   │   │   │   └── connection_manager.py  # WS connection pool
│   │   │   ├── mission/
│   │   │   │   ├── manager.py             # Mission risk scoring
│   │   │   │   └── drone_registry.py      # Airframe topology
│   │   │   ├── alerting/service.py        # Alert dedup & severity
│   │   │   └── db/
│   │   │       ├── schema.sql             # TimescaleDB DDL
│   │   │       └── models.py              # SQLAlchemy ORM
│   │   ├── config/
│   │   │   ├── drone_configs.yaml         # 3 airframes, 4 engines
│   │   │   ├── model_routing.yaml         # 5 routing rules
│   │   │   └── roles.yaml                 # RBAC definitions
│   │   ├── docker/
│   │   │   ├── docker-compose.yml         # 4-container stack
│   │   │   ├── Dockerfile                 # Python 3.12-slim
│   │   │   └── mosquitto.conf
│   │   └── vendor/aerotwin_physics/       # Core physics package
│   │       ├── __init__.py                # v1.0.0, public API
│   │       ├── config.py                  # All configuration dataclasses
│   │       ├── calibration.py             # calibration.json loader
│   │       ├── atmosphere.py              # ISA model
│   │       ├── sensors.py                 # 13-channel response model
│   │       ├── simulator.py               # Trajectory sim + RealTimeMonitor
│   │       ├── mission.py                 # Mission profile generator
│   │       ├── faults.py                  # Fault injection engine
│   │       ├── noise.py                   # AR(1) noise model
│   │       ├── residuals.py               # Mahalanobis anomaly detector
│   │       ├── diagnostics.py             # Cosine-similarity fault isolation
│   │       ├── degradation.py             # Wiener process + Model 4
│   │       ├── prognostics.py             # Wiener RUL + Model 5
│   │       ├── validation.py              # 4-family validation harness
│   │       ├── service.py                 # Session management
│   │       ├── logging_utils.py           # Logging utilities
│   │       ├── exceptions.py              # Exception hierarchy
│   │       └── data/
│   │           ├── calibration.json       # 598 lines, master calibration
│   │           ├── model4/
│   │           │   ├── model4_feature_list.json         # 184 features
│   │           │   ├── model4_healthy_baseline.json     # Channel means/stds
│   │           │   └── model4_health_extratrees.joblib  # LFS pointer (34.6 MB)
│   │           └── model5/
│   │               ├── model5_feature_list.json         # 53 features (LEAKY)
│   │               ├── model5_feature_list_clean.json   # 51 features
│   │               ├── model5_feature_list_final.json   # 51 features
│   │               ├── model5_metadata.json             # Leaky metrics
│   │               ├── model5_final_config.json         # Clean metrics
│   │               ├── model5_clean_oof_predictions.csv # 1100 OOF rows
│   │               ├── model5_rul_final.joblib           # LFS pointer
│   │               └── model5_rul_final_clean.joblib     # LFS pointer (137.3 MB)
│   └── frontend/
│       ├── package.json
│       ├── package-lock.json
│       ├── index.html
│       ├── main.jsx
│       ├── vite.config.js
│       ├── aerotwin-hums-dashboard.jsx    # 3366 lines, 135 KB
│       ├── .env.example
│       ├── src/
│       │   ├── config.js
│       │   └── auth/
│       │       ├── AuthContext.jsx
│       │       ├── LoginPage.jsx
│       │       ├── permissions.js
│       │       └── ProtectedRoute.jsx
│       └── server/                        # Legacy Express auth (INACTIVE)
│           ├── package.json
│           ├── index.js
│           ├── seed.js
│           ├── middleware/auth.js
│           └── routes/
```

---

## 3. Technology Stack (Audited Pinned Versions)

### Backend (`requirements.txt`)
| Package | Version | Role |
|---------|---------|------|
| `fastapi` | 0.115.0 | Async web framework |
| `uvicorn[standard]` | 0.30.6 | ASGI server |
| `pydantic` | 2.9.2 | Request/response validation |
| `pydantic-settings` | 2.5.2 | Environment configuration |
| `SQLAlchemy` | 2.0.35 | ORM / database abstraction |
| `asyncpg` | 0.29.0 | Async PostgreSQL driver |
| `psycopg[binary]` | 3.2.2 | Sync PostgreSQL driver |
| `alembic` | 1.13.2 | Database migration |
| `python-jose[cryptography]` | 3.3.0 | JWT token signing |
| `passlib[bcrypt]` | 1.7.4 | Password hashing |
| `bcrypt` | 3.2.2 | Bcrypt implementation |
| `paho-mqtt` | 2.1.0 | MQTT client (**UNWIRED**) |
| `cantools` | 39.4.5 | CAN DBC parsing (**UNWIRED**) |
| `python-can` | 4.4.2 | CAN bus interface (**UNWIRED**) |
| `numpy` | 1.26.4 | Numerical computation |
| `scikit-learn` | 1.5.2 | ML models (ExtraTrees, RF) |
| `scipy` | 1.13.1 | Statistical distributions |
| `joblib` | 1.4.2 | Model serialization |
| `PyYAML` | 6.0.2 | Configuration parsing |
| `orjson` | 3.10.7 | Fast JSON serialization |
| `redis` | 5.0.8 | Redis client (**COMPLETELY UNUSED**) |
| `httpx` | 0.27.2 | HTTP client |
| `websockets` | 13.1 | WebSocket client (dev simulator) |
| `zstandard` | 0.23.0 | Compression codec |
| `tenacity` | 8.5.0 | Retry logic |

### Frontend (`package-lock.json` resolved)
| Package | Version |
|---------|---------|
| `react` | 18.3.1 |
| `react-dom` | 18.3.1 |
| `react-router-dom` | 7.18.3 |
| `recharts` | 2.15.4 |
| `three` | 0.160.1 |
| `vite` | 5.4.21 |
| `@vitejs/plugin-react` | 4.3.4 |

---

## 4. Physics Package: Complete Parameter Inventory

### 4.1 Channel Registry

| Index | Channel Name | Unit | Physical Identity | Status |
|-------|-------------|------|-------------------|--------|
| 0 | `egt_a` | None (uncalibrated) | Exhaust Gas Temperature Bank A | Confirmed |
| 1 | `egt_b` | None (uncalibrated) | Exhaust Gas Temperature Bank B | Confirmed |
| 2 | `oil_pressure` | `psi-plausible` | Oil Pressure | Confirmed |
| 3 | `sensor_4` | None | **UNKNOWN** | Unresolved |
| 4 | `rpm` | `rev/min` | Crankshaft Speed | Confirmed |
| 5 | `map_kpa` | `kPa` | Manifold Absolute Pressure | Confirmed |
| 6 | `fuel_flow` | None (uncalibrated) | Fuel Flow | Confirmed |
| 7 | `vibration` | None (uncalibrated) | Crankcase Vibration | Confirmed |
| 8 | `turbine_inlet_temp_a` | None (uncalibrated) | Turbine Inlet Temperature Bank A | Confirmed |
| 9 | `turbine_inlet_temp_b` | None (uncalibrated) | Turbine Inlet Temperature Bank B | Confirmed |
| 10 | `sensor_11` | None | **UNKNOWN** | Unresolved |
| 11 | `cht_a` | None (uncalibrated) | Cylinder Head Temperature Bank A | Confirmed |
| 12 | `cht_b` | None (uncalibrated) | Cylinder Head Temperature Bank B | Confirmed |

### 4.2 Atmospheric Model (ISA)

```
T(h, ΔT_ISA) = 15.0 - 0.0065·h + ΔT_ISA                    [°C]
p(h) = 101325 · max(1 - 2.25577e-5·h, 1e-6)^5.25588         [Pa]
ρ(p, T) = p / (287.05 · (T + 273.15))                        [kg/m³]
```

### 4.3 Sensor Response Equations (11 Closed-Form)

```
P_req = 300.0 · engine_load                                   [power units]
mixture_setting = 1.0 - 4.0e-5 · altitude                     [dimensionless]

EGT_A = 420.0 + 300.0 · throttle + 0.003 · altitude
EGT_B = 410.0 + 290.0 · throttle + 0.003 · altitude
Oil_P = 60.0 + P_req/15.0 - 0.0009 · altitude
S_4   = 180.0 + 0.004 · altitude + 0.15 · P_req
RPM   = 2000.0 + 550.0 · throttle
MAP   = (p_ambient/1000) · (0.30 + 0.72 · throttle)
FF    = 5.0 + (55/3) · fuel_flow_command
Vib   = 0.4 + 1.6 · engine_load²
S_11  = 150.0 + (17/60) · P_req
CHT_A = 300.0 + 0.5 · P_req - 0.01 · airspeed
CHT_B = 295.0 + (29/60) · P_req - 0.009 · airspeed
```

### 4.4 TIT Quadratic Response Surface (2 Channels)

```
TIT_k = β₀ + Σᵢ βᵢxᵢ + Σᵢ Σⱼ≥ᵢ βᵢⱼxᵢxⱼ    (9 features, 45 terms per channel)
```

**Features:** throttle_position, propeller_pitch, mixture_setting, wastegate_position, boost_command, altitude, airspeed, engine_load, fuel_flow_command

**Intercepts:**
- TIT_A: β₀ = −161.63537
- TIT_B: β₀ = −151.11934

**Documented accuracy:** R² = 0.999991, residual σ = 0.217 (TIT_A), 0.212 (TIT_B)

### 4.5 Noise Model (Per-Channel)

| Channel | σ_rel | σ_abs | AR(1) φ | Reference Scale |
|---------|-------|-------|---------|-----------------|
| egt_a | 0.012785 | 7.7645 | 0.585 | 607.297 |
| egt_b | 0.008817 | 5.2132 | 0.000 | 591.288 |
| oil_pressure | 0.009683 | 0.6651 | 0.000 | 68.690 |
| sensor_4 | 0.010925 | 2.3347 | 0.000 | 213.700 |
| rpm | 0.012122 | 28.2506 | 0.000 | 2330.462 |
| map_kpa | 0.008251 | 0.4622 | 0.4946 | 56.015 |
| fuel_flow | 0.000922 | 0.3104 | 0.2373 | 336.659 |
| vibration | 0.016929 | 0.0152 | 0.000 | 0.898 |
| turbine_inlet_temp_a | 0.011451 | 10.4177 | 0.000 | 909.794 |
| turbine_inlet_temp_b | 0.011010 | 9.8515 | 0.000 | 894.799 |
| sensor_11 | 0.018800 | 3.6831 | 0.000 | 195.914 |
| cht_a | 0.012839 | 4.8732 | 0.000 | 379.549 |
| cht_b | 0.011370 | 4.2296 | 0.000 | 371.996 |

**Noise equation:**
```
σ_c(y) = σ_rel,c · max(|y|, 0.25 · |y_ref,c|)
ε_k,c = φ_c · ε_{k-1,c} + η_k,c,   η ~ N(0, σ² · max(1 - φ², 1e-12))
```

### 4.6 Fault Signature Gains Matrix (Unit Severity)

| Channel | cooling_restriction | misfire | oil_starvation | ring_wear | wastegate_leak | Wear Gain |
|---------|-------------------|---------|----------------|-----------|----------------|-----------|
| egt_a | +0.00718 | +0.12454 | +0.00640 | +0.16852 | +0.00679 | +0.03809 |
| egt_b | +0.00441 | −0.08337 | −0.00238 | +0.16759 | +0.00263 | +0.02283 |
| oil_pressure | −0.00031 | +0.01154 | −0.27482 | −0.10490 | +0.00232 | −0.05509 |
| sensor_4 | +0.16542 | +0.00770 | +0.22173 | −0.00184 | +0.00663 | +0.08131 |
| rpm | +0.00008 | +0.25862 | +0.00399 | −0.00867 | +0.01375 | −0.02675 |
| map_kpa | −0.00154 | +0.00127 | −0.00240 | −0.00281 | −0.13655 | +0.03971 |
| fuel_flow | −0.00037 | +0.00049 | −0.00001 | +0.00059 | +0.00023 | +0.00922 |
| vibration | +0.04769 | +0.60820 | +0.25027 | +0.50955 | +0.01977 | +0.15652 |
| turbine_inlet_temp_a | −0.01046 | +0.00904 | +0.00714 | +0.00072 | +0.22742 | +0.06973 |
| turbine_inlet_temp_b | −0.00323 | +0.00289 | +0.00373 | −0.00584 | +0.22503 | +0.05690 |
| sensor_11 | +0.01243 | −0.00205 | +0.00790 | +0.00372 | −0.00749 | +0.14851 |
| cht_a | +0.29771 | +0.00378 | +0.00813 | +0.00868 | +0.00395 | +0.05323 |
| cht_b | +0.24355 | +0.01293 | +0.01658 | +0.00293 | +0.00948 | +0.04023 |

**Fault injection model:**
```
δ_c = g_fault,c · severity + g_wear,c · degradation
y_faulted,c = y_nominal,c · (1 + δ_c)
```

### 4.7 Degradation Regime Parameters

| Regime | Drift μ (s⁻¹) | Volatility σ (s⁻¹/²) | Initial x₀ |
|--------|-------------|---------------------|------------|
| healthy | 0.0 (clamped from −1.13e-7) | 7.17e-7 | 0.00415 |
| degradation | 7.08e-5 | 9.28e-6 | 0.00050 |
| fault | 5.27e-8 | 7.59e-7 | 0.03490 |
| rul | 2.51e-4 | 2.51e-7 | 0.00021 |

### 4.8 Residual Reference Statistics

**Mean vector (13 channels):**
```
[+0.3912, −0.0643, +0.0022, +0.0192, +0.3614, +0.0019, +0.0013,
 +0.0000, +0.2289, +0.0773, +0.0162, +0.0384, +0.0164]
```

**Covariance diagonal (variance per channel):**
```
egt_a: 78.24, egt_b: 28.25, oil_pressure: 0.47, sensor_4: 5.84,
rpm: 816.54, map_kpa: 0.24, fuel_flow: 0.10, vibration: 0.000236,
tit_a: 111.05, tit_b: 100.06, sensor_11: 14.12, cht_a: 24.44, cht_b: 18.52
```

**Mahalanobis scale:** γ = 0.7659664168184794  
**Degrees of freedom:** 13

### 4.9 Dataset Target Benchmarks

| Metric | Reference Value |
|--------|----------------|
| Anomaly threshold | 0.70 |
| Anomaly flag rate | 26.636% |
| Edge trigger rate | 29.364% |
| Diagnosis overall accuracy (LOO) | 84.545% |
| Per-fault: cooling_restriction | 43.90% |
| Per-fault: misfire | 13.33% |
| Per-fault: oil_starvation | 35.29% |
| Per-fault: ring_wear | 61.76% |
| Per-fault: wastegate_leak | 25.53% |
| Health index MAE vs. true | 0.045388 |
| Residual norm median | 33.09 |

### 4.10 Operating Envelope Bounds

| Variable | Minimum | Maximum | Derived From |
|----------|---------|---------|--------------|
| Altitude (m) | 0.0 | 4438.0 | 22 reference trajectories |
| Airspeed (m/s) | 68.4 | 209.7 | 22 reference trajectories |
| Throttle | 0.226 | 0.919 | 22 reference trajectories |
| Engine load | 0.184 | 0.831 | 22 reference trajectories |
| Propeller pitch (°) | 20.37 | 38.87 | 22 reference trajectories |
| Fuel-flow command | 8.33 | 25.92 | 22 reference trajectories |
| Wastegate position | 0.305 | 0.888 | 22 reference trajectories |
| Boost command | 0.294 | 0.908 | 22 reference trajectories |

**Margin:** 10% expansion on each bound  
**Policy:** `clip` (default), `raise`, or `allow`

### 4.11 Configuration Constants

| Parameter | Value | Source |
|-----------|-------|--------|
| Sample interval | 60 s | `SimulationConfig` |
| Samples per trajectory | 50 | `SimulationConfig` |
| Random seed | 42 | `SimulationConfig` |
| Mission types | cargo, patrol, training, test_flight | `SimulationConfig` |
| Mission phases | climb, cruise, loiter, descent | `SimulationConfig` |
| Max concurrent sessions | 64 | `TwinService` |
| Session TTL | 21600 s (6 h) | `TwinService` |
| Edge trigger quantile | 0.60 | `RealTimeMonitor` |
| Sensor rate-check threshold | 0.30 (30%) | `SensorValidator` |
| Softmax temperature | 0.15 | `DiagnosticsConfig` |
| Min cosine similarity | 0.30 | `DiagnosticsConfig` |
| Unknown channel weight | 0.5 | `DiagnosticsConfig` |
| Kalman process noise Q | 1e-10 | `PrognosticsConfig` |
| Kalman measurement noise R | 1e-6 | `PrognosticsConfig` |
| Model 5 min samples | 5 | `MLRULPredictor` |
| Model 5 provisional count | 10 | `MLRULPredictor` |
| Model 5 cycle seconds | 60.0 | `MLRULPredictor` |
| Model 5 ±band | 15% | `MLRULPredictor` (NOT a confidence interval) |

---

## 5. Backend Integration Audit

### 5.1 API Endpoints

| Method/Path | Permission | Status |
|-------------|-----------|--------|
| `GET /health` | Public | Active |
| `POST /api/v1/auth/login` | Public | Active |
| `POST /api/v1/auth/refresh` | Public | Active |
| `GET /api/v1/auth/me` | Authenticated | Active |
| `POST /api/v1/predict` | `predictions:write` | Active |
| `POST /api/v1/ingest` | `ingestion:write` | Storage only, no inference |
| `WS /ws/ingest` | `ingestion:write` | **Primary live path** |
| `WS /ws/telemetry` | `predictions:read` | Dashboard feed |
| `GET /api/v1/alerts` | `alerts:read` | Active |
| `POST /api/v1/missions` | `missions:write` | Active |
| `POST /api/v1/missions/{id}/close` | `missions:write` | Active |

### 5.2 Model Routing Rules (5 rules)

1. `aerotwin_full_telemetry`: 13 AeroTwin channels → `aerotwin_physics_v1` (real physics)
2. `generic_sensors_high_risk`: 3 generic sensors → heuristic stubs
3. `generic_sensors_normal_risk`: 3 generic sensors → mock ML
4. `vibration_only_any_drone_type`: vibration only → heuristic stub
5. `minimal_data_fallback`: catch-all → mock anomaly score

### 5.3 Airframe Registry

| Drone ID | Type | Engines | CAN Base |
|----------|------|---------|----------|
| drone-01 | dual_engine | drone-01-eng1 (left), drone-01-eng2 (right) | 0x100, 0x110 |
| drone-02 | single_engine | drone-02-eng1 | 0x200 |
| drone-03 | single_engine | drone-03-eng1 | 0x300 |

### 5.4 Dashboard Bridge: A/B → 4-Cylinder Mapping

```
cht_a → c1, c2    egt_a → c1, c2
cht_b → c3, c4    egt_b → c3, c4
```

Unmodeled display channels filled with defaults: `batteryV = 12.6 V`, `injectorTimingDeg = 12.0°`

---

## 6. Frontend Audit

### 6.1 Data Source Classification

| Element | Live Backend | Mock/Local |
|---------|-------------|-----------|
| Sensor telemetry | WS `type: telemetry` | `makeSnapshot()` on 800ms interval |
| Health index | WS `type: health_index` | Scripted demo sequence |
| Anomaly detection | WS `type: anomaly` | Hardcoded at t=2000ms |
| Fault diagnosis | WS `type: diagnosis` | Hardcoded: "Misfire", Cyl 3, 94% |
| RUL estimation | WS `type: rul` | Stepped: 4.1h → 2.3h |
| Mission risk | WS `type: mission_risk` | Hardcoded at t=9200ms |
| Mission replay | N/A | 100% hardcoded (5 demo sorties) |
| Risk assessment | N/A | 100% local slider simulation |
| Predictive Mx | N/A | 100% static data |
| Mission clock/altitude | N/A | Always locally generated |

### 6.2 3D Engine Visualization

Procedural Three.js geometry (no external 3D assets):
- Crankcase: Box (4.3 × 1.0 × 1.6)
- 4 in-line cylinders with cooling fins
- Injector rail, exhaust manifold
- Cinematic camera tween on fault diagnosis
- Emissive fault pulsing: `intensity = severity · (0.35 + 0.45 · sin(t · 0.0022))`

---

## 7. Database Schema

7 TimescaleDB hypertables: `sensor_readings`, `residuals`, `health_index`, `anomalies`, `fault_diagnoses`, `rul_predictions`, `audit_log`

`sensor_readings` partitioned by time (1 day) and engine_id (8 space partitions). Compression after 7 days. Retention at 365 days. Audit log retention at 2555 days (7-year aerospace compliance).

---

## 8. Model 5 OOF Dataset Structure

**File:** `model5_clean_oof_predictions.csv`  
**Rows:** 1,100 (22 missions × 50 samples)  
**Columns:** mission_id, scenario_id, rul_target_cycles, rul_prediction_oof, absolute_error

| Regime | Missions | Scenario IDs | Rows |
|--------|----------|-------------|------|
| HEALTHY | MSN-2001 – MSN-2006 | HEALTHY-001 – 006 | 300 |
| FAULT | MSN-2007 – MSN-2011 | FAULT-007 – 011 | 250 |
| DEGRADATION | MSN-2012 – MSN-2016 | DEGRADATION-012 – 016 | 250 |
| RUL | MSN-2017 – MSN-2022 | RUL-017 – 022 | 300 |

**Target range:** [0.0, 6078.3] cycles  
**Prediction range:** [15.18, 5921.62] cycles  
**Error range:** [0.52, 4581.40] cycles
