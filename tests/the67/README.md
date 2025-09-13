# THE-67: LLM Explainer Integration Tests

## Overview

This directory contains comprehensive tests for THE-67: Implement LLM explainer for alert interpretation. The tests validate the integration of local LLM (llama.cpp) with the GhostMesh AI Explainer service.

## Test Structure

```
tests/the67/
├── README.md                    # This file
├── test_llm_integration.py      # LLM integration tests
└── test_results.json           # Test results (generated)
```

## Test Categories

### 1. LLM Service Tests
- **Service Initialization**: Test LLM service setup and configuration
- **Prompt Templates**: Validate available prompt templates (operator, analyst, hybrid)
- **Server Availability**: Check llama.cpp server connectivity

### 2. Explanation Generation Tests
- **Multi-user Explanations**: Test explanations for different user types
- **Fallback Mechanism**: Validate fallback when LLM is unavailable
- **Confidence Calculation**: Test confidence scoring logic
- **Risk Level Extraction**: Test risk assessment from explanations

### 3. Integration Tests
- **End-to-end Flow**: Test complete alert → explanation pipeline
- **MQTT Integration**: Validate explanation publishing
- **Error Handling**: Test graceful failure scenarios

## Running Tests

### Prerequisites
- All GhostMesh services running (`make start`)
- LLM server available at `http://localhost:8080`
- Python dependencies installed

### Quick Test
```bash
# Run all THE-67 tests
python3 tests/the67/test_llm_integration.py
```

### Individual Test Categories
```bash
# Test LLM service initialization
python3 -c "
import sys; sys.path.insert(0, 'explainer')
from tests.the67.test_llm_integration import test_llm_service_initialization
test_llm_service_initialization()
"

# Test explanation generation
python3 -c "
import sys; sys.path.insert(0, 'explainer')
from tests.the67.test_llm_integration import test_explanation_generation
test_explanation_generation()
"
```

## Test Scenarios

### 1. LLM Service Initialization
```python
def test_llm_service_initialization():
    """Test LLM service initialization."""
    config = LLMConfig(server_url="http://localhost:8080")
    service = LLMService(config)
    assert service is not None
```

### 2. Prompt Template Validation
```python
def test_prompt_templates():
    """Test prompt template availability."""
    service = LLMService()
    templates = service.get_available_templates()
    expected_templates = ["operator", "analyst", "hybrid"]
    for template in expected_templates:
        assert template in templates
```

### 3. Explanation Generation
```python
def test_explanation_generation():
    """Test explanation generation with different user types."""
    service = LLMService()
    test_alert = {
        "alertId": "test-123",
        "assetId": "press01",
        "signal": "temperature",
        "severity": "high",
        "current": 85.5,
        "reason": "z-score 8.2 vs mean 35.0±2.1 (120s)"
    }
    
    for user_type in ["operator", "analyst", "hybrid"]:
        explanation = service.generate_explanation(test_alert, user_type)
        assert explanation["userType"] == user_type
        assert 0.0 <= explanation["confidence"] <= 1.0
```

### 4. Fallback Mechanism
```python
def test_fallback_explanation():
    """Test fallback explanation when LLM is not available."""
    config = LLMConfig(server_url="http://invalid-server:8080")
    service = LLMService(config)
    explanation = service.generate_explanation(test_alert, "operator")
    assert explanation["source"] == "fallback"
    assert explanation["confidence"] == 0.5
```

## Expected Results

### Successful Test Run
```
============================================================
THE-67: LLM Integration Tests
============================================================
Testing LLM service initialization...
✓ LLM service initialized successfully

Testing prompt templates...
✓ Available templates: ['operator', 'analyst', 'hybrid']

Testing LLM server availability...
✓ LLM server is available

Testing explanation generation...
  Testing operator explanation...
    ✓ operator explanation generated (confidence: 0.85)
  Testing analyst explanation...
    ✓ analyst explanation generated (confidence: 0.82)
  Testing hybrid explanation...
    ✓ hybrid explanation generated (confidence: 0.83)
✓ All explanation types generated successfully

Testing fallback explanation...
✓ Fallback explanation generated successfully

Testing confidence calculation...
  ✓ Test case 1: confidence = 0.70
  ✓ Test case 2: confidence = 0.90
✓ Confidence calculation working correctly

Testing risk level extraction...
  ✓ Test case 1: risk level = high
  ✓ Test case 2: risk level = medium
  ✓ Test case 3: risk level = high
✓ Risk level extraction working correctly

============================================================
Test Results: 7 passed, 0 failed
============================================================
🎉 All tests passed!
```

## Troubleshooting

### Common Issues

#### LLM Server Not Available
```bash
# Check if LLM server is running
docker ps | grep llm-server

# Check server logs
docker logs ghostmesh-llm-server

# Restart LLM server
docker restart ghostmesh-llm-server
```

#### Model Not Downloaded
```bash
# Download model manually
docker exec -it ghostmesh-llm-server /app/download-model.sh

# Check model file
docker exec -it ghostmesh-llm-server ls -la /models/
```

#### Import Errors
```bash
# Install dependencies
pip3 install requests

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/explainer"
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

# Check explainer service logs
docker logs ghostmesh-explainer

# Monitor MQTT explanations
docker exec -it ghostmesh-mosquitto mosquitto_sub -t "explanations/#" -v
```

## Performance Benchmarks

### Expected Performance
- **LLM Service Initialization**: < 1 second
- **Explanation Generation**: 2-5 seconds (depending on model)
- **Fallback Explanation**: < 0.1 seconds
- **Confidence Calculation**: < 0.01 seconds

### Resource Usage
- **Memory**: ~100MB for explainer service
- **CPU**: Minimal for HTTP client operations
- **Network**: Low bandwidth for HTTP requests

## Integration with Makefile

The THE-67 tests are integrated into the main Makefile:

```makefile
test-explainer: ## Test AI explainer service
	@echo "$(BLUE)Testing AI explainer service...$(NC)"
	@if [ -f "tests/the67/test_llm_integration.py" ]; then \
		python3 tests/the67/test_llm_integration.py; \
	else \
		echo "$(YELLOW)No explainer tests found$(NC)"; \
	fi
	@echo "$(GREEN)✓ Explainer tests completed$(NC)"
```

## References

- [THE-67 Linear Issue](https://linear.app/theedgeworks/issue/THE-67)
- [LLM Explainer Documentation](../../docs/LLM_Explainer.md)
- [llama.cpp Documentation](https://github.com/ggerganov/llama.cpp)
- [GhostMesh Architecture](../../docs/Architecture.md)
