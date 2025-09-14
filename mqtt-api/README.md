# MQTT API Backend Service

The MQTT API Backend Service provides a REST API for interacting with the GhostMesh MQTT broker, allowing external systems to publish messages, subscribe to topics, and manage MQTT operations through HTTP endpoints.

## Features

- **REST API**: HTTP endpoints for MQTT operations
- **Real-time Updates**: WebSocket support for live message streaming
- **Message History**: Store and query message history
- **Statistics**: API and MQTT broker statistics
- **Health Monitoring**: Service health and status endpoints
- **Client Library**: Python client library for easy integration
- **Comprehensive Testing**: Unit tests, integration tests, and WebSocket tests

## Architecture

The service consists of several components:

- **FastAPI Application**: Main web server with REST endpoints
- **MQTT Client**: Paho MQTT client for broker communication
- **WebSocket Handler**: Real-time message broadcasting
- **Message Storage**: In-memory message history
- **Configuration Management**: Environment-based configuration
- **Client Library**: Python SDK for external integration

## API Endpoints

### Core Endpoints

- `GET /` - Service information and status
- `GET /health` - Health check and service status
- `POST /publish` - Publish message to MQTT topic
- `POST /subscribe` - Subscribe to MQTT topic
- `DELETE /subscribe/{topic}` - Unsubscribe from MQTT topic
- `GET /messages` - Get message history
- `GET /topics` - Get list of active topics
- `GET /stats` - Get API and MQTT statistics
- `WebSocket /ws` - Real-time message updates

### Message Publishing

Publish a message to an MQTT topic:

```bash
curl -X POST "http://localhost:8000/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "factory/line1/press1/temperature",
    "payload": "45.2",
    "qos": 1,
    "retain": false
  }'
```

### Topic Subscription

Subscribe to an MQTT topic:

```bash
curl -X POST "http://localhost:8000/subscribe" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "factory/+/+/temperature",
    "qos": 1
  }'
```

### Message History

Get message history with optional filtering:

```bash
# Get all messages
curl "http://localhost:8000/messages"

# Filter by topic
curl "http://localhost:8000/messages?topic=factory/line1/press1/temperature"

# Pagination
curl "http://localhost:8000/messages?limit=50&offset=0"
```

### Statistics

Get API and MQTT statistics:

```bash
curl "http://localhost:8000/stats"
```

## WebSocket Integration

Connect to the WebSocket endpoint for real-time message updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received message:', data);
};

// Send ping to keep connection alive
setInterval(() => {
    ws.send('ping');
}, 30000);
```

## Python Client Library

The service includes a comprehensive Python client library:

### Synchronous Client

```python
from client import MQTTAPIClient

# Initialize client
with MQTTAPIClient("http://localhost:8000") as client:
    # Check health
    health = client.health_check()
    print(f"API Health: {health}")
    
    # Publish message
    result = client.publish("test/topic", "Hello, MQTT!")
    print(f"Publish result: {result}")
    
    # Subscribe to topic
    result = client.subscribe("test/topic")
    print(f"Subscribe result: {result}")
    
    # Get message history
    messages = client.get_messages(limit=10)
    print(f"Recent messages: {messages}")
```

### Asynchronous Client

```python
import asyncio
from client import AsyncMQTTAPIClient

async def main():
    async with AsyncMQTTAPIClient("http://localhost:8000") as client:
        # Check health
        health = await client.health_check()
        print(f"API Health: {health}")
        
        # Publish message
        result = await client.publish("test/topic", "Hello, Async MQTT!")
        print(f"Publish result: {result}")
        
        # Subscribe to topic
        result = await client.subscribe("test/topic")
        print(f"Subscribe result: {result}")

asyncio.run(main())
```

### WebSocket Client

```python
import asyncio
from client import MQTTWebSocketClient

async def message_handler(data):
    print(f"Received: {data}")

async def main():
    client = MQTTWebSocketClient(message_handler=message_handler)
    
    try:
        await client.connect()
        await client.listen()
    except KeyboardInterrupt:
        print("Stopping WebSocket client...")
    finally:
        await client.disconnect()

asyncio.run(main())
```

## Configuration

The service can be configured using environment variables:

### MQTT Broker Configuration

- `MQTT_BROKER_HOST` - MQTT broker hostname (default: localhost)
- `MQTT_BROKER_PORT` - MQTT broker port (default: 1883)
- `MQTT_USERNAME` - MQTT username (default: api)
- `MQTT_PASSWORD` - MQTT password (default: api_password)
- `MQTT_KEEPALIVE` - MQTT keepalive interval (default: 60)
- `MQTT_CLEAN_SESSION` - MQTT clean session flag (default: true)

### API Server Configuration

- `API_HOST` - API server host (default: 0.0.0.0)
- `API_PORT` - API server port (default: 8000)
- `API_WORKERS` - Number of worker processes (default: 1)
- `API_RELOAD` - Enable auto-reload (default: false)

### Message Storage Configuration

- `MAX_HISTORY_SIZE` - Maximum message history size (default: 1000)
- `MESSAGE_RETENTION_HOURS` - Message retention period (default: 24)

### WebSocket Configuration

- `WS_HEARTBEAT_INTERVAL` - WebSocket heartbeat interval (default: 30)
- `WS_MAX_CONNECTIONS` - Maximum WebSocket connections (default: 100)

### Security Configuration

- `CORS_ORIGINS` - CORS allowed origins (default: *)
- `API_KEY_REQUIRED` - Require API key authentication (default: false)
- `API_KEY` - API key for authentication

### Logging Configuration

- `LOG_LEVEL` - Logging level (default: INFO)
- `LOG_FORMAT` - Log message format

## Installation and Setup

### Prerequisites

- Python 3.11 or higher
- MQTT broker (Mosquitto)
- Docker (optional)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mqtt-api
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   export MQTT_BROKER_HOST=localhost
   export MQTT_BROKER_PORT=1883
   export MQTT_USERNAME=api
   export MQTT_PASSWORD=api_password
   ```

4. **Run the service**:
   ```bash
   python app.py
   ```

### Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t ghostmesh-mqtt-api .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name mqtt-api \
     -p 8000:8000 \
     -e MQTT_BROKER_HOST=mosquitto \
     -e MQTT_USERNAME=api \
     -e MQTT_PASSWORD=api_password \
     ghostmesh-mqtt-api
   ```

### Docker Compose Integration

Add to your `docker-compose.yml`:

```yaml
services:
  mqtt-api:
    build: ./mqtt-api
    ports:
      - "8000:8000"
    environment:
      - MQTT_BROKER_HOST=mosquitto
      - MQTT_USERNAME=api
      - MQTT_PASSWORD=api_password
    depends_on:
      - mosquitto
    restart: unless-stopped
```

## Testing

The service includes comprehensive tests:

### Run All Tests

```bash
pytest test_api.py -v
```

### Run Specific Test Categories

```bash
# Unit tests
pytest test_api.py::TestMQTTAPI -v

# WebSocket tests
pytest test_api.py::TestWebSocket -v

# Client library tests
pytest test_api.py::TestClientLibrary -v

# Error handling tests
pytest test_api.py::TestErrorHandling -v

# Performance tests
pytest test_api.py::TestPerformance -v
```

### Test Coverage

```bash
pytest --cov=app test_api.py
```

## API Documentation

The service provides automatic API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Monitoring and Health Checks

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "mqtt_connected": true,
  "uptime": 3600.5,
  "message_count": 150,
  "active_subscriptions": 5,
  "websocket_connections": 2
}
```

### Statistics Endpoint

```bash
curl http://localhost:8000/stats
```

Response:
```json
{
  "total_messages": 150,
  "unique_topics": 10,
  "recent_messages": 25,
  "topic_counts": {
    "factory/line1/press1/temperature": 50,
    "factory/line1/press1/pressure": 30,
    "alerts/press1/temperature": 20
  },
  "mqtt_connected": true,
  "websocket_connections": 2,
  "uptime": 3600.5
}
```

## Error Handling

The service provides comprehensive error handling:

- **Validation Errors**: 422 for invalid request data
- **Service Errors**: 500 for internal server errors
- **Connection Errors**: 503 for MQTT broker unavailable
- **Authentication Errors**: 401 for unauthorized access
- **Rate Limiting**: 429 for too many requests

## Performance Considerations

- **Message History**: Limited to 1000 messages by default
- **WebSocket Connections**: Limited to 100 concurrent connections
- **Rate Limiting**: Configurable request rate limiting
- **Memory Usage**: In-memory storage for message history
- **Connection Pooling**: HTTP client connection pooling

## Security Features

- **CORS Support**: Configurable cross-origin resource sharing
- **API Key Authentication**: Optional API key authentication
- **Input Validation**: Comprehensive input validation
- **Error Sanitization**: Sanitized error messages
- **Rate Limiting**: Protection against abuse

## Troubleshooting

### Common Issues

1. **MQTT Connection Failed**:
   - Check MQTT broker is running
   - Verify connection credentials
   - Check network connectivity

2. **WebSocket Connection Failed**:
   - Check firewall settings
   - Verify WebSocket URL
   - Check for proxy interference

3. **High Memory Usage**:
   - Reduce MAX_HISTORY_SIZE
   - Implement message cleanup
   - Monitor WebSocket connections

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python app.py
```

### Log Analysis

Monitor logs for issues:

```bash
# Follow logs
tail -f logs/mqtt-api.log

# Search for errors
grep "ERROR" logs/mqtt-api.log

# Monitor WebSocket connections
grep "WebSocket" logs/mqtt-api.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- **Documentation**: Check this README and API docs
- **Issues**: Create an issue on GitHub
- **Community**: Join the GhostMesh community
- **Email**: Contact the development team

## Changelog

### Version 1.0.0

- Initial release
- REST API endpoints
- WebSocket support
- Python client library
- Comprehensive testing
- Docker support
- Health monitoring
- Message history
- Statistics and analytics
