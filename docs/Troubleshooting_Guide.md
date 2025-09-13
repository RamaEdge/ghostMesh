# GhostMesh Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the GhostMesh edge AI security system.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Service-Specific Issues](#service-specific-issues)
- [Common Error Messages](#common-error-messages)
- [Performance Issues](#performance-issues)
- [Network Issues](#network-issues)
- [Resource Issues](#resource-issues)
- [Configuration Issues](#configuration-issues)
- [Recovery Procedures](#recovery-procedures)

## Quick Diagnostics

### System Health Check

```bash
# Check all service status
make status

# Check service logs
make logs

# Check resource usage
docker stats

# Check network connectivity
docker network ls
```

### Service-Specific Health Checks

```bash
# MQTT Broker
docker exec ghostmesh-mosquitto mosquitto_pub -h localhost -t test -m "healthcheck" -u iot -P iotpass

# LLM Server
curl -f http://localhost:8080/health

# Dashboard
curl -f http://localhost:8501/health
```

## Service-Specific Issues

### MQTT Broker (Mosquitto)

**Issue: Service won't start**
```bash
# Check configuration
docker logs ghostmesh-mosquitto

# Common causes:
# - Port 1883 already in use
# - Invalid configuration file
# - Missing password file
```

**Solutions:**
1. Check if port 1883 is available: `netstat -tulpn | grep 1883`
2. Validate configuration: `mosquitto -c mosquitto/mosquitto.conf -v`
3. Recreate password file: `make setup-mqtt-users`

**Issue: Authentication failures**
```bash
# Check password file
docker exec ghostmesh-mosquitto cat /mosquitto/config/passwd

# Test authentication
docker exec ghostmesh-mosquitto mosquitto_pub -h localhost -t test -m "test" -u iot -P iotpass
```

**Solutions:**
1. Recreate password file: `make setup-mqtt-users`
2. Check ACL permissions: `cat mosquitto/acl.conf`
3. Verify username/password in service environment variables

### LLM Server

**Issue: Model loading fails**
```bash
# Check model file
docker exec ghostmesh-llm-server ls -la /models/

# Check server logs
docker logs ghostmesh-llm-server
```

**Solutions:**
1. Verify model file exists and is valid
2. Check available disk space: `df -h`
3. Rebuild container: `docker-compose build llm-server`
4. Check memory availability: `free -h`

**Issue: Server responds slowly**
```bash
# Check resource usage
docker stats ghostmesh-llm-server

# Check server logs for errors
docker logs ghostmesh-llm-server
```

**Solutions:**
1. Increase memory allocation
2. Reduce context size in configuration
3. Check for memory leaks
4. Restart service: `docker-compose restart llm-server`

### OPC UA Gateway

**Issue: No data flowing**
```bash
# Check gateway logs
docker logs ghostmesh-gateway

# Check MQTT topics
docker exec ghostmesh-mosquitto mosquitto_sub -h localhost -u gateway -P gatewaypass -t "factory/+/+/+" -C 5
```

**Solutions:**
1. Verify OPC UA server is running
2. Check mapping configuration: `cat opcua2mqtt/mapping.yaml`
3. Verify MQTT connection
4. Check network connectivity to OPC UA server

**Issue: Connection to OPC UA server fails**
```bash
# Test OPC UA connectivity
docker exec ghostmesh-gateway python -c "import asyncio; from asyncua import Client; print('OPC UA client available')"
```

**Solutions:**
1. Check OPC UA server endpoint
2. Verify network connectivity
3. Check firewall settings
4. Validate OPC UA server configuration

### Anomaly Detector

**Issue: No anomalies detected**
```bash
# Check detector logs
docker logs ghostmesh-detector

# Check data flow
docker exec ghostmesh-mosquitto mosquitto_sub -h localhost -u iot -P iotpass -t "factory/+/+/+" -C 10
```

**Solutions:**
1. Verify data is flowing to MQTT
2. Check anomaly threshold settings
3. Ensure sufficient data for analysis
4. Check detector configuration

**Issue: Too many false positives**
```bash
# Check detector configuration
docker exec ghostmesh-detector env | grep ANOMALY
```

**Solutions:**
1. Increase anomaly threshold
2. Adjust window size
3. Check data quality
4. Review detection algorithm

### AI Explainer

**Issue: No explanations generated**
```bash
# Check explainer logs
docker logs ghostmesh-explainer

# Check LLM server connectivity
docker exec ghostmesh-explainer curl -f http://llm-server:8080/health
```

**Solutions:**
1. Verify LLM server is running
2. Check explanation timeout settings
3. Verify alert data format
4. Check MQTT topic subscriptions

**Issue: Explanations are poor quality**
```bash
# Check LLM server logs
docker logs ghostmesh-llm-server

# Test LLM directly
curl -X POST http://localhost:8080/completion -H "Content-Type: application/json" -d '{"prompt": "Test prompt", "max_tokens": 50}'
```

**Solutions:**
1. Check model quality
2. Adjust prompt templates
3. Increase context window
4. Verify input data quality

### Policy Engine

**Issue: Actions not executing**
```bash
# Check policy engine logs
docker logs ghostmesh-policy

# Check policy configuration
docker exec ghostmesh-policy env | grep POLICY
```

**Solutions:**
1. Verify policy mode is set correctly
2. Check action timeout settings
3. Verify MQTT permissions
4. Check action implementation

### Dashboard

**Issue: Dashboard won't load**
```bash
# Check dashboard logs
docker logs ghostmesh-dashboard

# Check port availability
netstat -tulpn | grep 8501
```

**Solutions:**
1. Check if port 8501 is available
2. Verify MQTT connection
3. Check dashboard configuration
4. Restart service: `docker-compose restart dashboard`

**Issue: No data displayed**
```bash
# Check MQTT connection
docker exec ghostmesh-dashboard python -c "import paho.mqtt.client as mqtt; print('MQTT client available')"
```

**Solutions:**
1. Verify MQTT broker is running
2. Check MQTT credentials
3. Verify topic subscriptions
4. Check data flow

## Common Error Messages

### Docker/Podman Errors

**"Port already in use"**
```bash
# Find process using port
sudo netstat -tulpn | grep :1883
sudo lsof -i :1883

# Kill process or change port
sudo kill -9 <PID>
```

**"Container name already in use"**
```bash
# Remove existing container
docker rm -f ghostmesh-mosquitto

# Or use different name
docker-compose up --force-recreate
```

**"Image not found"**
```bash
# Rebuild images
docker-compose build

# Or pull from registry
docker-compose pull
```

### MQTT Errors

**"Connection refused"**
- Check if MQTT broker is running
- Verify port 1883 is accessible
- Check firewall settings

**"Authentication failed"**
- Verify username/password
- Check password file
- Recreate password file

**"Topic not allowed"**
- Check ACL configuration
- Verify user permissions
- Update ACL file

### LLM Server Errors

**"Model file not found"**
- Check model file path
- Verify model download
- Check disk space

**"Out of memory"**
- Increase container memory limit
- Reduce model size
- Check system memory

**"Server not responding"**
- Check server logs
- Verify port 8080
- Restart service

## Performance Issues

### High CPU Usage

**Diagnosis:**
```bash
# Check CPU usage
docker stats
htop
```

**Solutions:**
1. Increase CPU limits
2. Optimize service configuration
3. Reduce logging verbosity
4. Scale services horizontally

### High Memory Usage

**Diagnosis:**
```bash
# Check memory usage
docker stats
free -h
```

**Solutions:**
1. Increase memory limits
2. Optimize model size
3. Reduce context windows
4. Enable memory monitoring

### Slow Response Times

**Diagnosis:**
```bash
# Check service response times
time curl -f http://localhost:8080/health
time curl -f http://localhost:8501/health
```

**Solutions:**
1. Optimize service configuration
2. Increase resource limits
3. Check network latency
4. Optimize database queries

## Network Issues

### Service Communication

**Issue: Services can't communicate**
```bash
# Check network
docker network ls
docker network inspect ghostmesh_ghostmesh-network
```

**Solutions:**
1. Verify network configuration
2. Check service names
3. Verify port mappings
4. Check firewall settings

### External Connectivity

**Issue: Can't access from outside**
```bash
# Check port mappings
docker-compose ps
netstat -tulpn | grep :8501
```

**Solutions:**
1. Verify port mappings
2. Check firewall rules
3. Configure reverse proxy
4. Use VPN for secure access

## Resource Issues

### Disk Space

**Issue: Out of disk space**
```bash
# Check disk usage
df -h
docker system df
```

**Solutions:**
1. Clean up unused images: `docker system prune`
2. Remove old logs
3. Increase disk space
4. Use external storage

### Memory

**Issue: Out of memory**
```bash
# Check memory usage
free -h
docker stats
```

**Solutions:**
1. Increase system memory
2. Optimize service memory usage
3. Use swap space
4. Scale services

## Configuration Issues

### Invalid Configuration

**Issue: Service won't start due to config**
```bash
# Validate configuration
docker-compose config
```

**Solutions:**
1. Check YAML syntax
2. Verify environment variables
3. Check file permissions
4. Validate configuration files

### Missing Files

**Issue: Configuration files not found**
```bash
# Check file existence
ls -la mosquitto/
ls -la opcua2mqtt/
```

**Solutions:**
1. Verify file paths
2. Check file permissions
3. Recreate missing files
4. Run setup scripts

## Recovery Procedures

### Complete System Reset

```bash
# Stop all services
make stop

# Clean up containers and images
make clean

# Rebuild everything
make build

# Restart services
make start
```

### Service-Specific Recovery

```bash
# Restart specific service
docker-compose restart <service-name>

# Rebuild specific service
docker-compose build <service-name>

# Remove and recreate service
docker-compose rm -f <service-name>
docker-compose up -d <service-name>
```

### Data Recovery

```bash
# Backup volumes
docker run --rm -v ghostmesh_mosquitto_data:/data -v $(pwd):/backup alpine tar czf /backup/mosquitto_data.tar.gz -C /data .

# Restore volumes
docker run --rm -v ghostmesh_mosquitto_data:/data -v $(pwd):/backup alpine tar xzf /backup/mosquitto_data.tar.gz -C /data
```

## Getting Help

### Log Collection

```bash
# Collect all logs
make logs > ghostmesh_logs.txt 2>&1

# Collect system information
docker system info > docker_info.txt
docker-compose config > compose_config.txt
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG
make dev
```

### Community Support

- Check GitHub issues
- Review documentation
- Join community discussions
- Submit bug reports

## Prevention

### Regular Maintenance

1. Monitor resource usage
2. Update dependencies regularly
3. Backup configurations
4. Test recovery procedures
5. Monitor logs for issues

### Best Practices

1. Use production profiles for deployment
2. Enable health checks
3. Configure monitoring
4. Set up alerting
5. Regular testing
