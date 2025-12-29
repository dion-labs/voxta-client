# Contributing

We welcome contributions to the Voxta Python Client!

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

### 1. Clone the repository

```bash
git clone https://github.com/dion-labs/voxta-client.git
cd voxta-client
```

### 2. Install dependencies

```bash
uv sync --all-extras
```

### 3. Install pre-commit hooks

```bash
uv run pre-commit install
```

### 4. Run tests

```bash
uv run pytest
```

### 5. Build documentation locally

```bash
uv run mkdocs serve
```

## Pull Request Process

1.  Create a new branch for your changes.
2.  Ensure tests pass and the code is properly formatted (`ruff format .`).
3.  Submit a pull request with a clear description of your changes.

