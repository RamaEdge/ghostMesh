# GhostMesh LLM Server
# Multi-stage build for llama.cpp server with local LLM inference

# Build stage - includes build tools and downloads model
FROM ubuntu:24.04 AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    libcurl4-openssl-dev \
    libssl-dev \
    libc6-dev \
    libstdc++6 \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone and build llama.cpp from source with static linking
RUN git clone https://github.com/ggerganov/llama.cpp.git && \
    cd llama.cpp && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF && \
    make -j$(nproc) llama-server && \
    cp bin/llama-server /app/server && \
    ldd /app/server && \
    echo "Binary dependencies check:" && \
    /app/server --help | head -5 && \
    cd /app && \
    rm -rf llama.cpp

# Create models directory and download model
RUN mkdir -p /models

# Copy authentication file (if it exists) - this will be removed in final stage
COPY .hf_token* /app/

# Download the model with authentication
RUN if [ -f /app/.hf_token ]; then \
        . /app/.hf_token && \
        wget --header="Authorization: Bearer $HF_TOKEN" \
             -O /models/tinyllama-1.1b-chat.gguf \
             "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"; \
    else \
        echo "Warning: No .hf_token file found. Model download may fail." && \
        wget -O /models/tinyllama-1.1b-chat.gguf \
             "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"; \
    fi

# Runtime stage - minimal image without build tools or tokens
FROM ubuntu:24.04 AS runtime

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libssl3 \
    libc6 \
    libstdc++6 \
    libgcc-s1 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy built binary and model from builder stage
COPY --from=builder /app/server /app/server
COPY --from=builder /models /models

# Copy and setup startup script
COPY start-server.sh /app/start-server.sh
RUN chmod +x /app/start-server.sh

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the server
CMD ["/app/start-server.sh"]
