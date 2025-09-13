"""
GhostMesh Anomaly Detector
Rolling Z-Score Anomaly Detection Service

This service implements rolling z-score anomaly detection with:
- 120-second sliding window
- Severity thresholds (medium: z≥4, high: z≥8)
- Debounce logic (30 seconds)
- MQTT integration for telemetry and alerts
"""

import asyncio
import json
import logging
import os
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import paho.mqtt.client as mqtt
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RollingZScoreDetector:
    """Rolling z-score anomaly detector with debounce logic."""
    
    def __init__(self, window_size: int = 120, debounce_seconds: int = 30):
        """
        Initialize the detector.
        
        Args:
            window_size: Size of the rolling window in seconds
            debounce_seconds: Minimum time between alerts for the same asset/signal
        """
        self.window_size = window_size
        self.debounce_seconds = debounce_seconds
        
        # Data storage: {asset_signal: deque of (timestamp, value)}
        self.data_windows: Dict[str, deque] = {}
        
        # Debounce tracking: {asset_signal: last_alert_time}
        self.last_alert_times: Dict[str, float] = {}
        
        # Severity thresholds
        self.thresholds = {
            'medium': 4.0,
            'high': 8.0
        }
        
        logger.info(f"Initialized detector with {window_size}s window, {debounce_seconds}s debounce")
    
    def add_data_point(self, asset_id: str, signal: str, value: float, timestamp: float) -> Optional[Dict]:
        """
        Add a data point and check for anomalies.
        
        Args:
            asset_id: Asset identifier
            signal: Signal name
            value: Signal value
            timestamp: Unix timestamp
            
        Returns:
            Alert dictionary if anomaly detected, None otherwise
        """
        key = f"{asset_id}_{signal}"
        current_time = time.time()
        
        # Initialize window if needed
        if key not in self.data_windows:
            self.data_windows[key] = deque()
        
        # Add new data point
        self.data_windows[key].append((timestamp, value))
        
        # Remove old data points (older than window_size seconds)
        cutoff_time = timestamp - self.window_size
        while (self.data_windows[key] and 
               self.data_windows[key][0][0] < cutoff_time):
            self.data_windows[key].popleft()
        
        # Need at least 10 data points for reliable statistics
        if len(self.data_windows[key]) < 10:
            logger.debug(f"Insufficient data for {key}: {len(self.data_windows[key])} points")
            return None
        
        # Calculate z-score
        values = [point[1] for point in self.data_windows[key]]
        z_score = self._calculate_z_score(values, value)
        
        if z_score is None:
            logger.debug(f"Could not calculate z-score for {key}")
            return None
        
        # Check for anomaly
        severity = self._get_severity(z_score)
        if severity is None:
            return None
        
        # Check debounce
        if self._is_debounced(key, current_time):
            logger.debug(f"Alert for {key} debounced (z={z_score:.2f})")
            return None
        
        # Generate alert
        alert = self._create_alert(asset_id, signal, value, z_score, severity, values)
        
        # Update debounce tracking
        self.last_alert_times[key] = current_time
        
        logger.info(f"Anomaly detected: {key} z={z_score:.2f} severity={severity}")
        return alert
    
    def _calculate_z_score(self, values: List[float], current_value: float) -> Optional[float]:
        """Calculate z-score for current value against historical data."""
        try:
            if len(values) < 2:
                return None
            
            mean = np.mean(values)
            std = np.std(values, ddof=1)  # Sample standard deviation
            
            # Handle zero variance
            if std == 0:
                return None
            
            z_score = abs((current_value - mean) / std)
            return z_score
            
        except Exception as e:
            logger.error(f"Error calculating z-score: {e}")
            return None
    
    def _get_severity(self, z_score: float) -> Optional[str]:
        """Determine severity based on z-score thresholds."""
        if z_score >= self.thresholds['high']:
            return 'high'
        elif z_score >= self.thresholds['medium']:
            return 'medium'
        else:
            return None
    
    def _is_debounced(self, key: str, current_time: float) -> bool:
        """Check if alert is within debounce period."""
        if key not in self.last_alert_times:
            return False
        
        time_since_last = current_time - self.last_alert_times[key]
        return time_since_last < self.debounce_seconds
    
    def _create_alert(self, asset_id: str, signal: str, current_value: float, 
                     z_score: float, severity: str, values: List[float]) -> Dict:
        """Create alert dictionary following the architecture schema."""
        # Calculate statistics for reason
        mean = np.mean(values)
        std = np.std(values, ddof=1)
        
        alert = {
            "alertId": f"a-{uuid.uuid4().hex[:8]}",
            "assetId": asset_id,
            "signal": signal,
            "severity": severity,
            "reason": f"z-score {z_score:.1f} vs mean {mean:.1f}±{std:.1f} ({self.window_size}s)",
            "current": current_value,
            "ts": datetime.now(timezone.utc).isoformat()
        }
        
        return alert

class AnomalyDetectorService:
    """Main anomaly detector service with MQTT integration."""
    
    def __init__(self):
        self.detector = RollingZScoreDetector()
        self.mqtt_client = None
        self.running = False
        
        # MQTT configuration
        self.mqtt_host = os.getenv('MQTT_HOST', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
        self.mqtt_username = os.getenv('MQTT_USERNAME', 'iot')
        self.mqtt_password = os.getenv('MQTT_PASSWORD', 'iotpass')
        self.mqtt_qos = int(os.getenv('MQTT_QOS', '1'))
        
        logger.info(f"Initialized service with MQTT: {self.mqtt_host}:{self.mqtt_port}")
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to telemetry topics
            client.subscribe("factory/+/+/+", qos=self.mqtt_qos)
            logger.info("Subscribed to factory/+/+/+ topics")
        else:
            logger.error(f"Failed to connect to MQTT broker. Code: {rc}")
    
    def on_message(self, client, userdata, msg):
        """MQTT message callback."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Parse topic: factory/<line>/<asset>/<signal>
            topic_parts = topic.split('/')
            if len(topic_parts) != 4 or topic_parts[0] != 'factory':
                return
            
            line, asset_id, signal = topic_parts[1], topic_parts[2], topic_parts[3]
            
            # Extract value and timestamp
            value = payload.get('value')
            timestamp = payload.get('ts')
            
            if value is None or timestamp is None:
                logger.warning(f"Missing value or timestamp in {topic}")
                return
            
            # Convert timestamp to float
            try:
                if isinstance(timestamp, str):
                    # Parse ISO format timestamp
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp_float = dt.timestamp()
                else:
                    timestamp_float = float(timestamp)
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid timestamp format in {topic}: {e}")
                return
            
            # Check for anomaly
            alert = self.detector.add_data_point(asset_id, signal, value, timestamp_float)
            
            if alert:
                # Publish alert
                alert_topic = f"alerts/{asset_id}/{signal}"
                alert_payload = json.dumps(alert)
                
                client.publish(alert_topic, alert_payload, qos=self.mqtt_qos, retain=True)
                logger.info(f"Published alert to {alert_topic}: {alert['alertId']}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from {msg.topic}: {e}")
        except Exception as e:
            logger.error(f"Error processing message from {msg.topic}: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback."""
        logger.warning(f"Disconnected from MQTT broker. Code: {rc}")
    
    def start(self):
        """Start the anomaly detector service."""
        logger.info("Starting anomaly detector service...")
        
        # Create MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        
        try:
            # Connect to MQTT broker
            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.running = True
            
            # Start MQTT loop
            self.mqtt_client.loop_start()
            
            logger.info("Anomaly detector service started successfully")
            
            # Keep running
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Error starting service: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the anomaly detector service."""
        logger.info("Stopping anomaly detector service...")
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        logger.info("Anomaly detector service stopped")

def main():
    """Main entry point."""
    service = AnomalyDetectorService()
    service.start()

if __name__ == "__main__":
    main()
