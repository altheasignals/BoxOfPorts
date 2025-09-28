# BoxOfPorts - SMS Gateway Management CLI
# Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.

FROM python:3.11-slim

# Build arguments for version info and labels
ARG VERSION=unknown
ARG BUILD_DATE=unknown
ARG GIT_SHA=unknown

# Set metadata with dynamic values
LABEL maintainer="Althea Signals Network LLC <support@altheasignals.net>"
LABEL org.opencontainers.image.title="BoxOfPorts"
LABEL org.opencontainers.image.description="SMS Gateway Management CLI for EJOIN Router Operators"
LABEL org.opencontainers.image.vendor="Althea Signals Network LLC"
LABEL org.opencontainers.image.url="https://altheasignals.net"
LABEL org.opencontainers.image.version="1.2.12"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${GIT_SHA}"
LABEL org.opencontainers.image.source="https://github.com/altheasignals/boxofports"
LABEL org.opencontainers.image.documentation="https://github.com/altheasignals/boxofports/blob/main/README.md"
# BoxOfPorts specific labels
LABEL io.boxofports.version="${VERSION}"
LABEL io.boxofports.built-by="GitHub Actions"

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

# Copy application source code
COPY boxofports/ ./boxofports/
COPY tests/ ./tests/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p /app/data /app/config /app/logs && \
    chown -R boxofports:boxofports /app

# Copy configuration examples (create empty example)
RUN echo "# Example gateway configuration file" > ./config/gateways.csv.example && \
    echo "# Format: name,host,port,username,password" >> ./config/gateways.csv.example && \
    echo "# gateway1,192.168.1.100,22,admin,password" >> ./config/gateways.csv.example

# Copy entrypoint script
COPY docker-entrypoint.sh /app/entrypoint.sh

# Set proper permissions
RUN chmod +x /app/entrypoint.sh && \
    chown -R boxofports:boxofports /app

# Switch to non-root user
USER boxofports

# Add version info to environment for runtime access
ENV BOXOFPORTS_VERSION=${VERSION}
ENV BOXOFPORTS_BUILD_DATE=${BUILD_DATE}
ENV BOXOFPORTS_GIT_SHA=${GIT_SHA}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /usr/local/bin/boxofports --version || exit 1

# Expose potential web interface port (future feature)
EXPOSE 8080

# Set volumes for persistent data
VOLUME ["/app/data", "/app/config", "/app/logs"]

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["--help"]