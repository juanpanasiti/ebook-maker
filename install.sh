#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Installing project dependencies..."
# Install the project and dev dependencies
uv sync --all-extras --dev

echo "✅ Project installed successfully."
