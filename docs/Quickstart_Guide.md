# GhostMesh Quickstart Guide

**Get GhostMesh running in 5 minutes**

This guide will help you quickly set up and run the GhostMesh edge AI security copilot on your system.

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for initial setup

### Required Software
- **Podman** (recommended) or Docker
- **Podman Compose** or Docker Compose
- **Git** for cloning the repository

### Installation Commands

**macOS (using Homebrew):**
```bash
brew install podman podman-compose git
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install podman podman-compose git
```

**CentOS/RHEL/Fedora:**
```bash
sudo dnf install podman podman-compose git
```

## Quick Setup (3 Commands)

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd ghostmesh
```

### 2. Start All Services
```bash
make quick-start
```

This command will:
- Set up MQTT users and permissions
- Build all container images
- Start the mock OPC UA server
- Start the MQTT broker
- Start the OPC UA to MQTT gateway
- Start the anomaly detector
- Start the policy engine
- Start the Streamlit dashboard
- Verify all services are running

### 3. Verify Installation
```bash
make test
```

### Quick Commands (Shortcuts)
```bash
make quick-start    # Setup and start all services
make quick-test     # Start services and run tests
make quick-restart  # Stop and start all services
make dev            # Start development environment
```

## What's Running

After successful setup, you'll have these services running:

| Service | Port | Description |
|---------|------|-------------|
| **Mock OPC UA Server** | 4840 | Simulates industrial equipment data |
| **MQTT Broker** | 1883 | Message broker with authentication |
| **OPC UA Gateway** | - | Converts OPC UA data to MQTT telemetry |
| **Anomaly Detector** | - | Rolling z-score anomaly detection |
| **Policy Engine** | - | Enforces security actions and audit logging |
| **Streamlit Dashboard** | 8501 | Real-time monitoring and control interface |

## Verify Data Flow

### Check Service Status
```bash
make status
```

Expected output:
```
CONTAINER ID  IMAGE                                  COMMAND               CREATED        STATUS                  PORTS                   NAMES                 
d3d32c7c3fc3  localhost/ghostmesh_mock-opcua:latest  python simple_moc...  2 minutes ago  Up 2 minutes            0.0.0.0:4840->4840/tcp  ghostmesh-mock-opcua  
e39bea302c75  docker.io/library/eclipse-mosquitto:2  /usr/sbin/mosquit...  2 minutes ago  Up 2 minutes (healthy)  0.0.0.0:1883->1883/tcp  ghostmesh-mosquitto   
8de273ccb349  localhost/ghostmesh_opcua2mqtt:latest  python opcua2mqtt...  2 minutes ago  Up 2 minutes                                    ghostmesh-gateway     
```

### View Live Telemetry Data
```bash
# Subscribe to all telemetry topics
timeout 10s podman exec ghostmesh-mosquitto mosquitto_sub -h localhost -u gateway -P gatewaypass -t "factory/+/+/+" -C 5 -W 5
```

Expected output:
```json
{"assetId":"press01","line":"A","signal":"temperature","value":33.66,"unit":"C","ts":"2025-09-13T10:25:52.797652+00:00","quality":"Good","source":"opcua","seq":347}
{"assetId":"press01","line":"A","signal":"pressure","value":14.87,"unit":"bar","ts":"2025-09-13T10:25:52.800687+00:00","quality":"Good","source":"opcua","seq":347}
{"assetId":"press01","line":"A","signal":"vibration","value":6.32,"unit":"mm/s","ts":"2025-09-13T10:25:52.803504+00:00","quality":"Good","source":"opcua","seq":347}
```

### View Service Logs
```bash
# View all logs
make logs

# View specific service logs
make logs-gateway
make logs-mock-opcua
make logs-mqtt
```

## Available MQTT Topics

The system publishes data to these topic patterns:

### Telemetry Topics
- `factory/A/press01/temperature` - Press01 temperature data
- `factory/A/press01/pressure` - Press01 pressure data
- `factory/A/press01/vibration` - Press01 vibration data
- `factory/A/press01/status` - Press01 operational status
- `factory/A/press02/*` - Press02 equipment data
- `factory/B/conveyor01/*` - Conveyor01 equipment data

### State Topics
- `state/press01` - Press01 asset state (retained)
- `state/press02` - Press02 asset state (retained)
- `state/conveyor01` - Conveyor01 asset state (retained)

## Common Commands

### Service Management
```bash
make start          # Start all services
make stop           # Stop all services
make restart        # Restart all services
make status         # Check service status
```

### Development
```bash
make build          # Build all containers
make test           # Run all tests
make test-mqtt      # Test MQTT connectivity
make test-gateway   # Test gateway functionality
make dev            # Start development environment
```

### Debugging
```bash
make logs           # View all service logs
```

### Information
```bash
make info           # Show project information
make help           # Show all available commands
```

### Cleanup
```bash
make clean          # Stop services and remove containers
```

### Setup
```bash
make setup          # Initial project setup
```

## All Available Commands

For a complete list of all available commands, run:
```bash
make help
```

This will show all 18 available targets:

| Command | Description |
|---------|-------------|
| `make help` | Show this help message |
| `make setup` | Initial project setup |
| `make build` | Build all container images |
| `make start` | Start all services |
| `make stop` | Stop all services |
| `make restart` | Restart all services |
| `make status` | Show service status |
| `make logs` | Show logs for all services |
| `make test` | Run all tests |
| `make test-mqtt` | Test MQTT broker connectivity |
| `make test-gateway` | Test OPC UA gateway |
| `make clean` | Clean up containers and images |
| `make quick-start` | Quick start: setup and start all services |
| `make quick-test` | Quick test: start services and run tests |
| `make quick-restart` | Quick restart: stop and start all services |
| `make dev` | Start development environment |
| `make info` | Show project information |

## Troubleshooting

### Services Not Starting
```bash
# Check if Podman is running
podman --version

# Check service status
make status

# View error logs
make logs
```

### No Telemetry Data
```bash
# Check gateway connection
make logs-gateway

# Verify OPC UA server
make logs-mock-opcua

# Test MQTT connectivity
make test-mqtt
```

### Permission Issues
```bash
# Rebuild containers
make build

# Restart services
make restart

# Or use quick restart
make quick-restart
```

### Port Conflicts
If ports 4840 or 1883 are already in use:
```bash
# Stop conflicting services
sudo lsof -i :4840
sudo lsof -i :1883

# Or modify ports in docker-compose.yml
```

## Next Steps

Once you have GhostMesh running:

1. **Explore the Data**: Use MQTT clients to subscribe to telemetry topics
2. **Monitor Logs**: Watch the real-time data flow in service logs
3. **Customize Configuration**: Modify `opcua2mqtt/mapping.yaml` for different equipment
4. **Develop Extensions**: Build anomaly detection or policy engines
5. **Deploy to Production**: Use the same setup on Raspberry Pi or edge devices

## Getting Help

### Makefile Help
```bash
make help          # Show all 18 available Makefile targets
make info          # Show project information
```

See the "All Available Commands" section above for the complete list of all 18 targets.

### Documentation
- **Documentation**: See [Project README](Project_README.md) for detailed documentation
- **Architecture**: Review [Architecture Guide](Architecture.md) for system design
- **Issues**: Check service logs with `make logs` for error details
- **Support**: Create an issue in the project repository

### Validation
```bash
make test          # Run all tests
make quick-test    # Start services and run tests
```

## Advanced Configuration

### Custom OPC UA Server
To connect to a real OPC UA server instead of the mock server:

1. Update `opcua2mqtt/mapping.yaml`:
```yaml
opcua:
  endpoint: "opc.tcp://your-server:4840"
  username: "your-username"
  password: "your-password"
```

2. Update node mappings to match your server's node IDs
3. Rebuild and restart:
```bash
make build-gateway
make restart
```

### MQTT Authentication
The system uses these default credentials:
- **Gateway User**: `gateway` / `gatewaypass`
- **Dashboard User**: `dashboard` / `dashboardpass`
- **Detector User**: `detector` / `detectorpass`

To change credentials, update `mosquitto/passwd` and restart services.

### Hugging Face Authentication (for LLM Server)

To download models from Hugging Face, you need to set up authentication:

1. **Get your token** from [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. **Set up authentication**:
   ```bash
   make setup-hf-auth
   ```
3. **Edit the token file** and add your actual token:
   ```bash
   # Edit llm-server/.hf_token and replace 'your_huggingface_token_here' with your actual token
   nano llm-server/.hf_token
   ```
4. **Build the LLM server**:
   ```bash
   make build-llm-server
   ```

**Model**: We use **TinyLlama-1.1B-Chat-v1.0** (~637MB) - optimized for Raspberry Pi with excellent performance for chat/instruct tasks.

**Note**: The `.hf_token` file is automatically excluded from git commits for security.

---

**Congratulations!** You now have GhostMesh running with real-time industrial data flowing from OPC UA to MQTT. The foundation is ready for anomaly detection, AI explanation, and policy enforcement features.
