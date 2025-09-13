#!/usr/bin/env python3
"""
GhostMesh OPC UA Gateway Test Suite
Tests OPC UA to MQTT gateway functionality
"""

import asyncio
import json
import pytest
import yaml
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

# Import the gateway module
from opcua2mqtt import OPCUAMQTTGateway, GatewayConfig, NodeMapping, OPCUAConfig, MQTTConfig


class TestOPCUAMQTTGateway:
    """Test suite for OPC UA to MQTT Gateway"""
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            "opcua": {
                "endpoint": "opc.tcp://localhost:4840",
                "security_policy": "None",
                "security_mode": "None",
                "username": "test",
                "password": "testpass"
            },
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "username": "gateway",
                "password": "gatewaypass",
                "qos": 1,
                "retain_state": True
            },
            "mappings": [
                {
                    "nodeId": "ns=2;s=Press01.Temperature",
                    "topic": "factory/A/press01/temperature",
                    "unit": "C",
                    "data_type": "float",
                    "description": "Press01 temperature sensor"
                },
                {
                    "nodeId": "ns=2;s=Press01.Pressure",
                    "topic": "factory/A/press01/pressure",
                    "unit": "bar",
                    "data_type": "float",
                    "description": "Press01 pressure sensor"
                }
            ],
            "settings": {
                "publish_interval": 1000,
                "max_reconnect_attempts": 3
            }
        }
    
    @pytest.fixture
    def gateway(self, sample_config, tmp_path):
        """Create gateway instance for testing"""
        config_file = tmp_path / "test_mapping.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(sample_config, f)
        
        gateway = OPCUAMQTTGateway(str(config_file))
        return gateway
    
    def test_config_loading(self, gateway, sample_config):
        """Test configuration loading"""
        asyncio.run(gateway.load_config())
        
        assert gateway.config is not None
        assert gateway.config.opcua.endpoint == sample_config["opcua"]["endpoint"]
        assert gateway.config.mqtt.host == sample_config["mqtt"]["host"]
        assert len(gateway.config.mappings) == 2
    
    def test_asset_info_extraction(self, gateway):
        """Test asset information extraction from topics"""
        # Test valid topic
        asset_id, line, signal = gateway.extract_asset_info("factory/A/press01/temperature")
        assert asset_id == "press01"
        assert line == "A"
        assert signal == "temperature"
        
        # Test invalid topic
        asset_id, line, signal = gateway.extract_asset_info("invalid/topic")
        assert asset_id == "unknown"
        assert line == "unknown"
        assert signal == "unknown"
    
    @pytest.mark.asyncio
    async def test_telemetry_message_creation(self, gateway):
        """Test telemetry message creation"""
        await gateway.load_config()
        
        mapping = gateway.config.mappings[0]
        value = 25.5
        
        # Mock MQTT client
        gateway.mqtt_client = AsyncMock()
        gateway.sequence_numbers[mapping.topic] = 0
        
        await gateway.publish_telemetry(mapping, value)
        
        # Verify MQTT publish was called
        gateway.mqtt_client.publish.assert_called_once()
        
        # Verify message content
        call_args = gateway.mqtt_client.publish.call_args
        topic = call_args[0][0]
        message_json = call_args[0][1]
        
        assert topic == mapping.topic
        
        message = json.loads(message_json)
        assert message["assetId"] == "press01"
        assert message["line"] == "A"
        assert message["signal"] == "temperature"
        assert message["value"] == value
        assert message["unit"] == "C"
        assert message["source"] == "opcua"
        assert message["seq"] == 1
    
    @pytest.mark.asyncio
    async def test_state_message_creation(self, gateway):
        """Test state message creation"""
        await gateway.load_config()
        
        # Mock MQTT client
        gateway.mqtt_client = AsyncMock()
        
        # Set up last values
        gateway.last_values = {
            "factory/A/press01/temperature": {
                "value": 25.5,
                "quality": "Good",
                "timestamp": "2025-01-01T12:00:00Z"
            },
            "factory/A/press01/pressure": {
                "value": 10.2,
                "quality": "Good",
                "timestamp": "2025-01-01T12:00:00Z"
            }
        }
        
        await gateway.publish_state("press01", "A")
        
        # Verify MQTT publish was called
        gateway.mqtt_client.publish.assert_called_once()
        
        # Verify message content
        call_args = gateway.mqtt_client.publish.call_args
        topic = call_args[0][0]
        message_json = call_args[0][1]
        
        assert topic == "state/press01"
        
        message = json.loads(message_json)
        assert message["assetId"] == "press01"
        assert message["line"] == "A"
        assert message["source"] == "opcua"
        assert "temperature" in message["signals"]
        assert "pressure" in message["signals"]
    
    @pytest.mark.asyncio
    async def test_opcua_connection_mock(self, gateway):
        """Test OPC UA connection with mocked client"""
        await gateway.load_config()
        
        # Mock OPC UA client
        mock_client = AsyncMock()
        gateway.opcua_client = mock_client
        
        # Mock connection
        mock_client.connect.return_value = None
        
        result = await gateway.connect_opcua()
        assert result is True
        mock_client.connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mqtt_connection_mock(self, gateway):
        """Test MQTT connection with mocked client"""
        await gateway.load_config()
        
        # Mock MQTT client
        mock_client = AsyncMock()
        gateway.mqtt_client = mock_client
        
        # Mock connection
        mock_client.connect.return_value = None
        
        result = await gateway.connect_mqtt()
        assert result is True
        mock_client.connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_subscription_setup_mock(self, gateway):
        """Test subscription setup with mocked OPC UA client"""
        await gateway.load_config()
        
        # Mock OPC UA client and nodes
        mock_client = AsyncMock()
        mock_node = AsyncMock()
        mock_node.read_value.return_value = 25.5
        
        gateway.opcua_client = mock_client
        gateway.opcua_client.get_node.return_value = mock_node
        
        result = await gateway.setup_subscriptions()
        assert result is True
        assert len(gateway.subscriptions) == 2
    
    def test_sequence_number_management(self, gateway):
        """Test sequence number management"""
        topic = "factory/A/press01/temperature"
        gateway.sequence_numbers[topic] = 0
        
        # Simulate multiple publishes
        for i in range(5):
            gateway.sequence_numbers[topic] += 1
        
        assert gateway.sequence_numbers[topic] == 5
    
    @pytest.mark.asyncio
    async def test_error_handling(self, gateway):
        """Test error handling in various scenarios"""
        await gateway.load_config()
        
        # Test with invalid configuration
        gateway.config = None
        result = await gateway.load_config()
        assert result is False
        
        # Test connection failure handling
        gateway.config = GatewayConfig(
            opcua=OPCUAConfig(endpoint="opc.tcp://invalid:4840"),
            mqtt=MQTTConfig(host="invalid"),
            mappings=[]
        )
        
        result = await gateway.connect_opcua()
        assert result is False


class TestConfigurationValidation:
    """Test configuration validation"""
    
    def test_valid_configuration(self):
        """Test valid configuration creation"""
        config = GatewayConfig(
            opcua=OPCUAConfig(endpoint="opc.tcp://localhost:4840"),
            mqtt=MQTTConfig(host="localhost"),
            mappings=[
                NodeMapping(
                    nodeId="ns=2;s=Test",
                    topic="factory/A/test/signal",
                    unit="unit",
                    data_type="float",
                    description="Test signal"
                )
            ]
        )
        
        assert config.opcua.endpoint == "opc.tcp://localhost:4840"
        assert config.mqtt.host == "localhost"
        assert len(config.mappings) == 1
    
    def test_invalid_configuration(self):
        """Test invalid configuration handling"""
        with pytest.raises(Exception):
            GatewayConfig(
                opcua=OPCUAConfig(endpoint=""),  # Invalid endpoint
                mqtt=MQTTConfig(host=""),        # Invalid host
                mappings=[]
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
