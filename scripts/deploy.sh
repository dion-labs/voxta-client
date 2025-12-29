#!/bin/bash
set -e

# Clean the dist directory
echo "Cleaning dist directory..."
rm -rf dist/

# Prepare for release: remove dev suffix if present
echo "Preparing release version..."
uv version --bump stable
VERSION=$(grep -E '^version = ' pyproject.toml | cut -d '"' -f 2)
echo "Releasing version: $VERSION"

# Build the latest artifacts
echo "Building the package..."
uv build

# Git commit and tag stable version
echo "Committing stable version..."
git add pyproject.toml uv.lock
git commit -m "chore: release version $VERSION"
git tag -a "v$VERSION" -m "version $VERSION"

# Upload to PyPI
echo "Uploading to PyPI..."
uv run twine upload dist/*

# Bump to the next development version
echo "Bumping to next development version..."
uv version --bump patch --bump dev
NEXT_VERSION=$(grep -E '^version = ' pyproject.toml | cut -d '"' -f 2)
echo "Next development version: $NEXT_VERSION"

# Git commit development version
echo "Committing development version..."
git add pyproject.toml uv.lock
git commit -m "chore: bump to $NEXT_VERSION"

# Push all changes and tags
echo "Pushing to remote..."
git push origin main --tags
