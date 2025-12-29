#!/bin/bash
set -e

# Build the latest artifacts
echo "Building the package..."
uv build

# Upload to PyPI
echo "Uploading to PyPI..."
uv run twine upload dist/*

