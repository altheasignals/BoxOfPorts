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

One-liner (replace <GITHUB_OWNER> with your GitHub handle or org):

```bash
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | bash
```

This installs a `bop` wrapper to `/usr/local/bin/bop` by default.

Options:
- Set IMAGE override at install time:
  ```bash
  IMAGE=altheasignals/boxofports:1.0.0 \
  curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | bash
  ```
- Install to a custom prefix (e.g., in CI):
  ```bash
  PREFIX=$HOME/.local BIN_DIR=$HOME/.local/bin \
  curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | bash
  ```

## Using the CLI

- First run creates `~/.boxofports` if not present.
- Your current directory is mounted to `/app/data` (so commands operate on local files by default).
- Config is mounted from `~/.boxofports` to `/app/config`.

Examples:
```bash
bop --help
bop gateway list
bop --update gateway status
bop --config ~/.boxofports --data $PWD gateway import --file ./gateways.csv
```

Advanced:
- Override image: `bop --image altheasignals/boxofports:1.0.1 -- gateway list`
- Apple Silicon forcing platform: `BOP_DOCKER_PLATFORM=linux/arm64 bop --help`
- Pass env vars through: `BOXOFPORTS_LOG_LEVEL=DEBUG bop gateway list`

## Notes for Maintainers

- Ensure `pyproject.toml` [project.version] is kept in sync with release tags.
- The Dockerfile already sets a non-root user and defines volumes for `/app/config`, `/app/data`, `/app/logs`.
- Entry point forwards args to `python -m boxofports.cli`.