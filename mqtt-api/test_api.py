"""
Test suite for MQTT API Backend Service

This module contains comprehensive tests for the MQTT API endpoints,
including unit tests, integration tests, and WebSocket tests.
"""

import asyncio
import json
import pytest
import httpx
import websockets
from datetime import datetime
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Import the app and models
from app import app, mqtt_client, message_history, websocket_connections
from client import MQTTAPIClient, AsyncMQTTAPIClient, MQTTWebSocketClient

# Test client
client = TestClient(app)

class TestMQTTAPI:
    """Test class for MQTT API endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Clear message history
        message_history.clear()
        # Clear WebSocket connections
        websocket_connections.clear()
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "GhostMesh MQTT API Backend"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "mqtt_connected" in data
        assert "uptime" in data
        assert "message_count" in data
        assert "active_subscriptions" in data
        assert "websocket_connections" in data
    
    @patch('app.mqtt_client')
    def test_publish_message_success(self, mock_mqtt_client):
        """Test successful message publishing"""
        # Mock MQTT client
        mock_result = Mock()
        mock_result.rc = 0  # MQTT_ERR_SUCCESS
        mock_result.mid = 123
        mock_mqtt_client.publish.return_value = mock_result
        mock_mqtt_client._subscriptions = {}
        
        # Test data
        message_data = {
            "topic": "test/topic",
            "payload": "Hello, MQTT!",
            "qos": 1,
            "retain": False
        }
        
        response = client.post("/publish", json=message_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Message published successfully"
        assert data["data"]["topic"] == "test/topic"
        assert data["data"]["message_id"] == 123
    
    @patch('app.mqtt_client')
    def test_publish_message_failure(self, mock_mqtt_client):
        """Test message publishing failure"""
        # Mock MQTT client
        mock_result = Mock()
        mock_result.rc = 1  # MQTT_ERR_FAILURE
        mock_mqtt_client.publish.return_value = mock_result
        mock_mqtt_client._subscriptions = {}
        
        # Test data
        message_data = {
            "topic": "test/topic",
            "payload": "Hello, MQTT!",
            "qos": 1,
            "retain": False
        }
        
        response = client.post("/publish", json=message_data)
        assert response.status_code == 500
        data = response.json()
        assert "Failed to publish message" in data["detail"]
    
    def test_publish_message_mqtt_disconnected(self):
        """Test message publishing when MQTT is disconnected"""
        # Mock disconnected state
        with patch('app.mqtt_connected', False):
            message_data = {
                "topic": "test/topic",
                "payload": "Hello, MQTT!",
                "qos": 1,
                "retain": False
            }
            
            response = client.post("/publish", json=message_data)
            assert response.status_code == 503
            assert "MQTT broker not connected" in response.json()["detail"]
    
    @patch('app.mqtt_client')
    def test_subscribe_topic_success(self, mock_mqtt_client):
        """Test successful topic subscription"""
        # Mock MQTT client
        mock_mqtt_client.subscribe.return_value = (0, 1)  # (rc, mid)
        mock_mqtt_client._subscriptions = {}
        
        # Test data
        subscription_data = {
            "topic": "test/topic",
            "qos": 1
        }
        
        response = client.post("/subscribe", json=subscription_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Subscribed successfully"
        assert data["data"]["topic"] == "test/topic"
        assert data["data"]["qos"] == 1
    
    @patch('app.mqtt_client')
    def test_subscribe_topic_failure(self, mock_mqtt_client):
        """Test topic subscription failure"""
        # Mock MQTT client
        mock_mqtt_client.subscribe.return_value = (1, 0)  # (rc, mid) - failure
        mock_mqtt_client._subscriptions = {}
        
        # Test data
        subscription_data = {
            "topic": "test/topic",
            "qos": 1
        }
        
        response = client.post("/subscribe", json=subscription_data)
        assert response.status_code == 500
        data = response.json()
        assert "Failed to subscribe" in data["detail"]
    
    @patch('app.mqtt_client')
    def test_unsubscribe_topic_success(self, mock_mqtt_client):
        """Test successful topic unsubscription"""
        # Mock MQTT client
        mock_mqtt_client.unsubscribe.return_value = (0, 1)  # (rc, mid)
        mock_mqtt_client._subscriptions = {}
        
        response = client.delete("/subscribe/test/topic")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Unsubscribed successfully"
        assert data["data"]["topic"] == "test/topic"
    
    def test_get_message_history(self):
        """Test getting message history"""
        # Add test messages to history
        test_messages = [
            {
                "topic": "test/topic1",
                "payload": "Message 1",
                "timestamp": datetime.now().isoformat(),
                "qos": 0,
                "retain": False
            },
            {
                "topic": "test/topic2",
                "payload": "Message 2",
                "timestamp": datetime.now().isoformat(),
                "qos": 1,
                "retain": True
            }
        ]
        message_history.extend(test_messages)
        
        # Test getting all messages
        response = client.get("/messages")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Test filtering by topic
        response = client.get("/messages?topic=test/topic1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["topic"] == "test/topic1"
        
        # Test pagination
        response = client.get("/messages?limit=1&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    def test_get_topics(self):
        """Test getting active topics"""
        # Add test messages to history
        test_messages = [
            {
                "topic": "test/topic1",
                "payload": "Message 1",
                "timestamp": datetime.now().isoformat(),
                "qos": 0,
                "retain": False
            },
            {
                "topic": "test/topic2",
                "payload": "Message 2",
                "timestamp": datetime.now().isoformat(),
                "qos": 1,
                "retain": True
            },
            {
                "topic": "test/topic1",  # Duplicate topic
                "payload": "Message 3",
                "timestamp": datetime.now().isoformat(),
                "qos": 0,
                "retain": False
            }
        ]
        message_history.extend(test_messages)
        
        response = client.get("/topics")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Should be unique topics
        assert "test/topic1" in data
        assert "test/topic2" in data
        assert data == sorted(data)  # Should be sorted
    
    def test_get_statistics(self):
        """Test getting statistics"""
        # Add test messages to history
        test_messages = [
            {
                "topic": "test/topic1",
                "payload": "Message 1",
                "timestamp": datetime.now().isoformat(),
                "qos": 0,
                "retain": False
            },
            {
                "topic": "test/topic2",
                "payload": "Message 2",
                "timestamp": datetime.now().isoformat(),
                "qos": 1,
                "retain": True
            }
        ]
        message_history.extend(test_messages)
        
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_messages"] == 2
        assert data["unique_topics"] == 2
        assert "test/topic1" in data["topic_counts"]
        assert "test/topic2" in data["topic_counts"]
        assert data["topic_counts"]["test/topic1"] == 1
        assert data["topic_counts"]["test/topic2"] == 1
        assert "mqtt_connected" in data
        assert "websocket_connections" in data
        assert "uptime" in data

class TestWebSocket:
    """Test class for WebSocket functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        websocket_connections.clear()
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection and welcome message"""
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            # Should receive welcome message
            message = await websocket.recv()
            data = json.loads(message)
            assert data["type"] == "welcome"
            assert "Connected to GhostMesh MQTT API" in data["message"]
            assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_websocket_ping_pong(self):
        """Test WebSocket ping/pong functionality"""
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            # Receive welcome message
            await websocket.recv()
            
            # Send ping
            await websocket.send("ping")
            
            # Should receive pong
            message = await websocket.recv()
            data = json.loads(message)
            assert data["type"] == "pong"

class TestClientLibrary:
    """Test class for client library functionality"""
    
    def test_sync_client_initialization(self):
        """Test synchronous client initialization"""
        client = MQTTAPIClient("http://localhost:8000", "test-api-key")
        assert client.base_url == "http://localhost:8000"
        assert client.api_key == "test-api-key"
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer test-api-key"
        client.close()
    
    def test_async_client_initialization(self):
        """Test asynchronous client initialization"""
        client = AsyncMQTTAPIClient("http://localhost:8000", "test-api-key")
        assert client.base_url == "http://localhost:8000"
        assert client.api_key == "test-api-key"
        assert "Authorization" in client.client.headers
        assert client.client.headers["Authorization"] == "Bearer test-api-key"
    
    def test_websocket_client_initialization(self):
        """Test WebSocket client initialization"""
        client = MQTTWebSocketClient("ws://localhost:8000/ws")
        assert client.ws_url == "ws://localhost:8000/ws"
        assert client.message_handler is None
        assert client.websocket is None
        assert client.running is False

class TestErrorHandling:
    """Test class for error handling"""
    
    def test_invalid_json_payload(self):
        """Test handling of invalid JSON payload"""
        response = client.post("/publish", data="invalid json")
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        response = client.post("/publish", json={"topic": "test"})  # Missing payload
        assert response.status_code == 422  # Validation error
    
    def test_invalid_qos_value(self):
        """Test handling of invalid QoS value"""
        message_data = {
            "topic": "test/topic",
            "payload": "Hello, MQTT!",
            "qos": 5,  # Invalid QoS (should be 0-2)
            "retain": False
        }
        response = client.post("/publish", json=message_data)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_topic_format(self):
        """Test handling of invalid topic format"""
        message_data = {
            "topic": "",  # Empty topic
            "payload": "Hello, MQTT!",
            "qos": 0,
            "retain": False
        }
        response = client.post("/publish", json=message_data)
        assert response.status_code == 422  # Validation error

class TestPerformance:
    """Test class for performance testing"""
    
    def test_large_message_history(self):
        """Test handling of large message history"""
        # Add many messages to history
        for i in range(1500):  # More than MAX_HISTORY_SIZE
            message_history.append({
                "topic": f"test/topic{i}",
                "payload": f"Message {i}",
                "timestamp": datetime.now().isoformat(),
                "qos": 0,
                "retain": False
            })
        
        # Should still work and limit history size
        response = client.get("/messages")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1000  # Should be limited by MAX_HISTORY_SIZE
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10

# Fixtures for pytest
@pytest.fixture
def test_client():
    """Fixture for test client"""
    return TestClient(app)

@pytest.fixture
def sample_message():
    """Fixture for sample message"""
    return {
        "topic": "test/topic",
        "payload": "Hello, MQTT!",
        "qos": 1,
        "retain": False
    }

@pytest.fixture
def sample_subscription():
    """Fixture for sample subscription"""
    return {
        "topic": "test/topic",
        "qos": 1
    }

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
