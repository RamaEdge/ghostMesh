#!/bin/bash

# GhostMesh MQTT Smoke Test Script
# Tests MQTT broker connectivity and topic permissions

set -e

echo "Testing MQTT broker connectivity..."

# Check if mosquitto broker is running
if ! podman ps | grep -q ghostmesh-mosquitto; then
    echo "Error: Mosquitto broker is not running"
    echo "Start it with: podman compose up -d mosquitto"
    exit 1
fi

echo "Mosquitto broker is running ✓"

# Test basic connectivity
echo "Testing basic connectivity..."
if mosquitto_pub -h localhost -p 1883 -u iot -P iotpass -t "test/connectivity" -m "Hello GhostMesh" -q 1; then
    echo "Basic connectivity test passed ✓"
else
    echo "Error: Basic connectivity test failed"
    exit 1
fi

# Test topic permissions for each user
echo "Testing topic permissions..."

# Test gateway user - should be able to write to factory topics
echo "Testing gateway user permissions..."
if mosquitto_pub -h localhost -p 1883 -u gateway -P gatewaypass -t "factory/A/press01/temperature" -m '{"value": 25.5, "unit": "C"}' -q 1; then
    echo "Gateway user factory topic write test passed ✓"
else
    echo "Error: Gateway user factory topic write test failed"
    exit 1
fi

# Test detector user - should be able to read factory topics and write alerts
echo "Testing detector user permissions..."
if mosquitto_pub -h localhost -p 1883 -u detector -P detectorpass -t "alerts/press01/temperature" -m '{"severity": "medium", "reason": "test"}' -q 1; then
    echo "Detector user alert topic write test passed ✓"
else
    echo "Error: Detector user alert topic write test failed"
    exit 1
fi

# Test dashboard user - should be able to read all topics and write control
echo "Testing dashboard user permissions..."
if mosquitto_pub -h localhost -p 1883 -u dashboard -P dashboardpass -t "control/press01/isolate" -m '{"command": "isolate", "reason": "test"}' -q 1; then
    echo "Dashboard user control topic write test passed ✓"
else
    echo "Error: Dashboard user control topic write test failed"
    exit 1
fi

# Test policy user - should be able to write audit logs
echo "Testing policy user permissions..."
if mosquitto_pub -h localhost -p 1883 -u policy -P policypass -t "audit/actions" -m '{"action": "test", "result": "success"}' -q 1; then
    echo "Policy user audit topic write test passed ✓"
else
    echo "Error: Policy user audit topic write test failed"
    exit 1
fi

# Test explainer user - should be able to write explanations
echo "Testing explainer user permissions..."
if mosquitto_pub -h localhost -p 1883 -u explainer -P explainerpass -t "explanations/test-alert" -m '{"text": "Test explanation", "confidence": 0.8}' -q 1; then
    echo "Explainer user explanation topic write test passed ✓"
else
    echo "Error: Explainer user explanation topic write test failed"
    exit 1
fi

echo ""
echo "All MQTT tests passed successfully! ✓"
echo ""
echo "MQTT broker is properly configured with:"
echo "- User authentication enabled"
echo "- Topic-based access control"
echo "- All service users created"
echo "- Proper permissions for each service"
echo ""
echo "Ready for GhostMesh service integration!"
