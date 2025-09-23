# BoxOfPorts Shell Completion
*"What a long, strange trip completion has been..."*

## 🎯 Overview

BoxOfPorts now includes comprehensive shell completion support for both Bash and Zsh, making CLI usage much more efficient and user-friendly. The completion system understands the full command structure and provides context-aware suggestions.

## 🌟 Features

### ✅ Comprehensive Command Coverage
- **Main commands**: `sms`, `ops`, `status`, `inbox`, `config`, `test-connection`, `completion`
- **Subcommands**: All subcommands for each main command
- **Options**: All command-line options and flags
- **Values**: Context-aware completions for option values

### ✅ Smart Context Awareness
- **Message types**: Completes `--type` with valid message types (`regular`, `stop`, `system`, etc.)
- **Port specifications**: Suggests common port formats (`1A`, `1B`, `1A-1D`, `1.01`, etc.)
- **Profile names**: Dynamically loads existing profile names for `config switch/show/remove`
- **Shell types**: Completes `--shell` with `bash` or `zsh`

### ✅ Multi-Shell Support
- **Bash**: Native bash completion support
- **Zsh**: Compatible with zsh through `bashcompinit`
- **Auto-detection**: Automatically detects user's shell during installation

## 🚀 Installation Methods

### Method 1: Automatic Installation via install-bop.sh
The completion script is automatically installed when using the main installer:

```bash
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/install-bop.sh | bash
```

The installer will:
1. Detect your shell (bash/zsh)
2. Find appropriate completion directory
3. Download and install completion script
4. Provide instructions for activation

### Method 2: Using bop completion Command
If bop is already installed, you can manage completion directly:

```bash
# Install completion for current user
bop completion --install

# Generate completion script for bash
bop completion --shell bash

# Generate completion script for zsh  
bop completion --shell zsh
```

### Method 3: Manual Installation
Download and source the completion script manually:

```bash
# Download completion script
curl -fsSL https://raw.githubusercontent.com/altheasignals/BoxOfPorts/main/scripts/bop-completion.bash -o ~/.bop-completion.bash

# Add to your shell config
echo 'source ~/.bop-completion.bash' >> ~/.bashrc   # Bash
echo 'source ~/.bop-completion.bash' >> ~/.zshrc    # Zsh
```

## 📋 Completion Examples

### Basic Command Completion
```bash
bop <TAB>         # Shows: sms, ops, status, inbox, config, test-connection, completion
bop sms <TAB>     # Shows: send, spray  
bop inbox <TAB>   # Shows: list, search, stop, summary, show
```

### Option Completion
```bash
bop sms send <TAB>           # Shows: --to, --text, --ports, --repeat, --intvl-ms, --timeout, --var, --dry-run
bop inbox list <TAB>         # Shows: --start-id, --count, --type, --port, --sender, --contains, --no-delivery-reports, --delivery-reports-only, --json
```

### Value Completion  
```bash
bop inbox list --type <TAB>  # Shows: regular, stop, system, delivery_report, keyword
bop sms send --ports <TAB>   # Shows: 1A, 1B, 1C, 1D, 2A, 2B, 3A, 4A, 1A-1D, 2A-2D, 1A,2B,3C, 1.01, 2.02
bop config switch <TAB>      # Shows: available profile names (dynamically loaded)
```

## 🔧 Configuration

### Shell-Specific Setup

#### Bash
The completion script works with the standard bash completion system. Common locations:
- `~/.bash_completion.d/bop`
- `/usr/local/etc/bash_completion.d/bop`
- `/etc/bash_completion.d/bop`

#### Zsh
Works through `bashcompinit` compatibility layer. Common locations:
- `~/.zsh/completions/_bop`
- `~/.oh-my-zsh/completions/_bop`
- `/usr/local/share/zsh/site-functions/_bop`

### Activation
After installation, completion is activated by:
- **Bash**: `source ~/.bashrc` or restart shell
- **Zsh**: `autoload -U compinit && compinit` or restart shell

## 🧪 Testing

### Automated Tests
Run the included test script to verify completion functionality:

```bash
./scripts/test-completion.sh
```

### Manual Testing
Source the completion script and test interactively:

```bash
source ~/.bop-completion.bash
bop <TAB><TAB>              # Test main commands
bop sms send --<TAB><TAB>   # Test options
```

## 📊 Completion Structure

### Command Hierarchy
```
bop
├── sms
│   ├── send (--to --text --ports --repeat --intvl-ms --timeout --var --dry-run)
│   └── spray (--to --text --ports --intvl-ms)
├── ops  
│   ├── lock (--ports)
│   └── unlock (--ports)
├── status
│   └── subscribe (--callback --period)
├── inbox
│   ├── list (--start-id --count --type --port --sender --contains --no-delivery-reports --delivery-reports-only --json)
│   ├── search (--start-id --count --details)
│   ├── stop (--start-id --json)
│   ├── summary (--json)
│   └── show (--start-id)
├── config
│   ├── add-profile (--host --port --user --password)
│   ├── list
│   ├── switch (profile_name)
│   ├── show (profile_name)
│   ├── remove (profile_name)  
│   └── current
├── test-connection
└── completion (--shell --install)
```

### Dynamic Completions
- **Profile names**: Loaded from `bop config list` output
- **Message types**: `regular`, `stop`, `system`, `delivery_report`, `keyword`
- **Port examples**: Common patterns like `1A`, `1A-1D`, `1A,2B,3C`, `1.01`

## 🎵 Grateful Dead Connection

The completion script includes subtle references to the band's spirit:
- Comments reference lyrics like *"Such a long long time to be gone, and a short time to be there"*
- Maintains the "keep on truckin'" philosophy with smooth, efficient command completion
- Makes the CLI experience more "far out" and user-friendly

## 🐛 Troubleshooting

### Completion Not Working
1. **Check if completion is loaded**:
   ```bash
   type _bop_completion
   ```

2. **Manually source the script**:
   ```bash
   source ~/.bop-completion.bash
   ```

3. **Check shell compatibility**:
   ```bash
   echo $SHELL
   echo $ZSH_VERSION    # For zsh users
   echo $BASH_VERSION   # For bash users
   ```

### Permission Issues
If installation fails due to permissions:
1. The installer will fallback to `~/.bop-completion.bash`
2. Add `source ~/.bop-completion.bash` to your shell config manually
3. Use `bop completion --install` for user-space installation

### Zsh Compatibility
If using zsh and completion doesn't work:
1. Ensure `bashcompinit` is loaded:
   ```bash
   autoload -U +X bashcompinit && bashcompinit
   ```
2. The completion script automatically handles zsh compatibility

## 🎯 Future Enhancements

Potential improvements for future releases:
- **Dynamic port discovery**: Query actual device for available ports
- **Command history**: Complete based on recently used commands
- **File path completion**: For commands that accept file arguments
- **Remote completion**: Complete profile names from remote sources

---

*BoxOfPorts Shell Completion v1.0 - "Tab your way to the music"* 🎸