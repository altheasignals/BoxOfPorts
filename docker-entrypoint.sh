#!/bin/bash
set -e

# Set default environment variables if not provided
export BOXOFPORTS_DATA_DIR=${BOXOFPORTS_DATA_DIR:-/app/data}
export BOXOFPORTS_CONFIG_DIR=${BOXOFPORTS_CONFIG_DIR:-/app/config}
export BOXOFPORTS_LOG_LEVEL=${BOXOFPORTS_LOG_LEVEL:-INFO}

# Create directories if they don't exist
mkdir -p "$BOXOFPORTS_DATA_DIR" "$BOXOFPORTS_CONFIG_DIR"

# If no command provided, show help
if [ $# -eq 0 ]; then
    exec boxofports --help
fi

# Execute the command
exec boxofports "$@"
