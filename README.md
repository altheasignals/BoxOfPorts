# BoxOfPorts - SMS Gateway Management CLI

## 🚀 Quick Install

### User Installation (Recommended)

**No sudo required** - Installs to your user directory:

```bash
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | bash

# Essential first steps:
boxofports help-tree                    # Explore all available commands
boxofports --install-completion         # Enable shell completion
boxofports config add-profile mygateway # Add your gateway (saves typing credentials)
```

### System-wide Installation

**Requires elevated privileges** - Available to all users:

```bash
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | sudo bash -s -- --system
```

For details, see docs/DISTRIBUTION.md.

## 🎵 Release Tracks & Versioning

BoxOfPorts uses a dual-track release system designed for both stability and innovation:

- **🎯 Stable Track** (X.Y.0): Production-ready releases, thoroughly tested
- **🚀 Development Track** (X.Y.Z where Z>0): Latest features and fixes

The `bop` wrapper automatically selects the stable track by default:

```bash
# Uses stable track (production ready)
bop --help

# Switch to development track (latest features)
BOP_RELEASE_TRACK=dev bop --help

# Check current version and track
bop --bop-version
```

**Why dual-track?** No more surprise updates! You choose when to ride the bleeding edge.

For complete details on our release process, see [docs/VERSIONING.md](docs/VERSIONING.md).

## 🗑️ Uninstalling

To cleanly remove BoxOfPorts (detects all installation methods):

```bash
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/uninstall-bop.sh | bash
```

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/altheasignals/boxofports)
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
- 🌐 **Multi-Gateway Support** - Manage multiple EJOIN devices seamlessly with device aliases
- 🏷️ **Device Aliases** - Friendly names for gateways that appear in all tables and exports
- 🔌 **Smart Port Handling** - Support for ranges, lists, and mixed specifications
- 💾 **SQLite Storage** - Local task tracking and status history
- 🎯 **Rich CLI Output** - Beautiful tables, progress indicators, and error handling
- 📊 **Data Export** - CSV/JSON export for all table commands with pipeline integration

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

#### Shell Completion Setup (Highly Recommended)

**Enable TAB completion for all commands and options:**

```bash
# Install completion for your shell
boxofports --install-completion

# Restart your terminal or source your shell config
source ~/.bashrc  # For bash users
source ~/.zshrc   # For zsh users

# Test completion
boxofports <TAB>           # Shows all available commands
boxofports sms <TAB>       # Shows SMS subcommands
boxofports --<TAB>         # Shows global options
```

**Why use completion?** BoxOfPorts has many commands and options. Shell completion makes it much easier to:
- Discover available commands and subcommands
- Remember complex option names and formats
- Navigate the CLI efficiently
- Reduce typing errors

#### 🎯 Essential First Steps for New Users

**1. Explore the command structure:**
```bash
boxofports help-tree       # Visual tree of all available commands
```

**2. Create a profile (avoid typing credentials every time):**
```bash
# Add your gateway as a profile (one-time setup)
boxofports config add-profile mygateway \
  --host 192.168.1.100 --user admin --password yourpass

# Now use commands without credentials!
boxofports test-connection
boxofports sms send --to "+1234567890" --text "Hello" --ports "1A"
boxofports inbox list
```

**Why use profiles?** Instead of typing `--host 192.168.1.100 --user admin --password yourpass` with every command, profiles let you:
- Save connection details once and reuse them
- Switch between multiple gateways easily
- Keep credentials secure in config files
- Use friendly device aliases that appear in all tables

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

**First, set up shell completion (highly recommended):**
```bash
# Enable TAB completion for Docker wrapper too
boxofports --install-completion  # Same command works for Docker wrapper
# Restart terminal, then try: boxofports <TAB>
```

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

# Create multiple profiles for same device (internal/external access) with shared alias
boxofports config add-profile office-internal --host 10.0.0.5 --user admin --password secret --alias office
boxofports config add-profile office-external --host 203.0.113.50 --user admin --password secret --alias office

# Switch between profiles
boxofports config switch remote

# Now use commands without specifying connection details!
boxofports test-connection
boxofports sms send --to "+1234567890" --text "Hello from {{port}}" --ports "2A"
boxofports ops lock --ports "1A-1D"

# Switch to different server instantly
boxofports config switch local
boxofports test-connection  # Now connects to local server

# Edit current profile settings
boxofports config edit-profile --alias "main-gateway" --port 8080
```

**Docker Wrapper (bop):**

```bash
# Create profiles for your servers (one-time setup)
boxofports config add-profile remote --host 203.0.113.100:60140 --user root --password your_password
boxofports config add-profile local --host 192.168.1.100 --user admin --password your_password

# Create multiple profiles for same device with shared alias
boxofports config add-profile office-internal --host 10.0.0.5 --user admin --password secret --alias office
boxofports config add-profile office-external --host 203.0.113.50 --user admin --password secret --alias office

# Switch between profiles
boxofports config switch remote

# Now use commands without specifying connection details!
boxofports test-connection
boxofports sms send --to "+1234567890" --text "Hello from {{port}}" --ports "2A"
boxofports ops lock --ports "1A-1D"

# Switch to different server instantly
boxofports config switch local
boxofports test-connection  # Now connects to local server

# Edit current profile settings
boxofports config edit-profile --alias "main-gateway" --port 8080
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
>
> **💡 New User?** Start with the **Essential First Steps** above: run `boxofports help-tree` to explore commands, then `boxofports config add-profile` to avoid typing credentials repeatedly!

#### Profile Management

```bash
boxofports config add-profile <name>  # Add server profile (supports --alias option)
boxofports config edit-profile        # Edit current profile settings
boxofports config list                # List all profiles (shows Device Alias column)
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

## 🏷️ Device Aliases

Device aliases provide friendly names for your gateways that appear consistently across all tables and exports, making it easy to identify devices in multi-gateway setups.

### Creating Profiles with Aliases

```bash
# Explicit alias (recommended for shared devices)
boxofports config add-profile office-internal --host 10.0.0.5 --alias office
boxofports config add-profile office-external --host 203.0.113.50 --alias office

# Auto-generated alias (defaults to first word of profile name)
boxofports config add-profile production-gateway --host 192.168.1.100
# Creates alias: "production"
```

### Editing Profile Aliases

```bash
# Change alias for current profile
boxofports config edit-profile --alias "main-gateway"

# Update multiple settings at once
boxofports config edit-profile --host 192.168.1.200 --alias "backup"
```

### Benefits

- **Consistent Identification**: Same device shows same alias across all commands
- **Export Integration**: Device aliases included in all CSV/JSON exports 
- **Pipeline Friendly**: Filter and process data by device alias
- **Multi-Access Support**: Multiple profiles (internal/external) can share same alias

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

## 📊 Data Export & Pipeline Integration

BoxOfPorts supports CSV and JSON export for all table-producing commands, enabling powerful pipeline integration and data analysis workflows.

### Export Options

Every command that displays a table includes these options:

- `--csv` - Export data as CSV
- `--json` - Export data as JSON

### Console vs File Output

**Console Output (Pipeline Integration)**:
```bash
# Output CSV directly to stdout (no other output)
boxofports inbox list --csv

# Output JSON directly to stdout (no other output)  
boxofports config list --json

# Perfect for pipelines
boxofports inbox list --csv | grep "STOP" | wc -l
```

**File Output**:
```bash
# Save to specific file + show normal output
boxofports inbox list --csv messages.csv
boxofports config list --json profiles.json

# Auto-generated filenames
boxofports inbox stop --csv   # Creates: profile-inbox-stop-20250926_093010.csv
```

### Pipeline Examples

**Ripple Through Your Data** - Like ripples in still water:

```bash
# Get IMEI values and find specific ones (includes device alias)
boxofports ops get-imei --ports "1A-1D" --csv | grep "123456"

# Export messages and analyze with jq (includes device alias)
boxofports inbox list --count 100 --json | jq '.[] | select(.type == "stop")'

# Count messages by port (device alias helps identify sources)
boxofports inbox list --csv | tail -n +2 | cut -d, -f4 | sort | uniq -c

# Convert profiles to different formats (includes device aliases)
boxofports config list --csv | csvtojson > profiles.json

# Find high-volume senders by device
boxofports inbox list --json | jq -r '[.device_alias, .sender] | @csv' | sort | uniq -c

# Filter exports by device alias for multi-gateway setups
boxofports config list --csv | grep "office" | cut -d, -f1
```

**Data Analysis Workflows**:

```bash
# Export all data for analysis
boxofports inbox list --count 0 --csv > all_messages.csv
boxofports inbox stop --csv > stop_messages.csv  
boxofports config list --csv > profiles.csv

# Generate compliance reports
boxofports inbox stop --json | jq '{total: length, messages: [.[].content]}' > compliance_report.json
```

### Supported Commands

**SMS Operations**:
- `sms send --csv/--json` - Export task previews and results
- `sms spray --csv/--json` - Export spray operation data

**Device Operations**:
- `ops get-imei --csv/--json` - Export IMEI values

**Configuration**:
- `config list --csv/--json` - Export profile configurations

**Inbox Management**:
- `inbox list --csv/--json` - Export messages with filtering
- `inbox search --csv/--json` - Export search results
- `inbox stop --csv/--json` - Export STOP messages for compliance

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
# Test auto-bump system
# Second test
# Final test
