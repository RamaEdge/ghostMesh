"""
MQTT API Client Library

This module provides a Python client library for interacting with the
GhostMesh MQTT API Backend Service. It includes both synchronous and
asynchronous clients for different use cases.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import httpx
import websockets
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MQTTMessage(BaseModel):
    """MQTT message model"""
    topic: str
    payload: str
    qos: int = 0
    retain: bool = False

class MQTTSubscription(BaseModel):
    """MQTT subscription model"""
    topic: str
    qos: int = 0

class MessageHistory(BaseModel):
    """Message history model"""
    topic: str
    payload: str
    timestamp: datetime
    qos: int
    retain: bool

class MQTTAPIClient:
    """Synchronous MQTT API client"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = httpx.Client(timeout=30.0)
        
        # Set headers
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.session.headers.update(headers)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the client session"""
        self.session.close()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> Dict[str, Any]:
        """Publish a message to an MQTT topic"""
        message = MQTTMessage(topic=topic, payload=payload, qos=qos, retain=retain)
        response = self.session.post(f"{self.base_url}/publish", json=message.dict())
        response.raise_for_status()
        return response.json()
    
    def subscribe(self, topic: str, qos: int = 0) -> Dict[str, Any]:
        """Subscribe to an MQTT topic"""
        subscription = MQTTSubscription(topic=topic, qos=qos)
        response = self.session.post(f"{self.base_url}/subscribe", json=subscription.dict())
        response.raise_for_status()
        return response.json()
    
    def unsubscribe(self, topic: str) -> Dict[str, Any]:
        """Unsubscribe from an MQTT topic"""
        response = self.session.delete(f"{self.base_url}/subscribe/{topic}")
        response.raise_for_status()
        return response.json()
    
    def get_messages(self, topic: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get message history"""
        params = {"limit": limit, "offset": offset}
        if topic:
            params["topic"] = topic
        
        response = self.session.get(f"{self.base_url}/messages", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_topics(self) -> List[str]:
        """Get list of active topics"""
        response = self.session.get(f"{self.base_url}/topics")
        response.raise_for_status()
        return response.json()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API and MQTT statistics"""
        response = self.session.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

class AsyncMQTTAPIClient:
    """Asynchronous MQTT API client"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Set headers
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client.headers.update(headers)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the client session"""
        await self.client.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    async def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> Dict[str, Any]:
        """Publish a message to an MQTT topic"""
        message = MQTTMessage(topic=topic, payload=payload, qos=qos, retain=retain)
        response = await self.client.post(f"{self.base_url}/publish", json=message.dict())
        response.raise_for_status()
        return response.json()
    
    async def subscribe(self, topic: str, qos: int = 0) -> Dict[str, Any]:
        """Subscribe to an MQTT topic"""
        subscription = MQTTSubscription(topic=topic, qos=qos)
        response = await self.client.post(f"{self.base_url}/subscribe", json=subscription.dict())
        response.raise_for_status()
        return response.json()
    
    async def unsubscribe(self, topic: str) -> Dict[str, Any]:
        """Unsubscribe from an MQTT topic"""
        response = await self.client.delete(f"{self.base_url}/subscribe/{topic}")
        response.raise_for_status()
        return response.json()
    
    async def get_messages(self, topic: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get message history"""
        params = {"limit": limit, "offset": offset}
        if topic:
            params["topic"] = topic
        
        response = await self.client.get(f"{self.base_url}/messages", params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_topics(self) -> List[str]:
        """Get list of active topics"""
        response = await self.client.get(f"{self.base_url}/topics")
        response.raise_for_status()
        return response.json()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get API and MQTT statistics"""
        response = await self.client.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

class MQTTWebSocketClient:
    """WebSocket client for real-time MQTT message updates"""
    
    def __init__(self, ws_url: str = "ws://localhost:8000/ws", message_handler: Optional[Callable] = None):
        self.ws_url = ws_url
        self.message_handler = message_handler
        self.websocket = None
        self.running = False
    
    async def connect(self):
        """Connect to WebSocket endpoint"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.running = True
            logger.info("Connected to MQTT API WebSocket")
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from WebSocket endpoint"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from MQTT API WebSocket")
    
    async def listen(self):
        """Listen for messages from WebSocket"""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")
        
        try:
            while self.running:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                if self.message_handler:
                    await self.message_handler(data)
                else:
                    logger.info(f"Received message: {data}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            raise
    
    async def send_ping(self):
        """Send ping to keep connection alive"""
        if self.websocket and self.running:
            await self.websocket.send("ping")
    
    async def start_heartbeat(self, interval: int = 30):
        """Start heartbeat to keep connection alive"""
        while self.running:
            await asyncio.sleep(interval)
            await self.send_ping()

# Example usage functions
def example_sync_client():
    """Example of using the synchronous client"""
    with MQTTAPIClient() as client:
        # Check health
        health = client.health_check()
        print(f"API Health: {health}")
        
        # Publish a message
        result = client.publish("test/topic", "Hello, MQTT!")
        print(f"Publish result: {result}")
        
        # Subscribe to a topic
        result = client.subscribe("test/topic")
        print(f"Subscribe result: {result}")
        
        # Get message history
        messages = client.get_messages(limit=10)
        print(f"Recent messages: {messages}")
        
        # Get statistics
        stats = client.get_statistics()
        print(f"Statistics: {stats}")

async def example_async_client():
    """Example of using the asynchronous client"""
    async with AsyncMQTTAPIClient() as client:
        # Check health
        health = await client.health_check()
        print(f"API Health: {health}")
        
        # Publish a message
        result = await client.publish("test/topic", "Hello, Async MQTT!")
        print(f"Publish result: {result}")
        
        # Subscribe to a topic
        result = await client.subscribe("test/topic")
        print(f"Subscribe result: {result}")
        
        # Get message history
        messages = await client.get_messages(limit=10)
        print(f"Recent messages: {messages}")
        
        # Get statistics
        stats = await client.get_statistics()
        print(f"Statistics: {stats}")

async def example_websocket_client():
    """Example of using the WebSocket client"""
    async def message_handler(data):
        print(f"Received: {data}")
    
    client = MQTTWebSocketClient(message_handler=message_handler)
    
    try:
        await client.connect()
        
        # Start heartbeat in background
        heartbeat_task = asyncio.create_task(client.start_heartbeat())
        
        # Listen for messages
        await client.listen()
        
    except KeyboardInterrupt:
        print("Stopping WebSocket client...")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    # Run examples
    print("=== Synchronous Client Example ===")
    example_sync_client()
    
    print("\n=== Asynchronous Client Example ===")
    asyncio.run(example_async_client())
    
    print("\n=== WebSocket Client Example ===")
    print("Press Ctrl+C to stop...")
    asyncio.run(example_websocket_client())
