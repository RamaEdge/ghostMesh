# GhostMesh Makefile
# Edge AI Security Copilot - Build, Test, and Deploy Automation

.PHONY: help build test lint clean setup start stop logs status health check-mqtt format docs

# Default target
help: ## Show this help message
	@echo "GhostMesh - Edge AI Security Copilot"
	@echo "====================================="
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Container runtime detection
CONTAINER_RUNTIME := $(shell command -v podman >/dev/null 2>&1 && echo "podman" || echo "docker")
COMPOSE_CMD := $(CONTAINER_RUNTIME) compose

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Project configuration
PROJECT_NAME := ghostmesh
MQTT_PORT := 1883
DASHBOARD_PORT := 8501

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

build-mqtt: ## Build only MQTT broker
	@echo "$(BLUE)Building MQTT broker...$(NC)"
	$(COMPOSE_CMD) build mosquitto
	@echo "$(GREEN)✓ MQTT broker built$(NC)"

build-gateway: ## Build OPC UA gateway (when implemented)
	@echo "$(BLUE)Building OPC UA gateway...$(NC)"
	$(COMPOSE_CMD) build opcua2mqtt
	@echo "$(GREEN)✓ OPC UA gateway built$(NC)"

build-detector: ## Build anomaly detector (when implemented)
	@echo "$(BLUE)Building anomaly detector...$(NC)"
	$(COMPOSE_CMD) build anomaly
	@echo "$(GREEN)✓ Anomaly detector built$(NC)"

build-policy: ## Build policy engine (when implemented)
	@echo "$(BLUE)Building policy engine...$(NC)"
	$(COMPOSE_CMD) build policy
	@echo "$(GREEN)✓ Policy engine built$(NC)"

build-dashboard: ## Build Streamlit dashboard (when implemented)
	@echo "$(BLUE)Building Streamlit dashboard...$(NC)"
	$(COMPOSE_CMD) build dashboard
	@echo "$(GREEN)✓ Dashboard built$(NC)"

## Service Management
start: ## Start all services
	@echo "$(BLUE)Starting GhostMesh services...$(NC)"
	$(COMPOSE_CMD) up -d
	@echo "$(GREEN)✓ All services started$(NC)"
	@echo "$(YELLOW)Dashboard: http://localhost:$(DASHBOARD_PORT)$(NC)"
	@echo "$(YELLOW)MQTT: localhost:$(MQTT_PORT)$(NC)"

start-mqtt: ## Start only MQTT broker
	@echo "$(BLUE)Starting MQTT broker...$(NC)"
	$(COMPOSE_CMD) up -d mosquitto
	@echo "$(GREEN)✓ MQTT broker started$(NC)"

stop: ## Stop all services
	@echo "$(BLUE)Stopping GhostMesh services...$(NC)"
	$(COMPOSE_CMD) down
	@echo "$(GREEN)✓ All services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting GhostMesh services...$(NC)"
	$(COMPOSE_CMD) restart
	@echo "$(GREEN)✓ All services restarted$(NC)"

## Monitoring and Logs
logs: ## Show logs for all services
	$(COMPOSE_CMD) logs -f

logs-mqtt: ## Show MQTT broker logs
	$(COMPOSE_CMD) logs -f mosquitto

logs-gateway: ## Show gateway logs (when implemented)
	$(COMPOSE_CMD) logs -f opcua2mqtt

logs-detector: ## Show detector logs (when implemented)
	$(COMPOSE_CMD) logs -f anomaly

logs-policy: ## Show policy engine logs (when implemented)
	$(COMPOSE_CMD) logs -f policy

logs-dashboard: ## Show dashboard logs (when implemented)
	$(COMPOSE_CMD) logs -f dashboard

status: ## Show service status
	@echo "$(BLUE)GhostMesh Service Status$(NC)"
	@echo "=========================="
	$(COMPOSE_CMD) ps
	@echo ""
	@echo "$(BLUE)Container Health$(NC)"
	@echo "=================="
	@$(CONTAINER_RUNTIME) ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

health: ## Check service health
	@echo "$(BLUE)Checking service health...$(NC)"
	@$(COMPOSE_CMD) ps --format "table {{.Name}}\t{{.Status}}"
	@echo ""
	@echo "$(BLUE)Health check results:$(NC)"
	@$(CONTAINER_RUNTIME) inspect $$($(COMPOSE_CMD) ps -q) --format "{{.Name}}: {{.State.Health.Status}}" 2>/dev/null || echo "Health checks not configured"

## Testing
test: ## Run all tests
	@echo "$(BLUE)Running GhostMesh tests...$(NC)"
	@echo ""
	@echo "$(BLUE)1. MQTT Connectivity Test$(NC)"
	@make test-mqtt
	@echo ""
	@echo "$(BLUE)2. Service Health Check$(NC)"
	@make health
	@echo ""
	@echo "$(GREEN)✓ All tests completed$(NC)"

test-mqtt: ## Test MQTT broker connectivity and permissions
	@echo "$(BLUE)Testing MQTT broker...$(NC)"
	@./scripts/test-mqtt.sh
	@echo "$(GREEN)✓ MQTT tests completed$(NC)"

test-unit: ## Run unit tests (when implemented)
	@echo "$(BLUE)Running unit tests...$(NC)"
	@echo "$(YELLOW)Unit tests not yet implemented$(NC)"

test-integration: ## Run integration tests (when implemented)
	@echo "$(BLUE)Running integration tests...$(NC)"
	@echo "$(YELLOW)Integration tests not yet implemented$(NC)"

## Code Quality
lint: ## Run linting on all code
	@echo "$(BLUE)Running code linting...$(NC)"
	@echo "$(YELLOW)Linting not yet implemented - will add when Python services are created$(NC)"

lint-python: ## Run Python linting (when implemented)
	@echo "$(BLUE)Running Python linting...$(NC)"
	@echo "$(YELLOW)Python linting not yet implemented$(NC)"

format: ## Format all code
	@echo "$(BLUE)Formatting code...$(NC)"
	@echo "$(YELLOW)Code formatting not yet implemented$(NC)"

format-python: ## Format Python code (when implemented)
	@echo "$(BLUE)Formatting Python code...$(NC)"
	@echo "$(YELLOW)Python formatting not yet implemented$(NC)"

## MQTT Specific
check-mqtt: ## Check MQTT broker status and connectivity
	@echo "$(BLUE)Checking MQTT broker...$(NC)"
	@if $(COMPOSE_CMD) ps mosquitto | grep -q "Up"; then \
		echo "$(GREEN)✓ MQTT broker is running$(NC)"; \
		$(CONTAINER_RUNTIME) exec $$($(COMPOSE_CMD) ps -q mosquitto) mosquitto_pub -h localhost -t "test/health" -m "health check" -q 1 && echo "$(GREEN)✓ MQTT connectivity OK$(NC)" || echo "$(RED)✗ MQTT connectivity failed$(NC)"; \
	else \
		echo "$(RED)✗ MQTT broker is not running$(NC)"; \
	fi

mqtt-users: ## Show MQTT user information
	@echo "$(BLUE)MQTT Users$(NC)"
	@echo "==========="
	@if [ -f mosquitto/passwd ]; then \
		echo "$(GREEN)Password file exists$(NC)"; \
		echo "Users configured:"; \
		awk -F: '{print "  - " $$1}' mosquitto/passwd; \
	else \
		echo "$(RED)Password file not found$(NC)"; \
		echo "Run 'make setup' to create users"; \
	fi

## Documentation
docs: ## Generate documentation
	@echo "$(BLUE)Documentation is available in docs/ directory$(NC)"
	@echo ""
	@echo "Available documentation:"
	@echo "  - docs/Project_README.md - Complete project documentation"
	@echo "  - docs/Architecture.md - System architecture"
	@echo "  - docs/Implementation_Plan.md - Development timeline"
	@echo "  - docs/MQTT_Configuration.md - MQTT setup guide"

docs-serve: ## Serve documentation locally (if mkdocs is available)
	@echo "$(BLUE)Serving documentation...$(NC)"
	@if command -v mkdocs >/dev/null 2>&1; then \
		mkdocs serve; \
	else \
		echo "$(YELLOW)MkDocs not installed. Install with: pip install mkdocs$(NC)"; \
		echo "$(BLUE)Documentation available in docs/ directory$(NC)"; \
	fi

## Development
dev: ## Start development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	@make setup
	@make start-mqtt
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "$(YELLOW)MQTT broker running on localhost:$(MQTT_PORT)$(NC)"

dev-logs: ## Show development logs
	@echo "$(BLUE)Development logs (MQTT broker):$(NC)"
	@make logs-mqtt

## Cleanup
clean: ## Clean up containers, images, and volumes
	@echo "$(BLUE)Cleaning up GhostMesh environment...$(NC)"
	$(COMPOSE_CMD) down -v --remove-orphans
	$(CONTAINER_RUNTIME) system prune -f
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

clean-logs: ## Clean up log files
	@echo "$(BLUE)Cleaning up log files...$(NC)"
	@rm -rf mosquitto/logs/*
	@echo "$(GREEN)✓ Log files cleaned$(NC)"

clean-data: ## Clean up data files (WARNING: removes all data)
	@echo "$(RED)WARNING: This will remove all MQTT data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@rm -rf mosquitto/data/*
	@echo "$(GREEN)✓ Data files cleaned$(NC)"

## Production
prod-build: ## Build production images
	@echo "$(BLUE)Building production images...$(NC)"
	$(COMPOSE_CMD) -f docker-compose.yml -f docker-compose.prod.yml build
	@echo "$(GREEN)✓ Production images built$(NC)"

prod-start: ## Start production environment
	@echo "$(BLUE)Starting production environment...$(NC)"
	$(COMPOSE_CMD) -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✓ Production environment started$(NC)"

## Quick Commands
quick-start: setup start ## Quick start: setup and start all services
quick-test: start test ## Quick test: start services and run tests
quick-restart: stop start ## Quick restart: stop and start all services

## Information
info: ## Show project information
	@echo "$(BLUE)GhostMesh Project Information$(NC)"
	@echo "================================"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Container Runtime: $(CONTAINER_RUNTIME)"
	@echo "Compose Command: $(COMPOSE_CMD)"
	@echo "MQTT Port: $(MQTT_PORT)"
	@echo "Dashboard Port: $(DASHBOARD_PORT)"
	@echo ""
	@echo "$(BLUE)Available Services:$(NC)"
	@echo "  - MQTT Broker (Mosquitto)"
	@echo "  - OPC UA Gateway (planned)"
	@echo "  - Anomaly Detector (planned)"
	@echo "  - Policy Engine (planned)"
	@echo "  - Streamlit Dashboard (planned)"
	@echo ""
	@echo "$(BLUE)Documentation:$(NC)"
	@echo "  - docs/Project_README.md"
	@echo "  - docs/Architecture.md"
	@echo "  - docs/Implementation_Plan.md"
	@echo "  - docs/MQTT_Configuration.md"
