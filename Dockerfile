# BoxOfPorts - SMS Gateway Management CLI
# Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.

FROM python:3.11-slim

# Set metadata
LABEL maintainer="Althea Signals Network LLC <support@altheasignals.net>"
LABEL version="1.0.0"
LABEL description="BoxOfPorts - SMS Gateway Management CLI for EJOIN Router Operators"
LABEL vendor="Althea Signals Network LLC"
LABEL url="https://altheasignals.net"

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
RUN groupadd -r boxofports && useradd -r -g boxofports -m boxofports

# Copy requirements first for better caching
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Copy application source code
COPY boxofports/ ./boxofports/
COPY tests/ ./tests/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p /app/data /app/config /app/logs && \
    chown -R boxofports:boxofports /app

# Copy configuration examples
COPY server_access.csv ./config/gateways.csv.example

# Copy entrypoint script
COPY docker-entrypoint.sh /app/entrypoint.sh

# Set proper permissions
RUN chmod +x /app/entrypoint.sh && \
    chown -R boxofports:boxofports /app

# Switch to non-root user
USER boxofports

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import boxofports; print('boxofports is healthy')" || exit 1

# Expose potential web interface port (future feature)
EXPOSE 8080

# Set volumes for persistent data
VOLUME ["/app/data", "/app/config", "/app/logs"]

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["--help"]