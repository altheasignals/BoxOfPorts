# Changelog

All notable changes to BoxOfPorts will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-09-26

### Added
- **Sorting for All Tables**: New `--sort` option for all table-producing commands
  - Multi-column sorting with per-column ascending/descending control: `--sort 2,1d,4`
  - Smart default sorting behavior: timestamp descending → port ascending → second column ascending
  - Consistent sorting across display tables, CSV exports, and JSON exports
  - Column numbering matches display order for intuitive usage
- **Centralized Table Rendering**: Unified table display and export system
  - Single point of control for table formatting, sorting, and export integration
  - Maintains existing CSV/JSON export functionality and console-only modes
  - Improved code efficiency and consistency across all commands

### Enhanced
- **Pipeline Integration**: Sorted data flows through all pipeline modes
  - Console-only exports (`--csv`, `--json`) reflect the same sort order as displayed tables
  - File exports maintain sorted order for better downstream processing
  - Default sort provides natural ordering when no explicit sort specified

### Technical
- Intelligent coercion for timestamps, ports, and generic data types
- Stable multi-column sorting preserves relative order of equal elements
- Backward compatible with all existing export and display patterns
- No new external dependencies - uses only Python standard library

## [1.1.0] - 2025-01-26

### Added
- **Device Alias Feature**: New `device_alias` field in profile configurations
  - Add custom aliases to profiles using `--alias` option in `config add-profile`
  - Aliases default to the first word of the profile name if not specified
  - Device aliases appear as a new column in all tables and exports
  - Support for multiple profiles per device (e.g., internal vs external IP addresses)
  - New `config edit-profile` command to modify existing profiles including aliases
  - Backward compatibility: existing profiles automatically get aliases based on profile names
  - Environment variable support: `EJOIN_ALIAS` can be used to set device alias

### Enhanced
- **Table Export Consistency**: Device aliases included in all CSV/JSON exports
  - SMS send/spray task and results tables now include device alias
  - Inbox list, search, and stop commands include device alias
  - Operations get-imei command includes device alias
  - Configuration list shows device aliases
- **Command Completion**: Updated bash completion with new commands and options
- **Documentation**: Enhanced README with device alias usage examples and workflows

### Technical
- Improved backward compatibility with automatic profile migration
- Enhanced CSV/JSON export data conversion functions
- Consistent device alias threading across all command data flows
- Maintained pipeline-friendly console-only export modes

## [1.0.2] - Previous Release

### Features
- SMS operations with template support
- Inbox management and filtering
- Device operations (lock/unlock ports, IMEI management)
- Profile-based configuration management
- CSV/JSON export capabilities
- Rich terminal interface with tables
- Comprehensive CLI with bash completion

---

*"What a long strange trip it's been, but the river keeps flowing and the data keeps grooving!"* 🎵