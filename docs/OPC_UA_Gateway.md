# GhostMesh OPC UA to MQTT Gateway

**Status: ✅ IMPLEMENTED AND OPERATIONAL**

The OPC UA to MQTT Gateway is a critical component of GhostMesh that bridges industrial OPC UA devices with the MQTT messaging system, enabling real-time telemetry data flow for anomaly detection and monitoring.

## Overview

The gateway subscribes to OPC UA nodes, normalizes the data into JSON format, and publishes telemetry messages to MQTT topics following the GhostMesh architecture. It also publishes retained state messages for each asset.

**Current Implementation:**
- ✅ Async OPC UA client with proper error handling
- ✅ 11 node mappings for industrial equipment simulation
- ✅ Real-time data flow at ~1Hz
- ✅ JSON telemetry messages with structured schema
- ✅ MQTT topics following `factory/<line>/<asset>/<signal>` pattern
- ✅ Retained state messages to `state/<asset>` topics
- ✅ Comprehensive reconnection logic

## Architecture

```
[OPC UA Devices] → [OPC UA Gateway] → [MQTT Broker] → [Anomaly Detector]
                                      ↓
                                 [Dashboard]
```

## Features

- **Async OPC UA Client**: Uses asyncua library for efficient I/O operations
- **Configurable Mappings**: YAML-based configuration for node-to-topic mappings
- **JSON Normalization**: Converts OPC UA data to standardized JSON format
- **MQTT Publishing**: Publishes to factory/ and state/ topics
- **Error Handling**: Robust reconnection and error recovery
- **Health Monitoring**: Built-in health checks and logging

## Current Implementation Details

### Live Data Flow
The gateway is currently operational with the following configuration:

**OPC UA Server**: Mock server simulating industrial equipment
- **Endpoint**: `opc.tcp://mock-opcua:4840`
- **Security**: None (for development)
- **Namespace**: 2 (custom industrial namespace)

**Node Mappings**: 11 active subscriptions
- **Press01**: Temperature, Pressure, Vibration, Status
- **Press02**: Temperature, Pressure, Vibration, Status  
- **Conveyor01**: Speed, Load, Status

**MQTT Topics**: Following `factory/<line>/<asset>/<signal>` pattern
- `factory/A/press01/temperature`
- `factory/A/press01/pressure`
- `factory/A/press01/vibration`
- `factory/A/press01/status`
- `factory/A/press02/*`
- `factory/B/conveyor01/*`

**Telemetry Message Format**:
```json
{
  "assetId": "press01",
  "line": "A",
  "signal": "temperature",
  "value": 33.66,
  "unit": "C",
  "ts": "2025-09-13T10:25:52.797652+00:00",
  "quality": "Good",
  "source": "opcua",
  "seq": 347
}
```

### Verification Commands
```bash
# Check gateway status
make status

# View live telemetry data
timeout 10s podman exec ghostmesh-mosquitto mosquitto_sub -h localhost -u gateway -P gatewaypass -t "factory/+/+/+" -C 5 -W 5

# View gateway logs
make logs-gateway
```

## Configuration

### Mapping Configuration (mapping.yaml)

The gateway uses a YAML configuration file to define OPC UA server settings, MQTT broker connection, and node mappings.

```yaml
# OPC UA server configuration
opcua:
  endpoint: "opc.tcp://mock-opcua:4840"
  security_policy: "None"
  security_mode: "None"
  username: null
  password: null
  session_timeout: 60000
  connection_timeout: 10000
  reconnect_interval: 5000

# MQTT broker configuration
mqtt:
  host: "mosquitto"
  port: 1883
  username: "gateway"
  password: "gatewaypass"
  qos: 1
  retain_state: true
  keepalive: 60
  reconnect_interval: 5

# Node mappings
mappings:
  - nodeId: "ns=2;s=Press01.Temperature"
    topic: "factory/A/press01/temperature"
    unit: "C"
    data_type: "float"
    description: "Press01 temperature sensor"
```

### Configuration Parameters

#### OPC UA Settings
- `endpoint`: OPC UA server endpoint URL
- `security_policy`: Security policy (None, Basic256Sha256, etc.)
- `security_mode`: Security mode (None, Sign, SignAndEncrypt)
- `username`: OPC UA username (optional)
- `password`: OPC UA password (optional)
- `session_timeout`: Session timeout in milliseconds
- `connection_timeout`: Connection timeout in milliseconds
- `reconnect_interval`: Reconnection interval in milliseconds

#### MQTT Settings
- `host`: MQTT broker hostname
- `port`: MQTT broker port
- `username`: MQTT username
- `password`: MQTT password
- `qos`: Quality of Service level (0, 1, 2)
- `retain_state`: Retain state messages
- `keepalive`: Keep-alive interval in seconds
- `reconnect_interval`: Reconnection interval in seconds

#### Node Mapping
- `nodeId`: OPC UA node identifier
- `topic`: MQTT topic for publishing data
- `unit`: Unit of measurement
- `data_type`: Expected data type
- `description`: Human-readable description

## Message Formats

### Telemetry Message

Published to `factory/<line>/<asset>/<signal>` topics:

```json
{
  "assetId": "press01",
  "line": "A",
  "signal": "temperature",
  "value": 25.5,
  "unit": "C",
  "ts": "2025-01-01T12:00:00.000Z",
  "quality": "Good",
  "source": "opcua",
  "seq": 12345
}
```

### State Message

Published to `state/<asset>` topics (retained):

```json
{
  "assetId": "press01",
  "line": "A",
  "status": "running",
  "lastUpdate": "2025-01-01T12:00:00.000Z",
  "signals": {
    "temperature": {
      "value": 25.5,
      "quality": "Good",
      "timestamp": "2025-01-01T12:00:00.000Z"
    },
    "pressure": {
      "value": 10.2,
      "quality": "Good",
      "timestamp": "2025-01-01T12:00:00.000Z"
    }
  },
  "source": "opcua"
}
```

## Topic Structure

The gateway follows the GhostMesh MQTT topic structure:

- **Telemetry**: `factory/<line>/<asset>/<signal>`
- **State**: `state/<asset>` (retained)

### Examples
- `factory/A/press01/temperature` - Press01 temperature on line A
- `factory/A/press01/pressure` - Press01 pressure on line A
- `factory/B/conveyor01/speed` - Conveyor01 speed on line B
- `state/press01` - Press01 asset state
- `state/conveyor01` - Conveyor01 asset state

## Setup and Deployment

### Using Makefile

```bash
# Build the gateway
make build-gateway

# Start the gateway
make start

# View gateway logs
make logs-gateway

# Test gateway functionality
make test
```

### Manual Setup

1. **Install dependencies:**
   ```bash
   cd opcua2mqtt
   pip install -r requirements.txt
   ```

2. **Configure mappings:**
   Edit `mapping.yaml` with your OPC UA server details and node mappings.

3. **Run the gateway:**
   ```bash
   python opcua2mqtt.py
   ```

### Docker Deployment

```bash
# Build container
docker build -t ghostmesh-gateway ./opcua2mqtt

# Run container
docker run -d \
  --name ghostmesh-gateway \
  --network ghostmesh-network \
  -v $(pwd)/opcua2mqtt/mapping.yaml:/app/mapping.yaml:ro \
  ghostmesh-gateway
```

## Testing

### Unit Tests

Run the test suite:

```bash
cd opcua2mqtt
python -m pytest test_gateway.py -v
```

### Integration Tests

Test with a real OPC UA server:

```bash
# Start OPC UA simulator (if available)
# Update mapping.yaml with correct endpoint
# Run gateway and verify MQTT messages
```

### MQTT Testing

Verify telemetry messages are published:

```bash
# Subscribe to telemetry topics
mosquitto_sub -h localhost -t "factory/+/+/+" -v

# Subscribe to state topics
mosquitto_sub -h localhost -t "state/+" -v
```

## Monitoring and Logging

### Log Files

The gateway creates detailed logs:
- Console output with structured logging
- Log file: `opcua2mqtt.log`

### Health Checks

The gateway includes health checks:
- OPC UA connection status
- MQTT broker connectivity
- Node subscription status
- Message publishing success rate

### Metrics

Monitor these key metrics:
- Connection uptime
- Messages published per second
- Error rates
- Reconnection attempts
- Node read failures

## Troubleshooting

### Common Issues

1. **OPC UA Connection Failed**
   - Verify endpoint URL is correct
   - Check network connectivity
   - Validate credentials if authentication is enabled
   - Ensure OPC UA server is running

2. **MQTT Connection Failed**
   - Verify MQTT broker is running
   - Check broker hostname and port
   - Validate MQTT credentials
   - Ensure network connectivity

3. **Node Subscription Failed**
   - Verify node IDs are correct
   - Check node exists and is readable
   - Ensure proper permissions
   - Validate namespace and identifier format

4. **No Messages Published**
   - Check OPC UA node values are changing
   - Verify MQTT topic permissions
   - Check gateway logs for errors
   - Ensure mapping configuration is correct

### Debug Mode

Enable debug logging:

```yaml
settings:
  log_level: "DEBUG"
```

### Connection Testing

Test OPC UA connectivity:

```python
import asyncio
from asyncua import Client

async def test_opcua():
    client = Client("opc.tcp://localhost:4840")
    await client.connect()
    node = client.get_node("ns=2;s=Press01.Temperature")
    value = await node.read_value()
    print(f"Value: {value}")
    await client.disconnect()

asyncio.run(test_opcua())
```

## Security Considerations

### OPC UA Security
- Use secure security policies in production
- Implement proper authentication
- Use encrypted connections (SignAndEncrypt)
- Regularly rotate credentials

### MQTT Security
- Use strong passwords
- Implement proper ACLs
- Consider TLS encryption for production
- Monitor for unauthorized access

### Network Security
- Use internal networks for OPC UA communication
- Implement firewall rules
- Monitor network traffic
- Use VPNs for remote access

## Performance Optimization

### Connection Management
- Use connection pooling for multiple nodes
- Implement proper session management
- Optimize subscription intervals
- Use async operations for better performance

### Memory Management
- Limit retained message history
- Implement proper cleanup
- Monitor memory usage
- Use efficient data structures

### Network Optimization
- Batch multiple node reads
- Optimize MQTT QoS levels
- Use compression for large payloads
- Implement message queuing

## Future Enhancements

### Planned Features
- Support for OPC UA events
- Historical data access
- Bulk node operations
- Advanced filtering
- Metrics collection
- WebSocket interface

### Integration Improvements
- OPC UA discovery
- Automatic node mapping
- Configuration validation
- Hot-reload configuration
- Multi-server support
