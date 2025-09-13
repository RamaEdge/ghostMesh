#!/usr/bin/env python3
"""
GhostMesh OPC UA to MQTT Gateway
Converts OPC UA node values to MQTT telemetry messages
"""

import asyncio
import json
import logging
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

import yaml
import pydantic
from asyncua import Client, Node, ua
from paho.mqtt.client import Client as MQTTClient, MQTTMessage
import asyncio_mqtt


class NodeMapping(pydantic.BaseModel):
    """OPC UA node mapping configuration"""
    nodeId: str
    topic: str
    unit: str
    data_type: str
    description: str


class OPCUAConfig(pydantic.BaseModel):
    """OPC UA server configuration"""
    endpoint: str
    security_policy: str = "None"
    security_mode: str = "None"
    username: Optional[str] = None
    password: Optional[str] = None
    session_timeout: int = 60000
    connection_timeout: int = 10000
    reconnect_interval: int = 5000


class MQTTConfig(pydantic.BaseModel):
    """MQTT broker configuration"""
    host: str
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    qos: int = 1
    retain_state: bool = True
    keepalive: int = 60
    reconnect_interval: int = 5


class GatewayConfig(pydantic.BaseModel):
    """Complete gateway configuration"""
    opcua: OPCUAConfig
    mqtt: MQTTConfig
    mappings: List[NodeMapping]
    settings: Dict[str, Any] = {}


class TelemetryMessage(pydantic.BaseModel):
    """Telemetry message schema"""
    assetId: str
    line: str
    signal: str
    value: Any
    unit: str
    ts: str
    quality: str = "Good"
    source: str = "opcua"
    seq: int


class StateMessage(pydantic.BaseModel):
    """Asset state message schema"""
    assetId: str
    line: str
    status: str
    lastUpdate: str
    signals: Dict[str, Any]
    source: str = "opcua"


class OPCUAMQTTGateway:
    """OPC UA to MQTT Gateway implementation"""
    
    def __init__(self, config_path: str = "mapping.yaml"):
        self.config_path = Path(config_path)
        self.config: Optional[GatewayConfig] = None
        self.opcua_client: Optional[Client] = None
        self.mqtt_client: Optional[asyncio_mqtt.Client] = None
        self.subscriptions: Dict[str, Node] = {}
        self.sequence_numbers: Dict[str, int] = {}
        self.last_values: Dict[str, Any] = {}
        self.running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        
        # Setup logging
        self.setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_logging(self):
        """Setup structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('opcua2mqtt.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def load_config(self) -> bool:
        """Load configuration from YAML file"""
        try:
            if not self.config_path.exists():
                self.logger.error(f"Configuration file not found: {self.config_path}")
                return False
            
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            self.config = GatewayConfig(**config_data)
            self.max_reconnect_attempts = self.config.settings.get('max_reconnect_attempts', 10)
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            self.logger.info(f"OPC UA endpoint: {self.config.opcua.endpoint}")
            self.logger.info(f"MQTT broker: {self.config.mqtt.host}:{self.config.mqtt.port}")
            self.logger.info(f"Node mappings: {len(self.config.mappings)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
    
    async def connect_opcua(self) -> bool:
        """Connect to OPC UA server"""
        try:
            self.logger.info(f"Connecting to OPC UA server: {self.config.opcua.endpoint}")
            
            self.opcua_client = Client(
                url=self.config.opcua.endpoint,
                timeout=self.config.opcua.connection_timeout
            )
            
            # Set security policy and mode
            if self.config.opcua.security_policy != "None":
                self.opcua_client.set_security_string(
                    f"Basic256Sha256,Sign,{self.config.opcua.username},{self.config.opcua.password}"
                )
            
            await self.opcua_client.connect()
            
            # Authenticate if credentials provided
            if self.config.opcua.username and self.config.opcua.password:
                await self.opcua_client.set_user(self.config.opcua.username)
                await self.opcua_client.set_password(self.config.opcua.password)
            
            self.logger.info("Successfully connected to OPC UA server")
            self.reconnect_attempts = 0
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to OPC UA server: {e}")
            return False
    
    async def connect_mqtt(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.logger.info(f"Connecting to MQTT broker: {self.config.mqtt.host}:{self.config.mqtt.port}")
            
            self.mqtt_client = asyncio_mqtt.Client(
                hostname=self.config.mqtt.host,
                port=self.config.mqtt.port,
                username=self.config.mqtt.username,
                password=self.config.mqtt.password,
                keepalive=self.config.mqtt.keepalive
            )
            
            await self.mqtt_client.connect()
            
            self.logger.info("Successfully connected to MQTT broker")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    async def setup_subscriptions(self) -> bool:
        """Setup OPC UA node subscriptions"""
        try:
            self.logger.info("Setting up OPC UA node subscriptions")
            
            for mapping in self.config.mappings:
                try:
                    # Get OPC UA node
                    node = self.opcua_client.get_node(mapping.nodeId)
                    
                    # Verify node exists and is readable
                    await node.read_value()
                    
                    # Store subscription
                    self.subscriptions[mapping.topic] = node
                    self.sequence_numbers[mapping.topic] = 0
                    
                    self.logger.info(f"Subscribed to node: {mapping.nodeId} -> {mapping.topic}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to subscribe to node {mapping.nodeId}: {e}")
                    continue
            
            if not self.subscriptions:
                self.logger.error("No valid node subscriptions created")
                return False
            
            self.logger.info(f"Successfully subscribed to {len(self.subscriptions)} nodes")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup subscriptions: {e}")
            return False
    
    def extract_asset_info(self, topic: str) -> tuple[str, str, str]:
        """Extract asset ID, line, and signal from MQTT topic"""
        # Topic format: factory/<line>/<asset>/<signal>
        parts = topic.split('/')
        if len(parts) >= 4 and parts[0] == 'factory':
            return parts[2], parts[1], parts[3]  # asset, line, signal
        return "unknown", "unknown", "unknown"
    
    async def publish_telemetry(self, mapping: NodeMapping, value: Any, quality: str = "Good"):
        """Publish telemetry data to MQTT"""
        try:
            # Extract asset information
            asset_id, line, signal = self.extract_asset_info(mapping.topic)
            
            # Increment sequence number
            self.sequence_numbers[mapping.topic] += 1
            
            # Create telemetry message
            telemetry = TelemetryMessage(
                assetId=asset_id,
                line=line,
                signal=signal,
                value=value,
                unit=mapping.unit,
                ts=datetime.now(timezone.utc).isoformat(),
                quality=quality,
                source="opcua",
                seq=self.sequence_numbers[mapping.topic]
            )
            
            # Publish to MQTT
            await self.mqtt_client.publish(
                mapping.topic,
                telemetry.model_dump_json(),
                qos=self.config.mqtt.qos
            )
            
            # Store last value for state messages
            self.last_values[mapping.topic] = {
                'value': value,
                'quality': quality,
                'timestamp': telemetry.ts
            }
            
            self.logger.debug(f"Published telemetry: {mapping.topic} = {value} {mapping.unit}")
            
        except Exception as e:
            self.logger.error(f"Failed to publish telemetry for {mapping.topic}: {e}")
    
    async def publish_state(self, asset_id: str, line: str):
        """Publish asset state message"""
        try:
            # Collect all signals for this asset
            asset_signals = {}
            status = "unknown"
            last_update = None
            
            for topic, data in self.last_values.items():
                if f"factory/{line}/{asset_id}/" in topic:
                    signal_name = topic.split('/')[-1]
                    asset_signals[signal_name] = {
                        'value': data['value'],
                        'quality': data['quality'],
                        'timestamp': data['timestamp']
                    }
                    
                    if signal_name == 'status':
                        status = str(data['value'])
                    
                    if not last_update or data['timestamp'] > last_update:
                        last_update = data['timestamp']
            
            if asset_signals:
                # Create state message
                state = StateMessage(
                    assetId=asset_id,
                    line=line,
                    status=status,
                    lastUpdate=last_update or datetime.now(timezone.utc).isoformat(),
                    signals=asset_signals,
                    source="opcua"
                )
                
                # Publish to MQTT with retention
                state_topic = f"state/{asset_id}"
                await self.mqtt_client.publish(
                    state_topic,
                    state.model_dump_json(),
                    qos=self.config.mqtt.qos,
                    retain=self.config.mqtt.retain_state
                )
                
                self.logger.debug(f"Published state: {state_topic}")
            
        except Exception as e:
            self.logger.error(f"Failed to publish state for {asset_id}: {e}")
    
    async def read_and_publish(self):
        """Read OPC UA values and publish to MQTT"""
        try:
            # Read all subscribed nodes
            for topic, node in self.subscriptions.items():
                try:
                    # Read node value
                    value = await node.read_value()
                    quality = "Good"
                    
                    # Handle different data types
                    if isinstance(value, ua.DataValue):
                        actual_value = value.Value.Value
                        quality = "Good" if value.StatusCode.is_good() else "Bad"
                    else:
                        actual_value = value
                    
                    # Find mapping for this topic
                    mapping = next((m for m in self.config.mappings if m.topic == topic), None)
                    if mapping:
                        await self.publish_telemetry(mapping, actual_value, quality)
                    
                except Exception as e:
                    self.logger.error(f"Failed to read node {topic}: {e}")
                    continue
            
            # Publish state messages for each asset
            assets = set()
            for mapping in self.config.mappings:
                asset_id, line, _ = self.extract_asset_info(mapping.topic)
                assets.add((asset_id, line))
            
            for asset_id, line in assets:
                await self.publish_state(asset_id, line)
            
        except Exception as e:
            self.logger.error(f"Failed to read and publish data: {e}")
    
    async def run(self):
        """Main gateway loop"""
        self.logger.info("Starting GhostMesh OPC UA to MQTT Gateway")
        
        # Load configuration
        if not await self.load_config():
            self.logger.error("Failed to load configuration")
            return
        
        self.running = True
        
        while self.running:
            try:
                # Connect to OPC UA server
                if not await self.connect_opcua():
                    await self.handle_reconnect()
                    continue
                
                # Connect to MQTT broker
                if not await self.connect_mqtt():
                    await self.handle_reconnect()
                    continue
                
                # Setup subscriptions
                if not await self.setup_subscriptions():
                    await self.handle_reconnect()
                    continue
                
                self.logger.info("Gateway is running and connected")
                
                # Main data loop
                publish_interval = self.config.settings.get('publish_interval', 1000) / 1000.0
                
                while self.running:
                    await self.read_and_publish()
                    await asyncio.sleep(publish_interval)
                
            except Exception as e:
                self.logger.error(f"Gateway error: {e}")
                await self.handle_reconnect()
    
    async def handle_reconnect(self):
        """Handle reconnection logic"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error("Maximum reconnection attempts reached, shutting down")
            self.running = False
            return
        
        self.reconnect_attempts += 1
        reconnect_interval = self.config.opcua.reconnect_interval / 1000.0
        
        self.logger.info(f"Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        self.logger.info(f"Retrying in {reconnect_interval} seconds...")
        
        await asyncio.sleep(reconnect_interval)
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down gateway...")
        self.running = False
        
        if self.mqtt_client:
            await self.mqtt_client.disconnect()
        
        if self.opcua_client:
            await self.opcua_client.disconnect()
        
        self.logger.info("Gateway shutdown complete")


async def main():
    """Main entry point"""
    gateway = OPCUAMQTTGateway()
    
    try:
        await gateway.run()
    except KeyboardInterrupt:
        self.logger.info("Received keyboard interrupt")
    finally:
        await gateway.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
