# Port Argument Consistency Updates

## Overview
Standardized all router port specification arguments to use `--ports` throughout the application, maintaining harmony like a well-tuned ensemble.

## Changes Made

### ✅ **Inbox List Command Updated**
**Before:**
```bash
boxofports inbox list --port 1A
boxofports inbox list --port ports.csv
```

**After:**
```bash
boxofports inbox list --ports 1A
boxofports inbox list --ports 1A,2B,3C
boxofports inbox list --ports ports.csv
```

### ✅ **Enhanced Port Parsing**
The inbox list command now supports:
- **Single ports**: `--ports 1A`
- **Multiple ports**: `--ports 1A,2B,3C`  
- **Port ranges**: `--ports 1A-4D`
- **CSV files**: `--ports ports.csv`
- **Mixed formats**: `--ports 1A,ports.csv,8-12`

## Consistency Verification

All router port-related commands now consistently use `--ports`:

| Command | Argument | Supports |
|---------|----------|----------|
| `sms send` | `--ports` | CSV, ranges, lists |
| `sms spray` | `--ports` | CSV, ranges, lists |
| `ops lock` | `--ports` | CSV, ranges, lists |
| `ops unlock` | `--ports` | CSV, ranges, lists |
| `ops get-imei` | `--ports` | CSV, ranges, lists |
| `ops set-imei` | `--ports` | CSV, ranges, lists |
| `inbox list` | `--ports` | CSV, ranges, lists |

## What Stayed the Same

**Network/Connection ports remain as `--port`:**
- `boxofports --port 8080` (device HTTP port)
- `boxofports config add-profile --port 80` (device network port)

These are different from router ports and correctly remain singular.

## Updated Documentation

- Updated help text for `inbox list` command
- Updated CSV support documentation
- Updated bash completion scripts
- Enhanced error handling for multiple port specifications

## Backward Compatibility

**✅ No Breaking Changes:**
All commands now accept both `--port` and `--ports` as aliases. Users can continue using their preferred format:

```bash
# Both work identically
boxofports inbox list --port 1A
boxofports inbox list --ports 1A

# Both work with CSV files
boxofports sms send --port ports.csv --to 1234567890 --text "Hello"
boxofports sms send --ports ports.csv --to 1234567890 --text "Hello"
```

Existing scripts continue to work without modification.

## Benefits

1. **Consistency**: All router port arguments use the same format
2. **Enhanced Functionality**: Inbox filtering now supports multiple ports and CSV files
3. **Intuitive**: `--ports` clearly indicates support for multiple values
4. **Future-Proof**: Consistent interface for all port-related operations

The rhythm of the CLI now flows harmoniously - every command dances to the same beat! 🎵