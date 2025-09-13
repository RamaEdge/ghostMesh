#!/bin/bash

# GhostMesh LLM Server Startup Script
# Starts the llama.cpp server with TinyLlama model

cd /app

# Check if model file exists
if [ ! -f "/models/tinyllama-1.1b-chat.gguf" ]; then
    echo "ERROR: Model file not found at /models/tinyllama-1.1b-chat.gguf"
    echo "Please ensure the model was downloaded during build"
    exit 1
fi

# Check if server binary exists
if [ ! -f "/app/server" ]; then
    echo "ERROR: Server binary not found at /app/server"
    echo "Please ensure llama.cpp was built correctly"
    exit 1
fi

echo "Starting GhostMesh LLM Server..."
echo "Model: /models/tinyllama-1.1b-chat.gguf"
echo "Host: 0.0.0.0:8080"
echo "Context Size: 2048"
echo "Threads: 4"

# Start the llama.cpp server
exec ./server \
    -m /models/tinyllama-1.1b-chat.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    --ctx-size 2048 \
    --threads 4

