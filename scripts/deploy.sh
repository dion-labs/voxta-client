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

# Bump the version to the next patch
echo "Bumping version..."
python3 -c '
import re
from pathlib import Path

content = open("pyproject.toml").read()
match = re.search(r"version = \"(\d+)\.(\d+)\.(\d+)\"", content)
if match:
    major, minor, patch = map(int, match.groups())
    new_version = f"{major}.{minor}.{patch + 1}"
    new_content = content.replace(f"version = \"{major}.{minor}.{patch}\"", f"version = \"{new_version}\"")
    open("pyproject.toml", "w").write(new_content)
    print(f"Bumped version to {new_version}")
else:
    print("Could not find version in pyproject.toml")
    exit(1)
'

