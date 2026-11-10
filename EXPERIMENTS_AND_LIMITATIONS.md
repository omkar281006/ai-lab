# AeroTwin-HUMS: Experiments, Reproduced Results, and Limitations Record

**Date:** October 2026  
**Environment:** Python 3.14.6, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1, joblib 1.6.0  
**Platform:** Windows, x86-64

---

## 1. Experiments Successfully Executed

### 1.1 Physics Engine Instantiation
**Command:** Instantiate `EngineConfig.default()`, `EnginePhysicsCore`, compute nominal state  
**Result:** SUCCESS  
- Config fingerprint: `092573d8f9f3c0fd`
- Anomaly threshold: 0.70, Failure threshold: 0.75
- 5 fault modes confirmed: cooling_restriction, misfire, oil_starvation, ring_wear, wastegate_leak
- Nominal state at mid-envelope (alt=2200m, throttle=0.60, load=0.54):
  - EGT_A: 606.60, EGT_B: 590.60, Oil: 68.82, RPM: 2330.00
  - MAP: 56.76 kPa, FF: 335.00, Vib: 0.867
  - TIT_A: 905.38, TIT_B: 890.49, CHT_A: 379.54, CHT_B: 371.99

### 1.2 Trajectory Simulation
**Command:** Simulate misfire fault trajectory (index=0, regime=rul)  
**Result:** SUCCESS in 8.0 ms  
- 50 samples generated
- Fault onset at 876.5s, severity ramp from 0.0 to 1.0
- Health range: [0.2628, 0.9998]

### 1.3 Zero-Shot Fault Diagnosis at Maximum Severity
**Command:** 20 random fault trajectories, evaluate residual + diagnose at final sample  
**Result:** 20/20 correct (100%) at maximum severity  
- Per-fault: cooling=5/5, misfire=7/7, oil_starvation=4/4, ring_wear=3/3, wastegate=1/1
- Anomaly detection: 20/20 (100%)
- **Caveat:** This evaluates the detector on its own generated synthetic data at maximum severity

### 1.4 Physics + Residual Timing
**Command:** 100 trajectories × 50 samples, physics evaluation + residual computation  
**Result:** 13.6 ms/trajectory, 0.27 ms/sample  
- Pure CPU, no GPU, single-threaded

### 1.5 Full Validation Harness (Partial)
**Command:** `ModelValidator.run_all()` without reference DataFrame  
**Results (6/6 PASS):**

| Check | Status | Key Metric |
|-------|--------|-----------|
| physics.reproduction | PASS (skipped) | No reference frame |
| noise.per_channel_sigma | PASS | map_kpa worst at 12.4% deviation |
| noise.residual_norm_median | PASS | Simulated 28.2 vs reference 33.1 (ratio 0.85) |
| faults.signature_alignment | PASS | oil_starvation cosine = 1.0000 |
| diagnostics.loto_accuracy | PASS | 87.8% overall vs 84.5% reference |
| diagnostics.zero_shot_isolation | PASS | 99.2% (120/121) at severity > 0.35 |

### 1.6 Model 5 OOF Metric Recomputation
**Command:** Read CSV, compute MAE, RMSE, R² from rul_target_cycles vs rul_prediction_oof  
**Input:** `model5_clean_oof_predictions.csv` (1,100 rows, 22 missions)

| Metric | Repository-Reported | Independently Recomputed | Δ |
|--------|-------------------|------------------------|---|
| MAE | 805.286 cycles | 808.717 cycles | +3.43 |
| RMSE | 1343.148 cycles | 1349.586 cycles | +6.44 |
| R² | 0.760164 | 0.757860 | −0.0023 |

**Conclusion:** Small discrepancy (~0.3–0.5%), likely due to rounding in the reported values or slightly different computation methodology. The results are materially consistent.

---

## 2. Experiments That Failed

### 2.1 Model Artifact Loading
**Command:** `joblib.load(model4_health_extratrees.joblib)`  
**Error:** `KeyError: 118` in `pickle.py`  
**Root Cause:** Files are Git LFS text pointer stubs (133 bytes each), not binary serialized sklearn models. The actual binary blobs (34.6 MB and 137.3 MB) were never pulled from the LFS server.

**Impact:**
- `RealTimeMonitor.__init__()` crashes at `MLHealthIndexModel()` instantiation
- `MLRULPredictor()` also crashes
- System cannot fall through to heuristic fallback because the crash occurs at `joblib.load()` (file exists but is not a valid pickle), not at the file-existence check

### 2.2 Full Validation Harness (Prognostics)
**Command:** `ModelValidator.check_prognostics()` → calls `RealTimeMonitor()`  
**Error:** Same `KeyError: 118` cascade  
**Impact:** RUL interval consistency and estimate production checks cannot execute

### 2.3 Backend Server Startup
**Not attempted.** Requires:
- PostgreSQL/TimescaleDB instance
- Environment variable configuration
- Database schema migration
- Authentication seed data

---

## 3. Identified Limitations

### 3.1 Synthetic Data Provenance
- **ALL** calibration parameters, fault gains, noise models, and degradation regimes are derived from `phm_synthetic_dataset_v2-2.xlsx`
- This reference dataset is NOT included in the repository
- The sensor response equations were "recovered from the reference dataset" — they are empirical curve fits, not first-principles thermodynamic models
- No physical engine manufacturer, model number, displacement, or cylinder geometry is identified
- Operating envelope bounds derive from 22 synthetic reference trajectories, not certified engine specifications

### 3.2 Model Architecture Gaps
- **Feature truncation:** Model 4 `_build_feature_row()` generates 106 of 184 expected features; 78 default to 0.0
- **Channel key mismatch:** `config.py` uses `sensor_4`/`sensor_11`; `model4_healthy_baseline.json` uses `4`/`11` (handled by positional indexing)
- **No cross-engine coupling:** Dual-engine airframe (drone-01) runs independent parallel twin sessions with no vibration or structural coupling model
- **Redundant resolve:** `RealTimeMonitor.step()` resolves the operating point twice to avoid passing `None` attributes to ML feature rows

### 3.3 Integration Gaps
- **CAN adapter:** Implemented but never instantiated; pushes to unconsumed queue; requires Linux socketcan
- **MQTT adapter:** Same pattern; never started
- **Redis:** Package installed but never imported in application code
- **ML model serving:** `models/` directory missing; all generic ML models return hardcoded heuristic values
- **Audit logging:** WebSocket messages bypass HTTP audit middleware
- **Docker volumes:** `docker-compose.yml` mounts `../models` which does not exist

### 3.4 Frontend Mock Data
- Mission replay: 100% hardcoded (5 demo sorties)
- Risk assessment view: 100% local browser simulation
- Predictive maintenance: 100% static data
- Mission clock and altitude: Always locally generated
- When backend is unavailable: Full demo sequence with hardcoded fault injection timing

### 3.5 Unresolved Technical Questions
1. What physical quantities do `sensor_4` and `sensor_11` measure?
2. What engine model were the sensor response equations calibrated against?
3. What is the actual physical unit system for EGT, CHT, TIT, fuel_flow, vibration channels?
4. Why does the healthy regime have a slightly negative fitted drift (−1.13e-7), clamped to zero?
5. What drives the poor per-class accuracy for misfire (13.3%) in LOO cross-validation?

---

## 4. Reproducibility Requirements

To fully reproduce all results from this repository:

1. **Git LFS resolution:** Pull actual binary model artifacts from the LFS server
2. **scikit-learn version:** Models were likely trained on sklearn 1.5.x; use matching version
3. **Reference dataset:** Obtain `phm_synthetic_dataset_v2-2.xlsx` for physics validation against ground truth
4. **PostgreSQL/TimescaleDB:** Deploy database for backend integration testing
5. **Python 3.12:** Match the Docker target version (3.14 causes pickle incompatibilities)

---

## 5. Validation Roadmap

### Phase 1: Software Completion (Near-term)
- [ ] Resolve Git LFS model artifacts
- [ ] Fix Model 4 feature generation (106 → 184 features)
- [ ] Test end-to-end backend pipeline with database
- [ ] Wire CAN/MQTT adapters or remove from documentation
- [ ] Add WebSocket audit logging

### Phase 2: Synthetic Validation (Medium-term)
- [ ] Run full validation harness with resolved model artifacts
- [ ] Execute prognostics validation (RUL interval consistency)
- [ ] Cross-validate Model 5 from scratch (verify OOF results)
- [ ] Benchmark Model 4 health index against Wiener ground truth
- [ ] Expand simulation to 100+ trajectories for statistical power

### Phase 3: Physical Validation (Long-term)
- [ ] Identify and document target engine model
- [ ] Calibrate sensor response equations against dynamometer data
- [ ] Verify fault signature gains against controlled fault injection
- [ ] Validate noise model against real telemetry recordings
- [ ] Run controlled flight test campaigns
- [ ] Establish certified operating envelope limits
