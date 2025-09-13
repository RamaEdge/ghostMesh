#!/usr/bin/env python3
"""
THE-66: Anomaly Injection and Alert Validation Testing

This module provides synthetic anomaly injection capabilities for testing
the GhostMesh anomaly detection and alert system.

Anomaly Types:
- Spike: Sudden value increase/decrease
- Flood: Rapid successive value changes
- Drift: Gradual value change over time
"""

import json
import time
import random
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable
import paho.mqtt.client as mqtt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyInjector:
    """Injects synthetic anomalies into the GhostMesh system for testing."""
    
    def __init__(self, mqtt_host: str = "localhost", mqtt_port: int = 1883,
                 mqtt_username: str = "iot", mqtt_password: str = "iotpass"):
        """Initialize the anomaly injector with MQTT connection."""
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        
        # MQTT client setup
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(mqtt_username, mqtt_password)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        
        # Test state tracking
        self.injection_active = False
        self.injection_thread = None
        self.alert_timestamps = {}
        self.latency_measurements = []
        
        # Asset configurations for testing
        self.test_assets = {
            "press01": {
                "line": "A",
                "signals": {
                    "temperature": {"base": 35.0, "range": 5.0, "unit": "C"},
                    "pressure": {"base": 150.0, "range": 20.0, "unit": "bar"},
                    "speed": {"base": 1200.0, "range": 100.0, "unit": "rpm"},
                    "vibration": {"base": 2.5, "range": 0.5, "unit": "mm/s"}
                }
            },
            "press02": {
                "line": "A", 
                "signals": {
                    "temperature": {"base": 32.0, "range": 4.0, "unit": "C"},
                    "pressure": {"base": 145.0, "range": 15.0, "unit": "bar"},
                    "speed": {"base": 1180.0, "range": 80.0, "unit": "rpm"},
                    "vibration": {"base": 2.2, "range": 0.4, "unit": "mm/s"}
                }
            },
            "conveyor01": {
                "line": "B",
                "signals": {
                    "temperature": {"base": 28.0, "range": 3.0, "unit": "C"},
                    "speed": {"base": 50.0, "range": 5.0, "unit": "m/min"},
                    "vibration": {"base": 1.8, "range": 0.3, "unit": "mm/s"}
                }
            }
        }
    
    def _on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection."""
        if rc == 0:
            logger.info("Anomaly injector connected to MQTT broker")
            # Subscribe to alert topics to measure latency
            client.subscribe("alerts/+/+")
            client.message_callback_add("alerts/+/+", self._on_alert_received)
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection."""
        logger.info("Anomaly injector disconnected from MQTT broker")
    
    def _on_alert_received(self, client, userdata, message):
        """Handle received alerts to measure latency."""
        try:
            alert_data = json.loads(message.payload.decode())
            alert_id = alert_data.get("alertId")
            asset_id = alert_data.get("assetId")
            signal = alert_data.get("signal")
            
            if alert_id in self.alert_timestamps:
                injection_time = self.alert_timestamps[alert_id]
                detection_time = time.time()
                latency = detection_time - injection_time
                
                self.latency_measurements.append({
                    "alert_id": alert_id,
                    "asset_id": asset_id,
                    "signal": signal,
                    "latency_seconds": latency,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                logger.info(f"Alert latency: {latency:.3f}s for {asset_id}/{signal}")
                
                # Remove from tracking
                del self.alert_timestamps[alert_id]
                
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
    
    def connect(self):
        """Connect to MQTT broker."""
        try:
            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            time.sleep(1)  # Allow connection to establish
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
    
    def _generate_normal_value(self, asset_id: str, signal: str) -> float:
        """Generate a normal value for the given asset and signal."""
        if asset_id not in self.test_assets:
            return 0.0
        
        signal_config = self.test_assets[asset_id]["signals"].get(signal)
        if not signal_config:
            return 0.0
        
        base = signal_config["base"]
        range_val = signal_config["range"]
        
        # Add some normal variation
        variation = random.uniform(-range_val/4, range_val/4)
        return base + variation
    
    def _publish_telemetry(self, asset_id: str, signal: str, value: float, 
                          unit: str, sequence: int = None):
        """Publish telemetry data to MQTT."""
        if asset_id not in self.test_assets:
            return
        
        line = self.test_assets[asset_id]["line"]
        topic = f"factory/{line}/{asset_id}/{signal}"
        
        telemetry = {
            "assetId": asset_id,
            "line": line,
            "signal": signal,
            "value": round(value, 2),
            "unit": unit,
            "ts": datetime.now(timezone.utc).isoformat(),
            "quality": "Good",
            "source": "anomaly_injector",
            "seq": sequence or int(time.time() * 1000) % 10000
        }
        
        self.mqtt_client.publish(topic, json.dumps(telemetry), qos=1, retain=False)
    
    def inject_spike_anomaly(self, asset_id: str, signal: str, 
                           spike_multiplier: float = 3.0, duration_seconds: int = 5):
        """Inject a spike anomaly (sudden value increase/decrease)."""
        if asset_id not in self.test_assets or signal not in self.test_assets[asset_id]["signals"]:
            logger.error(f"Invalid asset/signal: {asset_id}/{signal}")
            return
        
        signal_config = self.test_assets[asset_id]["signals"][signal]
        base_value = signal_config["base"]
        unit = signal_config["unit"]
        
        # Generate unique alert ID for latency tracking
        alert_id = f"spike_{asset_id}_{signal}_{int(time.time())}"
        
        logger.info(f"Injecting spike anomaly: {asset_id}/{signal} (multiplier: {spike_multiplier})")
        
        # Record injection time for latency measurement
        self.alert_timestamps[alert_id] = time.time()
        
        # Inject spike value
        spike_value = base_value * spike_multiplier
        self._publish_telemetry(asset_id, signal, spike_value, unit)
        
        # Wait for detection
        time.sleep(duration_seconds)
        
        # Return to normal
        normal_value = self._generate_normal_value(asset_id, signal)
        self._publish_telemetry(asset_id, signal, normal_value, unit)
        
        return alert_id
    
    def inject_flood_anomaly(self, asset_id: str, signal: str, 
                           flood_count: int = 10, interval_seconds: float = 0.1):
        """Inject a flood anomaly (rapid successive value changes)."""
        if asset_id not in self.test_assets or signal not in self.test_assets[asset_id]["signals"]:
            logger.error(f"Invalid asset/signal: {asset_id}/{signal}")
            return
        
        signal_config = self.test_assets[asset_id]["signals"][signal]
        base_value = signal_config["base"]
        range_val = signal_config["range"]
        unit = signal_config["unit"]
        
        # Generate unique alert ID for latency tracking
        alert_id = f"flood_{asset_id}_{signal}_{int(time.time())}"
        
        logger.info(f"Injecting flood anomaly: {asset_id}/{signal} ({flood_count} rapid changes)")
        
        # Record injection time for latency measurement
        self.alert_timestamps[alert_id] = time.time()
        
        # Inject rapid value changes
        for i in range(flood_count):
            # Vary the anomaly intensity
            anomaly_factor = 2.0 + (i * 0.5)  # Increasing intensity
            flood_value = base_value + (range_val * anomaly_factor)
            
            self._publish_telemetry(asset_id, signal, flood_value, unit)
            time.sleep(interval_seconds)
        
        # Return to normal
        normal_value = self._generate_normal_value(asset_id, signal)
        self._publish_telemetry(asset_id, signal, normal_value, unit)
        
        return alert_id
    
    def inject_drift_anomaly(self, asset_id: str, signal: str, 
                           drift_rate: float = 0.1, duration_seconds: int = 30):
        """Inject a drift anomaly (gradual value change over time)."""
        if asset_id not in self.test_assets or signal not in self.test_assets[asset_id]["signals"]:
            logger.error(f"Invalid asset/signal: {asset_id}/{signal}")
            return
        
        signal_config = self.test_assets[asset_id]["signals"][signal]
        base_value = signal_config["base"]
        range_val = signal_config["range"]
        unit = signal_config["unit"]
        
        # Generate unique alert ID for latency tracking
        alert_id = f"drift_{asset_id}_{signal}_{int(time.time())}"
        
        logger.info(f"Injecting drift anomaly: {asset_id}/{signal} (rate: {drift_rate}/s)")
        
        # Record injection time for latency measurement
        self.alert_timestamps[alert_id] = time.time()
        
        # Inject gradual drift
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            elapsed = time.time() - start_time
            drift_value = base_value + (range_val * drift_rate * elapsed)
            
            self._publish_telemetry(asset_id, signal, drift_value, unit)
            time.sleep(1.0)  # 1Hz update rate
        
        # Return to normal
        normal_value = self._generate_normal_value(asset_id, signal)
        self._publish_telemetry(asset_id, signal, normal_value, unit)
        
        return alert_id
    
    def run_comprehensive_test(self, test_duration_minutes: int = 5):
        """Run a comprehensive test with multiple anomaly types."""
        logger.info(f"Starting comprehensive anomaly injection test ({test_duration_minutes} minutes)")
        
        start_time = time.time()
        test_count = 0
        
        while time.time() - start_time < (test_duration_minutes * 60):
            # Select random asset and signal
            asset_id = random.choice(list(self.test_assets.keys()))
            signal = random.choice(list(self.test_assets[asset_id]["signals"].keys()))
            
            # Select random anomaly type
            anomaly_type = random.choice(["spike", "flood", "drift"])
            
            try:
                if anomaly_type == "spike":
                    self.inject_spike_anomaly(asset_id, signal, 
                                            spike_multiplier=random.uniform(2.0, 4.0))
                elif anomaly_type == "flood":
                    self.inject_flood_anomaly(asset_id, signal,
                                            flood_count=random.randint(5, 15))
                elif anomaly_type == "drift":
                    self.inject_drift_anomaly(asset_id, signal,
                                            drift_rate=random.uniform(0.05, 0.2),
                                            duration_seconds=random.randint(10, 30))
                
                test_count += 1
                logger.info(f"Completed test #{test_count}: {anomaly_type} on {asset_id}/{signal}")
                
                # Wait between tests
                time.sleep(random.uniform(5, 15))
                
            except Exception as e:
                logger.error(f"Test failed: {e}")
        
        logger.info(f"Comprehensive test completed: {test_count} anomalies injected")
        return test_count
    
    def get_latency_statistics(self) -> Dict:
        """Get latency measurement statistics."""
        if not self.latency_measurements:
            return {"count": 0, "message": "No latency measurements available"}
        
        latencies = [m["latency_seconds"] for m in self.latency_measurements]
        
        return {
            "count": len(latencies),
            "min_latency": min(latencies),
            "max_latency": max(latencies),
            "avg_latency": sum(latencies) / len(latencies),
            "measurements": self.latency_measurements
        }
    
    def clear_measurements(self):
        """Clear all latency measurements."""
        self.latency_measurements.clear()
        self.alert_timestamps.clear()


def main():
    """Main function for testing the anomaly injector."""
    injector = AnomalyInjector()
    
    if not injector.connect():
        logger.error("Failed to connect to MQTT broker")
        return
    
    try:
        # Test individual anomaly types
        logger.info("Testing spike anomaly...")
        injector.inject_spike_anomaly("press01", "temperature", spike_multiplier=3.0)
        time.sleep(5)
        
        logger.info("Testing flood anomaly...")
        injector.inject_flood_anomaly("press02", "pressure", flood_count=8)
        time.sleep(5)
        
        logger.info("Testing drift anomaly...")
        injector.inject_drift_anomaly("conveyor01", "speed", drift_rate=0.15, duration_seconds=20)
        time.sleep(5)
        
        # Print latency statistics
        stats = injector.get_latency_statistics()
        logger.info(f"Latency Statistics: {stats}")
        
    finally:
        injector.disconnect()


if __name__ == "__main__":
    main()
