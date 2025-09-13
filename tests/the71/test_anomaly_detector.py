#!/usr/bin/env python3
"""
Simple test script to verify anomaly detector is working
"""

import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

def test_anomaly_detector():
    """Test anomaly detector with proper float values."""
    
    # Connect to MQTT
    client = mqtt.Client()
    client.username_pw_set('iot', 'iotpass')
    client.connect('localhost', 1883, 60)
    
    print("✅ Connected to MQTT broker")
    
    # Create test telemetry with proper float values
    telemetry_data = {
        "assetId": "test-asset",
        "line": "test-line", 
        "signal": "temperature",
        "value": 150.0,  # Explicitly float
        "unit": "°C",
        "ts": datetime.now(timezone.utc).isoformat(),
        "quality": "good",
        "source": "test",
        "seq": 1
    }
    
    # Publish test telemetry
    topic = "factory/test-line/test-asset/temperature"
    client.publish(topic, json.dumps(telemetry_data), qos=1)
    print(f"📤 Published test telemetry: {telemetry_data['value']}°C")
    
    # Wait a moment
    time.sleep(2)
    
    client.disconnect()
    print("✅ Test completed")

if __name__ == "__main__":
    test_anomaly_detector()
