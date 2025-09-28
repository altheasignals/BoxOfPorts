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

# Show current GitHub versions available for installation
show_version_comparison() {
    local github_stable="unknown"
    local github_dev="unknown"
    
    # Fetch GitHub versions if curl is available
    if command -v curl >/dev/null 2>&1; then
        github_stable=$(curl -s "https://api.github.com/repos/altheasignals/boxofports/releases/latest" 2>/dev/null | 
                       grep '"tag_name"' | cut -d'"' -f4 | sed 's/^v//' 2>/dev/null || echo "unknown")
        github_dev=$(curl -s "https://raw.githubusercontent.com/altheasignals/boxofports/main/version_registry.json" 2>/dev/null | 
                    grep '"development"' | head -1 | cut -d'"' -f4 2>/dev/null || echo "unknown")
    fi
    
    # Display available versions if we have version info
    if [[ "$github_stable" != "unknown" ]] || [[ "$github_dev" != "unknown" ]]; then
        echo "📊 Available Versions"
        echo "==================="
        printf "%-15s %-10s\n" "Track" "Version"
        printf "%-15s %-10s\n" "-----" "-------"
        printf "%-15s %-10s\n" "Stable:" "v$github_stable"
        printf "%-15s %-10s\n" "Development:" "v$github_dev"
        echo ""
    fi
}

show_version_comparison

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
echo "   • For regular users who just want to use boxofports"
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