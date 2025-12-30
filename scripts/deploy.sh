#!/bin/bash
set -e

# Check if git status is clean
echo "Checking git status..."
if [[ -n $(git status --porcelain) ]]; then
    echo "ERROR: Git working directory is not clean. Please commit or stash your changes."
    exit 1
fi

RELEASE_TYPE=${1:-patch}

# Clean the dist directory
echo "Cleaning dist directory..."
rm -rf dist/

# Prepare for release: remove dev suffix if present
echo "Preparing release version..."
if [[ "$RELEASE_TYPE" == "minor" ]]; then
    uv version --bump minor
else
    uv version --bump stable
fi
VERSION=$(grep -E '^version = ' pyproject.toml | cut -d '"' -f 2)
echo "Releasing version: $VERSION"

# Update documentation version
echo "Updating documentation version to $VERSION..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/^\*\*Client Version:\*\* .*/\*\*Client Version:\*\* $VERSION/" docs/PYTHON_DEVELOPMENT_GUIDE.md
else
    sed -i "s/^\*\*Client Version:\*\* .*/\*\*Client Version:\*\* $VERSION/" docs/PYTHON_DEVELOPMENT_GUIDE.md
fi

# Check if CHANGELOG.md has been updated for this version
echo "Checking CHANGELOG.md for version $VERSION..."
if ! grep -q "## \[$VERSION\]" CHANGELOG.md; then
    echo "ERROR: CHANGELOG.md has not been updated for version $VERSION."
    echo "Please add a section for ## [$VERSION] and try again."
    # Revert pyproject.toml changes if version was bumped but release failed
    git checkout pyproject.toml
    exit 1
fi

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
if [[ "$RELEASE_TYPE" == "minor" ]]; then
    uv version --bump patch --bump dev
else
    uv version --bump patch --bump dev
fi
NEXT_VERSION=$(grep -E '^version = ' pyproject.toml | cut -d '"' -f 2)
echo "Next development version: $NEXT_VERSION"

# Git commit development version
echo "Committing development version..."
git add pyproject.toml uv.lock
git commit -m "chore: bump to $NEXT_VERSION"

# Push all changes and tags
echo "Pushing to remote..."
git push origin main --tags
