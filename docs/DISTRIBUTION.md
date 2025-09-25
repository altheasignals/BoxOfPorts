# BoxOfPorts Distribution (Docker Hub + Wrapper)

This doc explains how we publish the container and how users install the `bop` wrapper without needing to install Python or the codebase.

## Publishing to Docker Hub

Prereqs:
- A Docker Hub repo: `altheasignals/boxofports`
- GitHub repo secrets:
  - `DOCKERHUB_USERNAME`
  - `DOCKERHUB_TOKEN` (a Docker Hub access token)

Publish steps:
1) Merge to `main` or push a tag `vX.Y.Z`
2) GitHub Actions will build multi-arch images (amd64/arm64) and push:
   - `altheasignals/boxofports:latest`
   - `altheasignals/boxofports:X.Y.Z` (from `pyproject.toml`)

## User Installation

### Default: User Installation (No sudo required)
```bash
curl -fsSL https://raw.githubusercontent.com/altheasignals/boxofports/main/scripts/install-bop.sh | bash
```

This installs a `bop` wrapper to `~/.local/bin/boxofports` by default.

### System-wide Installation (Requires elevated privileges)
```bash
curl -fsSL https://raw.githubusercontent.com/altheasignals/boxofports/main/scripts/install-bop.sh | sudo bash -s -- --system
```

This installs to `/usr/local/bin/boxofports` and is available to all users.

Options:
- Set IMAGE override at install time:
  ```bash
  IMAGE=altheasignals/boxofports:1.0.0 \
  curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | bash
  ```
- Install to a custom directory:
  ```bash
  PREFIX=/opt/boxofports BIN_DIR=/opt/boxofports/bin \
  curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | bash
  ```

## Using the CLI

- First run creates `~/.boxofports` if not present.
- Your current directory is mounted to `/app/data` (so commands operate on local files by default).
- Config is mounted from `~/.boxofports` to `/app/config`.

Examples:
```bash
boxofports --help
boxofports gateway list
boxofports --update gateway status
boxofports --config ~/.boxofports --data $PWD gateway import --file ./gateways.csv
```

Advanced:
- Override image: `boxofports --image altheasignals/boxofports:1.0.1 -- gateway list`
- Apple Silicon forcing platform: `BOP_DOCKER_PLATFORM=linux/arm64 boxofports --help`
- Pass env vars through: `BOXOFPORTS_LOG_LEVEL=DEBUG boxofports gateway list`

## Uninstalling

To avoid version conflicts, use the uninstaller script:

```bash
# Download and run the uninstaller
curl -fsSL https://raw.githubusercontent.com/altheasignals/boxofports/main/scripts/uninstall-bop.sh | bash

# Or if you have the repo locally:
./scripts/uninstall-bop.sh
```

Options:
- `--list-only` - Just show what's installed without removing anything
- `--auto-docker` - Automatically remove Docker installations only

The uninstaller detects:
- pip global and user installations 
- Docker wrapper scripts
- Docker images
- Configuration directories (`~/.boxofports`)
- Development/editable installations

## Notes for Maintainers

- Ensure `pyproject.toml` [project.version] is kept in sync with release tags.
- The Dockerfile already sets a non-root user and defines volumes for `/app/config`, `/app/data`, `/app/logs`.
- Entry point forwards args to `python -m boxofports.cli`.
- The uninstaller excludes cloud storage directories (Google Drive, iCloud, etc.) to avoid slow scans.
