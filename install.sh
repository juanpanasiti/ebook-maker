#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Installing ebook-maker..."

# Clear cached builds to ensure the latest code is used
uv cache clean ebook-maker

# Install as a global tool
uv tool install . --force

# Copy .env to global config directory so ebook-maker works from anywhere
CONFIG_DIR="$HOME/.config/ebook-maker"
if [ -f ".env" ]; then
    mkdir -p "$CONFIG_DIR"
    cp .env "$CONFIG_DIR/.env"
    echo "📋 Configuration copied to $CONFIG_DIR/.env"
else
    echo "⚠️  No .env file found in current directory. Skipping global config."
fi

echo "✅ ebook-maker installed successfully. You can run it from anywhere with: ebook-maker"
