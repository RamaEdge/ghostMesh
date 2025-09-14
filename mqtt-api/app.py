#!/usr/bin/env python3
"""
MQTT API Backend Service

This service provides a REST API for interacting with the MQTT broker,
allowing external systems to publish messages, subscribe to topics,
and manage MQTT operations through HTTP endpoints.

Features:
- Publish messages to MQTT topics
- Subscribe to MQTT topics and receive messages via WebSocket
- Query message history and statistics
- Manage MQTT connections and sessions
- Health monitoring and status endpoints
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import unquote

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', 'localhost')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', '1883'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'api')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'api_password')
API_PORT = int(os.getenv('API_PORT', '8000'))
API_HOST = os.getenv('API_HOST', '0.0.0.0')

# Global MQTT client
mqtt_client: Optional[mqtt.Client] = None
mqtt_connected = False

# Message storage for history
message_history: List[Dict[str, Any]] = []
MAX_HISTORY_SIZE = 1000

# WebSocket connections for real-time updates
websocket_connections: List[WebSocket] = []

# FastAPI app
app = FastAPI(
    title="GhostMesh MQTT API",
    description="REST API for MQTT broker operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MQTTMessage(BaseModel):
    topic: str = Field(..., description="MQTT topic to publish to")
    payload: str = Field(..., description="Message payload")
    qos: int = Field(0, ge=0, le=2, description="Quality of Service level")
    retain: bool = Field(False, description="Retain message on broker")

class MQTTSubscription(BaseModel):
    topic: str = Field(..., description="MQTT topic to subscribe to")
    qos: int = Field(0, ge=0, le=2, description="Quality of Service level")

class MQTTResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class MessageHistory(BaseModel):
    topic: str
    payload: str
    timestamp: datetime
    qos: int
    retain: bool

class HealthStatus(BaseModel):
    status: str
    mqtt_connected: bool
    uptime: float
    message_count: int
    active_subscriptions: int
    websocket_connections: int

# MQTT event handlers
def on_mqtt_connect(client, userdata, flags, rc):
    """Handle MQTT connection events"""
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        logger.info("Connected to MQTT broker")
    else:
        mqtt_connected = False
        logger.error(f"Failed to connect to MQTT broker: {rc}")

def on_mqtt_disconnect(client, userdata, rc):
    """Handle MQTT disconnection events"""
    global mqtt_connected
    mqtt_connected = False
    logger.warning(f"Disconnected from MQTT broker: {rc}")

def on_mqtt_message(client, userdata, msg):
    """Handle incoming MQTT messages"""
    try:
        # Decode message payload
        payload = msg.payload.decode('utf-8')
        
        # Create message record
        message_record = {
            "topic": msg.topic,
            "payload": payload,
            "timestamp": datetime.now().isoformat(),
            "qos": msg.qos,
            "retain": msg.retain
        }
        
        # Store in history
        message_history.append(message_record)
        if len(message_history) > MAX_HISTORY_SIZE:
            message_history.pop(0)
        
        # Send to WebSocket connections
        asyncio.create_task(broadcast_to_websockets(message_record))
        
        logger.info(f"Received message on {msg.topic}: {payload[:100]}...")
        
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")

async def broadcast_to_websockets(message: Dict[str, Any]):
    """Broadcast message to all WebSocket connections"""
    if websocket_connections:
        disconnected = []
        for websocket in websocket_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected WebSockets
        for ws in disconnected:
            websocket_connections.remove(ws)

def setup_mqtt_client():
    """Setup and connect MQTT client"""
    global mqtt_client
    
    try:
        # Create MQTT client
        mqtt_client = mqtt.Client()
        mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
        # Set event handlers
        mqtt_client.on_connect = on_mqtt_connect
        mqtt_client.on_disconnect = on_mqtt_disconnect
        mqtt_client.on_message = on_mqtt_message
        
        # Connect to broker
        mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        mqtt_client.loop_start()
        
        logger.info(f"MQTT client setup complete, connecting to {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        
    except Exception as e:
        logger.error(f"Failed to setup MQTT client: {e}")
        raise

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting MQTT API Backend Service")
    setup_mqtt_client()
    
    # Wait for MQTT connection
    for _ in range(10):
        if mqtt_connected:
            break
        await asyncio.sleep(1)
    
    if not mqtt_connected:
        logger.warning("MQTT connection not established, continuing anyway")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global mqtt_client
    logger.info("Shutting down MQTT API Backend Service")
    
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "GhostMesh MQTT API Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - start_time
    return HealthStatus(
        status="healthy" if mqtt_connected else "degraded",
        mqtt_connected=mqtt_connected,
        uptime=uptime,
        message_count=len(message_history),
        active_subscriptions=len(getattr(mqtt_client, '_subscriptions', {})) if mqtt_client else 0,  # Fixed: use getattr for compatibility
        websocket_connections=len(websocket_connections)
    )

@app.post("/publish", response_model=MQTTResponse)
async def publish_message(message: MQTTMessage):
    """Publish a message to an MQTT topic"""
    if not mqtt_connected:
        raise HTTPException(status_code=503, detail="MQTT broker not connected")
    
    try:
        # Publish message
        result = mqtt_client.publish(
            message.topic,
            message.payload,
            qos=message.qos,
            retain=message.retain
        )
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Published message to {message.topic}")
            return MQTTResponse(
                success=True,
                message="Message published successfully",
                data={"topic": message.topic, "message_id": result.mid}
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to publish message: {result.rc}")
            
    except Exception as e:
        logger.error(f"Error publishing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/subscribe", response_model=MQTTResponse)
async def subscribe_to_topic(subscription: MQTTSubscription):
    """Subscribe to an MQTT topic"""
    if not mqtt_connected:
        raise HTTPException(status_code=503, detail="MQTT broker not connected")
    
    try:
        # Subscribe to topic
        result = mqtt_client.subscribe(subscription.topic, qos=subscription.qos)
        
        if result[0] == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Subscribed to {subscription.topic}")
            return MQTTResponse(
                success=True,
                message="Subscribed successfully",
                data={"topic": subscription.topic, "qos": subscription.qos}
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to subscribe: {result[0]}")
            
    except Exception as e:
        logger.error(f"Error subscribing to topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/subscribe/{topic:path}", response_model=MQTTResponse)
async def unsubscribe_from_topic(topic: str):
    """Unsubscribe from an MQTT topic"""
    if not mqtt_connected:
        raise HTTPException(status_code=503, detail="MQTT broker not connected")
    
    try:
        # Decode URL-encoded topic
        decoded_topic = unquote(topic)
        
        # Unsubscribe from topic
        result = mqtt_client.unsubscribe(decoded_topic)
        
        if result[0] == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Unsubscribed from {decoded_topic}")
            return MQTTResponse(
                success=True,
                message="Unsubscribed successfully",
                data={"topic": decoded_topic}
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to unsubscribe: {result[0]}")
            
    except Exception as e:
        logger.error(f"Error unsubscribing from topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages", response_model=List[MessageHistory])
async def get_message_history(
    topic: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get message history with optional filtering"""
    try:
        # Filter messages by topic if specified
        filtered_messages = message_history
        if topic:
            filtered_messages = [msg for msg in message_history if msg["topic"] == topic]
        
        # Apply pagination
        start_idx = offset
        end_idx = offset + limit
        paginated_messages = filtered_messages[start_idx:end_idx]
        
        # Convert to response format
        response_messages = []
        for msg in paginated_messages:
            response_messages.append(MessageHistory(
                topic=msg["topic"],
                payload=msg["payload"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
                qos=msg["qos"],
                retain=msg["retain"]
            ))
        
        return response_messages
        
    except Exception as e:
        logger.error(f"Error retrieving message history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/topics", response_model=List[str])
async def get_active_topics():
    """Get list of active topics from message history"""
    try:
        topics = list(set(msg["topic"] for msg in message_history))
        return sorted(topics)
    except Exception as e:
        logger.error(f"Error retrieving topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=Dict[str, Any])
async def get_statistics():
    """Get API and MQTT statistics"""
    try:
        # Calculate message statistics
        total_messages = len(message_history)
        topics = list(set(msg["topic"] for msg in message_history))
        
        # Calculate messages per topic
        topic_counts = {}
        for msg in message_history:
            topic_counts[msg["topic"]] = topic_counts.get(msg["topic"], 0) + 1
        
        # Calculate recent activity (last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_messages = [
            msg for msg in message_history
            if datetime.fromisoformat(msg["timestamp"]) > one_hour_ago
        ]
        
        return {
            "total_messages": total_messages,
            "unique_topics": len(topics),
            "recent_messages": len(recent_messages),
            "topic_counts": topic_counts,
            "mqtt_connected": mqtt_connected,
            "websocket_connections": len(websocket_connections),
            "uptime": time.time() - start_time
        }
        
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time message updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "message": "Connected to GhostMesh MQTT API",
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep connection alive
        while True:
            try:
                # Wait for client messages (ping/pong)
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

# Global variables
start_time = time.time()

if __name__ == "__main__":
    logger.info("Starting MQTT API Backend Service")
    uvicorn.run(
        "app:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info"
    )
# Cache buster: Sun Sep 14 10:24:04 CEST 2025
