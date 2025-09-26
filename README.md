# BoxOfPorts - SMS Gateway Management CLI

## 🚀 Quick Install

### User Installation (Recommended)

**No sudo required** - Installs to your user directory:

```bash
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | bash
boxofports --help
```

### System-wide Installation

**Requires elevated privileges** - Available to all users:

```bash
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | sudo bash -s -- --system
```

For details, see docs/DISTRIBUTION.md.

## 🗑️ Uninstalling

To cleanly remove BoxOfPorts (detects all installation methods):

```bash
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/uninstall-bop.sh | bash
```

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/altheasignals/boxofports)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

**SMS Gateway Management CLI for EJOIN Multi-WAN Router Operators**  
*Like Box of Rain, but... ports*

Developed by [Althea Signals Network LLC](https://altheasignals.net) - The leader in decentralized telecommunications infrastructure.

## 🌟 Overview

BoxOfPorts provides both a local CLI (`boxofports`) and a Docker wrapper (`bop`) designed for SMS gateway operators managing EJOIN multi-WAN routers. Built for the daily reality of managing dozens of gateways with failing ports, SIM card swaps, and compliance monitoring, it provides practical SMS operations, inbox management, device control, and automation capabilities.

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

BoxOfPorts supports multiple installation approaches:

#### Option 1: 🌐 Cloud Installation (Recommended)

**Uses Docker - No Python setup required**

```bash
# User installation (no sudo needed)
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | bash

# System-wide installation (requires sudo)
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | sudo bash -s -- --system
```

**Benefits:**

- No Python or dependencies to manage
- Always uses latest stable version
- Clean isolation via Docker
- Easy to update and remove
- Works on any system with Docker

#### Option 2: 👤 Local Python Installation

**For users who prefer local Python setup**

```bash
# Clone the repository
git clone https://github.com/altheasignals/BoxOfPorts.git
cd BoxOfPorts

# Run the local installer
./install-user.sh
```

**Benefits:**

- Direct Python installation
- Full control over dependencies
- No Docker required
- Installs to ~/.local/bin

#### Option 3: 🛠️ Development Mode

**For developers and contributors**

```bash
# Clone the repository
git clone https://github.com/altheasignals/BoxOfPorts.git
cd BoxOfPorts

# Development setup with pyenv
./install-dev.sh
```

**Benefits:**

- Code changes take effect immediately
- Perfect for development and testing
- Uses pyenv for Python version management
- Editable installation

#### Option 4: Using Docker

```bash
# Build the container
docker build -t altheasignals/boxofports .

# Run commands
docker run --rm altheasignals/boxofports boxofports --help

# Run with connection parameters
docker run --rm altheasignals/boxofports boxofports --host 192.168.1.100 --user admin --password your_password test-connection
```

### Choosing the Right Installation Method

- **🎆 Most Users**: Cloud Installation (Option 1) - No Python setup, always current
- **🔧 Power Users**: Local Python Installation (Option 2) - Full control, no Docker
- **👨‍💻 Developers**: Development Mode (Option 3) - Code changes, testing, contributions

> **Note**: All user data (configs, databases, profiles) remains private in your home directory regardless of installation method.

### Basic Usage

#### Local CLI Usage (Direct Installation)

```bash
# Test connection to your gateway
boxofports --host 192.168.1.100 --user admin --password your_password test-connection

# Test connection with custom port (host:port format) 
boxofports --host 203.0.113.100:60140 --user root --password your_password test-connection

# Send SMS via specific port
boxofports --host 192.168.1.100 --user admin --password your_password \
  sms send --to "+1234567890" --text "Hello from BoxOfPorts!" --ports "1A"
```

#### Docker Wrapper Usage (Container-based)

```bash
# Test connection to your gateway
boxofports --host 192.168.1.100 --user admin --password your_password test-connection

# Test connection with custom port (host:port format)
boxofports --host 203.0.113.100:60140 --user root --password your_password test-connection

# Send SMS via specific port  
boxofports --host 192.168.1.100 --user admin --password your_password \
  sms send --to "+1234567890" --text "Hello from BoxOfPorts!" --ports "1A"
```

#### Profile-Based Usage (Recommended)

**Local CLI (boxofports):**

```bash
# Create profiles for your servers (one-time setup)
boxofports config add-profile remote --host 203.0.113.100:60140 --user root --password your_password
boxofports config add-profile local --host 192.168.1.100 --user admin --password your_password

# Switch between profiles
boxofports config switch remote

# Now use commands without specifying connection details!
boxofports test-connection
boxofports sms send --to "+1234567890" --text "Hello from {{port}}" --ports "2A"
boxofports ops lock --ports "1A-1D"

# Switch to different server instantly
boxofports config switch local
boxofports test-connection  # Now connects to local server
```

**Docker Wrapper (bop):**

```bash
# Create profiles for your servers (one-time setup)
boxofports config add-profile remote --host 203.0.113.100:60140 --user root --password your_password
boxofports config add-profile local --host 192.168.1.100 --user admin --password your_password

# Switch between profiles
boxofports config switch remote

# Now use commands without specifying connection details!
boxofports test-connection
boxofports sms send --to "+1234567890" --text "Hello from {{port}}" --ports "2A"
boxofports ops lock --ports "1A-1D"

# Switch to different server instantly
boxofports config switch local
boxofports test-connection  # Now connects to local server
```

## 📖 Documentation

### Command Structure

```
boxofports [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Global Options

- `--host` - Gateway IP address (can include port like `192.168.1.100:8080`)
- `--port` - Gateway port (default: 80, ignored if port is in --host)
- `--user` - Username for authentication
- `--password` - Password for authentication
- `--verbose` - Enable detailed logging

### Available Commands

> **Note**: Commands work identically with both `boxofports` (local CLI) and `bop` (Docker wrapper). Examples below show local CLI format.

#### Profile Management

```bash
boxofports config add-profile <name>  # Add server profile
boxofports config list                # List all profiles
boxofports config switch <name>       # Switch to profile
boxofports config current             # Show current profile
boxofports config show [name]         # Show profile details
boxofports config remove <name>       # Remove profile
```

#### SMS Operations

```bash
boxofports sms send     # Send SMS with templating support
boxofports sms spray    # Spray SMS across multiple ports quickly
```

#### Inbox Management

```bash
boxofports inbox list     # List received messages with filtering
boxofports inbox search   # Search messages by content
boxofports inbox stop     # Show STOP/unsubscribe messages
boxofports inbox summary  # Inbox statistics and overview
boxofports inbox show     # Show detailed message information
```

#### Device Operations  

```bash
boxofports ops lock     # Lock specified ports
boxofports ops unlock   # Unlock specified ports
```

#### Status Monitoring

```bash
boxofports status subscribe  # Subscribe to status notifications
```

#### Utility

```bash
boxofports test-connection  # Test gateway connectivity
```

## 🎨 Template System

BoxOfPorts includes a powerful Jinja2-based template system for dynamic SMS content:

### Built-in Variables

- `{{port}}` - Current port identifier
- `{{ts}}` - UTC timestamp
- `{{idx}}` - Message index

### Example Templates

```bash
# Basic templating
boxofports sms send --text "Alert from port {{port}} at {{ts}}" --ports "1A"

# With custom variables and filters
boxofports sms send \
  --text "{{company | upper}} Alert: Port {{port}} Status {{status}}" \
  --ports "1A,2B" --var "company=Acme Corp" --var "status=OK"

# Preview templates before sending (--dry-run)
boxofports sms send --text "Alert from {{port}}" --ports "1A,2B" --dry-run
# Shows exactly what will be sent without actually sending
```

### Available Filters

- `upper` - Convert to uppercase
- `lower` - Convert to lowercase  
- `truncate(n)` - Truncate to n characters
- `phone('format')` - Format phone numbers

## 🔌 Port Specifications

BoxOfPorts supports flexible port specification formats:

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
boxofports sms send --to "+1234567890" \
  --text "Campaign #{{idx}} from {{port}}" \
  --ports "1A-4D" --repeat 2
```

### Emergency Alert System

```bash
# Lock all ports
boxofports ops lock --ports "1A-10D"

# Send alert
boxofports sms send --to "+1234567890" \
  --text "EMERGENCY: System locked at {{ts}}" --ports "1A"
```

### Eyes of the Inbox

```bash
# Monitor STOP messages (compliance)
boxofports inbox stop

# Get inbox overview
boxofports inbox summary

# Find messages containing specific text
boxofports inbox search "balance"

# List recent messages excluding delivery reports
boxofports inbox list --count 20 --no-delivery-reports

# Export STOP messages for compliance
boxofports inbox stop --json > stop_messages.json
```

### Multi-Gateway Management

```bash
# Gateway 1
boxofports --host 192.168.1.100 sms send --to "+1234567890" --text "From GW1" --ports "1A"

# Gateway 2  
boxofports --host 192.168.1.101 sms send --to "+1234567890" --text "From GW2" --ports "1A"
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
docker run --rm -it boxofports bash
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
mypy boxofports/
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_ports.py

# Run with coverage
pytest --cov=boxofports
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
# Increase timeout (local CLI)
boxofports --host 192.168.1.100 --timeout 60 test-connection

# Or with Docker wrapper
boxofports --host 192.168.1.100 --timeout 60 test-connection
```

#### Authentication Errors

```bash
# Verify credentials (local CLI)
boxofports --host 192.168.1.100 --user admin --password correct_password test-connection

# Or with Docker wrapper
boxofports --host 192.168.1.100 --user admin --password correct_password test-connection
```

#### Port Specification Errors

```bash
# Use dry-run to verify port parsing (local CLI)
boxofports sms send --ports "1A-1D" --text "test" --to "+1234567890" --dry-run

# Or with Docker wrapper
boxofports sms send --ports "1A-1D" --text "test" --to "+1234567890" --dry-run
```

## 📞 Support

For technical support, feature requests, or licensing inquiries:

- **Email**: <support@altheasignals.net>
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
Commands: `boxofports` (local) / `bop` (Docker wrapper)  
Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.
