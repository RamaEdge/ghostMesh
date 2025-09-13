# GhostMesh AI Explainer Service Dockerfile
# Containerized deployment for the AI Explainer service

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY explainer.py .

# Create non-root user for security
RUN useradd -m -u 1000 explainer && chown -R explainer:explainer /app
USER explainer

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import paho.mqtt.client as mqtt; client = mqtt.Client(); client.connect('localhost', 1883, 5); client.disconnect()" || exit 1

# Expose port (if needed for future HTTP API)
EXPOSE 8080

# Run the service
CMD ["python", "explainer.py"]
