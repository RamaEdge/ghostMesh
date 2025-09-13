# GhostMesh Makefile
# Edge AI Security Copilot - Essential Commands

.PHONY: help build build-dashboard build-anomaly build-policy build-explainer build-llm-server setup-hf-auth start stop test logs status clean setup validate-setup validate-runtime dev prod

# Default target
help: ## Show this help message
	@echo "GhostMesh - Edge AI Security Copilot"
	@echo "====================================="
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Container runtime detection - Force Podman usage
CONTAINER_RUNTIME := podman
COMPOSE_CMD := podman-compose

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Project configuration
PROJECT_NAME := ghostmesh
MQTT_PORT := 1883

## Setup and Configuration
setup: ## Initial project setup
	@echo "$(BLUE)Setting up GhostMesh project...$(NC)"
	@echo "$(YELLOW)Container runtime: $(CONTAINER_RUNTIME)$(NC)"
	@echo "$(YELLOW)Compose command: $(COMPOSE_CMD)$(NC)"
	@echo ""
	@echo "$(BLUE)Creating MQTT users...$(NC)"
	@./scripts/setup-mqtt-users.sh
	@echo "$(GREEN)✓ MQTT users created$(NC)"
	@echo ""
	@echo "$(BLUE)Setting up directories...$(NC)"
	@mkdir -p mosquitto/data mosquitto/logs
	@echo "$(GREEN)✓ Directories created$(NC)"
	@echo ""
	@echo "$(GREEN)Setup complete! Run 'make start' to start services.$(NC)"

## Building
build: ## Build all container images
	@echo "$(BLUE)Building GhostMesh containers...$(NC)"
	$(COMPOSE_CMD) build
	@echo "$(GREEN)✓ All containers built$(NC)"

build-dashboard: ## Build dashboard container
	@echo "$(BLUE)Building dashboard container...$(NC)"
	$(COMPOSE_CMD) build dashboard
	@echo "$(GREEN)✓ Dashboard container built$(NC)"

build-anomaly: ## Build anomaly detector container
	@echo "$(BLUE)Building anomaly detector container...$(NC)"
	$(COMPOSE_CMD) build anomaly
	@echo "$(GREEN)✓ Anomaly detector container built$(NC)"

build-policy: ## Build policy engine container
	@echo "$(BLUE)Building policy engine container...$(NC)"
	$(COMPOSE_CMD) build policy
	@echo "$(GREEN)✓ Policy engine container built$(NC)"

build-explainer: ## Build AI explainer container
	@echo "$(BLUE)Building AI explainer container...$(NC)"
	$(COMPOSE_CMD) build explainer
	@echo "$(GREEN)✓ AI explainer container built$(NC)"

setup-hf-auth: ## Set up Hugging Face authentication
	@echo "$(BLUE)Setting up Hugging Face authentication...$(NC)"
	@if [ ! -f llm-server/.hf_token ]; then \
		echo "$(YELLOW)Creating .hf_token file from template...$(NC)"; \
		cp llm-server/.hf_token.template llm-server/.hf_token; \
		echo "$(YELLOW)Please edit llm-server/.hf_token and add your Hugging Face token$(NC)"; \
		echo "$(YELLOW)Get your token from: https://huggingface.co/settings/tokens$(NC)"; \
	else \
		echo "$(GREEN).hf_token file already exists$(NC)"; \
	fi

build-llm-server: setup-hf-auth ## Build LLM server container
	@echo "$(BLUE)Building LLM server container...$(NC)"
	$(COMPOSE_CMD) build llm-server
	@echo "$(GREEN)✓ LLM server container built$(NC)"

## Service Management
start: ## Start all services
	@echo "$(BLUE)Starting GhostMesh services...$(NC)"
	$(COMPOSE_CMD) up -d
	@echo "$(GREEN)✓ All services started$(NC)"
	@echo "$(YELLOW)Dashboard: http://localhost:8501$(NC)"
	@echo "$(YELLOW)MQTT: localhost:$(MQTT_PORT)$(NC)"
	@echo "$(YELLOW)Mock OPC UA: localhost:4840$(NC)"
	@echo "$(YELLOW)LLM Server: http://localhost:8080$(NC)"

stop: ## Stop all services
	@echo "$(BLUE)Stopping GhostMesh services...$(NC)"
	$(COMPOSE_CMD) down
	@echo "$(GREEN)✓ All services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting GhostMesh services...$(NC)"
	$(COMPOSE_CMD) restart
	@echo "$(GREEN)✓ All services restarted$(NC)"

## Monitoring
status: ## Show service status
	@echo "$(BLUE)GhostMesh Service Status$(NC)"
	@echo "$(BLUE)==========================$(NC)"
	$(COMPOSE_CMD) ps
	@echo ""
	@echo "$(BLUE)Container Health$(NC)"
	@echo "$(BLUE)==================$(NC)"
	$(COMPOSE_CMD) ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

logs: ## Show logs for all services
	$(COMPOSE_CMD) logs -f

## Testing
test: ## Run all tests
	@echo "$(BLUE)Running GhostMesh tests...$(NC)"
	@echo ""
	@echo "$(BLUE)1. MQTT Connectivity Test$(NC)"
	@make test-mqtt
	@echo ""
	@echo "$(BLUE)2. OPC UA Gateway Test$(NC)"
	@make test-gateway
	@echo ""
	@echo "$(BLUE)3. Anomaly Detection Tests$(NC)"
	@make test-anomaly
	@echo ""
	@echo "$(BLUE)4. AI Explainer Tests$(NC)"
	@make test-explainer
	@echo ""
	@echo "$(GREEN)✓ All tests completed$(NC)"

test-mqtt: ## Test MQTT broker connectivity
	@echo "$(BLUE)Testing MQTT broker...$(NC)"
	@./scripts/test-mqtt.sh
	@echo "$(GREEN)✓ MQTT tests completed$(NC)"

test-gateway: ## Test OPC UA gateway
	@echo "$(BLUE)Testing OPC UA gateway...$(NC)"
	@if $(COMPOSE_CMD) ps | grep -q "opcua2mqtt.*Up"; then \
		echo "$(GREEN)✓ OPC UA gateway is running$(NC)"; \
		echo "$(YELLOW)Checking gateway logs for connection status...$(NC)"; \
		$(COMPOSE_CMD) logs opcua2mqtt --tail=5 | grep -q "Successfully subscribed" && echo "$(GREEN)✓ Gateway connected successfully$(NC)" || echo "$(RED)✗ Gateway connection issues$(NC)"; \
	else \
		echo "$(RED)✗ OPC UA gateway is not running$(NC)"; \
	fi
	@echo "$(GREEN)✓ Gateway tests completed$(NC)"

## Cleanup
clean: ## Clean up containers and images
	@echo "$(BLUE)Cleaning up GhostMesh...$(NC)"
	$(COMPOSE_CMD) down
	$(CONTAINER_RUNTIME) system prune -f
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

## Quick Commands
quick-start: setup start ## Quick start: setup and start all services
quick-test: start test ## Quick test: start services and run tests
quick-restart: stop start ## Quick restart: stop and start all services

test-anomaly: ## Test anomaly detection and injection
	@echo "$(BLUE)Testing anomaly detection and injection...$(NC)"
	@if [ -f "tests/the66/run_tests.py" ]; then \
		python3 tests/the66/run_tests.py; \
	else \
		echo "$(YELLOW)No anomaly tests found$(NC)"; \
	fi
	@echo "$(GREEN)✓ Anomaly tests completed$(NC)"

test-explainer: ## Test AI explainer service
	@echo "$(BLUE)Testing AI explainer service...$(NC)"
	@if [ -f "tests/the166/run_tests.py" ]; then \
		python3 tests/the166/run_tests.py; \
	else \
		echo "$(YELLOW)No explainer tests found$(NC)"; \
	fi
	@echo "$(GREEN)✓ Explainer tests completed$(NC)"

## Development
dev: ## Start development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	@make setup
	@make start
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "$(YELLOW)MQTT broker running on localhost:$(MQTT_PORT)$(NC)"
	@echo "$(YELLOW)Mock OPC UA server running on localhost:4840$(NC)"

## Information
info: ## Show project information
	@echo "$(BLUE)GhostMesh Project Information$(NC)"
	@echo "$(BLUE)================================$(NC)"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Container Runtime: $(CONTAINER_RUNTIME)"
	@echo "Compose Command: $(COMPOSE_CMD)"
	@echo "MQTT Port: $(MQTT_PORT)"
	@echo ""
	@echo "$(BLUE)Available Services:$(NC)"
	@echo "  - MQTT Broker (Mosquitto) ✓"
	@echo "  - Mock OPC UA Server ✓"
	@echo "  - OPC UA Gateway ✓"
	@echo "  - Streamlit Dashboard ✓"
	@echo "  - Anomaly Detector ✓"
	@echo "  - Policy Engine ✓"
	@echo "  - AI Explainer (LLM) ✓"
	@echo "  - LLM Server (llama.cpp) ✓"
	@echo ""
	@echo "$(BLUE)Documentation:$(NC)"
	@echo "  - docs/Project_README.md"
	@echo "  - docs/Architecture.md"
	@echo "  - docs/Quickstart_Guide.md"
	@echo "  - docs/Configuration_Guide.md"
	@echo "  - docs/Troubleshooting_Guide.md"

## Validation
validate-setup: ## Validate system setup and configuration
	@echo "$(BLUE)Validating GhostMesh setup...$(NC)"
	@python3 scripts/validate-setup.py --verbose
	@echo "$(GREEN)✓ Setup validation completed$(NC)"

validate-runtime: ## Validate runtime system health and data flow
	@echo "$(BLUE)Validating GhostMesh runtime...$(NC)"
	@python3 scripts/validate-runtime.py --verbose
	@echo "$(GREEN)✓ Runtime validation completed$(NC)"

## Deployment Profiles
dev: ## Start development environment with debug logging
	@echo "$(BLUE)Starting GhostMesh development environment...$(NC)"
	@echo "$(YELLOW)Features: Debug logging, hot reload, development tools$(NC)"
	$(COMPOSE_CMD) -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✓ Development environment started$(NC)"
	@echo "$(BLUE)Dashboard: http://localhost:8501$(NC)"
	@echo "$(BLUE)LLM Server: http://localhost:8080$(NC)"

prod: ## Start production environment with monitoring
	@echo "$(BLUE)Starting GhostMesh production environment...$(NC)"
	@echo "$(YELLOW)Features: Optimized settings, monitoring, security hardening$(NC)"
	$(COMPOSE_CMD) -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✓ Production environment started$(NC)"
	@echo "$(BLUE)Dashboard: http://localhost:8501$(NC)"
	@echo "$(BLUE)LLM Server: http://localhost:8080$(NC)"
	@echo "$(BLUE)Monitoring: http://localhost:9090$(NC)"

.PHONY: help setup build build-mock-opcua build-gateway build-dashboard build-anomaly build-policy build-explainer build-llm-server start stop restart status logs clean quick-start quick-test quick-restart test-anomaly test-explainer dev info test test-opcua test-gateway test-mqtt test-integration validate-setup validate-runtime prod