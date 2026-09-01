#!/usr/bin/env bash
# Install packages managed outside Brew

set -euo pipefail

echo "📦 Installing packages managed outside Brew..."

# claude-code
if ! command -v claude-code &> /dev/null; then
  echo "🤖 Installing Claude Code..."
  npm install -g @anthropic-ai/claude-code
else
  echo "✅ Claude Code already installed"
fi

# nvm
if [[ ! -d "$HOME/.nvm" ]]; then
  echo "📦 Installing NVM..."
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
  
  # Source nvm to make it available in current session
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  
  echo "📦 Installing latest LTS Node.js..."
  nvm install --lts
else
  echo "✅ NVM already installed"
fi
