#!/usr/bin/env python3
"""
Extended test script to verify anomaly detector is working with multiple data points
"""

import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

def test_anomaly_detector_extended():
    """Test anomaly detector with multiple data points to build up the data window."""
    
    # Connect to MQTT
    client = mqtt.Client()
    client.username_pw_set('iot', 'iotpass')
    client.connect('localhost', 1883, 60)
    
    print("✅ Connected to MQTT broker")
    
    # Create test telemetry with multiple data points
    base_value = 25.0
    topic = "factory/test-line/test-asset/temperature"
    
    # Send 15 data points to build up the data window (need at least 10)
    for i in range(15):
        telemetry_data = {
            "assetId": "test-asset",
            "line": "test-line", 
            "signal": "temperature",
            "value": base_value + (i * 0.5),  # Gradually increasing values
            "unit": "°C",
            "ts": datetime.now(timezone.utc).isoformat(),
            "quality": "good",
            "source": "test",
            "seq": i + 1
        }
        
        client.publish(topic, json.dumps(telemetry_data), qos=1)
        print(f"📤 Published data point {i+1}: {telemetry_data['value']}°C")
        time.sleep(0.5)  # Small delay between data points
    
    # Now send a high value that should trigger an alert
    high_value = 150.0
    telemetry_data = {
        "assetId": "test-asset",
        "line": "test-line", 
        "signal": "temperature",
        "value": high_value,
        "unit": "°C",
        "ts": datetime.now(timezone.utc).isoformat(),
        "quality": "good",
        "source": "test",
        "seq": 16
    }
    
    client.publish(topic, json.dumps(telemetry_data), qos=1)
    print(f"📤 Published high value: {high_value}°C (should trigger alert)")
    
    # Wait a moment for processing
    time.sleep(3)
    
    client.disconnect()
    print("✅ Extended test completed")

if __name__ == "__main__":
    test_anomaly_detector_extended()
