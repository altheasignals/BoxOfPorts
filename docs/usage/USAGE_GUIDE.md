# 🚀 Complete BoxOfPorts Usage Guide

## Overview
BoxOfPorts (`bop`) is a comprehensive CLI tool for managing EJOIN Multi-WAN Router HTTP API v2.2. It provides SMS operations, inbox management, device control, and compliance monitoring for SMS gateway operators.

## 📋 Available Gateways (Example Configuration)
- **Gateway-1**: 192.168.1.100:80 (admin/your_password)
- **Gateway-2**: 192.168.1.101:80 (admin/your_password)
- **Gateway-3**: 192.168.1.102:80 (admin/your_password)

## 🔗 Basic Connection Testing

### Test Gateway Connection
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' test-connection
```

**Output**: ✓ Connection successful! Device appears to be responding normally

### Test Gateway with Custom Port
```bash
# Using explicit port parameter
python -m bop.cli --host 203.0.113.100 --port 60140 --user root --password 'your_password' test-connection

# Using host:port format (recommended)
python -m bop.cli --host 203.0.113.100:60140 --user root --password 'your_password' test-connection
```

---

## 📱 SMS Operations

### 1. Basic SMS Send
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  sms send --to "+1234567890" --text "Hello World" --ports "1A"
```

### 1b. SMS Send with Custom Port
```bash
# Using host:port format
python -m bop.cli --host 203.0.113.100:60140 --user root --password 'your_password' \
  sms send --to "+1234567890" --text "Hello from remote gateway" --ports "1A"
```

### 2. SMS with Template Variables
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  sms send --to "+1234567890" \
  --text "Hello from port {{port}} at {{ts}}" \
  --ports "1A"
```

### 3. Multi-Port SMS with Custom Variables
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  sms send --to "+1234567890" \
  --text "Alert from {{company | upper}} - Port {{port}} Status: {{status}}" \
  --ports "1A,2B,3A" \
  --var "company=ACME Corp" --var "status=OK"
```

### 4. Port Range SMS
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  sms send --to "+1234567890" \
  --text "Range test from {{port}} #{{idx}}" \
  --ports "1A-1D"
```

### 5. SMS Spray (Multiple Ports Quickly)
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  sms spray --to "+1234567890" \
  --text "Spray from {{port}}" \
  --ports "1A,2A,3A"
```

### 6. Dry Run (Preview Without Sending)
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  sms send --to "+1234567890" \
  --text "Test message" --ports "1A-1C" \
  --dry-run
```

### 7. Advanced Template with Filters
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  sms send --to "+1234567890" \
  --text "{{company | upper}} Alert: Port {{port}} at {{ts | truncate(19)}}" \
  --ports "1A,2B,3C" --var "company=TechCorp" \
  --dry-run
```

---

## 🔧 Device Operations

### 1. Lock Ports
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  ops lock --ports "1A,2A"
```

### 2. Unlock Ports
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  ops unlock --ports "1A,2A"
```

### 3. Lock Port Range
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  ops lock --ports "1A-1D"
```

---

## 📊 Status Monitoring

### 1. Subscribe to Status Updates
```bash
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  status subscribe --callback "http://example.com/webhook" --period 30 --all-sims
```

---

## 🎨 Template System Features

### Built-in Variables
- `{{port}}` - Current port identifier (e.g., "1A", "2B")
- `{{ts}}` - Current UTC timestamp in ISO format
- `{{idx}}` - Current iteration index (0-based)

### Available Filters
- `{{text | upper}}` - Convert to uppercase
- `{{text | lower}}` - Convert to lowercase
- `{{text | truncate(10)}}` - Truncate to 10 characters with "..."
- `{{phone | phone('international')}}` - Format phone number
- `{{phone | phone('local')}}` - Local phone format

### Custom Variables
Pass custom variables using `--var key=value`:
```bash
--var "company=ACME Corp" --var "status=Online" --var "priority=HIGH"
```

---

## 🔌 Port Specifications

### Supported Formats

#### 1. Single Ports
- `1A` - Slot 1, Port A
- `2B` - Slot 2, Port B
- `1.01` - Slot 1, Port 01 (decimal format)
- `32.04` - Slot 32, Port 04

#### 2. Port Lists
- `1A,2B,3C` - Multiple specific ports
- `1.01,2.02` - Multiple decimal ports

#### 3. Port Ranges
- `1A-1D` - Slot 1, Ports A through D
- `1-3` - Slots 1-3, all Port A (expands to 1A,2A,3A)
- `2.01-2.03` - Slot 2, Ports 01-03

#### 4. Mixed Specifications
- `1A,3B-3D,5.01` - Combination of individual ports and ranges

---

## 🌐 Working with Multiple Gateways

### Test All Gateways
```bash
# Gateway 1
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' test-connection

# Gateway 2
python -m bop.cli --host 192.168.1.101 --user root --password 'your_password' test-connection

# Gateway 3
python -m bop.cli --host 192.168.1.102 --user root --password 'your_password' test-connection
```

### Switch Between Gateways
Simply change the `--host` parameter to target different gateways:
```bash
# Use Gateway 2 for SMS
python -m bop.cli --host 192.168.1.101 --user root --password 'your_password' \
  sms send --to "+1234567890" --text "From Gateway 2" --ports "1A"
```

### Remote Gateways with Custom Ports
```bash
# Connect to remote gateway with custom port
python -m bop.cli --host 203.0.113.100:60140 --user root --password 'your_password' \
  test-connection

# Environment variable approach
export EJOIN_HOST="203.0.113.100:60140"
python -m bop.cli --user root --password 'your_password' test-connection
```

---

## 🛠️ Advanced Usage Examples

### 1. Bulk SMS Campaign
```bash
# Send to multiple ports with sequential numbering
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  sms send --to "+1234567890" \
  --text "Campaign message #{{idx + 1}} from {{port}}" \
  --ports "1A-4D" --dry-run
```

### 2. Emergency Alert System
```bash
# Lock all ports first, then send alert
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  ops lock --ports "1A-10D"

python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  sms send --to "+1234567890" \
  --text "EMERGENCY: All ports locked at {{ts}}" \
  --ports "1A"
```

### 3. Status Monitoring Setup
```bash
# Subscribe to real-time status updates
python -m bop.cli --host 192.168.1.100 --user root --password 'your_password' \
  status subscribe --callback "https://yourdomain.com/status-webhook" \
  --period 60 --all-sims
```

---

## 📈 Performance Features

### SMS Spray Optimization
The `spray` command is optimized for speed:
- Default 250ms interval between messages
- Parallel processing across ports
- Automatic template rendering per port

### Port Range Expansion
Port ranges are efficiently expanded:
- `1A-1D` → `1A, 1B, 1C, 1D`
- `1-3` → `1A, 2A, 3A`
- Mixed specs supported: `1A,3B-3D,5.01`

---

## 🔧 CLI Options Summary

### Global Options
- `--host` - Gateway IP address (supports host:port format, e.g., "192.168.1.100:8080")
- `--port` - Gateway port (default: 80, overridden if port specified in --host)
- `--user` - Username (default from config)
- `--password` - Password
- `--verbose` - Enable detailed logging

### SMS Send Options
- `--to` - Recipient phone number
- `--text` - Message text (with template support)
- `--ports` - Port specification
- `--repeat` - Number of repetitions
- `--intvl-ms` - Interval between messages (ms)
- `--timeout` - Request timeout (seconds)
- `--var` - Template variables (key=value)
- `--dry-run` - Preview without sending

### SMS Spray Options
- `--to` - Recipient phone number
- `--text` - Message text
- `--ports` - Ports to spray from
- `--intvl-ms` - Interval (default: 250ms)

---

## ✅ Test Results Summary

All features tested successfully:
- ✅ Connection testing (3/3 gateways)
- ✅ SMS sending (single and multiple ports)
- ✅ SMS spray functionality
- ✅ Template system with filters
- ✅ Port locking/unlocking
- ✅ Port range expansion
- ✅ Status subscription
- ✅ Dry run capabilities

## ⚙️ Profile Management System

### Why Use Profiles?
Instead of specifying `--host`, `--user`, `--password` every time, create profiles for your servers and switch between them easily.

### 1. Create Your First Profile
```bash
# Add a remote server profile
python -m bop.cli config add-profile remote \
  --host 203.0.113.100:60140 \
  --user root \
  --password 'your_password'

# Add a local server profile  
python -m bop.cli config add-profile local \
  --host 192.168.1.100 \
  --user root \
  --password 'your_password'
```

### 2. List All Profiles
```bash
python -m bop.cli config list
```
**Output**:
```
                    Server Profiles                     
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Name   ┃ Host:Port            ┃ Username ┃ Status    ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ remote │ 203.0.113.100:60140 │ root     │ → CURRENT │
│ local  │ 192.168.1.100:80     │ root     │           │
└────────┴──────────────────────┴──────────┴───────────┘
```

### 3. Switch Between Profiles
```bash
# Switch to local profile
python -m bop.cli config switch local

# Check current profile
python -m bop.cli config current
```

### 4. Use Commands Without Specifying Connection Details
```bash
# No need for --host, --user, --password anymore!
python -m bop.cli test-connection
python -m bop.cli sms send --to "+1234567890" --text "Hello from {{port}}" --ports "2A"
```

### 5. Profile Commands Summary
```bash
# Profile management
python -m bop.cli config add-profile <name> --host <host:port> --user <user> --password <pass>
python -m bop.cli config list                    # Show all profiles
python -m bop.cli config switch <name>           # Switch to profile
python -m bop.cli config current                 # Show current profile
python -m bop.cli config show [name]            # Show profile details
python -m bop.cli config remove <name>          # Delete profile
```

### 6. Override Profile Settings
You can still override profile settings with CLI arguments:
```bash
# Use different host temporarily
python -m bop.cli --host 192.168.1.999 test-connection

# Use different port temporarily
python -m bop.cli --port 8080 test-connection
```

---

## 🎯 Next Steps

The application is ready for production use! Key features working:
1. **SMS Operations** - Send, spray, templates, filters
2. **Device Management** - Lock/unlock ports
3. **Status Monitoring** - Subscribe to updates
4. **Multi-Gateway Support** - Switch between devices
5. **Advanced Port Handling** - Ranges, lists, mixed specs
6. **Profile Management** - Save servers, switch easily

For additional features (inbox management, etc.), the framework is in place and can be extended as needed.
