# GhostMesh — Edge AI Security Copilot

GhostMesh is an edge-resident security copilot for industrial/IoT environments that detects anomalies in real-time, explains risks in plain language, and enforces policy actions.

## 🚀 Quick Start (3 Commands)

### Prerequisites
- **Podman** (recommended) or Docker installed
- **Podman Compose** or Docker Compose
- **Raspberry Pi 5** (8GB RAM) or compatible system
- **8GB RAM minimum** (16GB recommended for LLM)
- **1TB SSD** for model storage

### 3-Command Setup

```bash
git clone https://github.com/RamaEdge/ghostMesh.git && cd ghostMesh
make quick-start
make test          # Verify everything is working
```

### Alternative: Manual Setup

```bash
# 1. Clone and setup
git clone https://github.com/RamaEdge/ghostMesh.git
cd ghostMesh
make setup

# 2. Start services
make start

# 3. Verify installation
make test
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
make start         # Start all services (production)
make stop          # Stop all services
make test          # Run comprehensive tests
make logs          # Show service logs
make status        # Check service status
make build         # Build all containers
make clean         # Clean up containers and images
make dev           # Start development environment
make prod          # Start production environment
make quick-start   # Setup and start all services
make quick-test    # Start services and run tests
```

### Deployment Profiles

**Development Mode:**
```bash
make dev           # Start with debug logging and hot reload
```

**Production Mode:**
```bash
make prod          # Start with optimized settings and monitoring
```

**Manual Profile Selection:**
```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Documentation

- **[Quickstart Guide](docs/Quickstart_Guide.md)** - Get started in 5 minutes
- **[Project Overview](docs/Project_README.md)** - Complete project documentation
- **[Architecture](docs/Architecture.md)** - System architecture and design
- **[Configuration Guide](docs/Configuration_Guide.md)** - Complete configuration reference
- **[Troubleshooting Guide](docs/Troubleshooting_Guide.md)** - Common issues and solutions
- **[Implementation Plan](docs/Implementation_Plan.md)** - 2-day hackathon timeline
- **[MQTT Configuration](docs/MQTT_Configuration.md)** - MQTT broker setup and configuration
- **[OPC UA Gateway](docs/OPC_UA_Gateway.md)** - OPC UA to MQTT gateway implementation

## 📊 Project Status

This is a complete edge AI security system for industrial IoT environments, fully implemented and tested.

**✅ Complete Implementation:**
- ✅ **MQTT Broker** - Mosquitto with authentication and ACLs
- ✅ **Mock OPC UA Server** - Simulates industrial equipment data
- ✅ **OPC UA to MQTT Gateway** - Real-time data translation pipeline
- ✅ **Anomaly Detector** - Rolling z-score analysis with 120s windows
- ✅ **AI Explainer** - Local LLM (TinyLlama) for risk explanation
- ✅ **Policy Engine** - Automated isolate/throttle/unblock actions
- ✅ **Streamlit Dashboard** - Real-time monitoring and control UI
- ✅ **Containerized Services** - Podman-based deployment
- ✅ **Comprehensive Testing** - Automated test suite with anomaly injection
- ✅ **LLM Server** - Local TinyLlama-1.1B model for explanations

**🔄 Live Data Flow:**
```
OPC UA Server → Gateway → MQTT Broker → Anomaly Detection → AI Explanation → Policy Actions → Dashboard
```

**🎯 Key Features:**
- **Real-time Anomaly Detection**: Z-score analysis with configurable thresholds
- **AI-Powered Explanations**: Local LLM explains security risks in plain language
- **Automated Response**: Policy engine enforces security actions
- **Live Dashboard**: Streamlit UI for monitoring and control
- **Edge-Optimized**: Runs entirely on Raspberry Pi 5

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