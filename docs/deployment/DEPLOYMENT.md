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

### Prerequisites by Installation Method

#### For Automated Installation (Recommended)
**Only Python 3.11+ required** - our installer handles everything else:
```bash
# Check Python version
python3 --version
# Should show Python 3.11.0 or higher
```

#### For Development Mode
**Requires pyenv** for Python version management:
```bash
# Install pyenv first (macOS)
brew install pyenv

# Or follow: https://github.com/pyenv/pyenv#installation
```

#### For Manual Installation
**Requires Python 3.11+ with venv support** (usually included):
```bash
python3 --version  # 3.11.0+
python3 -m venv --help  # Should work
```

### Option 1: Automated Installation (Recommended)

#### Step 1: Install Python 3.11+ (if needed)
```bash
# macOS with Homebrew
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
git clone https://github.com/altheasignals/BoxOfPorts.git
cd BoxOfPorts

# Or if you have the package directly:
# tar -xzf bop-1.0.0.tar.gz
# cd bop-1.0.0

# Install in virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install bop
pip install -e .

# Verify installation
boxofports --help
```
### Option 2: System-wide Installation
```bash
# Install system-wide (requires admin privileges)
sudo pip3 install -e .

# Verify
boxofports --help
```

### macOS Configuration

#### Create Gateway Profiles (Recommended)
```bash
# Create profiles for your gateways
boxofports config add-profile gateway1 --host 192.168.1.100 --user admin --password secure_pass
boxofports config add-profile gateway2 --host 192.168.1.101 --user admin --password secure_pass

# List profiles
boxofports config list

# Switch between profiles
boxofports config switch gateway1
boxofports test-connection
```

#### Alternative: Environment Variables (Fallback)
```bash
# For single gateway setup, you can use environment variables
echo "export EJOIN_HOST=192.168.1.100" >> ~/.zshrc
echo "export EJOIN_USER=admin" >> ~/.zshrc
echo "export EJOIN_PASSWORD=secure_password" >> ~/.zshrc
source ~/.zshrc
```

## 🪟 Windows Installation

### Prerequisites
**Requirements:**
- **Python 3.11+** - our installer handles the rest
- **PowerShell** - included with most modern Windows versions

```powershell
# Check Python version (PowerShell)
python --version
# Should show Python 3.11.0 or higher

# Verify PowerShell is available
$PSVersionTable.PSVersion
# Should show PowerShell version info
```

### Option 1: Direct Installation (Recommended)

#### Step 1: Install Python (if needed)
1. Download Python 3.11+ from [python.org](https://www.python.org/downloads/windows/)
2. Run installer with these options:
   - ✅ Add Python to PATH
   - ✅ Install pip
   - ✅ Install for all users (if admin)

#### Step 2: Install boxofports (from a PowerShell terminal)
```powershell
# Create working directory
New-Item -ItemType Directory -Path "$env:USERPROFILE\bop" -Force
Set-Location "$env:USERPROFILE\bop"

# Clone repository or extract package
git clone https://github.com/altheasignals/BoxOfPorts.git
Set-Location BoxOfPorts

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install bop
pip install -e .

# Verify installation
python -m bop.cli --help
```

#### Step 3: Verify Installation
```powershell
# Test the installation
python -m boxofports.cli --help

# Create your first profile
python -m boxofports.cli config add-profile gateway1 --host 192.168.1.100 --user admin --password your_password

# Test connection
python -m boxofports.cli test-connection
```

### Option 2: Using Windows Subsystem for Linux (WSL)
```bash
# Install WSL if not already installed
wsl --install

# Inside WSL, follow the Linux/macOS instructions
```

### Windows Configuration

#### Create Gateway Profiles (Recommended)
```powershell
# Create profiles for your gateways
python -m boxofports.cli config add-profile gateway1 --host 192.168.1.100 --user admin --password secure_pass
python -m boxofports.cli config add-profile gateway2 --host 192.168.1.101 --user admin --password secure_pass

# List profiles
python -m boxofports.cli config list

# Switch between profiles
python -m boxofports.cli config switch gateway1
python -m boxofports.cli test-connection
```

## 🐳 Docker Deployment

### Quick Docker Setup

The repository includes a production-ready Dockerfile and docker-compose.yml:

```bash
# Clone and build
git clone https://github.com/altheasignals/BoxOfPorts.git
cd BoxOfPorts
docker build -t bop .

# Test it works
docker run --rm boxofports --help
```

### Docker Commands

#### Basic Usage
```bash
# Test connection to gateway
docker run --rm bop \\
  --host 192.168.1.100 --user admin --password your_password \\
  test-connection

# Send SMS
docker run --rm bop \\
  --host 192.168.1.100 --user admin --password your_password \\
  sms send --to "+1234567890" --text "Hello Docker!" --ports "1A"
```

#### Using Profiles in Docker
```bash
# Create data volume for persistent profiles
docker volume create bop_data

# Create profiles
docker run --rm -v bop_data:/app/data bop \\
  config add-profile gateway1 \\
  --host 192.168.1.100 --user admin --password pass1

docker run --rm -v bop_data:/app/data bop \\
  config add-profile gateway2 \\
  --host 192.168.1.101 --user admin --password pass2

# List profiles
docker run --rm -v bop_data:/app/data boxofports config list

# Use profiles (no need to specify connection details)
docker run --rm -v bop_data:/app/data boxofports test-connection
```

### Docker Compose (Production)

The included `docker-compose.yml` provides a full production setup:

```bash
# Start services
docker-compose up -d

# Run commands using the service
docker-compose exec boxofports config add-profile prod \\
  --host 192.168.1.100 --user admin --password secure_pass

docker-compose exec boxofports test-connection

# View logs
docker-compose logs -f bop
```

### Environment Variables (Fallback Only)

Environment variables provide fallback configuration when no profiles exist:

```bash
# Create .env file for fallback config
cat > .env << 'EOF'
EJOIN_HOST=192.168.1.100
EJOIN_PORT=80
EJOIN_USER=admin
EJOIN_PASSWORD=your_password
EOF

# Use with docker-compose (will use .env automatically)
docker-compose up -d
```

**Recommended:** Use profiles instead of environment variables for multiple gateways.

## 🚀 Quick Start Examples

### macOS Quick Start
```bash
# After installation
source ~/bop/bop/venv/bin/activate

# Test connection
boxofports --host 192.168.1.100 --user admin --password secret test-connection

# Send SMS
boxofports --host 192.168.1.100 --user admin --password secret \
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
docker run --rm bop \\
  --host 192.168.1.100 --user admin --password your_password \\
  test-connection

# Send SMS
docker run --rm bop \\
  --host 192.168.1.100 --user admin --password your_password \\
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
boxofports --verbose --host 192.168.1.100 test-connection

# Log to file
boxofports --host 192.168.1.100 test-connection 2>&1 | tee bop.log
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
boxofports sms spray --intvl-ms 100 --ports "1A-10D" --to "+1234567890" --text "Bulk message"
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
boxofports --host 192.168.1.100 --user admin test-connection

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
boxofports --version

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
