# ejoinctl - EJOIN Multi-WAN Router Management CLI

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/altheamesh/ejoinctl)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

**Professional command-line interface for EJOIN Multi-WAN Router HTTP API v2.2 management**

Developed by [Althea Signals Network LLC](https://altheamesh.com) - The leader in decentralized telecommunications infrastructure.

## 🌟 Overview

ejoinctl is a comprehensive, production-ready CLI tool designed for managing EJOIN multi-WAN routers. Built with enterprise-grade reliability and ease of use in mind, it provides powerful SMS operations, device management, real-time monitoring, and advanced templating capabilities.

### Key Features

- 📱 **Advanced SMS Operations** - Send, spray, and template SMS with per-port routing
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

#### Option 1: Direct Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/altheamesh/ejoinctl.git
cd ejoinctl

# Install dependencies
pip install -e .

# Verify installation
ejoinctl --help
```

#### Option 2: Using Docker
```bash
# Build the container
docker build -t ejoinctl .

# Run commands
docker run --rm ejoinctl --help
```

### Basic Usage

```bash
# Test connection to your gateway
ejoinctl --host 192.168.1.100 --user admin --password your_password test-connection

# Test connection with custom port (host:port format)
ejoinctl --host 13.228.130.204:60140 --user root --password your_password test-connection

# Send SMS via specific port
ejoinctl --host 192.168.1.100 --user admin --password your_password \
  sms send --to "+1234567890" --text "Hello from ejoinctl!" --ports "1A"

# Send SMS to gateway with custom port
ejoinctl --host 13.228.130.204:60140 --user root --password your_password \
  sms send --to "+1234567890" --text "Hello from port {{port}}" --ports "2A"

# Lock ports for maintenance
ejoinctl --host 192.168.1.100 --user admin --password your_password \
  ops lock --ports "1A-1D"
```

## 📖 Documentation

### Command Structure
```
ejoinctl [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Global Options
- `--host` - Gateway IP address (can include port like `192.168.1.100:8080`)
- `--port` - Gateway port (default: 80, ignored if port is in --host)
- `--user` - Username for authentication
- `--password` - Password for authentication
- `--verbose` - Enable detailed logging

### Available Commands

#### SMS Operations
```bash
ejoinctl sms send     # Send SMS with templating support
ejoinctl sms spray    # Spray SMS across multiple ports quickly
```

#### Device Operations  
```bash
ejoinctl ops lock     # Lock specified ports
ejoinctl ops unlock   # Unlock specified ports
```

#### Status Monitoring
```bash
ejoinctl status subscribe  # Subscribe to status notifications
```

#### Utility
```bash
ejoinctl test-connection  # Test gateway connectivity
```

## 🎨 Template System

ejoinctl includes a powerful Jinja2-based template system for dynamic SMS content:

### Built-in Variables
- `{{port}}` - Current port identifier
- `{{ts}}` - UTC timestamp
- `{{idx}}` - Message index

### Example Templates
```bash
# Basic templating
ejoinctl sms send --text "Alert from port {{port}} at {{ts}}" --ports "1A"

# With custom variables and filters
ejoinctl sms send \
  --text "{{company | upper}} Alert: Port {{port}} Status {{status}}" \
  --ports "1A,2B" --var "company=Acme Corp" --var "status=OK"
```

### Available Filters
- `upper` - Convert to uppercase
- `lower` - Convert to lowercase  
- `truncate(n)` - Truncate to n characters
- `phone('format')` - Format phone numbers

## 🔌 Port Specifications

ejoinctl supports flexible port specification formats:

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

### Bulk SMS Campaign
```bash
ejoinctl sms send --to "+1234567890" \
  --text "Campaign #{{idx}} from {{port}}" \
  --ports "1A-4D" --repeat 2
```

### Emergency Alert System
```bash
# Lock all ports
ejoinctl ops lock --ports "1A-10D"

# Send alert
ejoinctl sms send --to "+1234567890" \
  --text "EMERGENCY: System locked at {{ts}}" --ports "1A"
```

### Multi-Gateway Management
```bash
# Gateway 1
ejoinctl --host 192.168.1.100 sms send --to "+1234567890" --text "From GW1" --ports "1A"

# Gateway 2  
ejoinctl --host 192.168.1.101 sms send --to "+1234567890" --text "From GW2" --ports "1A"
```

## 🐳 Docker Usage

### Build and Run
```bash
# Build the image
docker build -t ejoinctl .

# Run with mounted config
docker run --rm -v $(pwd)/config:/app/config ejoinctl \
  --host 192.168.1.100 --user admin --password your_password test-connection

# Interactive mode
docker run --rm -it ejoinctl bash
```

### Docker Compose
```yaml
version: '3.8'
services:
  ejoinctl:
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
git clone https://github.com/altheamesh/ejoinctl.git
cd ejoinctl

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .

# Type checking
mypy ejoinctl/
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_ports.py

# Run with coverage
pytest --cov=ejoinctl
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
ejoinctl --host 192.168.1.100 --timeout 60 test-connection
```

#### Authentication Errors
```bash
# Verify credentials
ejoinctl --host 192.168.1.100 --user admin --password correct_password test-connection
```

#### Port Specification Errors
```bash
# Use dry-run to verify port parsing
ejoinctl sms send --ports "1A-1D" --text "test" --to "+1234567890" --dry-run
```

## 📞 Support

For technical support, feature requests, or licensing inquiries:

- **Email**: support@altheamesh.com
- **Website**: [https://altheamesh.com](https://altheamesh.com)
- **Documentation**: [Full documentation available online]

## 📄 License

This software is proprietary and owned by Althea Signals Network LLC. 
See [LICENSE](LICENSE) file for full terms and conditions.

## 🙏 About Althea Signals Network LLC

Althea Signals Network LLC is a pioneer in decentralized telecommunications infrastructure, 
providing innovative solutions for network operators, service providers, and enterprise customers.

Our mission is to democratize access to telecommunications infrastructure through 
cutting-edge technology and open protocols.

**Learn more**: [https://altheamesh.com](https://altheamesh.com)

---

**ejoinctl v1.0.0** - Professional EJOIN Gateway Management  
Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.