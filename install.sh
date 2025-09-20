#!/bin/bash
# ejoinctl Installation Script
# Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.
#
# Cross-platform installation script for ejoinctl
# Supports macOS, Linux, and Windows (via WSL)

set -e

# Colors for output
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
RESET='\033[0m'

# Project information
PROJECT_NAME="ejoinctl"
VERSION="1.0.0"
AUTHOR="Althea Signals Network LLC"
MIN_PYTHON_VERSION="3.11"

# Functions
log() {
    echo -e "${GREEN}[INFO]${RESET} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${RESET} $1"
}

error() {
    echo -e "${RED}[ERROR]${RESET} $1"
    exit 1
}

banner() {
    echo -e "${BLUE}"
    echo "════════════════════════════════════════════════════════════════"
    echo "  ejoinctl v${VERSION} - EJOIN Gateway Management CLI"
    echo "  Developed by ${AUTHOR}"
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${RESET}"
}

# Check if running as root (not recommended)
check_root() {
    if [[ $EUID -eq 0 ]]; then
        warn "Running as root is not recommended!"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Installation cancelled"
        fi
    fi
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ -n "$WSL_DISTRO_NAME" ]]; then
        OS="Windows/WSL"
    else
        warn "Unknown operating system: $OSTYPE"
        OS="Unknown"
    fi
    log "Detected OS: $OS"
}

# Check Python version
check_python() {
    log "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        error "Python is not installed. Please install Python ${MIN_PYTHON_VERSION}+ first."
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log "Found Python $PYTHON_VERSION"
    
    # Version comparison
    if [[ $(echo -e "${PYTHON_VERSION}\n${MIN_PYTHON_VERSION}" | sort -V | head -n1) != "${MIN_PYTHON_VERSION}" ]]; then
        error "Python ${MIN_PYTHON_VERSION}+ required. Found: ${PYTHON_VERSION}"
    fi
    
    log "✓ Python version check passed"
}

# Check pip installation
check_pip() {
    log "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        error "pip is not installed. Please install pip first."
    fi
    
    log "✓ Found pip: $PIP_CMD"
}

# Install system dependencies (if needed)
install_system_deps() {
    log "Checking system dependencies..."
    
    case $OS in
        "macOS")
            # Check for Homebrew
            if ! command -v brew &> /dev/null; then
                warn "Homebrew not found. Some features may require additional setup."
            fi
            ;;
        "Linux")
            # Check for package managers and install dependencies
            if command -v apt-get &> /dev/null; then
                log "Installing dependencies with apt..."
                sudo apt-get update
                sudo apt-get install -y python3-pip python3-venv build-essential
            elif command -v yum &> /dev/null; then
                log "Installing dependencies with yum..."
                sudo yum install -y python3-pip python3-devel gcc
            elif command -v pacman &> /dev/null; then
                log "Installing dependencies with pacman..."
                sudo pacman -S --noconfirm python-pip base-devel
            else
                warn "Unknown package manager. You may need to install dependencies manually."
            fi
            ;;
        "Windows/WSL")
            log "WSL detected. Using Linux package manager..."
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y python3-pip python3-venv build-essential
            fi
            ;;
    esac
    
    log "✓ System dependencies check complete"
}

# Create virtual environment
create_venv() {
    log "Creating virtual environment..."
    
    VENV_DIR="$HOME/.ejoinctl/venv"
    mkdir -p "$(dirname "$VENV_DIR")"
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    log "✓ Virtual environment created at $VENV_DIR"
}

# Install ejoinctl
install_ejoinctl() {
    log "Installing ejoinctl..."
    
    # If we're in the source directory, install from local
    if [[ -f "pyproject.toml" ]] && grep -q "ejoinctl" pyproject.toml; then
        log "Installing from local source..."
        pip install -e .
    else
        # For future: install from package repository
        error "Please run this script from the ejoinctl source directory"
    fi
    
    log "✓ ejoinctl installation complete"
}

# Create wrapper script
create_wrapper() {
    log "Creating wrapper script..."
    
    WRAPPER_SCRIPT="$HOME/.local/bin/ejoinctl"
    mkdir -p "$(dirname "$WRAPPER_SCRIPT")"
    
    cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# ejoinctl wrapper script
# Copyright (c) 2025 Althea Signals Network LLC

source "$HOME/.ejoinctl/venv/bin/activate"
python -m ejoinctl.cli "\$@"
EOF
    
    chmod +x "$WRAPPER_SCRIPT"
    
    log "✓ Wrapper script created at $WRAPPER_SCRIPT"
}

# Update shell configuration
update_shell_config() {
    log "Updating shell configuration..."
    
    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    
    case $SHELL_NAME in
        "bash")
            SHELL_RC="$HOME/.bashrc"
            [[ -f "$HOME/.bash_profile" ]] && SHELL_RC="$HOME/.bash_profile"
            ;;
        "zsh")
            SHELL_RC="$HOME/.zshrc"
            ;;
        "fish")
            SHELL_RC="$HOME/.config/fish/config.fish"
            ;;
        *)
            warn "Unknown shell: $SHELL_NAME. You may need to update PATH manually."
            return
            ;;
    esac
    
    # Add to PATH if not already there
    if [[ -f "$SHELL_RC" ]] && ! grep -q "$HOME/.local/bin" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# Added by ejoinctl installer" >> "$SHELL_RC"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        log "✓ Updated $SHELL_RC"
    fi
    
    # Source the config for current session
    export PATH="$HOME/.local/bin:$PATH"
}

# Create configuration directory
create_config() {
    log "Creating configuration directory..."
    
    CONFIG_DIR="$HOME/.config/ejoinctl"
    mkdir -p "$CONFIG_DIR"
    
    # Copy example configuration if available
    if [[ -f "server_access.csv" ]]; then
        cp "server_access.csv" "$CONFIG_DIR/gateways.csv.example"
        log "✓ Example gateway configuration copied"
    fi
    
    log "✓ Configuration directory created at $CONFIG_DIR"
}

# Test installation
test_installation() {
    log "Testing installation..."
    
    if command -v ejoinctl &> /dev/null; then
        ejoinctl --help > /dev/null
        log "✓ ejoinctl is working correctly"
    else
        warn "ejoinctl command not found in PATH. You may need to restart your shell."
        log "Try running: source ~/.bashrc (or ~/.zshrc)"
    fi
}

# Show completion message
show_completion() {
    echo -e "${GREEN}"
    echo "════════════════════════════════════════════════════════════════"
    echo "  Installation Complete!"
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${RESET}"
    echo "ejoinctl has been successfully installed!"
    echo ""
    echo "Quick start commands:"
    echo "  ejoinctl --help                 - Show help"
    echo "  ejoinctl test-connection        - Test gateway connection"
    echo ""
    echo "Configuration:"
    echo "  Config directory: ~/.config/ejoinctl"
    echo "  Virtual environment: ~/.ejoinctl/venv"
    echo ""
    echo "Documentation:"
    echo "  README.md - Main documentation"
    echo "  DEPLOYMENT.md - Deployment guide"
    echo "  USAGE_GUIDE.md - Complete usage examples"
    echo ""
    echo "Support: support@altheamesh.com"
    echo "Website: https://altheamesh.com"
    echo ""
    if ! command -v ejoinctl &> /dev/null; then
        echo -e "${YELLOW}Note: Restart your shell or run 'source ~/.bashrc' to use ejoinctl${RESET}"
    fi
}

# Main installation function
main() {
    banner
    
    # Parse arguments
    SKIP_DEPS=false
    FORCE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --skip-deps    Skip system dependency installation"
                echo "  --force        Force installation even if already installed"
                echo "  --help, -h     Show this help message"
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
    
    # Check if already installed
    if command -v ejoinctl &> /dev/null && [[ "$FORCE" != true ]]; then
        warn "ejoinctl is already installed. Use --force to reinstall."
        ejoinctl --help
        exit 0
    fi
    
    # Installation steps
    check_root
    detect_os
    check_python
    check_pip
    
    if [[ "$SKIP_DEPS" != true ]]; then
        install_system_deps
    fi
    
    create_venv
    install_ejoinctl
    create_wrapper
    update_shell_config
    create_config
    test_installation
    show_completion
}

# Run main function
main "$@"