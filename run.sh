#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🏃 Running Ebook Maker..."
# Run the application through the python interpreter directly
uv run python -m ebook_maker.main
