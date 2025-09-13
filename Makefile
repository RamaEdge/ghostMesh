# GhostMesh Makefile
# Edge AI Security Copilot - Essential Commands

.PHONY: help build build-dashboard build-anomaly build-policy start stop test logs status clean setup

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

## Service Management
start: ## Start all services
	@echo "$(BLUE)Starting GhostMesh services...$(NC)"
	$(COMPOSE_CMD) up -d
	@echo "$(GREEN)✓ All services started$(NC)"
	@echo "$(YELLOW)Dashboard: http://localhost:8501$(NC)"
	@echo "$(YELLOW)MQTT: localhost:$(MQTT_PORT)$(NC)"
	@echo "$(YELLOW)Mock OPC UA: localhost:4840$(NC)"

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
	@echo ""
	@echo "$(BLUE)Documentation:$(NC)"
	@echo "  - docs/Project_README.md"
	@echo "  - docs/Architecture.md"
	@echo "  - docs/Quickstart_Guide.md"