# GhostMesh Comprehensive Testing Framework (THE-71)

This directory contains comprehensive testing and validation tools for GhostMesh, implementing all requirements for THE-71.

## Overview

The testing framework provides:

- **Latency Measurement**: Measures alert latency from telemetry injection to alert generation
- **System Validation**: Tests false positive handling, debounce behavior, system recovery, and edge cases
- **Performance Monitoring**: Monitors resource usage and performance metrics for Pi 5 optimization
- **Comprehensive Test Runner**: Orchestrates all tests and generates detailed reports

## Test Components

### 1. Latency Measurement (`latency_measurement.py`)

Measures end-to-end alert latency with target ≤2 seconds.

**Features:**
- Injects test telemetry data
- Tracks alert generation timing
- Calculates latency statistics (avg, min, max, percentiles)
- Measures success rate and performance against targets

**Usage:**
```bash
python latency_measurement.py --tests 10 --delay 2.0
```

### 2. System Validation (`system_validation.py`)

Comprehensive system reliability and edge case testing.

**Test Categories:**
- **False Positive Handling**: Tests normal values don't trigger alerts
- **Debounce Behavior**: Tests rapid value changes trigger single alerts
- **System Recovery**: Tests service restart and recovery
- **Edge Cases**: Tests invalid data, missing fields, extreme values
- **Performance Under Load**: Tests system behavior with high message volume

**Usage:**
```bash
python system_validation.py
```

### 3. Performance Monitor (`performance_monitor.py`)

Monitors system performance and resource usage.

**Metrics Tracked:**
- CPU usage (average, peak, temperature)
- Memory consumption (RAM, swap)
- Disk usage and I/O
- Network I/O
- Container-specific metrics
- Service health status

**Usage:**
```bash
python performance_monitor.py --duration 300
```

### 4. Comprehensive Test Runner (`run_comprehensive_tests.py`)

Orchestrates all tests and generates comprehensive reports.

**Features:**
- Runs all test suites in sequence
- Generates detailed test reports
- Assesses acceptance criteria
- Saves results to JSON files
- Provides pass/fail status

**Usage:**
```bash
python run_comprehensive_tests.py --save-report
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure GhostMesh services are running:
```bash
podman-compose up -d
```

## Running Tests

### Quick Test
Run all tests with default settings:
```bash
python run_comprehensive_tests.py
```

### Individual Tests
Run specific test components:
```bash
# Latency measurement only
python latency_measurement.py --tests 20

# System validation only
python system_validation.py

# Performance monitoring only
python performance_monitor.py --duration 600
```

### Advanced Options
```bash
# Custom MQTT broker
python run_comprehensive_tests.py --host mosquitto --port 1883

# Save detailed report
python run_comprehensive_tests.py --save-report
```

## Acceptance Criteria

The testing framework validates these THE-71 acceptance criteria:

- [ ] **Alert latency consistently under 2 seconds**
  - Measured by `latency_measurement.py`
  - Target: ≤2s average, ≥95% under 2s

- [ ] **False positive rate within acceptable limits**
  - Tested by `system_validation.py`
  - Normal values should not trigger alerts

- [ ] **System recovers gracefully from failures**
  - Tested by `system_validation.py`
  - Services restart and resume normal operation

- [ ] **Edge cases handled properly**
  - Tested by `system_validation.py`
  - Invalid data, missing fields, extreme values handled gracefully

- [ ] **Performance metrics within Pi 5 limits**
  - Monitored by `performance_monitor.py`
  - CPU <80%, Memory <85%, Disk <90%

## Test Results

### Success Criteria
- All test suites pass
- Latency targets met
- System performance within limits
- No false positives
- Graceful error handling

### Report Format
Test results are saved in JSON format with:
- Timestamp and test suite information
- Individual test results with pass/fail status
- Detailed metrics and statistics
- Acceptance criteria assessment
- Overall pass/fail status

## Troubleshooting

### Common Issues

1. **MQTT Connection Failed**
   - Ensure mosquitto service is running
   - Check MQTT broker host/port settings
   - Verify network connectivity

2. **Services Not Running**
   - Run `podman-compose ps` to check service status
   - Start services with `podman-compose up -d`

3. **Permission Errors**
   - Ensure proper permissions for container operations
   - Check podman/docker access

4. **High Resource Usage**
   - Monitor system resources during tests
   - Adjust test parameters if needed
   - Consider running tests during low-usage periods

### Debug Mode
Enable verbose logging by setting environment variable:
```bash
export GHOSTMESH_DEBUG=1
python run_comprehensive_tests.py
```

## Integration

The testing framework integrates with:
- **GhostMesh Services**: Tests all core services
- **MQTT Broker**: Uses MQTT for test data injection
- **Container Runtime**: Monitors container performance
- **System Metrics**: Tracks Pi 5 resource usage

## Contributing

When adding new tests:
1. Follow the existing test structure
2. Add appropriate error handling
3. Include detailed logging
4. Update this README
5. Add to the comprehensive test runner

## License

Part of the GhostMesh project. See main project license.
