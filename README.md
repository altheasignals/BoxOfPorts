# BoxOfPorts - SMS Gateway Management CLI

Quick install (Docker Hub + wrapper):

```bash
# Replace <GITHUB_OWNER> with your GitHub username or org
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/scripts/install-bop.sh | bash
bop --help
```

For details, see docs/DISTRIBUTION.md.

## Uninstalling

To avoid version conflicts when switching installation methods:

```bash
curl -fsSL https://raw.githubusercontent.com/<GITHUB_OWNER>/gateway-manager/main/scripts/uninstall-bop.sh | bash
```

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/altheasignals/boxofports)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

**SMS Gateway Management CLI for EJOIN Multi-WAN Router Operators**  
*Like Box of Rain, but... ports*

Developed by [Althea Signals Network LLC](https://altheasignals.net) - The leader in decentralized telecommunications infrastructure.

## 🌟 Overview

BoxOfPorts (`bop`) is a comprehensive CLI tool designed for SMS gateway operators managing EJOIN multi-WAN routers. Built for the daily reality of managing dozens of gateways with failing ports, SIM card swaps, and compliance monitoring, it provides practical SMS operations, inbox management, device control, and automation capabilities.

### Key Features

- 📱 **Advanced SMS Operations** - Send, spray, and template SMS with per-port routing
- 📥 **SMS Inbox Management** - Retrieve, filter, and analyze received messages
- 🔧 **Device Management** - Lock/unlock ports, execute device operations
- 📊 **Real-time Monitoring** - Status subscriptions with webhook callbacks
- 🎨 **Template System** - Jinja2-powered templating with custom filters
- 🌐 **Multi-Gateway Support** - Manage multiple EJOIN devices seamlessly
- 🔌 **Smart Port Handling** - Support for ranges, lists, and mixed specifications
- 💾 **SQLite Storage** - Local task tracking and status history
- 🎯 **Rich CLI Output** - Beautiful tables, progress indicators, and error handling

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Network access to EJOIN gateway devices
- Valid EJOIN device credentials

### Installation

BoxOfPorts supports three installation modes to accommodate different use cases:

#### Option 1: 👤 User Mode (local installation)
**Recommended for most users**

```bash
# Clone the repository
git clone https://github.com/altheasignals/BoxOfPorts.git
cd BoxOfPorts

# Run the installer and select option 2
./install.sh

# Or install directly
./install-user.sh
```

**Benefits:**
- Clean isolated installation in ~/.local/bin
- No sudo required
- Doesn't affect system Python
- Easy to update and remove

#### Option 2: 🛠️ Development Mode (pyenv + editable install)
**Perfect for developers and operators who modify the code**

```bash
# Clone the repository
git clone https://github.com/altheasignals/BoxOfPorts.git
cd BoxOfPorts

# Run the installer and select option 1
./install.sh

# Or install directly if you have pyenv
./install-dev.sh
```

**Benefits:**
- Code changes take effect immediately
- Perfect for development and testing
- Uses pyenv for Python version management
- No sudo required

#### Option 3: 🌐 System Mode (global installation)
**For administrators managing multi-user systems**

```bash
# Clone the repository
git clone https://github.com/altheasignals/BoxOfPorts.git
cd BoxOfPorts

# Run the installer and select option 3
./install.sh

# Or install directly with sudo
sudo ./install-system.sh
```

**Benefits:**
- Available to all users on the system
- Centralized maintenance
- User data remains private per user
- Requires sudo/root privileges

#### Option 4: Using Docker
```bash
# Build the container
docker build -t bop .

# Run commands
docker run --rm bop --help

# Run with connection parameters
docker run --rm bop --host 192.168.1.100 --user admin --password your_password test-connection
```

### Choosing the Right Installation Mode

- **👨‍💻 Developer/Operator**: Use Development Mode for immediate code changes
- **🧑‍💻 Regular User**: Use User Mode for clean, isolated installation
- **👨‍💼 System Admin**: Use System Mode for enterprise/multi-user environments
- **🐳 Container User**: Use Docker for containerized deployments

> **Note**: Regardless of installation mode, all user data (configs, databases, profiles) remains private in each user's home directory.

### Basic Usage

#### Option 1: Quick Commands (specify connection details each time)
```bash
# Test connection to your gateway
bop --host 192.168.1.100 --user admin --password your_password test-connection

# Test connection with custom port (host:port format)
bop --host 203.0.113.100:60140 --user root --password your_password test-connection

# Send SMS via specific port
bop --host 192.168.1.100 --user admin --password your_password \
  sms send --to "+1234567890" --text "Hello from bop!" --ports "1A"
```

#### Option 2: Profile-Based Usage (Recommended)
```bash
# Create profiles for your servers (one-time setup)
bop config add-profile remote --host 203.0.113.100:60140 --user root --password your_password
bop config add-profile local --host 192.168.1.100 --user admin --password your_password

# Switch between profiles
bop config switch remote

# Now use commands without specifying connection details!
bop test-connection
bop sms send --to "+1234567890" --text "Hello from {{port}}" --ports "2A"
bop ops lock --ports "1A-1D"

# Switch to different server instantly
bop config switch local
bop test-connection  # Now connects to local server
```

## 📖 Documentation

### Command Structure
```
bop [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Global Options
- `--host` - Gateway IP address (can include port like `192.168.1.100:8080`)
- `--port` - Gateway port (default: 80, ignored if port is in --host)
- `--user` - Username for authentication
- `--password` - Password for authentication
- `--verbose` - Enable detailed logging

### Available Commands

#### Profile Management
```bash
bop config add-profile <name>  # Add server profile
bop config list                # List all profiles
bop config switch <name>       # Switch to profile
bop config current             # Show current profile
bop config show [name]         # Show profile details
bop config remove <name>       # Remove profile
```

#### SMS Operations
```bash
bop sms send     # Send SMS with templating support
bop sms spray    # Spray SMS across multiple ports quickly
```

#### Inbox Management
```bash
bop inbox list     # List received messages with filtering
bop inbox search   # Search messages by content
bop inbox stop     # Show STOP/unsubscribe messages
bop inbox summary  # Inbox statistics and overview
bop inbox show     # Show detailed message information
```

#### Device Operations  
```bash
bop ops lock     # Lock specified ports
bop ops unlock   # Unlock specified ports
```

#### Status Monitoring
```bash
bop status subscribe  # Subscribe to status notifications
```

#### Utility
```bash
bop test-connection  # Test gateway connectivity
```

## 🎨 Template System

bop includes a powerful Jinja2-based template system for dynamic SMS content:

### Built-in Variables
- `{{port}}` - Current port identifier
- `{{ts}}` - UTC timestamp
- `{{idx}}` - Message index

### Example Templates
```bash
# Basic templating
bop sms send --text "Alert from port {{port}} at {{ts}}" --ports "1A"

# With custom variables and filters
bop sms send \
  --text "{{company | upper}} Alert: Port {{port}} Status {{status}}" \
  --ports "1A,2B" --var "company=Acme Corp" --var "status=OK"

# Preview templates before sending (--dry-run)
bop sms send --text "Alert from {{port}}" --ports "1A,2B" --dry-run
# Shows exactly what will be sent without actually sending
```

### Available Filters
- `upper` - Convert to uppercase
- `lower` - Convert to lowercase  
- `truncate(n)` - Truncate to n characters
- `phone('format')` - Format phone numbers

## 🔌 Port Specifications

bop supports flexible port specification formats:

### Single Ports
- `1A` - Slot 1, Port A
- `2.02` - Slot 2, Port 02 (decimal format)

### Port Lists
- `1A,2B,3C` - Multiple specific ports

### Port Ranges
- `1A-1D` - Slot 1, Ports A through D
- `1-3` - Slots 1-3, all Port A

### Mixed Specifications
- `1A,3B-3D,5.01` - Combination of formats

## 📊 Examples

### Let It Ripple - Bulk SMS Campaign
```bash
bop sms send --to "+1234567890" \
  --text "Campaign #{{idx}} from {{port}}" \
  --ports "1A-4D" --repeat 2
```

### Emergency Alert System
```bash
# Lock all ports
bop ops lock --ports "1A-10D"

# Send alert
bop sms send --to "+1234567890" \
  --text "EMERGENCY: System locked at {{ts}}" --ports "1A"
```

### Eyes of the Inbox
```bash
# Monitor STOP messages (compliance)
bop inbox stop

# Get inbox overview
bop inbox summary

# Find messages containing specific text
bop inbox search "balance"

# List recent messages excluding delivery reports
bop inbox list --count 20 --no-delivery-reports

# Export STOP messages for compliance
bop inbox stop --json > stop_messages.json
```

### Multi-Gateway Management
```bash
# Gateway 1
bop --host 192.168.1.100 sms send --to "+1234567890" --text "From GW1" --ports "1A"

# Gateway 2  
bop --host 192.168.1.101 sms send --to "+1234567890" --text "From GW2" --ports "1A"
```

## 🐳 Docker Usage

### Build and Run
```bash
# Build the image
docker build -t bop .

# Run with mounted config
docker run --rm -v $(pwd)/config:/app/config bop \
  --host 192.168.1.100 --user admin --password your_password test-connection

# Interactive mode
docker run --rm -it bop bash
```

### Docker Compose
```yaml
version: '3.8'
services:
  bop:
    build: .
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    environment:
      - EJOIN_HOST=192.168.1.100
      - EJOIN_USER=admin
      - EJOIN_PASSWORD=your_password
```

## 🛠️ Development

### Setting up Development Environment
```bash
# Clone repository
git clone https://github.com/altheasignals/BoxOfPorts.git
cd BoxOfPorts

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .

# Type checking
mypy bop/
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_ports.py

# Run with coverage
pytest --cov=bop
```

## 📋 Requirements

### System Requirements
- Python 3.11+
- 50MB disk space
- Network connectivity to EJOIN devices

### Python Dependencies
- typer >= 0.9.0
- httpx >= 0.25.0
- pydantic >= 2.0.0
- rich >= 13.0.0
- jinja2 >= 3.1.0
- python-dotenv >= 1.0.0

## 🐛 Troubleshooting

### Common Issues

#### Connection Timeouts
```bash
# Increase timeout
bop --host 192.168.1.100 --timeout 60 test-connection
```

#### Authentication Errors
```bash
# Verify credentials
bop --host 192.168.1.100 --user admin --password correct_password test-connection
```

#### Port Specification Errors
```bash
# Use dry-run to verify port parsing
bop sms send --ports "1A-1D" --text "test" --to "+1234567890" --dry-run
```

## 📞 Support

For technical support, feature requests, or licensing inquiries:

- **Email**: support@altheasignals.net
- **Website**: [https://altheasignals.net](https://altheasignals.net)
- **Documentation**: [Full documentation available online]

## 📚 Complete Documentation

This README provides a quick start guide. For comprehensive documentation, see the [docs/](docs/) directory:

### 📖 User Guides
- **[Usage Guide](docs/usage/USAGE_GUIDE.md)** - Complete usage examples and tutorials
- **[Inbox Documentation](docs/usage/INBOX_DOCUMENTATION.md)** - SMS inbox management guide

### 🚀 Deployment Guides
- **[Deployment Guide](docs/deployment/DEPLOYMENT.md)** - Comprehensive deployment guide for all platforms
- **[Distribution Summary](docs/deployment/DISTRIBUTION_SUMMARY.md)** - Distribution package overview

### 🛠️ Developer Resources
- **[Test Summary](docs/development/TEST_SUMMARY.md)** - Testing implementation and results
- **[Development Documentation](docs/development/)** - Architecture and implementation details

> 💡 **Tip**: Start with the [Documentation Index](docs/README.md) for a complete overview of available resources.

## 📄 License

This software is proprietary and owned by Althea Signals Network LLC. 
See [LICENSE](LICENSE) file for full terms and conditions.

## 🙏 About Althea Signals Network LLC

Althea Signals Network LLC is a pioneer in decentralized telecommunications infrastructure, 
providing innovative solutions for network operators, service providers, and enterprise customers.

Our mission is to democratize access to telecommunications infrastructure through 
cutting-edge technology and open protocols.

**Learn more**: [https://altheasignals.net](https://altheasignals.net)

---

**BoxOfPorts** - SMS Gateway Management CLI  
*Like "Box of Rain", but for ports*  
Command: `bop`  
Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.
