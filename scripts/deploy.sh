#!/bin/bash
set -e

# Clean the dist directory
echo "Cleaning dist directory..."
rm -rf dist/

# Prepare for release: remove dev suffix if present
echo "Preparing release version..."
uv version --bump stable

# Build the latest artifacts
echo "Building the package..."
uv build

# Upload to PyPI
echo "Uploading to PyPI..."
uv run twine upload dist/*

# Bump to the next development version
echo "Bumping to next development version..."
uv version --bump patch --bump dev

