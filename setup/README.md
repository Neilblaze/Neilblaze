# dotfiles

##  Setup

For pre-commit secret scanning, set up [Gitleaks](https://github.com/gitleaks/):

```sh
pipx install pre-commit
brew install gitleaks
pre-commit install
```

## Usage

Run everything:

```sh
./setup.sh
```

Or run individual steps:

```sh
./scripts/setup-basics.sh   # Xcode CLI Tools + Homebrew
./scripts/setup-configs.sh  # Clone repo, brew bundle, stow dotfiles
./scripts/setup-macos.sh    # Dock, keyboard, Finder preferences
```

## How it works

### Dotfiles

Managed with [GNU Stow](https://www.gnu.org/software/stow/). The `setup-configs.sh` script symlinks configs from `dotfiles/` into `$HOME`:

```
dotfiles/
├── aerospace     # AeroSpace tiling WM
├── claude        # Claude desktop
├── fish          # Fish shell + plugins
├── gh            # GitHub CLI
├── ghostty       # Ghostty terminal
├── git           # git config
├── git-cz        # git-cz (conventional commits)
├── gitmoji       # gitmoji config
├── starship      # Starship prompt
└── vim           # vim config
```

### Applications

Installed via [Homebrew](https://brew.sh/) using two separate Brewfiles:

- `Brewfile.personal` — languages, CLI tools, GUI apps
- `Brewfile.work` — work-specific tools (Slack, 1Password, Terraform, etc.)

Additional packages not managed by Brew (NVM, Claude Code) are handled by `scripts/utils/package-installs.sh`.

### macOS preferences

`setup-macos.sh` sets keyboard repeat rate, hides the Dock, clears default Dock apps, and adds a custom set back.

## TODO

- Scriptify swapping Ctrl ↔ Fn keys
- iCloud sync automation
- Auto-clone key repos (e.g. Obsidian vaults)
- SSH key creation script

## Inspiration

- [joelazar/dotfiles](https://github.com/joelazar/dotfiles)
- [omerxx/dotfiles](https://github.com/omerxx/dotfiles)
- [Swiss-Mac-User/macOS-scripted-setup](https://github.com/Swiss-Mac-User/macOS-scripted-setup)
- [MacAutoSetup](https://github.com/NLaundry/MacAutoSetup)
