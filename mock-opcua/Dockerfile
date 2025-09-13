FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY simple_mock_server.py .

# Create non-root user
RUN useradd -m -u 1000 mockuser && chown -R mockuser:mockuser /app
USER mockuser

# Expose OPC UA port
EXPOSE 4840

# Run the simple mock server
CMD ["python", "simple_mock_server.py"]
