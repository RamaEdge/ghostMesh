# GhostMesh — Edge AI Security Copilot

GhostMesh is an edge-resident security copilot for industrial/IoT environments that detects anomalies in real-time, explains risks in plain language, and enforces policy actions.

## Quick Start

### Prerequisites
- **Podman** (recommended) or Docker installed
- **Podman Compose** or Docker Compose
- **Raspberry Pi 5** (8GB RAM) or compatible system

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

### Available Commands

```bash
make help          # Show all available commands
make setup         # Initial project setup
make start         # Start all services
make stop          # Stop all services
make test          # Run comprehensive tests
make logs          # Show service logs
make status        # Check service status
make build         # Build all containers
make clean         # Clean up containers and images
make dev           # Start development environment
make quick-start   # Setup and start all services
make quick-test    # Start services and run tests
```

## Documentation

- **[Quickstart Guide](docs/Quickstart_Guide.md)** - Get started in 5 minutes
- **[Project Overview](docs/Project_README.md)** - Complete project documentation
- **[Architecture](docs/Architecture.md)** - System architecture and design
- **[Implementation Plan](docs/Implementation_Plan.md)** - 2-day hackathon timeline
- **[MQTT Configuration](docs/MQTT_Configuration.md)** - MQTT broker setup and configuration
- **[OPC UA Gateway](docs/OPC_UA_Gateway.md)** - OPC UA to MQTT gateway implementation

## Project Status

This is a hackathon project implementing edge AI security for industrial IoT environments.

**Current Implementation:**
- ✅ **MQTT Broker** - Mosquitto with authentication and ACLs
- ✅ **Mock OPC UA Server** - Simulates industrial equipment data
- ✅ **OPC UA to MQTT Gateway** - Real-time data translation pipeline
- ✅ **Containerized Services** - Podman-based deployment
- ✅ **Comprehensive Testing** - Automated test suite
- 🔄 **Anomaly Detector** - Rolling z-score analysis (planned)
- 🔄 **AI Explainer** - LLM-based risk explanation (planned)
- 🔄 **Policy Engine** - Automated response actions (planned)
- 🔄 **Streamlit Dashboard** - Real-time monitoring UI (planned)

**Live Data Flow:**
```
OPC UA Server → Gateway → MQTT Broker → [Future: Anomaly Detection → AI Explanation → Policy Actions]
```

**Sample Telemetry:**
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

## Contributing

See [Project README](docs/Project_README.md) for detailed setup and development instructions.