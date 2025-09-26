# Changelog

All notable changes to BoxOfPorts will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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