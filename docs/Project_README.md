# GhostMesh — Edge AI Security Copilot

**Complete Project Documentation**

This is the comprehensive documentation for the GhostMesh project. For a quick overview, see the [root README](../README.md).

GhostMesh is an edge-resident security copilot for industrial/IoT environments that detects anomalies in real-time, explains risks in plain language, and enforces policy actions.

## Overview

GhostMesh provides invisible AI defense at the edge by:

- Ingesting device signals via OPC UA
- Normalizing them to MQTT topics
- Detecting anomalies using z-score analysis
- Explaining risks via LLM
- Enforcing policy actions (throttle/isolate/unblock)

## Architecture

**Data Flow:** OPC UA → MQTT → AI Detection → Explanation → Policy Action

**Core Services:**
- ✅ **OPC UA → MQTT Gateway**: Subscribes to OPC UA nodes, publishes to MQTT
- ✅ **MQTT Broker**: Mosquitto with user authentication and ACLs
- ✅ **Mock OPC UA Server**: Simulates industrial equipment data
- ✅ **Streamlit Dashboard**: Real-time monitoring and control interface
- 🔄 **Anomaly Detector**: Rolling z-score detection over 120s windows (planned)
- 🔄 **AI Explainer**: Local LLM or API for alert explanations (planned)
- 🔄 **Policy Engine**: Enforces isolate/throttle/unblock actions (planned)

## Current Implementation Status

### ✅ Completed Features

**OPC UA to MQTT Gateway (THE-60)**
- Async OPC UA client using `asyncua` library
- 11 node mappings for Press01, Press02, and Conveyor01 equipment
- JSON telemetry messages with structured schema
- MQTT topics following `factory/<line>/<asset>/<signal>` pattern
- Retained state messages to `state/<asset>` topics
- Comprehensive error handling and reconnection logic
- Real-time data flow at ~1Hz

**Streamlit Dashboard (THE-61 & THE-64)**
- Real-time telemetry charts using Plotly with MQTT data integration
- Interactive alerts table with severity-based color coding
- Functional control buttons for policy enforcement (Isolate, Throttle, Unblock)
- GhostMesh branding with professional gradient design
- Live data updates with optimized 2Hz refresh rate
- MQTT client with connection controls and command publishing
- Responsive layout with sidebar navigation and status indicators
- System metrics and live data point counters
- Containerized deployment on port 8501

**Anomaly Detector (THE-62)**
- Rolling z-score algorithm with 120-second sliding window
- Severity thresholds: medium (z≥4), high (z≥8)
- 30-second debounce logic to prevent alert spam
- MQTT subscription to `factory/+/+/+` telemetry topics
- Alert publishing to `alerts/<asset>/<signal>` topics
- Edge case handling for insufficient data and zero variance
- Performance optimized for Raspberry Pi
- Containerized deployment with health checks

**Infrastructure**
- Mock OPC UA server for development and testing
- MQTT broker with authentication and ACLs
- Containerized services with Podman
- Comprehensive Makefile for build, test, and deployment
- Automated test suite

**Sample Telemetry Data:**
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

### ✅ Completed Features

**Anomaly Detector (THE-62)**
- Rolling z-score analysis over 120s windows
- Severity thresholds: medium (z≥4), high (z≥8)
- 30-second debounce logic to prevent alert spam
- MQTT subscription to telemetry topics
- Alert publishing to `alerts/<asset>/<signal>` topics
- Edge case handling for insufficient data and zero variance
- Performance optimized for Raspberry Pi
- Containerized deployment with health checks

**Policy Engine (THE-63)**
- MQTT subscription to alerts and control command topics
- App-layer blocking mechanism with state tracking
- Comprehensive audit logging with unique action IDs
- Support for isolate, throttle, and unblock commands
- Auto-policy enforcement for high severity alerts
- Command validation and error handling
- Audit event publishing to `audit/actions` topic
- Performance optimized for Raspberry Pi

### 🔄 Planned Features
- **AI Explainer**: LLM-based risk explanation for detected anomalies

## Quick Start

> **New to GhostMesh?** Start with the [Quickstart Guide](Quickstart_Guide.md) for a 5-minute setup walkthrough.

### Prerequisites

- Podman or Docker installed
- Podman Compose or Docker Compose
- Raspberry Pi 5 (8GB RAM) or compatible system

### 3-Command Setup

```bash
git clone <repo> && cd ghostmesh
make quick-start
make test          # Verify everything is working
```

### Verify Installation

```bash
# Check service status
make status

# View live telemetry data
timeout 10s podman exec ghostmesh-mosquitto mosquitto_sub -h localhost -u gateway -P gatewaypass -t "factory/+/+/+" -C 5 -W 5

# View service logs
make logs
```

### Makefile Commands

The project includes a comprehensive Makefile for all development tasks:

```bash
# Setup and Configuration
make setup         # Initial project setup
make build         # Build all containers
make start         # Start all services
make stop          # Stop all services

# Testing and Quality
make test          # Run all tests
make test-mqtt     # Test MQTT connectivity
make lint          # Run code linting
make format        # Format code

# Monitoring
make logs          # Show all logs
make status        # Check service status
make health        # Check service health

# Development
make dev           # Start development environment
make quick-start   # Setup and start services
make quick-test    # Start and test services
```

### Detailed Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ghostmesh
   ```

2. **Set up MQTT users (generates password file with encrypted credentials):**
   ```bash
   ./scripts/setup-mqtt-users.sh
   ```

3. **Start the MQTT broker:**
   ```bash
   podman compose up -d mosquitto
   ```

4. **Test MQTT connectivity:**
   ```bash
   ./scripts/test-mqtt.sh
   ```

5. **Start all services:**
   ```bash
   podman compose up -d --build
   ```

6. **Access the dashboard:**
   Open http://localhost:8501 in your browser

## MQTT Topics

The system uses the following MQTT topic structure:

- **Telemetry**: `factory/<line>/<asset>/<signal>`
- **State**: `state/<asset>` (retained)
- **Alerts**: `alerts/<asset>/<signal>`
- **Explanations**: `explanations/<alertId>`
- **Control**: `control/<asset>/<command>`
- **Audit**: `audit/actions`

## Service Configuration

### MQTT Broker

The Mosquitto broker is configured with:
- User authentication (no anonymous access)
- Topic-based access control (ACL)
- Persistence for retained messages
- Health checks and logging

### Service Users

| Username | Purpose | Permissions |
|----------|---------|-------------|
| `gateway` | OPC UA to MQTT gateway | Write factory/ and state/ topics |
| `detector` | Anomaly detector | Read factory/, write alerts/ |
| `explainer` | LLM explainer | Read alerts/, write explanations/ |
| `policy` | Policy engine | Read alerts/ and control/, write audit/ |
| `dashboard` | Streamlit dashboard | Read all topics, write control/ |
| `iot` | Testing and development | Read/write all topics |

## Development

### Project Structure

```
ghostmesh/
├── docker-compose.yml          # Container orchestration
├── mosquitto/                  # MQTT broker configuration
│   ├── mosquitto.conf         # Broker configuration
│   ├── passwd                 # User passwords
│   ├── acl.conf               # Access control list
│   └── README.md              # MQTT documentation
├── scripts/                   # Setup and test scripts
│   ├── setup-mqtt-users.sh   # User creation script
│   └── test-mqtt.sh          # Connectivity test script
├── opcua2mqtt/               # OPC UA gateway (to be implemented)
├── anomaly/                  # Anomaly detector (to be implemented)
├── policy/                   # Policy engine (to be implemented)
├── dashboard/                # Streamlit dashboard (to be implemented)
└── docs/                     # Architecture and implementation docs
```

### Testing

Run the MQTT connectivity test:
```bash
./scripts/test-mqtt.sh
```

This script verifies:
- Broker connectivity
- User authentication
- Topic permissions
- Message publishing/subscribing

## Security

### Authentication
- Password-based authentication for all MQTT connections
- No anonymous access allowed
- Encrypted password storage
- **Password file not included in repository** - generated locally by setup script

### Credentials
The MQTT password file (`mosquitto/passwd`) contains encrypted credentials and is:
- Generated locally using `./scripts/setup-mqtt-users.sh`
- Excluded from version control via `.gitignore`
- Required for MQTT broker operation

### Access Control
- Topic-based permissions using ACL
- Principle of least privilege
- Service-specific user accounts

### Network Security
- Internal container networking
- No external port exposure except dashboard (8501)
- Health checks for service monitoring

## Performance

### Optimization for Raspberry Pi 5
- Lightweight container images
- Efficient data structures for sliding windows
- Capped UI refresh rates (1-2 Hz)
- Resource limits and health checks

### Latency Requirements
- Alert generation: ≤ 2 seconds
- UI updates: 1-2 Hz
- Message processing: Real-time

## Troubleshooting

### Common Issues

1. **MQTT connection failed:**
   - Check if broker is running: `podman ps`
   - Verify user credentials in `mosquitto/passwd`
   - Test connectivity: `./scripts/test-mqtt.sh`

2. **Permission denied:**
   - Check ACL configuration in `mosquitto/acl.conf`
   - Verify user has proper topic permissions

3. **Service not starting:**
   - Check logs: `podman compose logs <service-name>`
   - Verify dependencies are running
   - Check resource limits

### Logs

View service logs:
```bash
podman compose logs mosquitto
podman compose logs -f  # Follow all logs
```

## Roadmap

### Current Implementation (Hackathon)
- Basic MQTT broker with authentication
- OPC UA to MQTT gateway
- Rolling z-score anomaly detection
- Streamlit dashboard
- Policy engine with isolate/unblock

### Future Enhancements
- TLS encryption for MQTT
- Advanced anomaly detection algorithms
- MITRE ATT&CK mapping
- Federated threat sharing
- Predictive maintenance capabilities

## Contributing

This is a hackathon project. For development:

1. Create a feature branch
2. Implement changes following the architecture
3. Test with the provided scripts
4. Submit pull request

## License

See LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the architecture documentation
- Test with the provided scripts