# BoxOfPorts Deployment Guide

Complete instructions for deploying and running BoxOfPorts (`bop`) on macOS, Windows, and Docker environments.

**Developed by Althea Signals Network LLC**  
Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.

## 📋 System Requirements

### Minimum Requirements
- **CPU**: 1 core, 1GHz
- **Memory**: 512MB RAM
- **Storage**: 100MB free disk space
- **Network**: Internet connectivity and access to EJOIN gateways
- **Python**: Version 3.11 or higher

### Recommended Requirements
- **CPU**: 2+ cores, 2GHz+
- **Memory**: 2GB+ RAM
- **Storage**: 1GB+ free disk space
- **Network**: Stable network connection with low latency to gateways

## 🍎 macOS Installation

### Prerequisites Check
```bash
# Check Python version
python3 --version
# Should show Python 3.11.0 or higher

# Check pip
pip3 --version
```

### Option 1: Direct Installation (Recommended)

#### Step 1: Install Python (if needed)
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Or download from python.org
# Visit: https://www.python.org/downloads/macos/
```

#### Step 2: Clone and Install bop
```bash
# Create working directory
mkdir -p ~/bop
cd ~/bop

# Clone repository (if available) or extract package
git clone https://github.com/altheasignals/boxofports.git
cd bop

# Or if you have the package directly:
# tar -xzf bop-1.0.0.tar.gz
# cd bop-1.0.0

# Install in virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install bop
pip install -e .

# Verify installation
bop --help
```

#### Step 3: Create Desktop Shortcut (Optional)
```bash
# Create application launcher
cat > ~/Desktop/bop.command << 'EOF'
#!/bin/bash
cd ~/bop/bop
source venv/bin/activate
python -m bop.cli "$@"
EOF

chmod +x ~/Desktop/bop.command
```

### Option 2: System-wide Installation
```bash
# Install system-wide (requires admin privileges)
sudo pip3 install -e .

# Verify
bop --help
```

### macOS Configuration

#### Create Configuration Directory
```bash
mkdir -p ~/.config/bop
```

#### Sample Configuration File
```bash
cat > ~/.config/bop/config.ini << 'EOF'
[default]
host = 192.168.1.100
port = 80
username = admin
password = your_secure_password
timeout = 30

[gateway1]
host = 192.168.1.234
username = root
password = zyg0-poPx-tHey

[gateway2]
host = 192.168.1.150
username = root
password = zyg0-poPx-tHey
EOF
```

## 🪟 Windows Installation

### Prerequisites Check
```powershell
# Check Python version (PowerShell)
python --version
# Should show Python 3.11.0 or higher

# Check pip
pip --version
```

### Option 1: Direct Installation (Recommended)

#### Step 1: Install Python (if needed)
1. Download Python 3.11+ from [python.org](https://www.python.org/downloads/windows/)
2. Run installer with these options:
   - ✅ Add Python to PATH
   - ✅ Install pip
   - ✅ Install for all users (if admin)

#### Step 2: Install bop
```powershell
# Create working directory
New-Item -ItemType Directory -Path "$env:USERPROFILE\bop" -Force
Set-Location "$env:USERPROFILE\bop"

# Clone repository or extract package
git clone https://github.com/altheasignals/boxofports.git
Set-Location bop

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install bop
pip install -e .

# Verify installation
python -m bop.cli --help
```

#### Step 3: Create Batch File (Optional)
```powershell
# Create convenient launcher
@"
@echo off
cd /d "%USERPROFILE%\bop\bop"
call venv\Scripts\activate.bat
python -m bop.cli %*
pause
"@ | Out-File -FilePath "$env:USERPROFILE\Desktop\bop.bat" -Encoding ASCII
```

### Option 2: Using Windows Subsystem for Linux (WSL)
```bash
# Install WSL if not already installed
wsl --install

# Inside WSL, follow the Linux/macOS instructions
```

### Windows Configuration

#### Create Configuration Directory
```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.config\bop" -Force
```

#### Sample Configuration File
```powershell
@"
[default]
host = 192.168.1.100
port = 80
username = admin
password = your_secure_password
timeout = 30

[gateway1]
host = 192.168.1.234
username = root
password = zyg0-poPx-tHey
"@ | Out-File -FilePath "$env:USERPROFILE\.config\bop\config.ini" -Encoding UTF8
```

## 🐳 Docker Deployment

### Option 1: Build from Source

#### Create Dockerfile
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create data directory
RUN mkdir -p /app/data

# Set entrypoint
ENTRYPOINT ["python", "-m", "bop.cli"]
CMD ["--help"]
```

#### Build and Run
```bash
# Build image
docker build -t bop:1.0.0 .

# Run commands
docker run --rm bop:1.0.0 --help

# Run with persistent data
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  bop:1.0.0 \
  --host 192.168.1.100 --user admin --password secret \
  test-connection
```

### Option 2: Docker Compose (Recommended)

#### Create docker-compose.yml
```yaml
version: '3.8'

services:
  bop:
    build: .
    container_name: bop
    volumes:
      # Mount configuration
      - ./config:/app/config:ro
      # Mount data directory for persistence
      - ./data:/app/data
      # Optional: mount logs
      - ./logs:/app/logs
    environment:
      # Default gateway settings
      - EJOIN_HOST=192.168.1.100
      - EJOIN_PORT=80
      - EJOIN_USER=admin
      - EJOIN_PASSWORD=your_password
      - PYTHONUNBUFFERED=1
    networks:
      - bop_network
    restart: unless-stopped
    
  # Optional: Web dashboard (future feature)
  # bop-web:
  #   build: 
  #     context: .
  #     dockerfile: Dockerfile.web
  #   ports:
  #     - "8080:8080"
  #   depends_on:
  #     - bop

networks:
  bop_network:
    driver: bridge

volumes:
  bop_data:
  bop_config:
```

#### Create Directory Structure
```bash
mkdir -p {config,data,logs}

# Create sample configuration
cat > config/gateways.csv << 'EOF'
Device Name,Device Local IP,Internal Access URL,Username,Password
Gateway1,192.168.1.234,http://192.168.1.234:80/,root,zyg0-poPx-tHey
Gateway2,192.168.1.150,http://192.168.1.150:80/,root,zyg0-poPx-tHey
Gateway3,192.168.1.109,http://192.168.1.109:80/,root,zyg0-poPx-tHey
EOF
```

#### Deploy with Docker Compose
```bash
# Start services
docker-compose up -d

# Run commands
docker-compose exec bop python -m bop.cli --help

# View logs
docker-compose logs -f bop

# Stop services
docker-compose down
```

### Docker Production Setup

#### Environment Variables
```bash
# Create environment file
cat > .env << 'EOF'
# Default gateway configuration
EJOIN_HOST=192.168.1.100
EJOIN_PORT=80
EJOIN_USER=admin
EJOIN_PASSWORD=your_secure_password

# Application settings
BOXOFPORTS_LOG_LEVEL=INFO
BOXOFPORTS_DATA_DIR=/app/data
BOXOFPORTS_CONFIG_DIR=/app/config

# Database settings
BOXOFPORTS_DB_PATH=/app/data/bop.db
EOF
```

## 🚀 Quick Start Examples

### macOS Quick Start
```bash
# After installation
source ~/bop/bop/venv/bin/activate

# Test connection
bop --host 192.168.1.100 --user admin --password secret test-connection

# Send SMS
bop --host 192.168.1.100 --user admin --password secret \
  sms send --to "+1234567890" --text "Hello from macOS!" --ports "1A"
```

### Windows Quick Start
```powershell
# After installation (PowerShell)
Set-Location "$env:USERPROFILE\bop\bop"
.\venv\Scripts\Activate.ps1

# Test connection
python -m bop.cli --host 192.168.1.100 --user admin --password secret test-connection

# Send SMS
python -m bop.cli --host 192.168.1.100 --user admin --password secret `
  sms send --to "+1234567890" --text "Hello from Windows!" --ports "1A"
```

### Docker Quick Start
```bash
# Test connection
docker run --rm bop:1.0.0 \
  --host 192.168.1.100 --user admin --password secret \
  test-connection

# Send SMS
docker run --rm bop:1.0.0 \
  --host 192.168.1.100 --user admin --password secret \
  sms send --to "+1234567890" --text "Hello from Docker!" --ports "1A"
```

## 🔧 Advanced Configuration

### Configuration File Locations

#### macOS/Linux
- System-wide: `/etc/bop/config.ini`
- User-specific: `~/.config/bop/config.ini`
- Local project: `./config/config.ini`

#### Windows
- System-wide: `C:\ProgramData\bop\config.ini`
- User-specific: `%USERPROFILE%\.config\bop\config.ini`
- Local project: `.\config\config.ini`

### Environment Variables
```bash
# Gateway connection
export EJOIN_HOST=192.168.1.100
export EJOIN_PORT=80
export EJOIN_USER=admin
export EJOIN_PASSWORD=secret

# Application settings
export BOXOFPORTS_LOG_LEVEL=INFO
export BOXOFPORTS_TIMEOUT=30
export BOXOFPORTS_RETRIES=3
```

### Logging Configuration
```bash
# Enable debug logging
bop --verbose --host 192.168.1.100 test-connection

# Log to file
bop --host 192.168.1.100 test-connection 2>&1 | tee bop.log
```

## 🛠️ Troubleshooting

### Common Installation Issues

#### Python Version Conflicts
```bash
# macOS: Use specific Python version
python3.11 -m pip install -e .

# Windows: Use py launcher
py -3.11 -m pip install -e .
```

#### Permission Issues
```bash
# macOS/Linux: Use virtual environment
python3 -m venv venv
source venv/bin/activate

# Windows: Run as administrator if needed
# Or use virtual environment
```

#### Network Issues
```bash
# Test network connectivity
ping 192.168.1.100

# Test port connectivity
telnet 192.168.1.100 80
# Or use nc: nc -zv 192.168.1.100 80
```

### Performance Tuning

#### For High-Volume SMS Operations
```bash
# Increase timeout and retries
export BOXOFPORTS_TIMEOUT=60
export BOXOFPORTS_RETRIES=5

# Use specific intervals
bop sms spray --intvl-ms 100 --ports "1A-10D" --to "+1234567890" --text "Bulk message"
```

#### For Multiple Gateways
```bash
# Use configuration file with multiple gateways
# Run parallel operations using scripts or process managers
```

## 🔐 Security Best Practices

### Credential Management
```bash
# Use environment variables instead of command line
export EJOIN_PASSWORD=secure_password
bop --host 192.168.1.100 --user admin test-connection

# Use configuration files with restricted permissions
chmod 600 ~/.config/bop/config.ini
```

### Network Security
- Use VPN connections to gateway networks
- Implement firewall rules for gateway access
- Use HTTPS where supported by gateways
- Monitor and log all gateway access

## 📞 Support and Maintenance

### Getting Help
- **Documentation**: Full docs available online
- **Email Support**: support@altheasignals.net
- **Issue Reporting**: Include version, OS, and error messages

### Version Updates
```bash
# Check current version
bop --version

# Update to latest version
git pull origin main
pip install -e . --upgrade
```

### Backup and Recovery
```bash
# Backup configuration and data
tar -czf bop-backup-$(date +%Y%m%d).tar.gz ~/.config/bop ./data

# Restore from backup
tar -xzf bop-backup-20250101.tar.gz
```

---

**BoxOfPorts Deployment Guide**  
Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.

For technical support: support@altheasignals.net  
Learn more: https://altheasignals.net
