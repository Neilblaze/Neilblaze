#!/usr/bin/env bash

set -e

echo "🚀 Starting macOS setup..."

echo "Step 1: 📋 Running basic setup..."
bash scripts/setup-basics.sh

echo "Step 2: ⚙️ Running config setup..."
bash scripts/setup-configs.sh

echo "Step 3: 🛠️ Running macOS preferences setup..."
bash scripts/setup-macos.sh

echo "✅ Setup complete!"
