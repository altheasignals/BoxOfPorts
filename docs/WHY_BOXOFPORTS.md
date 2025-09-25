# BoxOfPorts - GitHub Repository Description

## Short Description (for GitHub "About" section)
```
BoxOfPorts - Professional SMS Gateway Management CLI for EJOIN Multi-WAN Routers. Inspired by "Box of Rain" - Grateful Dead. Manage dozens of gateways, handle failing ports, automate SMS operations, and ensure compliance monitoring with style. 🎵
```

## Detailed Description (for README/main description)

### 🎵 BoxOfPorts - SMS Gateway Management CLI
*"Box of Rain" - Grateful Dead inspired tool for managing your box of ports*

**Professional SMS Gateway Management for EJOIN Multi-WAN Router Operators**

BoxOfPorts (`bop`) is a comprehensive command-line interface designed for the daily reality of SMS gateway operators managing EJOIN multi-WAN routers. Built for professionals dealing with dozens of gateways, failing ports, SIM card swaps, and strict compliance monitoring requirements.

---

### 🌟 Why BoxOfPorts?

In the world of SMS gateway operations, you're dealing with:
- **Dozens of gateways** with hundreds of ports
- **Failing SIM cards** that need constant monitoring  
- **Compliance requirements** for STOP message handling
- **Bulk SMS campaigns** across multiple carriers
- **Port management** complexity (lock/unlock, ranges, mixed formats)
- **Real-time monitoring** needs with webhook integration

BoxOfPorts transforms this complexity into elegant, powerful command-line operations that scale with your infrastructure.

---

### ⚡ Key Features

#### 🚀 **Advanced SMS Operations**
- **Smart templating** with Jinja2 (port variables, timestamps, custom filters)
- **Bulk messaging** with configurable intervals and retry logic
- **Port range expansion** (`1A-4D`, `2.01-2.08`, mixed formats)
- **Multi-gateway support** with profile switching

#### 📥 **Professional Inbox Management**
- **STOP message monitoring** for compliance requirements
- **Advanced filtering** by sender, content, port, date ranges  
- **Delivery report handling** with automatic classification
- **Export capabilities** for auditing and compliance

#### 🎛️ **Device Operations**
- **Port management** (lock/unlock operations across ranges)
- **Real-time status monitoring** with webhook subscriptions
- **Connection testing** with detailed diagnostics
- **Multi-device orchestration**

#### 🛠️ **Professional Features**
- **Profile management** for multiple gateway environments
- **SQLite storage** for task tracking and audit trails
- **Rich CLI output** with progress indicators and colored tables
- **Comprehensive error handling** with retry mechanisms
- **JSON API support** for automation and integration

---

### 🎯 Perfect For

- **SMS Gateway Operators** managing multiple EJOIN devices
- **Telecom Infrastructure Teams** handling bulk messaging
- **Compliance Officers** monitoring STOP messages and opt-outs
- **Network Operations Centers** requiring real-time SMS capabilities
- **Developers** building SMS-integrated applications
- **System Administrators** automating SMS infrastructure

---

### 🚀 Quick Start

```bash
# Multi-mode installation (choose your deployment style)
git clone https://github.com/altheasignals/boxofports.git
cd boxofports
./install.sh

# Create gateway profile (one-time setup)
boxofports config add-profile production --host 192.168.1.100 --user admin

# Switch and start managing
boxofports config switch production
boxofports test-connection
boxofports sms send --to "+1234567890" --text "Hello from {{port}}" --ports "1A-2D"
boxofports inbox stop  # Monitor compliance
```

---

### 💼 Enterprise Ready

#### **Multi-Installation Modes**
- **Development Mode**: Live code changes, perfect for operators who customize
- **User Mode**: Clean local installation, recommended for most users  
- **System Mode**: Global installation for enterprise multi-user environments

#### **Security & Compliance**
- **User data isolation** (configs, databases stay private per user)
- **Credential management** with environment variables and profiles
- **Audit trails** with comprehensive logging and task tracking
- **STOP message compliance** monitoring and reporting

#### **Production Features**
- **Docker support** for containerized deployments
- **REST API integration** for webhook callbacks
- **Bulk operations** with rate limiting and retry logic
- **Multi-platform support** (macOS, Linux, Windows/WSL)

---

### 🎨 The "Box of Rain" Philosophy

Named after the Grateful Dead's "Box of Rain," BoxOfPorts embodies the spirit of turning complexity into harmony. Just as the song transforms life's complexities into beautiful simplicity, BoxOfPorts transforms the chaos of SMS gateway management into elegant, powerful operations.

*"Such a long long time to be gone, and a short time to be there..."*  
Like the fleeting nature of SMS messages across your network, BoxOfPorts helps you manage the flow with grace and precision.

---

### 🏢 About Althea Signals Network LLC

Developed by **Althea Signals Network LLC**, pioneers in decentralized telecommunications infrastructure. We provide innovative solutions for network operators, service providers, and enterprise customers working to democratize access to telecommunications infrastructure.

**Learn more**: [https://altheasignals.net](https://altheasignals.net)

---

### 📞 Support & Community

- **Email Support**: support@altheasignals.net
- **Documentation**: Comprehensive guides in `docs/` directory
- **Issue Reporting**: Use GitHub issues with detailed system information
- **Professional Support**: Available for enterprise deployments

---

**BoxOfPorts** - Where SMS gateway management meets the Grateful Dead spirit of turning complexity into harmony. 🎵✨

*Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.*