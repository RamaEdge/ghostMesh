#!/usr/bin/env python3
"""
MQTT API Backend Service Example

This script demonstrates how to use the MQTT API Backend Service
for publishing messages, subscribing to topics, and receiving
real-time updates via WebSocket.
"""

import asyncio
import json
import time
from datetime import datetime
from client import MQTTAPIClient, AsyncMQTTAPIClient, MQTTWebSocketClient

def example_sync_client():
    """Example using the synchronous client"""
    print("=== Synchronous Client Example ===")
    
    with MQTTAPIClient("http://localhost:8000") as client:
        # Check API health
        print("1. Checking API health...")
        health = client.health_check()
        print(f"   API Status: {health['status']}")
        print(f"   MQTT Connected: {health['mqtt_connected']}")
        print(f"   Uptime: {health['uptime']:.2f} seconds")
        
        # Publish some test messages
        print("\n2. Publishing test messages...")
        topics = [
            "factory/line1/press1/temperature",
            "factory/line1/press1/pressure",
            "factory/line1/press1/vibration",
            "alerts/press1/temperature"
        ]
        
        for i, topic in enumerate(topics):
            payload = f"Test message {i+1} at {datetime.now().isoformat()}"
            result = client.publish(topic, payload, qos=1)
            print(f"   Published to {topic}: {result['success']}")
            time.sleep(0.5)
        
        # Subscribe to topics
        print("\n3. Subscribing to topics...")
        for topic in topics:
            result = client.subscribe(topic, qos=1)
            print(f"   Subscribed to {topic}: {result['success']}")
        
        # Get message history
        print("\n4. Getting message history...")
        messages = client.get_messages(limit=10)
        print(f"   Retrieved {len(messages)} recent messages")
        for msg in messages[-3:]:  # Show last 3 messages
            print(f"   - {msg['topic']}: {msg['payload'][:50]}...")
        
        # Get active topics
        print("\n5. Getting active topics...")
        topics = client.get_topics()
        print(f"   Active topics: {topics}")
        
        # Get statistics
        print("\n6. Getting statistics...")
        stats = client.get_statistics()
        print(f"   Total messages: {stats['total_messages']}")
        print(f"   Unique topics: {stats['unique_topics']}")
        print(f"   Recent messages: {stats['recent_messages']}")
        print(f"   Topic counts: {stats['topic_counts']}")

async def example_async_client():
    """Example using the asynchronous client"""
    print("\n=== Asynchronous Client Example ===")
    
    async with AsyncMQTTAPIClient("http://localhost:8000") as client:
        # Check API health
        print("1. Checking API health...")
        health = await client.health_check()
        print(f"   API Status: {health['status']}")
        print(f"   MQTT Connected: {health['mqtt_connected']}")
        
        # Publish messages concurrently
        print("\n2. Publishing messages concurrently...")
        tasks = []
        for i in range(5):
            topic = f"async/test/topic{i}"
            payload = f"Async message {i+1} at {datetime.now().isoformat()}"
            task = client.publish(topic, payload, qos=1)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        for i, result in enumerate(results):
            print(f"   Published message {i+1}: {result['success']}")
        
        # Subscribe to topics concurrently
        print("\n3. Subscribing to topics concurrently...")
        tasks = []
        for i in range(5):
            topic = f"async/test/topic{i}"
            task = client.subscribe(topic, qos=1)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        for i, result in enumerate(results):
            print(f"   Subscribed to topic {i+1}: {result['success']}")
        
        # Get statistics
        print("\n4. Getting statistics...")
        stats = await client.get_statistics()
        print(f"   Total messages: {stats['total_messages']}")
        print(f"   Unique topics: {stats['unique_topics']}")

async def example_websocket_client():
    """Example using the WebSocket client"""
    print("\n=== WebSocket Client Example ===")
    
    received_messages = []
    
    async def message_handler(data):
        """Handle incoming WebSocket messages"""
        received_messages.append(data)
        print(f"   Received: {data['type']} - {data.get('topic', 'N/A')}")
        if 'payload' in data:
            print(f"   Payload: {data['payload'][:50]}...")
    
    client = MQTTWebSocketClient("ws://localhost:8000/ws", message_handler)
    
    try:
        print("1. Connecting to WebSocket...")
        await client.connect()
        print("   Connected successfully!")
        
        print("\n2. Listening for messages (30 seconds)...")
        print("   (Publish some messages to see them here)")
        
        # Listen for messages for 30 seconds
        listen_task = asyncio.create_task(client.listen())
        heartbeat_task = asyncio.create_task(client.start_heartbeat(10))
        
        try:
            await asyncio.wait_for(listen_task, timeout=30.0)
        except asyncio.TimeoutError:
            print("   Timeout reached, stopping listener...")
        
        # Cancel tasks
        listen_task.cancel()
        heartbeat_task.cancel()
        
        print(f"\n3. Received {len(received_messages)} messages total")
        
    except Exception as e:
        print(f"   Error: {e}")
    finally:
        await client.disconnect()
        print("   Disconnected from WebSocket")

def example_industrial_scenario():
    """Example simulating an industrial IoT scenario"""
    print("\n=== Industrial IoT Scenario Example ===")
    
    with MQTTAPIClient("http://localhost:8000") as client:
        # Simulate industrial equipment data
        equipment_data = {
            "factory/line1/press1/temperature": [45.2, 46.1, 47.8, 49.2, 50.1],
            "factory/line1/press1/pressure": [12.5, 12.8, 13.1, 13.4, 13.7],
            "factory/line1/press1/vibration": [2.1, 2.3, 2.5, 2.8, 3.1],
            "factory/line1/press1/status": ["running", "running", "running", "running", "running"],
            "factory/line1/press2/temperature": [44.8, 45.5, 46.2, 47.1, 48.3],
            "factory/line1/press2/pressure": [11.9, 12.2, 12.5, 12.8, 13.1],
            "factory/line1/press2/vibration": [1.9, 2.1, 2.3, 2.6, 2.9],
            "factory/line1/press2/status": ["running", "running", "running", "running", "running"]
        }
        
        print("1. Simulating industrial equipment data...")
        
        # Subscribe to all topics first
        for topic in equipment_data.keys():
            client.subscribe(topic, qos=1)
        
        # Publish simulated data
        for i in range(5):
            print(f"   Publishing data batch {i+1}...")
            for topic, values in equipment_data.items():
                payload = json.dumps({
                    "value": values[i],
                    "timestamp": datetime.now().isoformat(),
                    "unit": "°C" if "temperature" in topic else "bar" if "pressure" in topic else "mm/s" if "vibration" in topic else "status"
                })
                client.publish(topic, payload, qos=1)
            time.sleep(1)
        
        # Simulate an anomaly
        print("\n2. Simulating temperature anomaly...")
        anomaly_payload = json.dumps({
            "value": 95.7,
            "timestamp": datetime.now().isoformat(),
            "unit": "°C",
            "anomaly": True,
            "severity": "high"
        })
        client.publish("factory/line1/press1/temperature", anomaly_payload, qos=2, retain=True)
        
        # Generate alert
        alert_payload = json.dumps({
            "alert_id": "alert-001",
            "asset": "press1",
            "signal": "temperature",
            "value": 95.7,
            "threshold": 50.0,
            "severity": "high",
            "timestamp": datetime.now().isoformat(),
            "message": "Temperature reading exceeds safe operating limits"
        })
        client.publish("alerts/press1/temperature", alert_payload, qos=2, retain=True)
        
        # Get recent messages
        print("\n3. Retrieving recent messages...")
        messages = client.get_messages(limit=20)
        print(f"   Retrieved {len(messages)} recent messages")
        
        # Filter for alerts
        alert_messages = [msg for msg in messages if "alerts/" in msg["topic"]]
        print(f"   Found {len(alert_messages)} alert messages")
        
        # Get statistics
        print("\n4. Getting statistics...")
        stats = client.get_statistics()
        print(f"   Total messages: {stats['total_messages']}")
        print(f"   Unique topics: {stats['unique_topics']}")
        print(f"   Recent messages: {stats['recent_messages']}")
        
        # Show topic distribution
        print("\n5. Topic distribution:")
        for topic, count in stats['topic_counts'].items():
            print(f"   {topic}: {count} messages")

async def main():
    """Main function to run all examples"""
    print("GhostMesh MQTT API Backend Service Examples")
    print("=" * 50)
    
    try:
        # Run synchronous client example
        example_sync_client()
        
        # Run asynchronous client example
        await example_async_client()
        
        # Run WebSocket client example
        await example_websocket_client()
        
        # Run industrial scenario example
        example_industrial_scenario()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure the MQTT API Backend Service is running on http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(main())
