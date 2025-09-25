# CSV Port Support for BoxOfPorts

When the music plays, the ports dance together in harmony. This document describes how to use CSV files to specify multiple ports across all BoxOfPorts commands - like a river flowing into the sea.

## Overview

All `--ports` modifiers in BoxOfPorts now accept CSV files as input. This enables powerful batch operations and makes managing large numbers of ports as smooth as a Garcia riff.

## Basic Usage

Instead of specifying ports manually:
```bash
boxofports sms send --ports 1A,2B,3C,4D --to 1234567890 --text "Hello world"
```

You can use a CSV file:
```bash
boxofports sms send --ports ports.csv --to 1234567890 --text "Hello world"
```

## CSV Format Requirements

### Required Column
- **`port`**: The port specification (required)

### Optional Column  
- **`slot`**: The slot specification (optional)

### CSV Examples

#### Simple Port List
```csv
port
1A
2B
3C
4D
```

#### Ports with Explicit Slots
```csv
port,slot
1,A
2,B
3,C
4,D
```

#### Mixed Format with Decimal Slots
```csv
port,slot
1,01
2,02
3,03
4,04
```

#### Mixed Numeric and Letter Slots
```csv
port,slot
1,A
2,02
3,C
4,04
5
```

When no slot is specified, the system defaults to slot 1 (equivalent to 'A' or '.01').

## Slot Format Rules

The magic happens in how ports and slots combine:

### Letter Format
- **Port + Letter Slot**: `port=1, slot=A` → `1A`
- **Port + Letter Slot**: `port=2, slot=D` → `2D`

### Decimal Format  
- **Port + Numeric Slot**: `port=3, slot=01` → `3.01`
- **Port + Numeric Slot**: `port=4, slot=04` → `4.04`

### Equivalencies
These formats are equivalent:
- `1A` = `1.01` (Port 1, Slot 1)
- `2B` = `2.02` (Port 2, Slot 2) 
- `3C` = `3.03` (Port 3, Slot 3)
- `4D` = `4.04` (Port 4, Slot 4)

## Supported Commands

CSV port support is available across all port-related commands:

### SMS Commands
```bash
# Send SMS using CSV ports
boxofports sms send --ports ports.csv --to 1234567890 --text "Hello"

# Spray SMS using CSV ports  
boxofports sms spray --ports ports.csv --to 1234567890 --text "Urgent message"
```

### Operations Commands
```bash
# Lock ports from CSV
boxofports ops lock --ports ports.csv

# Unlock ports from CSV
boxofports ops unlock --ports ports.csv

# Get IMEI values for CSV ports
boxofports ops get-imei --ports ports.csv

# Generate IMEI template with CSV ports
boxofports ops imei-template --ports ports.csv --output template.csv
```

### IMEI Management (Enhanced)
The `set-imei` command now uses a unified approach:

```bash
# Set IMEI for multiple ports with matching IMEIs
boxofports ops set-imei --ports ports.csv --imeis 123456789012345,987654321098765

# Use CSV for both ports and IMEIs  
boxofports ops set-imei --ports ports.csv --imeis imeis.csv

# Supports all existing port formats too
boxofports ops set-imei --ports "1A,2B,3-6" --imeis imeis.csv
boxofports ops set-imei --ports "*" --imeis all_imeis.csv  # All ports
```

### Inbox Filtering
```bash  
# Filter inbox messages by CSV ports
boxofports inbox list --ports ports.csv

# Show only messages from specific ports
boxofports inbox list --ports ports.csv --type regular

# Filter by multiple individual ports
boxofports inbox list --ports "1A,2B,3C" --type regular
```

## Advanced Features

### Wildcard Support
Use `*` or `all` to process all ports in the gateway:
```bash
boxofports ops get-imei --ports "*"
boxofports sms send --ports "all" --to 1234567890 --text "Broadcast message"
```

### Mixed Specifications
Combine CSV files with other port formats:
```bash
boxofports ops lock --ports "1A,ports.csv,8-12"  # Single + CSV + Range
```

### IMEI CSV Format
For IMEI operations, CSV files can include IMEI values:

```csv  
port,slot,imei
1,A,123456789012345
2,B,987654321098765
3,01,111222333444555
4,02,999888777666555
```

Or just IMEI values:
```csv
imei
123456789012345
987654321098765
111222333444555
```

## Error Handling

The system provides helpful error messages:

- **Missing required column**: `CSV file must contain a 'port' column`
- **Empty files**: `No valid ports found in CSV file`
- **Invalid formats**: `Invalid port format: 'XYZ'`
- **Port/IMEI mismatch**: `Port and IMEI count mismatch: Ports: 3, IMEIs: 2`

## Slot Confirmation

When using ports without explicit slots (defaulting to slot 1), the system will ask for confirmation:

```
⚠️  Some ports don't specify a slot - defaulting to slot 1
Ports can specify slots as: 1A, 1B, 1C, 1D or 1.01, 1.02, 1.03, 1.04

Proceed with slot 1 as default? [y/N]: 
```

Use `--force` to skip this confirmation in automated scripts.

## Best Practices

### File Organization
Keep your CSV files organized like a well-tuned setlist:
```
ports/
├── main_ports.csv          # Primary ports
├── backup_ports.csv        # Backup ports  
├── testing_ports.csv       # Test ports
└── imei_changes.csv        # IMEI mappings
```

### Naming Conventions
Use descriptive names that flow like the music:
- `production_ports.csv`
- `emergency_ports.csv` 
- `maintenance_ports.csv`
- `new_imei_values.csv`

### Validation
Always test with `--dry-run` first:
```bash
boxofports ops set-imei --ports ports.csv --imeis imeis.csv --dry-run
```

## Integration with Existing Workflows

CSV support seamlessly integrates with existing port specifications. The system automatically detects CSV files and processes them accordingly, while maintaining full backward compatibility with all existing port formats.

This enhancement makes BoxOfPorts even more powerful for managing large-scale EJOIN router deployments, letting you orchestrate your ports like Jerry conducting a cosmic jam session. 🎸

---

*"Sometimes the light's all shinin' on me, other times I can barely see"* - Just like managing ports, CSV support brings clarity to complex configurations.