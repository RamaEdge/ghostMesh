#!/bin/bash

# GhostMesh MQTT User Setup Script
# Creates password file with proper hashes for all service users

set -e

echo "Setting up MQTT users for GhostMesh..."

# Create mosquitto directory if it doesn't exist
mkdir -p mosquitto

# Remove existing password file
rm -f mosquitto/passwd

# Create password file with all users
echo "Creating password file..."

# Create users with their passwords using podman
podman run --rm -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -c -b /mosquitto/config/passwd iot iotpass
podman run --rm -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -b /mosquitto/config/passwd gateway gatewaypass
podman run --rm -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -b /mosquitto/config/passwd detector detectorpass
podman run --rm -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -b /mosquitto/config/passwd explainer explainerpass
podman run --rm -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -b /mosquitto/config/passwd policy policypass
podman run --rm -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -b /mosquitto/config/passwd dashboard dashboardpass

echo "MQTT users created successfully!"
echo ""
echo "Users created:"
echo "- iot (password: iotpass)"
echo "- gateway (password: gatewaypass)"
echo "- detector (password: detectorpass)"
echo "- explainer (password: explainerpass)"
echo "- policy (password: policypass)"
echo "- dashboard (password: dashboardpass)"
echo ""
echo "Password file location: mosquitto/passwd"
echo "ACL file location: mosquitto/acl.conf"
echo ""
echo "To test MQTT connectivity, run: ./scripts/test-mqtt.sh"
