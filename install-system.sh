#!/bin/bash

# BoxOfPorts System-Wide Installation Script
# Installs BoxOfPorts globally for all users via /usr/local/bin

set -e  # Exit on any error

echo "🌐 BoxOfPorts System-Wide Installation"
echo "======================================"
echo ""
echo "This installation mode is perfect for:"
echo "• System administrators managing multi-user environments"
echo "• Servers where multiple users need access to boxofports"
echo "• Enterprise deployments"
echo ""
echo "⚠️  Important Notes:"
echo "• Requires sudo/root privileges"
echo "• Installs boxofports command globally for all users"
echo "• User data (configs, databases) remain private per user"
echo ""

# Check if running with sudo privileges
if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
    echo "❌ This installation requires sudo privileges"
    echo "   Please run with: sudo ./install-system.sh"
    echo "   Or ensure you have passwordless sudo access"
    exit 1
fi

echo "✅ Administrative privileges confirmed"

# Check Python version
echo "📋 Checking Python version..."
if ! python3 --version | grep -E "Python 3\.(11|12|13)" > /dev/null; then
    echo "❌ Python 3.11 or higher required"
    echo "   Current version: $(python3 --version)"
    exit 1
fi
echo "✅ Python version OK: $(python3 --version)"

# Check if we're in the BoxOfPorts source directory
if [[ ! -f "pyproject.toml" ]] || ! grep -q "boxofports" pyproject.toml; then
    echo "❌ Please run this script from the BoxOfPorts source directory"
    echo "   Expected files: pyproject.toml, boxofports/ directory"
    exit 1
fi

echo "✅ BoxOfPorts source directory detected"

# Create system-wide installation directory
INSTALL_DIR="/opt/boxofports"
VENV_PATH="$INSTALL_DIR/venv"
BIN_PATH="/usr/local/bin/boxofports"

echo ""
echo "📦 Installing BoxOfPorts system-wide..."
echo "   Installation directory: $INSTALL_DIR"
echo "   Global command: $BIN_PATH"

# Remove existing installation if present
if [[ -d "$INSTALL_DIR" ]]; then
    echo "⚠️  Removing existing installation..."
    sudo rm -rf "$INSTALL_DIR"
fi

# Create installation directory
sudo mkdir -p "$INSTALL_DIR"

# Create virtual environment as root
echo "🐍 Creating system virtual environment..."
sudo python3 -m venv "$VENV_PATH"

# Install BoxOfPorts in the system venv
echo "📦 Installing BoxOfPorts..."
sudo "$VENV_PATH/bin/pip" install --upgrade pip
sudo "$VENV_PATH/bin/pip" install -e .

echo "✅ BoxOfPorts installed in system environment"

# Create global wrapper script
echo "🔗 Creating global command wrapper..."
sudo tee "$BIN_PATH" > /dev/null << EOF
#!/bin/bash
# BoxOfPorts Global System Wrapper
# Installed: $(date)

# Use the system-wide virtual environment
source "$VENV_PATH/bin/activate"

# Run BoxOfPorts with all user arguments
# User data will be stored in each user's home directory
python -m boxofports "\$@"
EOF

# Make executable
sudo chmod +x "$BIN_PATH"
echo "✅ Global command created: $BIN_PATH"

# Set proper ownership and permissions
sudo chown -R root:root "$INSTALL_DIR"
sudo chmod -R 755 "$INSTALL_DIR"

# Test installation
echo ""
echo "🧪 Testing system installation..."

if command -v boxofports > /dev/null 2>&1; then
    echo "✅ boxofports command available globally"
    
    # Test as regular user if not root
    if [[ $EUID -eq 0 ]] && command -v sudo > /dev/null 2>&1; then
        # Find a regular user to test with
        TEST_USER=$(getent passwd | grep '/home/' | head -1 | cut -d: -f1 2>/dev/null || echo "")
        if [[ -n "$TEST_USER" ]]; then
            echo "🧪 Testing as user: $TEST_USER"
            sudo -u "$TEST_USER" boxofports --version
        fi
    else
        boxofports --version
    fi
else
    echo "❌ Installation verification failed"
    exit 1
fi

echo ""
echo "🎉 System-Wide Installation Complete!"
echo "===================================="
echo ""
echo "✨ System Benefits:"
echo "  • boxofports command available to all users"
echo "  • Centralized maintenance and updates"
echo "  • Consistent version across the system"
echo "  • User data remains private per user"
echo ""
echo "🚀 Usage for Users:"
echo "  boxofports --version              # Check installation"
echo "  boxofports --help                 # Show all commands"
echo "  boxofports help-tree              # Explore complete command structure"
echo "  boxofports config add-profile     # Create personal gateway profile"
echo ""
echo "🔧 Shell Completion (Per User):"
echo "  boxofports --install-completion   # Each user should run this"
echo "  # Restart terminal after running the above command"
echo "  # Enables TAB completion for all commands and options"
echo ""
echo "📁 Important Locations:"
echo "  System install:    $INSTALL_DIR"
echo "  Global command:    $BIN_PATH"
echo "  User configs:      ~/.config/boxofports/ (per user)"
echo "  User data:         ~/.boxofports/ (per user)"
echo ""
echo "🔧 Administrator Notes:"
echo "  • Update: Re-run this script from new source"
echo "  • Remove: sudo rm -rf $INSTALL_DIR $BIN_PATH"
echo "  • Users keep their individual configurations"
echo "  • No user data is shared between accounts"
echo ""
echo "💡 Security Notes:"
echo "  • Each user's data remains in their home directory"
echo "  • No shared configuration or data between users"
echo "  • Users cannot access other users' gateway profiles"
echo ""
echo "🎵 \"Box of rain will wash this thought away...\" 🎵"