# BoxOfPorts Versioning & Release Management

*"Sometimes the light's all shinin' on me, other times I can barely see"*

This document describes how BoxOfPorts manages versions, releases, and Docker images through our automated workflows.

## 📖 Overview

BoxOfPorts uses a **dual-track release system** with human-controlled version management:

- **Stable Track** (X.Y.0): Thoroughly tested releases for production use
- **Development Track** (X.Y.Z where Z>0): Latest features and fixes for testing

No more surprise version bumps! All releases are **intentional and controlled**.

## 🎯 Version Classification

### Stable Versions (X.Y.0)
- **Format**: `1.2.0`, `1.3.0`, `2.0.0`  
- **Purpose**: Production-ready releases
- **Docker Tag**: Must be manually promoted to `:stable` 
- **Usage**: Default track for `bop` wrapper

### Development Versions (X.Y.Z)
- **Format**: `1.2.1`, `1.2.2`, `1.3.1`
- **Purpose**: Latest builds with new features/fixes
- **Docker Tag**: Automatically updates `:latest`
- **Usage**: Available via `BOP_RELEASE_TRACK=dev`

## 🚀 Release Workflows

### 1. Version Bump (Manual)

**When to use**: Create a new version number and optionally tag it

**Location**: GitHub Actions → "Version Bump" workflow

**Options**:
- `dev-patch`: 1.2.0 → 1.2.1 (development increment)
- `minor`: 1.2.3 → 1.3.0 (new stable release)  
- `major`: 1.3.2 → 2.0.0 (breaking changes)
- `set-exact`: Specify exact version (e.g., 1.2.5)

**Features**:
- ✅ Dry run mode for testing
- ✅ Create PR instead of direct commit
- ✅ Automatic tag creation
- ✅ Version validation

**Example Usage**:
```bash
# Via GitHub UI: Actions → Version Bump → Run workflow
# Select mode: "dev-patch"  
# ✓ Create tag: true
# ✓ Dry run: false
```

### 2. Publish on Tag (Automatic)

**When it runs**: Automatically triggered when you push a Git tag (`v*.*.*`)

**What it does**:
- 🏗️ Builds multi-architecture Docker images (AMD64, ARM64)
- 🏷️ Tags images with version and major.minor
- 📦 Creates GitHub release with installation instructions
- 🔄 For development versions: Updates `:latest` tag automatically
- 🎯 For stable versions: Leaves `:stable` tag unchanged (manual promotion required)

**Docker Tags Created**:
```bash
# For v1.2.3 (development):
altheasignals/boxofports:1.2.3
altheasignals/boxofports:1.2
altheasignals/boxofports:latest  # ← automatically updated

# For v1.3.0 (stable):
altheasignals/boxofports:1.3.0
altheasignals/boxofports:1.3
# stable tag remains unchanged until manually promoted
```

### 3. Promote Stable (Manual)

**When to use**: Move a stable version (X.Y.0) to the `:stable` Docker tag

**Location**: GitHub Actions → "Promote Stable" workflow

**Safety Features**:
- ✅ Only allows X.Y.0 versions
- ✅ Verifies source image exists
- ✅ Dry run mode
- ✅ Auto-selection of latest stable
- ✅ Rollback logging

**Example Usage**:
```bash
# Via GitHub UI: Actions → Promote Stable → Run workflow
# Target version: 1.3.0 (or check "auto-select")
# ✓ Dry run: false
```

## 🐳 Docker Tag Strategy

| Docker Tag | Purpose | Updated By | Points To |
|------------|---------|------------|-----------|
| `:stable` | Production deployments | Manual promotion only | Latest promoted X.Y.0 |
| `:latest` | Development/testing | Auto-updated on dev releases | Latest X.Y.Z where Z>0 |
| `:1.2.3` | Specific version | Publish workflow | Exact build |
| `:1.2` | Major.minor series | Publish workflow | Latest in 1.2.x series |

## 🎛️ Using the bop Wrapper

The `bop` wrapper automatically handles track selection:

### Stable Track (Default)
```bash
# Uses :stable Docker tag - only X.Y.0 versions
bop --help
bop --version  # Shows stable version
```

### Development Track
```bash
# Uses :latest Docker tag - latest development build
BOP_RELEASE_TRACK=dev bop --help
BOP_RELEASE_TRACK=dev bop --version
```

### Configuration Methods
1. **Environment variable**: `BOP_RELEASE_TRACK=dev`
2. **Config file**: `~/.boxofports/bop.conf`
3. **Command flag**: `bop --track dev --help`

### Track Auto-Detection
If stable track resolves to a non-X.Y.0 version, bop shows a helpful error:

```bash
❌ The wheel is turning but you can't slow down — stable track expects X.Y.0, but got 1.2.1.
💡 Try: BOP_RELEASE_TRACK=dev bop [command] or set release_track=dev in ~/.boxofports/bop.conf
```

## 📋 Common Release Scenarios

### Creating a Development Release

1. **Bump version**: Run "Version Bump" workflow with `dev-patch` mode
   - Creates version like 1.2.1, 1.2.2, etc.
   - Automatically creates and pushes Git tag
2. **Automatic build**: Publish workflow triggers automatically
   - Builds and pushes Docker images
   - Updates `:latest` tag automatically
3. **Ready to use**: Development track users get the update immediately

### Creating a Stable Release

1. **Bump to stable**: Run "Version Bump" workflow with `minor` mode  
   - Creates version like 1.3.0, 2.0.0, etc.
   - Automatically creates and pushes Git tag
2. **Automatic build**: Publish workflow builds the images
   - Images are built but `:stable` tag is NOT updated
3. **Testing phase**: Test the new X.Y.0 version thoroughly
4. **Promote to stable**: Run "Promote Stable" workflow
   - Updates `:stable` tag to point to the new version
   - All stable track users get the update

### Emergency Rollback

If a stable release has issues:

```bash
# Rollback stable tag to previous version
./scripts/retag_by_digest.sh \
  altheasignals/boxofports:1.2.0 \
  altheasignals/boxofports:stable
```

## 🛠️ Local Development Workflow

### For Contributors

1. Make your changes on a feature branch
2. Test locally: `./scripts/bop --help` (uses current stable)
3. Create PR - no version changes needed in PR
4. After merge: Maintainer creates development release if needed

### For Maintainers

```bash
# Create a development release for testing  
# GitHub UI: Version Bump → dev-patch → Run

# After testing, create stable release
# GitHub UI: Version Bump → minor → Run  

# After validation, promote to stable
# GitHub UI: Promote Stable → target_version: X.Y.0 → Run
```

## 🔧 Troubleshooting

### "Current version X.Y.Z is not stable"
**Problem**: bop wrapper rejects non-X.Y.0 versions on stable track  
**Solution**: Use development track: `BOP_RELEASE_TRACK=dev bop --help`

### "Source image not found"  
**Problem**: Trying to promote a version that wasn't built  
**Solution**: Ensure the Git tag was created and publish workflow completed successfully

### "No stable versions found"
**Problem**: Auto-select couldn't find any X.Y.0 Git tags  
**Solution**: Create a stable release first using Version Bump with `minor` or `major` mode

## 🎵 Philosophy

*"The music never stopped playing..."*

This system embodies the Deadhead philosophy of **intentional flow**:

- 🌊 **Steady rhythm**: Stable releases provide reliable foundation
- 🎭 **Creative exploration**: Development releases enable innovation  
- 🤝 **Community choice**: Users choose their comfort level
- 🎼 **No surprises**: Every release is deliberate and announced

The river flows, but now we choose the current.

---

*Built with ❤️ by Althea Signals Network LLC*