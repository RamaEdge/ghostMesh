# LLM Explainer Service

## Overview

The LLM Explainer Service is a core component of GhostMesh that generates intelligent, context-aware explanations for security alerts using local Large Language Model (LLM) integration via llama.cpp. This service replaces hardcoded rule-based explanations with dynamic, AI-powered interpretations that adapt to different user types and alert contexts.

## Architecture

### Components

- **LLM Service**: Core service for LLM integration and prompt management
- **AI Explainer**: Main service that processes alerts and generates explanations
- **LLM Server**: llama.cpp server for local model inference
- **Prompt Templates**: Configurable templates for different user types

### Data Flow

```
Alert (MQTT) → AI Explainer → LLM Service → LLM Server → Explanation (MQTT)
```

## Features

### LLM Integration

- **Local LLM Support**: Uses llama.cpp server for local inference
- **Model**: TinyLlama-1.1B-Chat-v1.0 (lightweight, optimized for Raspberry Pi)
- **API Communication**: HTTP-based communication with llama.cpp server
- **Fallback Mechanism**: Graceful degradation when LLM is unavailable

### Prompt Templates

The service supports three user types with specialized prompt templates:

#### Operator Template
- **Audience**: Industrial operators
- **Focus**: Immediate actions and safety implications
- **Style**: Clear, actionable, concise
- **Max Tokens**: 200
- **Temperature**: 0.6

#### Analyst Template
- **Audience**: Security analysts
- **Focus**: Technical details and forensic implications
- **Style**: Detailed, technical, comprehensive
- **Max Tokens**: 400
- **Temperature**: 0.7

#### Hybrid Template
- **Audience**: Mixed audience (operators and analysts)
- **Focus**: Balanced technical and practical information
- **Style**: Accessible but detailed
- **Max Tokens**: 300
- **Temperature**: 0.65

### Explanation Generation

#### Input Context
The LLM receives comprehensive alert context:
- Asset ID and signal type
- Severity level and current value
- Statistical reason (z-score analysis)
- Timestamp and alert ID

#### Output Schema
```json
{
  "alertId": "alert-123",
  "text": "Generated explanation text",
  "confidence": 0.85,
  "riskLevel": "high",
  "userType": "operator",
  "recommendations": [
    "Immediate action 1",
    "Immediate action 2"
  ],
  "ts": "2025-09-13T15:00:00Z",
  "source": "llm"
}
```

#### Confidence Scoring
Confidence is calculated based on:
- Explanation length and detail
- Mention of specific values
- Asset context inclusion
- Action-oriented language

## Configuration

### Environment Variables

#### AI Explainer Service
- `LLM_SERVER_URL`: URL of the llama.cpp server (default: `http://llm-server:8080`)
- `DEFAULT_USER_TYPE`: Default user type for explanations (default: `hybrid`)
- `EXPLANATION_TIMEOUT`: Timeout for LLM requests in seconds (default: `10`)

#### LLM Server
- `MODEL_PATH`: Path to the model file (default: `/models/tinyllama-1.1b-chat.gguf`)

### Model Configuration

The service uses TinyLlama-1.1B-Chat-v1.0 model with the following characteristics:
- **Size**: ~1.1B parameters
- **Format**: GGUF (Q4_K_M quantized)
- **Context**: 2048 tokens
- **Threads**: 4 (configurable)
- **Memory**: ~2GB RAM usage
- **File Size**: ~637MB

## Deployment

### Docker Compose Integration

The LLM Explainer is integrated into the GhostMesh docker-compose stack:

```yaml
# LLM Server
llm-server:
  build: ./llm-server
  container_name: ghostmesh-llm-server
  ports:
    - "8080:8080"
  volumes:
    - llm_models:/models
  environment:
    - MODEL_PATH=/models/tinyllama-1.1b-chat.gguf
  restart: unless-stopped
  networks:
    - ghostmesh-network

# AI Explainer Service
explainer:
  build: ./explainer
  container_name: ghostmesh-explainer
  depends_on:
    mosquitto:
      condition: service_healthy
    llm-server:
      condition: service_healthy
  environment:
    - LLM_SERVER_URL=http://llm-server:8080
    - DEFAULT_USER_TYPE=hybrid
    - EXPLANATION_TIMEOUT=10
  restart: unless-stopped
  networks:
    - ghostmesh-network
```

### Model Download

The model is automatically downloaded during container startup:

```bash
# Download TinyLlama-1.1B model
./llm-server/download-model.sh
```

## Usage

### Starting the Service

```bash
# Start all services including LLM server
make start

# Or start individual services
make build-llm-server
make build-explainer
```

### Monitoring

#### Service Health
```bash
# Check service status
make status

# View logs
make logs-explainer
make logs-llm-server
```

#### LLM Server Health
```bash
# Check LLM server health
curl http://localhost:8080/health
```

### Testing

```bash
# Test explainer service
make test-explainer

# Test with specific user type
curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test prompt",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

## Performance

### Latency Requirements

- **Target**: < 5 seconds for explanation generation
- **Typical**: 2-3 seconds for TinyLlama-1.1B model
- **Fallback**: < 1 second for hardcoded explanations

### Resource Usage

#### LLM Server
- **CPU**: 2-4 cores recommended
- **RAM**: ~2GB for model + 1GB overhead
- **Storage**: ~3GB for model file

#### AI Explainer
- **CPU**: Minimal (HTTP client)
- **RAM**: ~100MB
- **Network**: Low bandwidth (HTTP requests)

### Optimization

- **Model Quantization**: Q4_K_M quantization for balance of size/quality
- **Context Size**: Limited to 2048 tokens for performance
- **Caching**: Explanation caching for repeated alerts (future enhancement)
- **Batch Processing**: Multiple alerts in single request (future enhancement)

## Troubleshooting

### Common Issues

#### LLM Server Not Available
```bash
# Check if server is running
docker ps | grep llm-server

# Check server logs
docker logs ghostmesh-llm-server

# Restart server
docker restart ghostmesh-llm-server
```

#### Model Download Issues
```bash
# Manual model download
docker exec -it ghostmesh-llm-server /app/download-model.sh

# Check model file
docker exec -it ghostmesh-llm-server ls -la /models/
```

#### Explanation Generation Failures
```bash
# Check explainer logs
docker logs ghostmesh-explainer

# Test LLM connectivity
docker exec -it ghostmesh-explainer python -c "
from llm_service import LLMService
service = LLMService()
print(f'LLM Available: {service.is_available()}')
"
```

### Debug Commands

```bash
# Test LLM server directly
curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, how are you?",
    "max_tokens": 50,
    "temperature": 0.7
  }'

# Monitor MQTT topics
docker exec -it ghostmesh-mosquitto mosquitto_sub -t "explanations/#" -v
```

## Future Enhancements

### Planned Features

1. **Model Selection**: Support for multiple models (Qwen2-0.5B, Phi-3-mini, Llama-3.2-1B)
2. **Explanation Caching**: Cache explanations for similar alerts
3. **Batch Processing**: Process multiple alerts in single LLM request
4. **Custom Prompts**: User-configurable prompt templates
5. **Multi-language Support**: Explanations in different languages
6. **Confidence Learning**: Improve confidence scoring based on feedback

### Stretch Goals

1. **External API Support**: Integration with OpenAI, Anthropic APIs
2. **Fine-tuning**: Custom model fine-tuning for industrial contexts
3. **Real-time Learning**: Continuous improvement from user feedback
4. **Multi-modal**: Support for image and sensor data in explanations

## Security Considerations

### Model Security

- **Local Processing**: All inference happens locally
- **No Data Transmission**: Alert data never leaves the system
- **Model Integrity**: Signed model files and verification
- **Access Control**: LLM server only accessible from internal network

### Data Privacy

- **No Logging**: Alert data not logged by LLM server
- **Memory Management**: Model context cleared after each request
- **Audit Trail**: All explanations logged with metadata only

## References

- [llama.cpp Documentation](https://github.com/ggerganov/llama.cpp)
- [TinyLlama Model Documentation](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0)
- [GhostMesh Architecture](../docs/Architecture.md)
- [THE-67 Linear Issue](https://linear.app/theedgeworks/issue/THE-67)
