#!/usr/bin/env python3
"""
GhostMesh AI Explainer Service
Intelligent Alert Explanation Generation

This service processes security alerts from the anomaly detector and generates
human-readable explanations of potential security risks, helping operators
understand and respond to threats effectively.

Features:
- Real-time alert processing from MQTT
- Context-aware explanation generation
- Confidence scoring and risk assessment
- Integration with GhostMesh dashboard
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIExplainer:
    """AI Explainer service for generating alert explanations."""
    
    def __init__(self):
        self.mqtt_client = None
        self.running = False
        
        # MQTT configuration
        self.mqtt_host = os.getenv('MQTT_HOST', 'mosquitto')
        self.mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
        self.mqtt_username = os.getenv('MQTT_USERNAME', 'explainer')
        self.mqtt_password = os.getenv('MQTT_PASSWORD', 'explainerpass')
        self.mqtt_qos = int(os.getenv('MQTT_QOS', '1'))
        
        # Explanation configuration
        self.explanation_timeout = int(os.getenv('EXPLANATION_TIMEOUT', '5'))
        
        # Processing statistics
        self.stats = {
            'alerts_processed': 0,
            'explanations_generated': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
        logger.info(f"Initialized AI Explainer with MQTT: {self.mqtt_host}:{self.mqtt_port}")
    
    def on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection events."""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            client.subscribe("alerts/#", qos=self.mqtt_qos)
            logger.info("Subscribed to alerts/# topics")
        else:
            logger.error(f"Failed to connect to MQTT broker. Code: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            if topic.startswith("alerts/"):
                self._process_alert(topic, payload)
            
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from topic {msg.topic}: {msg.payload.decode()}")
            self.stats['errors'] += 1
        except Exception as e:
            logger.error(f"Error processing MQTT message on topic {msg.topic}: {e}")
            self.stats['errors'] += 1
    
    def _process_alert(self, topic: str, alert_data: Dict) -> None:
        """Process an alert and generate an explanation."""
        try:
            self.stats['alerts_processed'] += 1
            
            # Extract alert information
            alert_id = alert_data.get('alertId', f"alert-{uuid.uuid4().hex[:8]}")
            asset_id = alert_data.get('assetId', 'unknown')
            signal = alert_data.get('signal', 'unknown')
            severity = alert_data.get('severity', 'unknown')
            current_value = alert_data.get('current', 0)
            reason = alert_data.get('reason', 'Anomaly detected')
            
            logger.info(f"Processing alert {alert_id} for {asset_id} - {signal} ({severity})")
            
            # Generate explanation
            explanation = self._generate_explanation(
                alert_id, asset_id, signal, severity, current_value, reason
            )
            
            # Publish explanation
            self._publish_explanation(alert_id, explanation)
            
            self.stats['explanations_generated'] += 1
            
        except Exception as e:
            logger.error(f"Error processing alert {alert_data.get('alertId', 'unknown')}: {e}")
            self.stats['errors'] += 1
    
    def _generate_explanation(self, alert_id: str, asset_id: str, signal: str, 
                            severity: str, current_value: float, reason: str) -> Dict:
        """Generate an intelligent explanation for an alert."""
        
        # Base explanation components
        explanation_parts = []
        confidence = 0.8  # Base confidence
        risk_level = severity.lower()
        recommended_actions = []
        
        # Asset-specific context
        asset_context = self._get_asset_context(asset_id)
        
        # Signal-specific analysis
        signal_analysis = self._analyze_signal(signal, current_value, severity)
        
        # Build explanation text
        explanation_parts.append(f"{signal_analysis['description']} detected on {asset_id}")
        
        if asset_context:
            explanation_parts.append(f"({asset_context})")
        
        explanation_parts.append(signal_analysis['impact'])
        
        if signal_analysis['immediate_concern']:
            explanation_parts.append(signal_analysis['immediate_concern'])
        
        # Generate recommendations
        recommended_actions = signal_analysis['recommendations']
        
        # Adjust confidence based on signal type and severity
        confidence = self._calculate_confidence(signal, severity, current_value)
        
        # Combine explanation
        explanation_text = ". ".join(explanation_parts) + "."
        
        return {
            "alertId": alert_id,
            "text": explanation_text,
            "confidence": round(confidence, 2),
            "riskLevel": risk_level,
            "recommendedActions": recommended_actions,
            "ts": datetime.now(timezone.utc).isoformat()
        }
    
    def _get_asset_context(self, asset_id: str) -> str:
        """Get contextual information about an asset."""
        asset_contexts = {
            "Press01": "hydraulic press",
            "Press02": "hydraulic press", 
            "Conveyor01": "conveyor belt system",
            "Valve03": "control valve",
            "Sensor05": "environmental sensor"
        }
        return asset_contexts.get(asset_id, "industrial equipment")
    
    def _analyze_signal(self, signal: str, value: float, severity: str) -> Dict:
        """Analyze a signal and provide context-specific information."""
        
        signal_analyses = {
            "Temperature": {
                "description": f"Temperature anomaly ({value}°C)",
                "impact": "This could indicate overheating, cooling system failure, or thermal stress",
                "immediate_concern": "Immediate inspection of cooling systems and equipment status is recommended",
                "recommendations": ["inspect_equipment", "check_cooling_system", "monitor_temperature"]
            },
            "Pressure": {
                "description": f"Pressure anomaly ({value} bar)",
                "impact": "This could indicate system pressure issues, leaks, or valve malfunctions",
                "immediate_concern": "Check for leaks, valve positions, and system integrity",
                "recommendations": ["check_for_leaks", "inspect_valves", "verify_system_pressure"]
            },
            "Speed": {
                "description": f"Speed anomaly ({value} rpm)",
                "impact": "This could indicate motor issues, mechanical problems, or control system faults",
                "immediate_concern": "Inspect motor operation and mechanical components",
                "recommendations": ["inspect_motor", "check_mechanical_components", "verify_control_signals"]
            },
            "Vibration": {
                "description": f"Vibration anomaly ({value} mm/s)",
                "impact": "This could indicate mechanical wear, misalignment, or bearing failure",
                "immediate_concern": "Immediate mechanical inspection is recommended to prevent equipment damage",
                "recommendations": ["inspect_bearings", "check_alignment", "monitor_vibration_trends"]
            }
        }
        
        return signal_analyses.get(signal, {
            "description": f"{signal} anomaly ({value})",
            "impact": "This could indicate equipment malfunction or system issues",
            "immediate_concern": "Investigate the root cause of this anomaly",
            "recommendations": ["investigate_anomaly", "check_equipment_status", "monitor_trends"]
        })
    
    def _calculate_confidence(self, signal: str, severity: str, value: float) -> float:
        """Calculate confidence score for the explanation."""
        base_confidence = 0.8
        
        # Adjust based on signal type (some signals are more predictable)
        signal_confidence = {
            "Temperature": 0.9,
            "Pressure": 0.85,
            "Speed": 0.8,
            "Vibration": 0.75
        }
        
        # Adjust based on severity
        severity_confidence = {
            "low": 0.7,
            "medium": 0.8,
            "high": 0.9
        }
        
        confidence = base_confidence
        confidence *= signal_confidence.get(signal, 0.8)
        confidence *= severity_confidence.get(severity.lower(), 0.8)
        
        # Ensure confidence is within valid range
        return max(0.5, min(1.0, confidence))
    
    def _publish_explanation(self, alert_id: str, explanation: Dict) -> None:
        """Publish explanation to MQTT."""
        try:
            topic = f"explanations/{alert_id}"
            payload = json.dumps(explanation)
            
            self.mqtt_client.publish(topic, payload, qos=self.mqtt_qos, retain=True)
            logger.info(f"Published explanation for alert {alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish explanation for alert {alert_id}: {e}")
            self.stats['errors'] += 1
    
    def on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection events."""
        logger.warning(f"Disconnected from MQTT broker. Code: {rc}")
    
    def get_stats(self) -> Dict:
        """Get service statistics."""
        uptime = time.time() - self.stats['start_time']
        return {
            **self.stats,
            'uptime_seconds': round(uptime, 2),
            'alerts_per_minute': round(self.stats['alerts_processed'] / (uptime / 60), 2) if uptime > 0 else 0
        }
    
    def start(self):
        """Start the AI Explainer service."""
        logger.info("Starting AI Explainer service...")
        
        # Create MQTT client
        self.mqtt_client = mqtt.Client()
        # self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        
        try:
            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.running = True
            self.mqtt_client.loop_start()
            logger.info("AI Explainer service started successfully")
            
            # Main service loop
            while self.running:
                time.sleep(1)
                
                # Log statistics every 60 seconds
                if int(time.time()) % 60 == 0:
                    stats = self.get_stats()
                    logger.info(f"Service stats: {stats}")
                    
        except Exception as e:
            logger.error(f"Error starting service: {e}")
            self.running = False
        finally:
            self.stop()
    
    def stop(self):
        """Stop the AI Explainer service."""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("AI Explainer service stopped.")


if __name__ == "__main__":
    service = AIExplainer()
    service.start()
