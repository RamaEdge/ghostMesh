#!/bin/bash
# Download Qwen-0.5B model for GhostMesh LLM server

set -e

MODEL_DIR="/models"
MODEL_NAME="qwen-0.5b-instruct"
MODEL_URL="https://huggingface.co/Qwen/Qwen-0.5B-Instruct-GGUF/resolve/main/qwen-0.5b-instruct-q4_k_m.gguf"

echo "Downloading Qwen-0.5B model for GhostMesh LLM server..."

# Create models directory if it doesn't exist
mkdir -p "$MODEL_DIR"

# Download the model if it doesn't exist
if [ ! -f "$MODEL_DIR/$MODEL_NAME.gguf" ]; then
    echo "Downloading model from $MODEL_URL..."
    wget -O "$MODEL_DIR/$MODEL_NAME.gguf" "$MODEL_URL"
    echo "Model downloaded successfully!"
else
    echo "Model already exists at $MODEL_DIR/$MODEL_NAME.gguf"
fi

# Verify the model file
if [ -f "$MODEL_DIR/$MODEL_NAME.gguf" ]; then
    echo "Model verification:"
    ls -lh "$MODEL_DIR/$MODEL_NAME.gguf"
    echo "Model is ready for use!"
else
    echo "Error: Model download failed!"
    exit 1
fi
