# Voxta Client

[![PyPI version](https://img.shields.io/pypi/v/voxta-client.svg)](https://pypi.org/project/voxta-client/)
[![Python versions](https://img.shields.io/pypi/pyversions/voxta-client.svg)](https://pypi.org/project/voxta-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A core library for interacting with the [Voxta](https://voxta.ai) conversational AI platform using Python. This client enables real-time communication with Voxta characters using the SignalR protocol.

## Features

- **Real-time Interaction**: Full support for Voxta's SignalR/WebSockets protocol.
- **Event-Driven**: Simple callback system for handling server events (messages, state changes, etc.).
- **Session Management**: Easy handling of chat sessions, character selection, and context updates.
- **Lightweight**: Minimal dependencies, built for performance and reliability.

## Installation

```bash
pip install voxta-client
```

## Quick Start

```python
import asyncio
from voxta_client import VoxtaClient

async def main():
    # Initialize the client with your Voxta server URL
    client = VoxtaClient("http://localhost:5384")
    
    @client.on("welcome")
    async def on_welcome(data):
        print("Connected to Voxta!")
        # Start a chat with a specific character
        await client.start_chat("your_character_id")

    @client.on("message")
    async def on_message(payload):
        if payload.get("senderType") == "Character":
            print(f"Character: {payload.get('text')}")

    # Negotiate and connect
    token, cookies = client.negotiate()
    await client.connect(token, cookies)

if __name__ == "__main__":
    asyncio.run(main())
```

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and [Ruff](https://github.com/astral-sh/ruff) for linting.

### Setup

```bash
# Clone the repository
git clone https://github.com/dion-labs/voxta-client.git
cd voxta-client

# Install dependencies and setup venv
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
