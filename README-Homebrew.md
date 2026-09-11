# OpenDomain Homebrew Tap

This repository contains the Homebrew formula for the OpenDomain CLI.

## Installation

### Option 1: Install from custom tap (Recommended)

```bash
# Add the custom tap
brew tap etherealarchitect/homebrew-tap https://github.com/etherealarchitect/homebrew-tap.git

# Install OpenDomain
brew install opendomain
```

### Option 2: Direct formula install

```bash
# Download and install the formula directly
brew install etherealarchitect/open-domain/opendomain
```

## CLI Usage

Once installed:

```bash
# Get help
opendomain --help

# Login to an OpenDomain instance
opendomain login --api https://app.opendomain.dev/api/v1

# Search for domains
opendomain domains search "myproject"

# List your domains
opendomain domains list

# WHOIS lookup
opendomain whois example.com

# Use the AI agent
opendomain agent "Register opendomain.dev for 1 year with privacy on"
```

## Features

The OpenDomain CLI provides:

- **Full API coverage**: All platform operations via CLI
- **AI Agent integration**: Natural language commands via the AI agent
- **Tab completion**: Bash, Zsh, and Fish shell completions
- **Secure authentication**: Session-based auth with XDG state directory
- **JSON output**: Programmable output format for scripting
- **Idempotent operations**: Support for automation and CI/CD

## Development

To test the formula locally:

```bash
# Build and install from local source
cd /Users/scottkbrown/Documents/OpenDomain
brew install --build-from-source opendomain.rb
```

## Formula Details

- **Dependencies**: `python@3.12`
- **Version**: `0.1.0`
- **License**: MIT
- **Source**: [OpenDomain GitHub](https://github.com/etherealarchitect/OpenDomain)

## Post-installation

Shell completions are installed automatically:

- **Bash**: `completions/bash/opendomain` → `/usr/local/etc/bash_completion.d/opendomain`
- **Zsh**: `completions/zsh/_opendomain` → `${fpath}/_opendomain`
- **Fish**: `completions/fish/opendomain.fish` → `~/.config/fish/completions/opendomain.fish`

Reload your shell to enable completions.

## Troubleshooting

If you encounter issues:

1. **Python version conflicts**:
   ```bash
   brew upgrade python@3.12
   brew reinstall opendomain
   ```

2. **Missing completions**:
   ```bash
   # Manual completion installation
   mkdir -p ~/.config/fish/completions
   cp /usr/local/share/fish/vendor_completions.d/opendomain.fish ~/.config/fish/completions/
   ```

3. **Debug mode**:
   ```bash
   export OPENDOMAIN_DEBUG=1
   opendomain --help
   ```

## Updating

```bash
brew update
brew upgrade opendomain
```

## License

MIT © OpenDomain contributors