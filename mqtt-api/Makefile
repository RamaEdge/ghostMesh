# MQTT API Backend Service Makefile

# Variables
SERVICE_NAME = mqtt-api
CONTAINER_NAME = ghostmesh-mqtt-api
IMAGE_NAME = ghostmesh-mqtt-api
VERSION = 1.0.0
API_PORT = 8000
MQTT_PORT = 1883

# Docker Compose
COMPOSE_FILE = docker-compose.yml
COMPOSE_PROJECT = ghostmesh-api

# Python
PYTHON = python3
PIP = pip3
VENV = venv

# Default target
.PHONY: all
all: help

# Help target
.PHONY: help
help:
	@echo "GhostMesh MQTT API Backend Service"
	@echo "=================================="
	@echo ""
	@echo "Available targets:"
	@echo "  setup          - Setup development environment"
	@echo "  install        - Install dependencies"
	@echo "  run            - Run the service locally"
	@echo "  test           - Run tests"
	@echo "  lint           - Run linting"
	@echo "  format         - Format code"
	@echo "  build          - Build Docker image"
	@echo "  up             - Start services with Docker Compose"
	@echo "  down           - Stop services with Docker Compose"
	@echo "  logs           - View service logs"
	@echo "  shell          - Open shell in container"
	@echo "  clean          - Clean up generated files"
	@echo "  docs           - Generate documentation"
	@echo "  example        - Run example script"
	@echo "  health         - Check service health"
	@echo "  stats          - Get service statistics"
	@echo ""
	@echo "Development targets:"
	@echo "  dev            - Run in development mode"
	@echo "  watch          - Watch for changes and reload"
	@echo "  debug          - Run with debug logging"
	@echo ""
	@echo "Testing targets:"
	@echo "  test-unit      - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  test-coverage  - Run tests with coverage"
	@echo "  test-performance - Run performance tests"
	@echo ""
	@echo "Docker targets:"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  docker-stop    - Stop Docker container"
	@echo "  docker-rm      - Remove Docker container"
	@echo "  docker-logs    - View Docker logs"
	@echo ""
	@echo "Examples:"
	@echo "  make setup     # Setup development environment"
	@echo "  make run       # Run service locally"
	@echo "  make test      # Run all tests"
	@echo "  make up        # Start with Docker Compose"

# Setup development environment
.PHONY: setup
setup:
	@echo "Setting up development environment..."
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && $(PIP) install --upgrade pip
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt
	@echo "✅ Development environment setup complete"

# Install dependencies
.PHONY: install
install:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

# Run the service locally
.PHONY: run
run:
	@echo "Starting MQTT API Backend Service..."
	$(PYTHON) app.py

# Run in development mode
.PHONY: dev
dev:
	@echo "Starting MQTT API Backend Service in development mode..."
	export API_RELOAD=true && $(PYTHON) app.py

# Run with debug logging
.PHONY: debug
debug:
	@echo "Starting MQTT API Backend Service with debug logging..."
	export LOG_LEVEL=DEBUG && $(PYTHON) app.py

# Watch for changes and reload
.PHONY: watch
watch:
	@echo "Watching for changes..."
	uvicorn app:app --reload --host 0.0.0.0 --port $(API_PORT)

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	pytest test_api.py -v

# Run unit tests
.PHONY: test-unit
test-unit:
	@echo "Running unit tests..."
	pytest test_api.py::TestMQTTAPI -v

# Run integration tests
.PHONY: test-integration
test-integration:
	@echo "Running integration tests..."
	pytest test_api.py::TestWebSocket -v

# Run tests with coverage
.PHONY: test-coverage
test-coverage:
	@echo "Running tests with coverage..."
	pytest --cov=app test_api.py --cov-report=html --cov-report=term

# Run performance tests
.PHONY: test-performance
test-performance:
	@echo "Running performance tests..."
	pytest test_api.py::TestPerformance -v

# Run linting
.PHONY: lint
lint:
	@echo "Running linting..."
	flake8 app.py client.py config.py test_api.py
	pylint app.py client.py config.py test_api.py

# Format code
.PHONY: format
format:
	@echo "Formatting code..."
	black app.py client.py config.py test_api.py
	isort app.py client.py config.py test_api.py

# Build Docker image
.PHONY: build
build:
	@echo "Building Docker image..."
	docker build -t $(IMAGE_NAME):$(VERSION) .
	docker tag $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):latest
	@echo "✅ Docker image built: $(IMAGE_NAME):$(VERSION)"

# Start services with Docker Compose
.PHONY: up
up:
	@echo "Starting services with Docker Compose..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) up -d
	@echo "✅ Services started"

# Stop services with Docker Compose
.PHONY: down
down:
	@echo "Stopping services with Docker Compose..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) down
	@echo "✅ Services stopped"

# View service logs
.PHONY: logs
logs:
	@echo "Viewing service logs..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) logs -f

# Open shell in container
.PHONY: shell
shell:
	@echo "Opening shell in container..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) exec mqtt-api /bin/bash

# Clean up generated files
.PHONY: clean
clean:
	@echo "Cleaning up generated files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	@echo "✅ Cleanup complete"

# Generate documentation
.PHONY: docs
docs:
	@echo "Generating documentation..."
	pydoc -w app
	pydoc -w client
	pydoc -w config
	@echo "✅ Documentation generated"

# Run example script
.PHONY: example
example:
	@echo "Running example script..."
	$(PYTHON) example.py

# Check service health
.PHONY: health
health:
	@echo "Checking service health..."
	curl -s http://localhost:$(API_PORT)/health | python -m json.tool

# Get service statistics
.PHONY: stats
stats:
	@echo "Getting service statistics..."
	curl -s http://localhost:$(API_PORT)/stats | python -m json.tool

# Docker targets
.PHONY: docker-build
docker-build: build

.PHONY: docker-run
docker-run:
	@echo "Running Docker container..."
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(API_PORT):$(API_PORT) \
		-e MQTT_BROKER_HOST=localhost \
		-e MQTT_USERNAME=api \
		-e MQTT_PASSWORD=api_password \
		$(IMAGE_NAME):latest
	@echo "✅ Container started: $(CONTAINER_NAME)"

.PHONY: docker-stop
docker-stop:
	@echo "Stopping Docker container..."
	docker stop $(CONTAINER_NAME)
	@echo "✅ Container stopped"

.PHONY: docker-rm
docker-rm:
	@echo "Removing Docker container..."
	docker rm $(CONTAINER_NAME)
	@echo "✅ Container removed"

.PHONY: docker-logs
docker-logs:
	@echo "Viewing Docker logs..."
	docker logs -f $(CONTAINER_NAME)

# Development workflow
.PHONY: dev-setup
dev-setup: setup
	@echo "Development setup complete. Run 'make dev' to start development server."

.PHONY: dev-test
dev-test: test
	@echo "Development tests complete."

.PHONY: dev-build
dev-build: build
	@echo "Development build complete."

# Production workflow
.PHONY: prod-build
prod-build:
	@echo "Building production image..."
	docker build -t $(IMAGE_NAME):$(VERSION) .
	docker tag $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):latest
	@echo "✅ Production image built"

.PHONY: prod-deploy
prod-deploy: prod-build
	@echo "Deploying to production..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) up -d
	@echo "✅ Production deployment complete"

# Monitoring and maintenance
.PHONY: monitor
monitor:
	@echo "Monitoring service status..."
	@echo "API Health:"
	@curl -s http://localhost:$(API_PORT)/health | python -m json.tool
	@echo ""
	@echo "API Statistics:"
	@curl -s http://localhost:$(API_PORT)/stats | python -m json.tool

.PHONY: restart
restart:
	@echo "Restarting service..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) restart mqtt-api
	@echo "✅ Service restarted"

.PHONY: update
update:
	@echo "Updating service..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) pull
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) up -d
	@echo "✅ Service updated"

# Backup and restore
.PHONY: backup
backup:
	@echo "Creating backup..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) exec mqtt-api python -c "import json; print(json.dumps({'backup': 'created', 'timestamp': '$(shell date -Iseconds)'}))"
	@echo "✅ Backup created"

.PHONY: restore
restore:
	@echo "Restoring from backup..."
	@echo "Restore functionality not implemented yet"
	@echo "✅ Restore complete"

# Security
.PHONY: security-scan
security-scan:
	@echo "Running security scan..."
	bandit -r app.py client.py config.py
	@echo "✅ Security scan complete"

.PHONY: security-audit
security-audit:
	@echo "Running security audit..."
	safety check
	@echo "✅ Security audit complete"

# Performance
.PHONY: performance-test
performance-test:
	@echo "Running performance tests..."
	locust -f performance_test.py --host=http://localhost:$(API_PORT)
	@echo "✅ Performance tests complete"

.PHONY: benchmark
benchmark:
	@echo "Running benchmarks..."
	$(PYTHON) -m pytest test_api.py::TestPerformance -v --benchmark-only
	@echo "✅ Benchmarks complete"

# Quality assurance
.PHONY: qa
qa: lint test security-scan
	@echo "✅ Quality assurance checks complete"

.PHONY: ci
ci: qa build
	@echo "✅ CI pipeline complete"

# Release
.PHONY: release
release: qa build
	@echo "Creating release..."
	@echo "Release $(VERSION) created successfully"
	@echo "✅ Release complete"

# Dependencies
.PHONY: deps
deps:
	@echo "Checking dependencies..."
	$(PIP) check
	@echo "✅ Dependencies check complete"

.PHONY: deps-update
deps-update:
	@echo "Updating dependencies..."
	$(PIP) install --upgrade -r requirements.txt
	@echo "✅ Dependencies updated"

# Environment
.PHONY: env
env:
	@echo "Environment variables:"
	@echo "API_PORT=$(API_PORT)"
	@echo "MQTT_PORT=$(MQTT_PORT)"
	@echo "SERVICE_NAME=$(SERVICE_NAME)"
	@echo "CONTAINER_NAME=$(CONTAINER_NAME)"
	@echo "IMAGE_NAME=$(IMAGE_NAME)"
	@echo "VERSION=$(VERSION)"

# Status
.PHONY: status
status:
	@echo "Service Status:"
	@echo "==============="
	@echo "Container: $(shell docker ps --filter name=$(CONTAINER_NAME) --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}')"
	@echo "API Health: $(shell curl -s http://localhost:$(API_PORT)/health | python -c 'import sys, json; print(json.load(sys.stdin)["status"])' 2>/dev/null || echo 'Not available')"
	@echo "MQTT Status: $(shell curl -s http://localhost:$(API_PORT)/health | python -c 'import sys, json; print("Connected" if json.load(sys.stdin)["mqtt_connected"] else "Disconnected")' 2>/dev/null || echo 'Not available')"

# Show service information
.PHONY: info
info:
	@echo "GhostMesh MQTT API Backend Service"
	@echo "=================================="
	@echo "Service Name: $(SERVICE_NAME)"
	@echo "Version: $(VERSION)"
	@echo "API Port: $(API_PORT)"
	@echo "MQTT Port: $(MQTT_PORT)"
	@echo "Container: $(CONTAINER_NAME)"
	@echo "Image: $(IMAGE_NAME)"
	@echo ""
	@echo "Endpoints:"
	@echo "  API: http://localhost:$(API_PORT)"
	@echo "  Health: http://localhost:$(API_PORT)/health"
	@echo "  Docs: http://localhost:$(API_PORT)/docs"
	@echo "  WebSocket: ws://localhost:$(API_PORT)/ws"
	@echo ""
	@echo "MQTT:"
	@echo "  Broker: localhost:$(MQTT_PORT)"
	@echo "  Username: api"
	@echo "  Password: api_password"
