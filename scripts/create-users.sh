#!/bin/bash

# Create MQTT users one by one
echo "Creating MQTT users..."

# Remove existing password file
rm -f mosquitto/passwd

# Create users one by one
echo "iot" | podman run --rm -i -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -c /mosquitto/config/passwd iot
echo "gatewaypass" | podman run --rm -i -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -b /mosquitto/config/passwd gateway gatewaypass
echo "detectorpass" | podman run --rm -i -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -b /mosquitto/config/passwd detector detectorpass
echo "explainerpass" | podman run --rm -i -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -b /mosquitto/config/passwd explainer explainerpass
echo "policypass" | podman run --rm -i -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -b /mosquitto/config/passwd policy policypass
echo "dashboardpass" | podman run --rm -i -v $(pwd)/mosquitto:/mosquitto/config eclipse-mosquitto:2 mosquitto_passwd -b /mosquitto/config/passwd dashboard dashboardpass

echo "All users created successfully!"
cat mosquitto/passwd

