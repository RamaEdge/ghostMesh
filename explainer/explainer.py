#!/usr/bin/env python3
"""
GhostMesh AI Explainer Service
LLM-Powered Alert Explanation Generation

This service processes security alerts from the anomaly detector and generates
intelligent, context-aware explanations using local LLM integration via llama.cpp.

Features:
- Real-time alert processing from MQTT
- LLM-powered explanation generation
- Multiple prompt templates for different user types
- Confidence scoring and risk assessment
- Graceful fallback when LLM is unavailable
- Integration with GhostMesh dashboard
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

import paho.mqtt.client as mqtt

from llm_service import LLMService, LLMConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIExplainer:
    """AI Explainer service for generating intelligent alert explanations using LLM."""
    
    def __init__(self):
        self.mqtt_client = None
        self.running = False
        
        # MQTT configuration
        self.mqtt_host = os.getenv('MQTT_HOST', 'mosquitto')
        self.mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
        self.mqtt_username = os.getenv('MQTT_USERNAME', 'explainer')
        self.mqtt_password = os.getenv('MQTT_PASSWORD', 'explainerpass')
        self.mqtt_qos = int(os.getenv('MQTT_QOS', '1'))
        
        # LLM configuration
        self.llm_server_url = os.getenv('LLM_SERVER_URL', 'http://localhost:8080')
        self.default_user_type = os.getenv('DEFAULT_USER_TYPE', 'hybrid')
        self.explanation_timeout = int(os.getenv('EXPLANATION_TIMEOUT', '5'))
        
        # Initialize LLM service
        llm_config = LLMConfig(
            server_url=self.llm_server_url,
            timeout=self.explanation_timeout
        )
        self.llm_service = LLMService(llm_config)
        
        # Processing statistics
        self.stats = {
            'alerts_processed': 0,
            'explanations_generated': 0,
            'llm_explanations': 0,
            'fallback_explanations': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
        logger.info(f"Initialized AI Explainer with MQTT: {self.mqtt_host}:{self.mqtt_port}")
        logger.info(f"LLM Service Available: {self.llm_service.is_available()}")
        logger.info(f"Available Templates: {self.llm_service.get_available_templates()}")
    
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
        """Process an alert and generate an explanation using LLM."""
        try:
            self.stats['alerts_processed'] += 1
            
            # Extract alert information
            alert_id = alert_data.get('alertId', f"alert-{uuid.uuid4().hex[:8]}")
            asset_id = alert_data.get('assetId', 'unknown')
            signal = alert_data.get('signal', 'unknown')
            severity = alert_data.get('severity', 'unknown')
            
            logger.info(f"Processing alert {alert_id} for {asset_id} - {signal} ({severity})")
            
            # Generate explanation using LLM
            explanation = self._generate_llm_explanation(alert_data)
            
            # Publish explanation
            self._publish_explanation(alert_id, explanation)
            
            self.stats['explanations_generated'] += 1
            
            # Update statistics based on explanation source
            if explanation.get('source') == 'llm':
                self.stats['llm_explanations'] += 1
            else:
                self.stats['fallback_explanations'] += 1
            
        except Exception as e:
            logger.error(f"Error processing alert {alert_data.get('alertId', 'unknown')}: {e}")
            self.stats['errors'] += 1
    
    def _generate_llm_explanation(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation using LLM service."""
        try:
            # Determine user type based on alert severity or use default
            user_type = self._determine_user_type(alert_data)
            
            # Generate explanation using LLM
            explanation = self.llm_service.generate_explanation(alert_data, user_type)
            
            logger.info(f"Generated {explanation.get('source', 'unknown')} explanation for {alert_data.get('alertId', 'unknown')}")
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating LLM explanation: {e}")
            # Return fallback explanation
            return self._generate_fallback_explanation(alert_data)
    
    def _determine_user_type(self, alert_data: Dict[str, Any]) -> str:
        """Determine the appropriate user type for explanation generation."""
        severity = alert_data.get('severity', 'medium').lower()
        signal = alert_data.get('signal', '').lower()
        
        # High severity alerts might need operator-focused explanations
        if severity == 'high':
            return 'operator'
        
        # Technical signals might benefit from analyst explanations
        if signal in ['vibration', 'pressure', 'voltage', 'current']:
            return 'analyst'
        
        # Default to hybrid for balanced explanations
        return self.default_user_type
    
    def _generate_fallback_explanation(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a simple fallback explanation when LLM is not available."""
        alert_id = alert_data.get('alertId', 'unknown')
        asset_id = alert_data.get('assetId', 'unknown')
        signal = alert_data.get('signal', 'unknown')
        severity = alert_data.get('severity', 'medium')
        current_value = alert_data.get('current', 0)
        reason = alert_data.get('reason', 'Anomaly detected')
        
        # Simple fallback explanation
        explanation_text = f"Security alert detected on {asset_id} for {signal} signal. "
        explanation_text += f"Current value is {current_value}, which triggered a {severity} severity alert. "
        explanation_text += f"Reason: {reason}. "
        explanation_text += "Please investigate the anomaly and take appropriate action based on your operational procedures."
        
        return {
            "alertId": alert_id,
            "text": explanation_text,
            "confidence": 0.5,
            "riskLevel": severity.lower(),
            "userType": "fallback",
            "recommendations": [
                "Investigate the anomaly",
                "Check system logs",
                "Verify sensor readings",
                "Follow operational procedures",
                "Monitor for additional alerts"
            ],
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": "fallback"
        }
    
    def _publish_explanation(self, alert_id: str, explanation: Dict[str, Any]) -> None:
        """Publish explanation to MQTT topic."""
        try:
            topic = f"explanations/{alert_id}"
            payload = json.dumps(explanation, indent=2)
            
            result = self.mqtt_client.publish(topic, payload, qos=self.mqtt_qos, retain=True)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published explanation for alert {alert_id} to topic {topic}")
            else:
                logger.error(f"Failed to publish explanation for alert {alert_id}. Code: {result.rc}")
                self.stats['errors'] += 1
                
        except Exception as e:
            logger.error(f"Error publishing explanation for alert {alert_id}: {e}")
            self.stats['errors'] += 1
    
    def start(self):
        """Start the AI Explainer service."""
        try:
            # Initialize MQTT client
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message
            
            # Connect to MQTT broker
            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            
            self.running = True
            logger.info("AI Explainer service started successfully")
            
            # Keep the service running
            while self.running:
                time.sleep(1)
                
                # Log statistics every 60 seconds
                if int(time.time()) % 60 == 0:
                    self._log_statistics()
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            self.stop()
        except Exception as e:
            logger.error(f"Error starting AI Explainer service: {e}")
            self.stop()
    
    def stop(self):
        """Stop the AI Explainer service."""
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        logger.info("AI Explainer service stopped")
        self._log_final_statistics()
    
    def _log_statistics(self):
        """Log current processing statistics."""
        uptime = time.time() - self.stats['start_time']
        alerts_per_minute = (self.stats['alerts_processed'] / uptime) * 60 if uptime > 0 else 0
        
        logger.info(f"Statistics - Alerts: {self.stats['alerts_processed']}, "
                   f"Explanations: {self.stats['explanations_generated']}, "
                   f"LLM: {self.stats['llm_explanations']}, "
                   f"Fallback: {self.stats['fallback_explanations']}, "
                   f"Errors: {self.stats['errors']}, "
                   f"Rate: {alerts_per_minute:.1f}/min")
    
    def _log_final_statistics(self):
        """Log final statistics when service stops."""
        uptime = time.time() - self.stats['start_time']
        
        logger.info("=== Final Statistics ===")
        logger.info(f"Uptime: {uptime:.1f} seconds")
        logger.info(f"Alerts Processed: {self.stats['alerts_processed']}")
        logger.info(f"Explanations Generated: {self.stats['explanations_generated']}")
        logger.info(f"LLM Explanations: {self.stats['llm_explanations']}")
        logger.info(f"Fallback Explanations: {self.stats['fallback_explanations']}")
        logger.info(f"Errors: {self.stats['errors']}")
        
        if self.stats['alerts_processed'] > 0:
            llm_percentage = (self.stats['llm_explanations'] / self.stats['alerts_processed']) * 100
            logger.info(f"LLM Success Rate: {llm_percentage:.1f}%")


def main():
    """Main function to run the AI Explainer service."""
    explainer = AIExplainer()
    explainer.start()


if __name__ == "__main__":
    main()