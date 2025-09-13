# Anomaly Detector Documentation

## Overview

The GhostMesh Anomaly Detector implements rolling z-score analysis to detect anomalies in real-time telemetry data from industrial equipment. It processes data from MQTT telemetry topics and publishes alerts when anomalies are detected.

## Status: ✅ IMPLEMENTED AND OPERATIONAL

**Linear Issue:** THE-62  
**Implementation Date:** September 13, 2025  
**Service Name:** `anomaly`  
**Container:** `ghostmesh-detector`

## Core Features

### Rolling Z-Score Algorithm
- **Window Size:** 120 seconds sliding window
- **Statistical Method:** Z-score calculation using rolling mean and standard deviation
- **Data Structure:** Efficient deque operations for O(1) window management
- **Minimum Data Points:** Requires 10 data points for reliable statistics

### Severity Thresholds
- **Medium Severity:** z-score ≥ 4.0
- **High Severity:** z-score ≥ 8.0
- **No Alert:** z-score < 4.0

### Debounce Logic
- **Debounce Period:** 30 seconds
- **Purpose:** Prevents rapid alert generation for the same asset/signal
- **Implementation:** Tracks last alert time per asset/signal combination

## MQTT Integration

### Input Topics
- **Subscription Pattern:** `factory/+/+/+`
- **Topic Format:** `factory/<line>/<asset>/<signal>`
- **Message Format:** JSON telemetry data with `value` and `ts` fields

### Output Topics
- **Alert Pattern:** `alerts/<asset>/<signal>`
- **Retention:** Retained messages for persistence
- **QoS Level:** 1 (at least once delivery)

## Alert Schema

The anomaly detector publishes alerts following the GhostMesh architecture schema:

```json
{
  "alertId": "a-{uuid}",
  "assetId": "press01",
  "signal": "temperature",
  "severity": "high",
  "reason": "z-score 9.4 vs mean 42.1±1.0 (120s)",
  "current": 143.2,
  "ts": "2025-09-13T11:16:47.717Z"
}
```

### Field Descriptions
- **alertId:** Unique identifier with "a-" prefix and 8-character UUID
- **assetId:** Asset identifier extracted from MQTT topic
- **signal:** Signal name extracted from MQTT topic
- **severity:** "medium" or "high" based on z-score threshold
- **reason:** Human-readable explanation with z-score, mean, std deviation, and window size
- **current:** Current signal value that triggered the alert
- **ts:** ISO 8601 timestamp of alert generation

## Edge Case Handling

### Insufficient Data
- **Minimum Points:** Requires at least 10 data points in the 120s window
- **Behavior:** No alert generated, debug logging for insufficient data
- **Recovery:** Automatically starts generating alerts once sufficient data is available

### Zero Variance
- **Detection:** Standard deviation equals zero
- **Behavior:** No alert generated, prevents division by zero
- **Logging:** Error logged for zero variance scenarios

### Network Disconnections
- **MQTT Reconnection:** Automatic reconnection with exponential backoff
- **Data Persistence:** Sliding window data maintained during disconnections
- **Recovery:** Continues processing once MQTT connection is restored

## Performance Optimizations

### Memory Efficiency
- **Data Structure:** Deque for O(1) append/pop operations
- **Window Management:** Automatic cleanup of old data points
- **Memory Limit:** Maximum 100 data points per asset/signal (configurable)

### CPU Efficiency
- **Statistical Calculations:** Optimized numpy operations
- **Debounce Logic:** O(1) lookup for last alert times
- **Minimal Processing:** Only processes new data points

### Raspberry Pi Optimization
- **Lightweight Dependencies:** Only numpy and paho-mqtt
- **Efficient Algorithms:** Optimized for ARM architecture
- **Resource Monitoring:** Built-in logging for performance tracking

## Configuration

### Environment Variables
```bash
MQTT_HOST=mosquitto          # MQTT broker hostname
MQTT_PORT=1883              # MQTT broker port
MQTT_USERNAME=iot           # MQTT username (currently using iot user)
MQTT_PASSWORD=iotpass       # MQTT password
MQTT_QOS=1                  # MQTT Quality of Service level
```

### Runtime Configuration
- **Window Size:** 120 seconds (hardcoded)
- **Debounce Period:** 30 seconds (hardcoded)
- **Severity Thresholds:** Medium=4.0, High=8.0 (hardcoded)
- **Minimum Data Points:** 10 (hardcoded)

## Deployment

### Container Configuration
```yaml
anomaly:
  build: ./anomaly
  container_name: ghostmesh-detector
  depends_on:
    mosquitto:
      condition: service_healthy
  environment:
    - MQTT_HOST=mosquitto
    - MQTT_PORT=1883
    - MQTT_USERNAME=iot
    - MQTT_PASSWORD=iotpass
    - MQTT_QOS=1
  restart: unless-stopped
  networks:
    - ghostmesh-network
```

### Build Commands
```bash
# Build anomaly detector container
make build-anomaly

# Build all containers (includes anomaly detector)
make build

# Start all services (includes anomaly detector)
make start
```

## Monitoring and Debugging

### Logs
```bash
# View anomaly detector logs
podman-compose logs anomaly

# Follow logs in real-time
podman-compose logs -f anomaly

# View last 20 log entries
podman-compose logs anomaly --tail=20
```

### Status Checking
```bash
# Check if anomaly detector is running
make status

# Check container health
podman-compose ps anomaly
```

### MQTT Monitoring
```bash
# Subscribe to alert topics
podman exec ghostmesh-mosquitto mosquitto_sub -h localhost -t "alerts/+/+" -C 10

# Subscribe to specific asset alerts
podman exec ghostmesh-mosquitto mosquitto_sub -h localhost -t "alerts/press01/+" -C 10
```

## Testing

### Manual Testing
1. **Start Services:** `make start`
2. **Verify Connection:** Check logs for "Connected to MQTT broker"
3. **Monitor Alerts:** Subscribe to `alerts/+/+` topics
4. **Generate Anomalies:** Wait for natural anomalies or inject test data

### Integration Testing
```bash
# Run comprehensive test suite
make test

# Test specific anomaly detector functionality
make test-anomaly  # (if implemented)
```

## Troubleshooting

### Common Issues

**Connection Refused (Code 5)**
- **Cause:** MQTT authentication failure
- **Solution:** Verify MQTT credentials and user permissions

**Name or Service Not Known**
- **Cause:** Cannot resolve MQTT broker hostname
- **Solution:** Ensure MQTT broker is running and accessible

**No Alerts Generated**
- **Cause:** Insufficient data or low z-scores
- **Solution:** Wait for more data or check if values are within normal ranges

**High Memory Usage**
- **Cause:** Too many asset/signal combinations
- **Solution:** Monitor data windows and consider cleanup logic

### Debug Mode
Enable debug logging by modifying the logging level in `anomaly_detector.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Configurable Thresholds:** Runtime configuration of severity thresholds
- **Multiple Algorithms:** Support for IsolationForest and other detection methods
- **Alert Aggregation:** Group related alerts to reduce noise
- **Performance Metrics:** Built-in performance monitoring and reporting

### Integration Points
- **AI Explainer:** Alerts will be processed by the explainer service (THE-63)
- **Policy Engine:** Alerts will trigger policy actions (THE-64)
- **Dashboard:** Alerts will be displayed in real-time monitoring interface

## Technical Specifications

### Dependencies
- **Python:** 3.11+
- **numpy:** 1.24.0+ (statistical calculations)
- **paho-mqtt:** 1.6.1+ (MQTT client)

### Resource Requirements
- **Memory:** ~50MB base + ~1KB per asset/signal
- **CPU:** Minimal, optimized for ARM architecture
- **Network:** MQTT traffic only, minimal bandwidth usage

### Security Considerations
- **MQTT Authentication:** Currently using iot user (temporary)
- **Data Privacy:** No sensitive data stored, only statistical calculations
- **Network Security:** Runs in isolated container network

---

**Last Updated:** September 13, 2025  
**Version:** 1.0.0  
**Maintainer:** GhostMesh Development Team
