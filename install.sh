#!/bin/bash

# BoxOfPorts Multi-Mode Installation Script
# Supports three installation modes for different use cases

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎁 BoxOfPorts Installation Script"
echo "=================================="
echo ""
echo "BoxOfPorts - SMS Gateway Management CLI for EJOIN Router Operators"
echo "Like 'Box of Rain', but for ports"
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! python3 --version | grep -E "Python 3\.(11|12|13)" > /dev/null; then
    echo "❌ Python 3.11 or higher required"
    echo "   Current version: $(python3 --version)"
    exit 1
fi
echo "✅ Python version OK: $(python3 --version)"

# Detect environment capabilities
echo "🔍 Detecting environment capabilities..."

HAS_PYENV=false
if command -v pyenv > /dev/null 2>&1; then
    HAS_PYENV=true
    echo "✅ pyenv detected"
fi

HAS_SUDO=false
if sudo -n true 2>/dev/null; then
    HAS_SUDO=true
    echo "✅ sudo access available"
elif [ "$(id -u)" = "0" ]; then
    HAS_SUDO=true
    echo "✅ running as root"
fi

echo ""
echo "🎯 Installation Mode Selection"
echo "=============================="
echo ""
echo "Choose your installation mode based on your use case:"
echo ""
echo "1. 🛠️  DEVELOPMENT MODE (pyenv + editable install)"
echo "   • For developers and operators who modify the code"
echo "   • Immediate code changes without reinstalling"
echo "   • Best for development and testing"
echo "   • Requires: pyenv"
if [ "$HAS_PYENV" = false ]; then
    echo "   ❌ pyenv not detected - install pyenv first"
fi
echo ""

echo "2. 👤 USER MODE (local installation)"
echo "   • For regular users who just want to use bop"
echo "   • No sudo required, installs to ~/.local/bin"
echo "   • Clean isolated installation"
echo "   • Recommended for most users"
echo ""

echo "3. 🌐 SYSTEM MODE (global installation)"
echo "   • For administrators managing multi-user systems"
echo "   • Installs to /usr/local/bin for all users"
echo "   • Requires sudo privileges"
echo "   • User data still remains private per user"
if [ "$HAS_SUDO" = false ]; then
    echo "   ❌ sudo access required but not available"
fi
echo ""

# Get user choice
while true; do
    read -p "Select installation mode (1-3): " choice
    case $choice in
        1)
            if [ "$HAS_PYENV" = false ]; then
                echo "❌ pyenv is required for development mode"
                echo "   Install pyenv first: https://github.com/pyenv/pyenv#installation"
                continue
            fi
            echo "🛠️  Installing in DEVELOPMENT MODE..."
            exec "$SCRIPT_DIR/install-dev.sh"
            ;;
        2)
            echo "👤 Installing in USER MODE..."
            exec "$SCRIPT_DIR/install-user.sh"
            ;;
        3)
            if [ "$HAS_SUDO" = false ]; then
                echo "❌ sudo access is required for system mode"
                continue
            fi
            echo "🌐 Installing in SYSTEM MODE..."
            exec "$SCRIPT_DIR/install-system.sh"
            ;;
        *)
            echo "❌ Invalid choice. Please enter 1, 2, or 3."
            ;;
    esac
done