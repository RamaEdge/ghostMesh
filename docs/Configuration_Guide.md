# GhostMesh Configuration Guide

This guide covers all configuration options, environment variables, and deployment profiles for the GhostMesh edge AI security system.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Deployment Profiles](#deployment-profiles)
- [Service Configuration](#service-configuration)
- [MQTT Configuration](#mqtt-configuration)
- [LLM Configuration](#llm-configuration)
- [Security Configuration](#security-configuration)
- [Performance Tuning](#performance-tuning)

## Environment Variables

### Global Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug logging across all services |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `TZ` | `UTC` | Timezone for all services |

### MQTT Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_HOST` | `mosquitto` | MQTT broker hostname |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `MQTT_USERNAME` | Service-specific | MQTT username for authentication |
| `MQTT_PASSWORD` | Service-specific | MQTT password for authentication |
| `MQTT_QOS` | `1` | Quality of Service level (0, 1, 2) |

### LLM Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `/models/tinyllama-1.1b-chat.gguf` | Path to the LLM model file |
| `LLM_SERVER_URL` | `http://llm-server:8080` | LLM server endpoint URL |
| `DEFAULT_USER_TYPE` | `hybrid` | Default user type for explanations |
| `EXPLANATION_TIMEOUT` | `10` | Timeout for explanation generation (seconds) |

### Anomaly Detection Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANOMALY_THRESHOLD` | `2.5` | Z-score threshold for anomaly detection |
| `WINDOW_SIZE` | `120` | Rolling window size in seconds |
| `MIN_SAMPLES` | `10` | Minimum samples required for analysis |

### Policy Engine Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `POLICY_MODE` | `auto` | Policy enforcement mode (auto, manual, disabled) |
| `ACTION_TIMEOUT` | `30` | Timeout for policy actions (seconds) |
| `MAX_RETRIES` | `3` | Maximum retry attempts for actions |

## Deployment Profiles

### Development Profile

**Usage:**
```bash
make dev
# or
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

**Features:**
- Debug logging enabled
- Hot reload for source code changes
- Additional debug ports exposed
- Development tools container included
- Mock OPC UA server enabled

**Environment Overrides:**
- `DEBUG=true`
- `LOG_LEVEL=DEBUG`
- Source code mounted as volumes
- Debug ports exposed (5678, 5679, 8081, 8502)

### Production Profile

**Usage:**
```bash
make prod
# or
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

**Features:**
- Optimized resource limits
- Structured logging with rotation
- Monitoring service included
- Mock OPC UA server disabled
- Security hardening applied

**Environment Overrides:**
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- Resource limits configured
- Log rotation enabled
- Prometheus monitoring included

## Service Configuration

### MQTT Broker (Mosquitto)

**Configuration File:** `mosquitto/mosquitto.conf`

```ini
# Basic Configuration
listener 1883
allow_anonymous false
password_file /mosquitto/config/passwd
acl_file /mosquitto/config/acl.conf

# Persistence
persistence true
persistence_location /mosquitto/data/
autosave_interval 1800

# Logging
log_dest file /mosquitto/log/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information
```

**Authentication:** `mosquitto/passwd`
- Users: `iot`, `gateway`, `explainer`, `dashboard`, `policy`
- Passwords: Service-specific (see setup scripts)

**Access Control:** `mosquitto/acl.conf`
- Topic-based permissions for each service
- Read/write restrictions by user

### OPC UA Gateway

**Configuration File:** `opcua2mqtt/mapping.yaml`

```yaml
# OPC UA to MQTT mapping configuration
mappings:
  - opcua_node: "ns=2;i=1001"
    mqtt_topic: "factory/lineA/press01/temperature"
    data_type: "float"
    sampling_rate: 1000  # milliseconds
```

**Environment Variables:**
- `OPCUA_ENDPOINT`: OPC UA server endpoint
- `OPCUA_NAMESPACE`: OPC UA namespace
- `MAPPING_FILE`: Path to mapping configuration

### Anomaly Detector

**Configuration:**
- Rolling window: 120 seconds
- Z-score threshold: 2.5
- Minimum samples: 10
- Analysis frequency: 1 second

**MQTT Topics:**
- Subscribe: `factory/+/+/+`
- Publish: `alerts/<asset>/<signal>`

### AI Explainer

**Configuration:**
- Model: TinyLlama-1.1B-Chat
- Context window: 2048 tokens
- Temperature: 0.7
- Max tokens: 150

**User Types:**
- `operator`: Simple, actionable explanations
- `analyst`: Technical, detailed explanations
- `hybrid`: Balanced explanations

### Policy Engine

**Actions:**
- `isolate`: Block all communication
- `throttle`: Reduce data rate
- `unblock`: Restore normal operation

**Configuration:**
- Auto-mode: Automatic action execution
- Manual-mode: Require approval
- Disabled: Log only, no actions

### Dashboard

**Configuration:**
- Port: 8501
- Theme: Dark mode
- Auto-refresh: 5 seconds
- Data retention: 1 hour

## Security Configuration

### MQTT Security

**Authentication:**
- Username/password authentication
- Service-specific credentials
- No anonymous access

**Access Control:**
- Topic-based permissions
- Service isolation
- Read/write restrictions

**Network Security:**
- Internal network only
- No external port exposure
- TLS support (optional)

### Container Security

**Image Security:**
- Multi-stage builds
- No secrets in images
- Minimal base images
- Regular updates

**Runtime Security:**
- Non-root users
- Read-only filesystems
- Resource limits
- Health checks

## Performance Tuning

### Resource Allocation

**Development:**
- No resource limits
- Debug logging enabled
- Hot reload active

**Production:**
- Memory limits per service
- CPU limits per service
- Log rotation configured
- Health checks enabled

### Optimization Settings

**LLM Server:**
- Model quantization
- Context size optimization
- Thread count tuning
- Memory management

**Anomaly Detection:**
- Window size optimization
- Sampling rate adjustment
- Threshold tuning
- Batch processing

**MQTT Broker:**
- Connection limits
- Message size limits
- Persistence optimization
- Log level adjustment

## Troubleshooting

### Common Issues

**Service Startup Failures:**
1. Check resource availability
2. Verify network connectivity
3. Review service logs
4. Validate configuration files

**Performance Issues:**
1. Monitor resource usage
2. Check log levels
3. Optimize configuration
4. Scale resources if needed

**MQTT Connection Issues:**
1. Verify credentials
2. Check network connectivity
3. Review ACL permissions
4. Validate topic names

### Log Analysis

**Service Logs:**
```bash
make logs <service-name>
```

**MQTT Logs:**
```bash
docker logs ghostmesh-mosquitto
```

**System Logs:**
```bash
journalctl -u docker
```

### Health Checks

**Service Status:**
```bash
make status
```

**Health Endpoints:**
- LLM Server: `http://localhost:8080/health`
- Dashboard: `http://localhost:8501/health`
- MQTT: `mosquitto_pub` test command

## Configuration Validation

### Setup Validation

```bash
make validate-setup
```

**Checks:**
- Service dependencies
- Configuration files
- Network connectivity
- Resource availability
- Security settings

### Runtime Validation

```bash
make validate-runtime
```

**Checks:**
- Service health
- Data flow
- Performance metrics
- Error rates
- Resource usage

## Best Practices

### Development

1. Use development profile for local work
2. Enable debug logging for troubleshooting
3. Use hot reload for rapid iteration
4. Test with mock data first
5. Validate configuration changes

### Production

1. Use production profile for deployment
2. Monitor resource usage
3. Enable structured logging
4. Configure health checks
5. Set up monitoring and alerting

### Security

1. Use strong passwords
2. Limit network exposure
3. Regular security updates
4. Monitor access logs
5. Validate configurations

### Performance

1. Monitor resource usage
2. Optimize configuration
3. Use appropriate profiles
4. Scale resources as needed
5. Regular performance testing
