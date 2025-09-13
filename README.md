# GhostMesh — Edge AI Security Copilot

GhostMesh is an edge-resident security copilot for industrial/IoT environments that detects anomalies in real-time, explains risks in plain language, and enforces policy actions.

## Quick Start

```bash
git clone <repo> && cd ghostmesh
make quick-start
open http://<pi-ip>:8501   # Streamlit dashboard
```

### Available Commands

```bash
make help          # Show all available commands
make setup         # Initial project setup
make start         # Start all services
make test          # Run all tests
make logs          # Show service logs
make status        # Check service status
```

## Documentation

- **[Project Overview](docs/Project_README.md)** - Complete project documentation
- **[Architecture](docs/Architecture.md)** - System architecture and design
- **[Implementation Plan](docs/Implementation_Plan.md)** - 2-day hackathon timeline
- **[MQTT Configuration](docs/MQTT_Configuration.md)** - MQTT broker setup and configuration

## Project Status

This is a hackathon project implementing edge AI security for industrial IoT environments.

**Current Implementation:**
- ✅ MQTT broker with authentication and ACL
- 🔄 OPC UA to MQTT gateway (in progress)
- 🔄 Anomaly detector (planned)
- 🔄 Policy engine (planned)
- 🔄 Streamlit dashboard (planned)

## Contributing

See [Project README](docs/Project_README.md) for detailed setup and development instructions.