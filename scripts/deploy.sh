#!/bin/bash
set -e

# Clean the dist directory
echo "Cleaning dist directory..."
rm -rf dist/

# Build the latest artifacts
echo "Building the package..."
uv build

# Upload to PyPI
echo "Uploading to PyPI..."
uv run twine upload dist/*

# Bump the version to the next patch using uv
echo "Bumping version..."
uv version --bump patch

