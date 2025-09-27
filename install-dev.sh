#!/bin/bash

# BoxOfPorts Development Installation Script
# Uses pyenv with editable installation for developers and operators

set -e  # Exit on any error

echo "🛠️  BoxOfPorts Development Installation"
echo "======================================="
echo ""
echo "This installation mode is perfect for:"
echo "• Developers modifying the BoxOfPorts source code"
echo "• Operators who need to customize functionality"
echo "• Testing and development environments"
echo ""

# Check if pyenv is available
if ! command -v pyenv > /dev/null 2>&1; then
    echo "❌ pyenv is required for development mode"
    echo ""
    echo "Install pyenv first:"
    echo "  macOS: brew install pyenv"
    echo "  Linux: curl https://pyenv.run | bash"
    echo "  Manual: https://github.com/pyenv/pyenv#installation"
    exit 1
fi

echo "✅ pyenv detected: $(pyenv --version)"

# Check Python version
CURRENT_PYTHON=$(pyenv version-name)
echo "📋 Current Python: $CURRENT_PYTHON"

# Verify Python version meets requirements
if ! python3 --version | grep -E "Python 3\.(11|12|13)" > /dev/null; then
    echo "❌ Python 3.11+ required for BoxOfPorts"
    echo "   Current version: $(python3 --version)"
    echo ""
    echo "Install a compatible Python version with pyenv:"
    echo "  pyenv install 3.12.11"
    echo "  pyenv local 3.12.11"
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

# Install in editable mode
echo ""
echo "📦 Installing BoxOfPorts in development mode..."
echo "   This creates an editable installation - code changes are immediately active"

# Upgrade pip first
python3 -m pip install --upgrade pip

# Install in editable mode with development dependencies
python3 -m pip install -e ".[dev]" --user

echo "✅ BoxOfPorts installed in editable mode"

# Check if ~/.local/bin is in PATH
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo ""
    echo "⚠️  ~/.local/bin is not in your PATH"
    echo "   Adding to shell configuration..."
    
    # Detect shell and add to appropriate config file
    SHELL_NAME=$(basename "$SHELL")
    case $SHELL_NAME in
        "bash")
            SHELL_RC="$HOME/.bashrc"
            [[ -f "$HOME/.bash_profile" ]] && SHELL_RC="$HOME/.bash_profile"
            ;;
        "zsh")
            SHELL_RC="$HOME/.zshrc"
            ;;
        *)
            SHELL_RC="$HOME/.profile"
            ;;
    esac
    
    if [[ -f "$SHELL_RC" ]] && ! grep -q "/.local/bin" "$SHELL_RC"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        echo "✅ Added ~/.local/bin to PATH in $SHELL_RC"
        echo "   Please restart your shell or run: source $SHELL_RC"
    fi
    
    # Add to current session
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create configuration directory
CONFIG_DIR="$HOME/.config/bop"
mkdir -p "$CONFIG_DIR"
echo "✅ Configuration directory: $CONFIG_DIR"

# Test installation
echo ""
echo "🧪 Testing installation..."

if command -v bop > /dev/null 2>&1; then
    echo "✅ boxofports command available"
    boxofports --version
else
    echo "⚠️  boxofports command not found in PATH"
    echo "   You may need to restart your shell"
    echo "   Or run: source $SHELL_RC"
fi

echo ""
echo "🎉 Development Installation Complete!"
echo "====================================="
echo ""
echo "✨ Development Benefits:"
echo "  • Code changes are immediately active (no reinstalling)"
echo "  • Perfect for testing and development"
echo "  • All standard boxofports commands work normally"
echo ""
echo "🚀 Quick Start:"
echo "  boxofports --version              # Check installation"
echo "  boxofports --help                 # Show all commands"
echo "  boxofports help-tree              # Explore complete command structure"
echo "  boxofports config add-profile     # Create your first gateway profile"
echo ""
echo "🔧 Shell Completion Setup (Recommended):"
echo "  boxofports --install-completion   # Enable TAB completion for all commands"
echo "  # Then restart your terminal or run: source ~/.zshrc"
echo "  # This helps navigate the complex CLI options easily!"
echo ""
echo "📁 Important Locations:"
echo "  Source code:    $(pwd)"
echo "  Config:         $CONFIG_DIR"
echo "  User data:      ~/.bop/"
echo ""
echo "💡 Development Tips:"
echo "  • Edit source code in: boxofports/"
echo "  • Changes take effect immediately"
echo "  • Use 'git' for version control"
echo "  • Run tests with: python -m pytest"
echo "  • With completion installed, try: boxofports <TAB> or boxofports sms <TAB>"
echo ""
echo "🎵 \"Box of rain will wash this thought away...\" 🎵"
