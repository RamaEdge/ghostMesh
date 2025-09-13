# THE-66: Anomaly Injection and Alert Validation Testing

## Overview

This directory contains comprehensive tests for THE-66: Anomaly Injection and Alert Validation Testing. The tests validate the GhostMesh anomaly detection system's ability to:

- Induce synthetic anomalies (spike, flood, drift)
- Verify alert generation within 2-second latency requirement
- Test isolate/unblock functionality
- Validate alert severity classification
- Test debounce behavior and false positive handling

## Test Structure

```
tests/the66/
├── README.md                    # This file
├── anomaly_injector.py          # Anomaly injection mechanism
├── test_anomaly_validation.py   # Comprehensive validation tests
├── run_tests.py                 # Simple test runner
├── requirements.txt             # Python dependencies
└── test_results.json           # Test results (generated)
```

## Quick Start

### Prerequisites
- Python 3.9+
- All GhostMesh services running (`make start`)
- MQTT broker accessible

### Running Tests

#### Run All THE-66 Tests
```bash
# From project root
make test-the66

# Or directly
cd tests/the66
python3 run_tests.py
```

#### Run Individual Components
```bash
# Test anomaly injection only
python3 anomaly_injector.py

# Run comprehensive validation
python3 test_anomaly_validation.py
```

## Test Categories

### 1. Anomaly Injection Tests
**File:** `anomaly_injector.py`

Tests the ability to inject synthetic anomalies:
- **Spike Anomalies:** Sudden value increases/decreases
- **Flood Anomalies:** Rapid successive value changes
- **Drift Anomalies:** Gradual value changes over time

**Test Assets:**
- `press01`: Temperature, Pressure, Speed, Vibration
- `press02`: Temperature, Pressure, Speed, Vibration  
- `conveyor01`: Temperature, Speed, Vibration

### 2. Latency Validation Tests
**File:** `test_anomaly_validation.py`

Validates that alerts are generated within the 2-second latency requirement:
- Measures time from anomaly injection to alert generation
- Tracks latency statistics (min, max, average)
- Validates against 2-second requirement

### 3. Policy Enforcement Tests
**File:** `test_anomaly_validation.py`

Tests isolate/unblock functionality:
- Sends isolate commands via MQTT
- Sends unblock commands via MQTT
- Validates policy actions are received and processed

### 4. Severity Classification Tests
**File:** `test_anomaly_validation.py`

Validates alert severity classification:
- Tests different anomaly intensities
- Verifies correct severity assignment (low, medium, high)
- Validates z-score threshold mapping

### 5. Debounce Behavior Tests
**File:** `test_anomaly_validation.py`

Tests debounce behavior and false positive handling:
- Injects rapid successive anomalies
- Validates alert count is limited by debounce logic
- Tests 30-second debounce window

## Anomaly Types

### Spike Anomaly
```python
# Sudden value increase/decrease
injector.inject_spike_anomaly("press01", "temperature", spike_multiplier=3.0)
```

### Flood Anomaly
```python
# Rapid successive value changes
injector.inject_flood_anomaly("press02", "pressure", flood_count=8)
```

### Drift Anomaly
```python
# Gradual value change over time
injector.inject_drift_anomaly("conveyor01", "speed", drift_rate=0.15, duration_seconds=20)
```

## Test Results

Test results are saved to `test_results.json` with the following structure:

```json
{
  "test_summary": {
    "total_passed": 15,
    "total_failed": 0,
    "success_rate": 100.0
  },
  "detailed_results": {
    "anomaly_injection": {
      "passed": 3,
      "failed": 0,
      "details": [...]
    },
    "latency_validation": {
      "passed": 1,
      "failed": 0,
      "details": [...]
    },
    "policy_enforcement": {
      "passed": 2,
      "failed": 0,
      "details": [...]
    },
    "severity_classification": {
      "passed": 3,
      "failed": 0,
      "details": [...]
    },
    "debounce_behavior": {
      "passed": 1,
      "failed": 0,
      "details": [...]
    }
  }
}
```

## Acceptance Criteria

- [x] Anomalies can be injected reliably
- [x] Alerts generated within 2 seconds
- [x] Isolate action blocks asset data
- [x] Unblock action restores normal flow
- [x] Alert severity matches z-score thresholds

## Performance Requirements

- **Latency:** Alerts must be generated within 2 seconds
- **Debounce:** 30-second debounce window for same asset/signal
- **Severity Thresholds:**
  - Low: z-score < 4
  - Medium: z-score ≥ 4
  - High: z-score ≥ 8

## Troubleshooting

### Common Issues

#### Services Not Running
```bash
# Check service status
make status

# Start services
make start
```

#### MQTT Connection Issues
```bash
# Test MQTT connectivity
make test-mqtt

# Check MQTT logs
make logs-mqtt
```

#### Test Failures
```bash
# Run with verbose output
python3 test_anomaly_validation.py

# Check individual components
python3 anomaly_injector.py
```

### Debug Commands
```bash
# Monitor MQTT topics
make monitor-mqtt

# Check anomaly detector logs
make logs-anomaly

# Check policy engine logs
make logs-policy
```

## Integration with Makefile

The THE-66 tests are integrated into the main Makefile:

```makefile
test-the66:
	@echo "Running THE-66: Anomaly Injection and Alert Validation Tests"
	cd tests/the66 && python3 run_tests.py
```

## Time Estimate

**Estimated Duration:** 1 hour (18:30-19:30)

**Test Breakdown:**
- Anomaly Injection: 15 minutes
- Latency Validation: 10 minutes
- Policy Enforcement: 10 minutes
- Severity Classification: 15 minutes
- Debounce Behavior: 10 minutes

## References

- [THE-66 Linear Issue](https://linear.app/theedgeworks/issue/THE-66)
- [Anomaly Detector Documentation](../../docs/Anomaly_Detector.md)
- [Policy Engine Documentation](../../docs/Policy_Engine.md)
- [MQTT Configuration](../../docs/MQTT_Configuration.md)
