"""
GhostMesh Policy Engine
Policy Enforcement and Audit Logging Service

This service implements policy enforcement for security actions:
- Subscribes to alerts and control command topics
- Implements app-layer blocking mechanism
- Creates comprehensive audit trail
- Handles isolate, throttle, and unblock commands
"""

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PolicyEngine:
    """Policy engine for enforcing security actions and audit logging."""
    
    def __init__(self):
        self.mqtt_client = None
        self.running = False
        
        # MQTT configuration
        self.mqtt_host = os.getenv('MQTT_HOST', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
        self.mqtt_username = os.getenv('MQTT_USERNAME', 'iot')
        self.mqtt_password = os.getenv('MQTT_PASSWORD', 'iotpass')
        self.mqtt_qos = int(os.getenv('MQTT_QOS', '1'))
        
        # Policy state tracking
        self.blocked_assets: Set[str] = set()
        self.throttled_assets: Set[str] = set()
        self.audit_log: List[Dict] = []
        
        # Supported commands
        self.supported_commands = {'isolate', 'throttle', 'unblock'}
        
        logger.info(f"Initialized policy engine with MQTT: {self.mqtt_host}:{self.mqtt_port}")
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to required topics
            client.subscribe("alerts/#", qos=self.mqtt_qos)
            client.subscribe("control/#", qos=self.mqtt_qos)
            logger.info("Subscribed to alerts/# and control/# topics")
        else:
            logger.error(f"Failed to connect to MQTT broker. Code: {rc}")
    
    def on_message(self, client, userdata, msg):
        """MQTT message callback."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Route message based on topic
            if topic.startswith("alerts/"):
                self._handle_alert(topic, payload)
            elif topic.startswith("control/"):
                self._handle_control_command(topic, payload)
            else:
                logger.warning(f"Received message on unexpected topic: {topic}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from {msg.topic}: {e}")
        except Exception as e:
            logger.error(f"Error processing message from {msg.topic}: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback."""
        logger.warning(f"Disconnected from MQTT broker. Code: {rc}")
    
    def _handle_alert(self, topic: str, payload: Dict):
        """Handle incoming alert messages."""
        try:
            # Parse topic: alerts/<asset>/<signal>
            topic_parts = topic.split('/')
            if len(topic_parts) != 3 or topic_parts[0] != 'alerts':
                logger.warning(f"Invalid alert topic format: {topic}")
                return
            
            asset_id = topic_parts[1]
            signal = topic_parts[2]
            severity = payload.get('severity')
            alert_id = payload.get('alertId')
            
            logger.info(f"Received alert: {asset_id}/{signal} - {severity} (ID: {alert_id})")
            
            # Auto-policy: High severity alerts trigger automatic isolation
            if severity == 'high':
                logger.info(f"High severity alert detected, auto-isolating {asset_id}")
                self._execute_action(asset_id, 'isolate', 'auto_policy', alert_id)
            
        except Exception as e:
            logger.error(f"Error handling alert: {e}")
    
    def _handle_control_command(self, topic: str, payload: Dict):
        """Handle incoming control command messages."""
        try:
            # Parse topic: control/<asset>/<command>
            topic_parts = topic.split('/')
            if len(topic_parts) != 3 or topic_parts[0] != 'control':
                logger.warning(f"Invalid control topic format: {topic}")
                return
            
            asset_id = topic_parts[1]
            command = topic_parts[2]
            reason = payload.get('reason', 'operator_action')
            ref_alert_id = payload.get('refAlertId')
            
            logger.info(f"Received control command: {asset_id} - {command} (reason: {reason})")
            
            # Validate command
            if command not in self.supported_commands:
                logger.error(f"Unsupported command: {command}")
                self._create_audit_event(asset_id, command, 'validation_error', 'failed', 
                                       f"Unsupported command: {command}")
                return
            
            # Execute the command
            self._execute_action(asset_id, command, reason, ref_alert_id)
            
        except Exception as e:
            logger.error(f"Error handling control command: {e}")
    
    def _execute_action(self, asset_id: str, action: str, reason: str, ref_alert_id: Optional[str] = None):
        """Execute a policy action (isolate, throttle, unblock)."""
        try:
            logger.info(f"Executing action: {action} on {asset_id}")
            
            # Execute the action based on type
            if action == 'isolate':
                result = self._isolate_asset(asset_id)
            elif action == 'throttle':
                result = self._throttle_asset(asset_id)
            elif action == 'unblock':
                result = self._unblock_asset(asset_id)
            else:
                result = 'failed'
                logger.error(f"Unknown action: {action}")
            
            # Create audit event
            self._create_audit_event(asset_id, action, 'app_layer_blocking', result, 
                                   f"Action {action} executed for {asset_id}")
            
            # Log the action
            logger.info(f"Action {action} on {asset_id}: {result}")
            
        except Exception as e:
            logger.error(f"Error executing action {action} on {asset_id}: {e}")
            self._create_audit_event(asset_id, action, 'app_layer_blocking', 'failed', 
                                   f"Error executing action: {str(e)}")
    
    def _isolate_asset(self, asset_id: str) -> str:
        """Isolate an asset (block all traffic)."""
        try:
            # Add to blocked assets set
            self.blocked_assets.add(asset_id)
            
            # Remove from throttled assets if present
            self.throttled_assets.discard(asset_id)
            
            # In a real implementation, this would:
            # 1. Update MQTT broker ACL to deny traffic for this asset
            # 2. Configure nftables rules to drop traffic
            # 3. Update network policies
            
            # For demo purposes, we'll simulate the action
            logger.info(f"Asset {asset_id} isolated - all traffic blocked")
            
            return 'success'
            
        except Exception as e:
            logger.error(f"Failed to isolate asset {asset_id}: {e}")
            return 'failed'
    
    def _throttle_asset(self, asset_id: str) -> str:
        """Throttle an asset (limit traffic rate)."""
        try:
            # Add to throttled assets set
            self.throttled_assets.add(asset_id)
            
            # Remove from blocked assets if present
            self.blocked_assets.discard(asset_id)
            
            # In a real implementation, this would:
            # 1. Configure tc (traffic control) rules
            # 2. Update MQTT broker rate limits
            # 3. Apply bandwidth restrictions
            
            # For demo purposes, we'll simulate the action
            logger.info(f"Asset {asset_id} throttled - traffic rate limited")
            
            return 'success'
            
        except Exception as e:
            logger.error(f"Failed to throttle asset {asset_id}: {e}")
            return 'failed'
    
    def _unblock_asset(self, asset_id: str) -> str:
        """Unblock an asset (restore normal traffic)."""
        try:
            # Remove from both blocked and throttled sets
            self.blocked_assets.discard(asset_id)
            self.throttled_assets.discard(asset_id)
            
            # In a real implementation, this would:
            # 1. Remove nftables rules
            # 2. Remove tc rules
            # 3. Restore MQTT broker ACL permissions
            
            # For demo purposes, we'll simulate the action
            logger.info(f"Asset {asset_id} unblocked - normal traffic restored")
            
            return 'success'
            
        except Exception as e:
            logger.error(f"Failed to unblock asset {asset_id}: {e}")
            return 'failed'
    
    def _create_audit_event(self, asset_id: str, action: str, method: str, 
                          result: str, details: str = ""):
        """Create and publish an audit event."""
        try:
            # Generate unique action ID
            action_id = f"act-{uuid.uuid4().hex[:8]}"
            
            # Create audit event following the architecture schema
            audit_event = {
                "actionId": action_id,
                "assetId": asset_id,
                "action": action,
                "method": method,
                "result": result,
                "ts": datetime.now(timezone.utc).isoformat()
            }
            
            # Add details if provided
            if details:
                audit_event["details"] = details
            
            # Store in local audit log
            self.audit_log.append(audit_event)
            
            # Keep only last 1000 audit events
            if len(self.audit_log) > 1000:
                self.audit_log = self.audit_log[-1000:]
            
            # Publish audit event to MQTT
            if self.mqtt_client:
                audit_topic = "audit/actions"
                audit_payload = json.dumps(audit_event)
                
                self.mqtt_client.publish(audit_topic, audit_payload, qos=self.mqtt_qos, retain=True)
                logger.info(f"Published audit event: {action_id} - {action} on {asset_id}: {result}")
            
        except Exception as e:
            logger.error(f"Error creating audit event: {e}")
    
    def get_policy_status(self) -> Dict:
        """Get current policy status for all assets."""
        return {
            "blocked_assets": list(self.blocked_assets),
            "throttled_assets": list(self.throttled_assets),
            "total_audit_events": len(self.audit_log),
            "supported_commands": list(self.supported_commands)
        }
    
    def start(self):
        """Start the policy engine service."""
        logger.info("Starting policy engine service...")
        
        # Create MQTT client
        self.mqtt_client = mqtt.Client()
        # self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        
        try:
            # Connect to MQTT broker
            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.running = True
            
            # Start MQTT loop
            self.mqtt_client.loop_start()
            
            logger.info("Policy engine service started successfully")
            
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
        """Stop the policy engine service."""
        logger.info("Stopping policy engine service...")
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        logger.info("Policy engine service stopped")

def main():
    """Main entry point."""
    service = PolicyEngine()
    service.start()

if __name__ == "__main__":
    main()
