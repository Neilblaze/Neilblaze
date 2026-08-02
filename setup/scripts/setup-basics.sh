#!/usr/bin/env bash

set -e

# Install Xcode Command Line Tools (includes Git)
if ! command -v git &> /dev/null; then
  echo "Installing Xcode Command Line Tools (required for Git)... 🔧"
  xcode-select --install

  # Wait until installation is complete
  until command -v git &> /dev/null; do
    sleep 5
  done
  echo "Git is now installed. ✅"
fi

# Install Homebrew
if ! command -v brew &> /dev/null; then
  echo "Installing Homebrew 🍺..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$HOME/.zprofile"
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi
