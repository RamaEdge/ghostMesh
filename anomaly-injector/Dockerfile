FROM python:3.14-slim

# Create non-root user
RUN groupadd -r injector && useradd -r -g injector injector

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Change ownership to non-root user
RUN chown -R injector:injector /app
USER injector

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import paho.mqtt.client as mqtt; client = mqtt.Client(); client.connect('mosquitto', 1883, 5); client.disconnect()" || exit 1

# Default command
CMD ["python", "main.py"]
