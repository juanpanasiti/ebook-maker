#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🧪 Running tests and generating coverage report..."
uv run pytest tests/ --cov=src/ebook_maker --cov-report=term-missing
