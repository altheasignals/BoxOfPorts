# BoxOfPorts SMS Inbox Management Documentation

## Overview

The BoxOfPorts CLI (`bop`) provides comprehensive SMS inbox management capabilities, allowing you to retrieve, filter, search, and analyze received SMS messages from your EJOIN Multi-WAN Router.

## Features

### 🔍 Message Classification
Messages are automatically classified into types:
- **Regular**: Normal SMS messages from users
- **STOP**: Opt-out messages containing "STOP", "UNSUBSCRIBE", etc.
- **System**: Messages from operators/services (balance, alerts)
- **Delivery Report**: SMS delivery confirmations
- **Keyword**: Messages containing specific keywords

### 📱 Port Support
- Messages are tagged with receiving port (e.g., "1A", "2B")
- Filter messages by specific ports
- View port-based statistics

### 🎯 Advanced Filtering
- Filter by message type, sender, content, port
- Exclude or show only delivery reports
- Date range filtering
- Keyword-based filtering

## CLI Commands

### `inbox list` - List Messages

List received SMS messages with various filtering options.

```bash
# List all messages (default: 50 messages)
bop inbox list

# List all messages from start
bop inbox list --count 0

# List only STOP messages
bop inbox list --type stop

# List messages from specific port
bop inbox list --port 1A

# List messages containing specific text
bop inbox list --contains "balance"

# List messages from specific sender
bop inbox list --sender "12345"

# Exclude delivery reports
bop inbox list --no-delivery-reports

# Show only delivery reports
bop inbox list --delivery-reports-only

# Output as JSON
bop inbox list --json
```

**Options:**
- `--start-id INTEGER`: Starting SMS ID (default: 1)
- `--count INTEGER`: Number of messages to show, 0=all (default: 50)
- `--type TEXT`: Filter by message type (regular, stop, system, delivery_report)
- `--port TEXT`: Filter by port (e.g., 1A, 2B)
- `--sender TEXT`: Filter by sender number
- `--contains TEXT`: Filter by text content
- `--no-delivery-reports`: Exclude delivery reports
- `--delivery-reports-only`: Show only delivery reports
- `--json`: Output as JSON

### `inbox search` - Search Messages

Search for messages containing specific text.

```bash
# Search for messages containing "STOP"
bop inbox search "STOP"

# Search with detailed output
bop inbox search "balance" --details

# Search from specific starting point
bop inbox search "urgent" --start-id 100
```

**Options:**
- `--start-id INTEGER`: Starting SMS ID (default: 1)
- `--count INTEGER`: Max messages to search, 0=all (default: 0)
- `--details`: Show full message details

### `inbox stop` - STOP Messages

Quickly view all STOP/unsubscribe messages.

```bash
# Show all STOP messages
bop inbox stop

# Output STOP messages as JSON
bop inbox stop --json
```

**Options:**
- `--start-id INTEGER`: Starting SMS ID (default: 1)
- `--json`: Output as JSON

### `inbox summary` - Inbox Statistics

Get comprehensive inbox statistics and summary.

```bash
# Show inbox summary
bop inbox summary

# Output summary as JSON
bop inbox summary --json
```

**Provides:**
- Total message count
- Breakdown by message type
- Port-based statistics
- STOP message count
- Recent senders list
- Date range of messages

### `inbox show` - Message Details

Show detailed information about a specific message.

```bash
# Show details for message ID 123
bop inbox show 123

# Search from different starting point
bop inbox show 456 --start-id 400
```

## Message Types and Classification

### Automatic Classification Rules

1. **STOP Messages**: Contain keywords like:
   - "STOP", "UNSUBSCRIBE", "OPT OUT", "OPT-OUT"

2. **System Messages**: Contain keywords like:
   - "balance", "credit", "recharge", "expired"
   - "network", "service", "plan", "bundle"
   - "data", "minutes", "sms left"

3. **Delivery Reports**: 
   - Have delivery_flag = 1 in API data
   - Usually contain status codes like "DELIVRD"

4. **Regular Messages**: 
   - All other messages from regular users

### Keyword Detection

Messages are automatically scanned for important keywords:
- **stop**: STOP-related keywords
- **help**: Help/information requests
- **balance**: Balance/credit inquiries
- **urgent**: Urgent/emergency messages
- **promotion**: Marketing/promotional content

## Output Formats

### Table View (Default)
```
┌─────────────────── SMS Inbox (15 messages) ────────────────────┐
│ ID │ Type      │ Port │ From        │ Time      │ Content      │
├────┼───────────┼──────┼─────────────┼───────────┼──────────────┤
│ 1  │ 📱 Regular │ 1A   │ 1234567890  │ 01-20 14:30│ Hello world  │
│ 2  │ 🛑 STOP    │ 2B   │ 9876543210  │ 01-20 14:31│ STOP         │
│ 3  │ ⚙️ System  │ 1A   │ 12345       │ 01-20 14:32│ Balance: $10 │
└────┴───────────┴──────┴─────────────┴───────────┴──────────────┘
```

### JSON Output
```json
[
  {
    "id": 1,
    "type": "regular",
    "port": "1A",
    "timestamp": "2025-01-20T14:30:00",
    "sender": "1234567890",
    "recipient": "",
    "content": "Hello world",
    "is_delivery_report": false,
    "keywords": []
  }
]
```

## Filtering Examples

### Complex Filtering Scenarios

```bash
# Find all STOP messages from port 1A
bop inbox list --type stop --port 1A

# Find urgent messages (system classification)
bop inbox search "urgent" --details

# Get recent messages excluding delivery reports
bop inbox list --count 20 --no-delivery-reports

# Find balance-related messages
bop inbox search "balance"

# Check messages from specific short code
bop inbox list --sender "12345"
```

### Monitoring Scenarios

```bash
# Daily STOP message check
bop inbox stop

# Quick inbox health check
bop inbox summary

# Find issues or alerts
bop inbox search "error"
bop inbox search "failed"
bop inbox search "urgent"
```

## Integration Examples

### Shell Scripting

```bash
#!/bin/bash
# Check for new STOP messages and alert

STOP_COUNT=$(bop inbox stop --json | jq length)
if [ $STOP_COUNT -gt 0 ]; then
    echo "⚠️ Found $STOP_COUNT STOP messages!"
    bop inbox stop
fi
```

### JSON Processing

```bash
# Get STOP messages as JSON and process
bop inbox stop --json | jq '.[].sender' | sort | uniq

# Get summary statistics
bop inbox summary --json | jq '.total_messages'
```

## Best Practices

### Regular Monitoring
1. **Daily STOP Check**: `bop inbox stop`
2. **Weekly Summary**: `bop inbox summary`
3. **Filter Important**: `bop inbox list --no-delivery-reports`

### Performance Tips
1. Use `--count` to limit results for large inboxes
2. Use `--start-id` to paginate through messages
3. Use specific filters to reduce processing time
4. Use `--json` for programmatic processing

### STOP Message Management
1. Regularly monitor: `bop inbox stop`
2. Export for compliance: `bop inbox stop --json > stops.json`
3. Track by port: `bop inbox list --type stop --port 1A`

## Troubleshooting

### Common Issues

1. **No messages found**
   - Check router connectivity: `bop test-connection`
   - Verify SMS inbox has messages
   - Try different start-id: `--start-id 1`

2. **Classification seems wrong**
   - View raw content: `bop inbox show <id>`
   - Check message content for classification keywords

3. **Filtering not working**
   - Check exact parameter format
   - Use quotes for text with spaces: `--contains "hello world"`
   - Verify case sensitivity is handled

### Debug Commands
```bash
# Check basic connectivity
bop test-connection

# View raw message data
bop inbox show 1

# Test small batch first
bop inbox list --count 5
```

## API Integration

The inbox functionality uses the EJOIN HTTP API v2.2 SMS inbox endpoints:
- Retrieves messages via `/api/sms/query_inbox`
- Parses base64-encoded content
- Handles delivery reports and regular messages
- Supports pagination with SMS ID ranges

## Security Notes

- Messages are decoded from base64 automatically
- No sensitive data is logged by default
- Use JSON output for programmatic access
- Consider privacy when exporting message content

---

*For more information, use `bop inbox --help` or `bop inbox <command> --help`*