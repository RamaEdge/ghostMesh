# GhostMesh — Edge AI Security Copilot

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
- **OPC UA → MQTT Gateway**: Subscribes to OPC UA nodes, publishes to MQTT
- **MQTT Broker**: Mosquitto with user authentication and ACLs
- **Anomaly Detector**: Rolling z-score detection over 120s windows
- **AI Explainer**: Local LLM or API for alert explanations
- **Policy Engine**: Enforces isolate/throttle/unblock actions
- **Dashboard**: Streamlit UI for monitoring and control

## Quick Start

### Prerequisites

- Podman or Docker installed
- Podman Compose or Docker Compose
- Raspberry Pi 5 (8GB RAM) or compatible system

### 3-Command Setup

```bash
git clone <repo> && cd ghostmesh
podman compose up -d --build
open http://<pi-ip>:8501   # Streamlit dashboard
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