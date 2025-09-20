# ejoinctl - EJOIN Multi-WAN Router Management CLI
# Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.

FROM python:3.11-slim

# Set metadata
LABEL maintainer="Althea Signals Network LLC <support@altheamesh.com>"
LABEL version="1.0.0"
LABEL description="Professional CLI tool for EJOIN Multi-WAN Router HTTP API v2.2 management"
LABEL vendor="Althea Signals Network LLC"
LABEL url="https://altheamesh.com"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build dependencies
    gcc \
    g++ \
    # Network utilities for troubleshooting
    curl \
    wget \
    netcat-traditional \
    iputils-ping \
    telnet \
    # Git for potential future updates
    git \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r ejoinctl && useradd -r -g ejoinctl ejoinctl

# Copy requirements first for better caching
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application source code
COPY ejoinctl/ ./ejoinctl/
COPY tests/ ./tests/

# Create necessary directories
RUN mkdir -p /app/data /app/config /app/logs && \
    chown -R ejoinctl:ejoinctl /app

# Copy configuration examples
COPY server_access.csv ./config/gateways.csv.example

# Create entrypoint script
RUN cat > /app/entrypoint.sh << 'EOF'
#!/bin/bash
set -e

# Set default environment variables if not provided
export EJOINCTL_DATA_DIR=${EJOINCTL_DATA_DIR:-/app/data}
export EJOINCTL_CONFIG_DIR=${EJOINCTL_CONFIG_DIR:-/app/config}
export EJOINCTL_LOG_LEVEL=${EJOINCTL_LOG_LEVEL:-INFO}

# Create directories if they don't exist
mkdir -p "$EJOINCTL_DATA_DIR" "$EJOINCTL_CONFIG_DIR"

# If no command provided, show help
if [ $# -eq 0 ]; then
    exec python -m ejoinctl.cli --help
fi

# Execute the command
exec python -m ejoinctl.cli "$@"
EOF

# Set proper permissions
RUN chmod +x /app/entrypoint.sh && \
    chown -R ejoinctl:ejoinctl /app

# Switch to non-root user
USER ejoinctl

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import ejoinctl; print('ejoinctl is healthy')" || exit 1

# Expose potential web interface port (future feature)
EXPOSE 8080

# Set volumes for persistent data
VOLUME ["/app/data", "/app/config", "/app/logs"]

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["--help"]