#!/usr/bin/env python3
"""
GhostMesh Anomaly Injector Service

A containerized service that periodically injects synthetic anomalies
into the GhostMesh system for continuous testing of the anomaly detection system.

Features:
- Periodic anomaly injection every 60 seconds
- Multiple anomaly types (spike, flood, drift)
- Random asset and signal selection
- Comprehensive logging
- Graceful shutdown handling
"""

import json
import time
import random
import signal
import sys
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional
import paho.mqtt.client as mqtt
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AnomalyInjectorService:
    """Containerized anomaly injector service with periodic injection."""
    
    def __init__(self, mqtt_host: str = "mosquitto", mqtt_port: int = 1883,
                 mqtt_username: str = "iot", mqtt_password: str = "iotpass",
                 injection_interval: int = 60):
        """Initialize the anomaly injector service."""
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.injection_interval = injection_interval
        
        # MQTT client setup
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(mqtt_username, mqtt_password)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        
        # Service state
        self.running = False
        self.injection_thread = None
        self.stats = {
            'injections': 0,
            'spike_injections': 0,
            'flood_injections': 0,
            'drift_injections': 0,
            'start_time': None
        }
        
        # Available assets and signals for injection
        self.assets = [
            {'line': 'A', 'asset': 'press01', 'signals': ['temperature', 'pressure', 'vibration']},
            {'line': 'A', 'asset': 'press02', 'signals': ['temperature', 'pressure', 'vibration']},
            {'line': 'B', 'asset': 'conveyor01', 'signals': ['speed', 'load']},
        ]
        
        # Anomaly types with their configurations
        self.anomaly_types = [
            {
                'name': 'spike',
                'description': 'Sudden value spike',
                'multiplier_range': (3.0, 6.0),
                'duration': 5
            },
            {
                'name': 'flood',
                'description': 'Rapid successive changes',
                'multiplier_range': (1.5, 3.0),
                'duration': 10
            },
            {
                'name': 'drift',
                'description': 'Gradual value drift',
                'multiplier_range': (0.1, 0.3),
                'duration': 30
            }
        ]
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection."""
        if rc == 0:
            logger.info(f"✅ Connected to MQTT broker at {self.mqtt_host}:{self.mqtt_port}")
        else:
            logger.error(f"❌ Failed to connect to MQTT broker. Code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection."""
        if rc != 0:
            logger.warning(f"⚠️ Unexpected MQTT disconnection. Code: {rc}")
        else:
            logger.info("📤 Disconnected from MQTT broker")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            logger.info(f"🔌 Connecting to MQTT broker at {self.mqtt_host}:{self.mqtt_port}")
            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            time.sleep(1)  # Give time for connection
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        try:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("📤 Disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"❌ Error disconnecting from MQTT broker: {e}")
    
    def _generate_normal_value(self, signal: str) -> float:
        """Generate a normal value for the given signal."""
        base_values = {
            'temperature': 30.0,
            'pressure': 5.0,
            'vibration': 2.0,
            'speed': 8.0,
            'load': 80.0
        }
        base = base_values.get(signal, 50.0)
        return base + random.uniform(-0.5, 0.5)
    
    def _publish_telemetry(self, line: str, asset: str, signal: str, value: float):
        """Publish telemetry data to MQTT."""
        topic = f"factory/{line}/{asset}/{signal}"
        payload = {
            "assetId": asset,
            "line": line,
            "signal": signal,
            "value": value,
            "unit": self._get_unit(signal),
            "ts": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            self.mqtt_client.publish(topic, json.dumps(payload), qos=1)
            logger.debug(f"📤 Published {signal}={value} to {topic}")
        except Exception as e:
            logger.error(f"❌ Failed to publish to {topic}: {e}")
    
    def _get_unit(self, signal: str) -> str:
        """Get unit for signal."""
        units = {
            'temperature': 'C',
            'pressure': 'bar',
            'vibration': 'mm/s',
            'speed': 'm/min',
            'load': 'kg'
        }
        return units.get(signal, '')
    
    def inject_spike_anomaly(self, line: str, asset: str, signal: str, multiplier: float = 4.0):
        """Inject a spike anomaly."""
        logger.info(f"⚡ Injecting spike anomaly: {line}/{asset}/{signal} (multiplier: {multiplier})")
        
        # Generate normal value
        normal_value = self._generate_normal_value(signal)
        spike_value = normal_value * multiplier
        
        # Publish spike value
        self._publish_telemetry(line, asset, signal, spike_value)
        
        # Wait a bit, then return to normal
        time.sleep(2)
        self._publish_telemetry(line, asset, signal, normal_value)
        
        self.stats['spike_injections'] += 1
    
    def inject_flood_anomaly(self, line: str, asset: str, signal: str, multiplier: float = 2.0):
        """Inject a flood anomaly (rapid changes)."""
        logger.info(f"🌊 Injecting flood anomaly: {line}/{asset}/{signal} (multiplier: {multiplier})")
        
        normal_value = self._generate_normal_value(signal)
        
        # Generate rapid changes
        for i in range(5):
            flood_value = normal_value * (multiplier + random.uniform(-0.5, 0.5))
            self._publish_telemetry(line, asset, signal, flood_value)
            time.sleep(0.5)
        
        # Return to normal
        self._publish_telemetry(line, asset, signal, normal_value)
        self.stats['flood_injections'] += 1
    
    def inject_drift_anomaly(self, line: str, asset: str, signal: str, drift_rate: float = 0.2):
        """Inject a drift anomaly (gradual change)."""
        logger.info(f"📈 Injecting drift anomaly: {line}/{asset}/{signal} (drift: {drift_rate})")
        
        normal_value = self._generate_normal_value(signal)
        current_value = normal_value
        
        # Gradual drift
        for i in range(10):
            current_value += normal_value * drift_rate * random.uniform(-1, 1)
            self._publish_telemetry(line, asset, signal, current_value)
            time.sleep(1)
        
        # Return to normal
        self._publish_telemetry(line, asset, signal, normal_value)
        self.stats['drift_injections'] += 1
    
    def _injection_worker(self):
        """Worker thread for periodic anomaly injection."""
        logger.info(f"🚀 Starting periodic anomaly injection (every {self.injection_interval}s)")
        self.stats['start_time'] = datetime.now()
        
        while self.running:
            try:
                # Select random asset and signal
                asset_config = random.choice(self.assets)
                signal = random.choice(asset_config['signals'])
                
                # Select random anomaly type
                anomaly_type = random.choice(self.anomaly_types)
                
                # Generate anomaly parameters
                if anomaly_type['name'] == 'spike':
                    multiplier = random.uniform(*anomaly_type['multiplier_range'])
                    self.inject_spike_anomaly(asset_config['line'], asset_config['asset'], signal, multiplier)
                elif anomaly_type['name'] == 'flood':
                    multiplier = random.uniform(*anomaly_type['multiplier_range'])
                    self.inject_flood_anomaly(asset_config['line'], asset_config['asset'], signal, multiplier)
                elif anomaly_type['name'] == 'drift':
                    drift_rate = random.uniform(*anomaly_type['multiplier_range'])
                    self.inject_drift_anomaly(asset_config['line'], asset_config['asset'], signal, drift_rate)
                
                self.stats['injections'] += 1
                
                # Log statistics
                uptime = datetime.now() - self.stats['start_time']
                logger.info(f"📊 Injection #{self.stats['injections']} completed. "
                           f"Uptime: {uptime}. "
                           f"Stats: {self.stats['spike_injections']} spikes, "
                           f"{self.stats['flood_injections']} floods, "
                           f"{self.stats['drift_injections']} drifts")
                
                # Wait for next injection
                time.sleep(self.injection_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in injection worker: {e}")
                time.sleep(5)  # Wait before retrying
    
    def start(self):
        """Start the anomaly injector service."""
        if self.running:
            logger.warning("⚠️ Service is already running")
            return
        
        if not self.connect():
            logger.error("❌ Failed to connect to MQTT broker, cannot start service")
            return
        
        self.running = True
        self.injection_thread = threading.Thread(target=self._injection_worker, daemon=True)
        self.injection_thread.start()
        
        logger.info("🎯 Anomaly injector service started successfully")
    
    def stop(self):
        """Stop the anomaly injector service."""
        if not self.running:
            return
        
        logger.info("🛑 Stopping anomaly injector service...")
        self.running = False
        
        if self.injection_thread and self.injection_thread.is_alive():
            self.injection_thread.join(timeout=5)
        
        self.disconnect()
        
        # Log final statistics
        if self.stats['start_time']:
            uptime = datetime.now() - self.stats['start_time']
            logger.info(f"📊 Final statistics - Uptime: {uptime}, "
                       f"Total injections: {self.stats['injections']}, "
                       f"Spikes: {self.stats['spike_injections']}, "
                       f"Floods: {self.stats['flood_injections']}, "
                       f"Drifts: {self.stats['drift_injections']}")
        
        logger.info("✅ Anomaly injector service stopped")
    
    def run(self):
        """Run the service (blocking)."""
        try:
            self.start()
            
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Received keyboard interrupt")
        finally:
            self.stop()

def main():
    """Main entry point."""
    logger.info("🚀 Starting GhostMesh Anomaly Injector Service")
    
    # Get configuration from environment variables
    mqtt_host = os.getenv('MQTT_HOST', 'mosquitto')
    mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
    mqtt_username = os.getenv('MQTT_USERNAME', 'iot')
    mqtt_password = os.getenv('MQTT_PASSWORD', 'iotpass')
    injection_interval = int(os.getenv('INJECTION_INTERVAL', '60'))
    
    logger.info(f"📋 Configuration: MQTT={mqtt_host}:{mqtt_port}, "
               f"User={mqtt_username}, Interval={injection_interval}s")
    
    # Create and run the service
    service = AnomalyInjectorService(
        mqtt_host=mqtt_host,
        mqtt_port=mqtt_port,
        mqtt_username=mqtt_username,
        mqtt_password=mqtt_password,
        injection_interval=injection_interval
    )
    
    service.run()

if __name__ == "__main__":
    import os
    main()
