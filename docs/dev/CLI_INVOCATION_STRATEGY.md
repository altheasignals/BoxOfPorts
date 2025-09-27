# BoxOfPorts CLI Invocation Strategy & CI/CD Versioning Model

*"Such a long, long time to be gone, and a short time to be there"*

## 🎯 Overview

This document describes the implemented separation between the local `boxofports` CLI and the Docker-based `bop` wrapper, ensuring clear contexts and consistent usage patterns.

## 🔧 Command Strategy

### boxofports (Local CLI)
- **Context**: Native binary installation (user/developer/system-wide flavors)
- **Role**: Main CLI for direct Python usage
- **Storage**: `$HOME/.boxofports/`
- **Installation**: Local Python environment
- **Usage**: `boxofports --help`

### bop (Docker Wrapper)
- **Context**: Docker container service provided by Althea Signals
- **Role**: Ensures latest stable/bleeding edge Docker image usage
- **Storage**: Respects `$HOME/.boxofports/` via volume mounts
- **Installation**: Standalone script from `/docker/bop`
- **Usage**: `boxofports --help`

## 📈 Versioning Model

### Semantic Versioning: MAJOR.MINOR.PATCH

#### Rules
- **boxofports**: Follows semantic versioning
- **bop**: Tracks DockerHub image version
- **Stable releases**: Always PATCH 0 of MAJOR.MINOR (e.g., 1.5.0)
- **Current version**: 1.0.0 (starting point)

#### Automatic Workflow
Every merge to `main` triggers:
1. PATCH bump (1.0.1 → 1.0.2)
2. DockerHub image rebuild via GitHub Actions
3. Git tagging of release (e.g., v1.0.3)

## 🐳 Docker Wrapper Behavior

### Version Management
- **Default mode**: Uses stable releases (X.X.0)
- **Steal Your Face mode**: Syncs with latest development (X.X.X)
- **Version checking**: Hourly cache with upstream comparison
- **Force updates**: Automatically enforces stable when X.X.0 released

### Special Commands
- `boxofports --steal-your-face`: Toggle bleeding edge mode
- `boxofports --bop-version`: Show wrapper and container versions
- `boxofports --bop-update`: Force update check and pull

### Argument Passing
- **Philosophy**: boxofports never processes command-line arguments
- **Implementation**: All args passed directly to `boxofports` in container
- **Configuration**: Behavioral changes via environment variables only

## 🗂️ File Structure

```
gateway-manager/
├── boxofports/                    # Python package
│   ├── cli.py                    # Main CLI using 'boxofports'
│   ├── __version__.py            # Version info
│   └── ...
├── docker/
│   └── bop                       # Standalone Docker wrapper
├── scripts/
│   ├── bop                       # Copy of Docker wrapper
│   └── bop-legacy                # Original simple wrapper
├── .github/workflows/
│   └── release.yml               # CI/CD pipeline
├── pyproject.toml                # Only exports 'boxofports'
└── Dockerfile                    # Container build
```

## 🔄 Implementation Changes Made

### ✅ Completed Tasks

1. **CLI Entry Points**
   - Removed `bop` from `pyproject.toml` entry points
   - Only `boxofports` exported as local CLI

2. **Help Text & Messages**
   - Updated all CLI help text to use `boxofports`
   - Updated completion scripts
   - Fixed error messages and examples

3. **Docker Wrapper**
   - Created comprehensive `bop` wrapper with version management
   - Implemented "Steal Your Face" mode for bleeding edge
   - Added automatic stable enforcement

4. **CI/CD Pipeline**
   - GitHub Actions workflow for version bumping
   - Automated DockerHub publishing
   - Stable vs development tagging logic

5. **Installation Scripts**
   - Updated `install-user.sh` to use `boxofports`
   - Fixed Makefile targets
   - Updated Docker entry points

6. **Documentation**
   - Clear separation in README between local and Docker usage
   - Preserved Docker examples as `bop`
   - Updated local examples to `boxofports`

## 📚 Usage Examples

### Local Installation & Usage
```bash
# Install locally
./install-user.sh

# Use local CLI
boxofports config add-profile gateway --host 192.168.1.100
boxofports test-connection
boxofports sms send --to "+1234567890" --text "Hello" --ports "1A"
```

### Docker Wrapper Usage
```bash
# Install Docker wrapper
curl -fsSL https://raw.githubusercontent.com/altheasignals/gateway-manager/main/docker/bop | sudo tee /usr/local/bin/bop
chmod +x /usr/local/bin/bop

# Use Docker wrapper (same commands, managed container)
boxofports config add-profile gateway --host 192.168.1.100
boxofports test-connection
boxofports sms send --to "+1234567890" --text "Hello" --ports "1A"

# Enable bleeding edge mode
boxofports --steal-your-face
```

## 🎵 Philosophy

*"When the music never stops, the container keeps running"*

The design reflects the band's ethos:
- **boxofports**: For the musicians (developers) who want direct access
- **bop**: For the audience (users) who want the show without setup
- **Steal Your Face**: For the deadheads who want to be on the bus with latest changes

The music plays on, whether you're running locally or in the cosmic container! 🌌

---

*Built with ❤️ by Althea Signals Network LLC*