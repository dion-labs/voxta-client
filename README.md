# Voxta Client

[![Build](https://github.com/dion-labs/voxta-client/actions/workflows/ci.yml/badge.svg)](https://github.com/dion-labs/voxta-client/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/voxta-client.svg)](https://pypi.org/project/voxta-client/)
[![Python versions](https://img.shields.io/pypi/pyversions/voxta-client.svg)](https://pypi.org/project/voxta-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A core library for interacting with the [Voxta](https://voxta.ai) conversational AI platform using Python. This client enables real-time communication with Voxta characters using the SignalR protocol.

## Documentation

Full documentation is available at [https://voxta.dionlabs.ai/](https://voxta.dionlabs.ai/).
See the [Changelog](CHANGELOG.md) for recent updates.

### Compatibility
- **Voxta Server**: Designed for and tested with **v1.2.1**.
- **Python**: Supports **3.9+**.

## Features

- **Real-time Interaction**: Full support for Voxta's SignalR/WebSockets protocol.
- **Event-Driven**: Simple callback system for handling server events (messages, state changes, etc.).
- **Session Management**: Easy handling of chat sessions, character selection, and context updates.
- **Lightweight**: Minimal dependencies, built for performance and reliability.

## Protocol Support Matrix

This client implements the Voxta SignalR protocol. Below is the current support status compared to the full server capabilities.

| Category | Feature | Protocol Method | Status |
| :--- | :--- | :--- | :--- |
| **Core** | Authentication | `authenticate` | ✅ Supported |
| | App Registration | `registerApp` | ✅ Supported |
| | Chat Subscription | `subscribeToChat` | ✅ Supported |
| **Messaging** | Start Chat | `startChat` | ✅ Supported |
| | Resume Chat | `resumeChat` | ✅ Supported |
| | Send Message | `send` | ✅ Supported |
| | Character Speech Req | `characterSpeechRequest` | ✅ Supported |
| **Control** | Interrupt | `interrupt` | ✅ Supported |
| | Pause | `pause` | ✅ Supported |
| | Inspect Session | `inspect` | ✅ Supported |
| **Context** | Update Context | `updateContext` | ✅ Supported |
| | Actions/Events | `updateContext` | ✅ Supported |
| | Role Management | `enableRoles` | ✅ Supported |
| **Media** | Playback Sync | `speechPlaybackStart/Complete` | ✅ Supported |
| | Audio Streaming | `WebSocketStream` (PCM) | ❌ Not Planned |
| | Vision / Images | `visionCapture` | ❌ Not Planned |

## Installation

```bash
pip install voxta-client
```

## Quick Start

```python
import asyncio
from voxta_client import VoxtaClient

async def main():
    # 1. Initialize the client
    client = VoxtaClient("http://localhost:5384")
    
    # Set up event listeners
    @client.on("message")
    async def on_message(payload):
        if payload.get("senderType") == "Character":
            print(f"\nCharacter: {payload.get('text')}")

    # 2. Negotiate authentication
    print("Negotiating connection...")
    token, cookies = client.negotiate()
    
    # 3. Connect (runs the message loop in the background)
    connection_task = asyncio.create_task(client.connect(token, cookies))
    
    # Wait for the client to be ready (connected and session pinned)
    # The 'ready' event is triggered once a sessionId is acquired
    ready_event = asyncio.Event()
    client.on("ready", lambda _: ready_event.set())
    
    print("Connecting to Voxta...")
    await ready_event.wait()
    print(f"Connected! Session ID: {client.session_id}")

    # 4. Send a message
    print("Sending message...")
    await client.send_message("Hello! Tell me a short story.")
    
    # Wait for response
    await asyncio.sleep(10)
    
    # Clean up
    await client.close()
    await connection_task

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

## Credits

Special thanks to **Vega** from the official Voxta Discord for their invaluable work on the [Voxta Development Guide](https://github.com/vega-holdings/voxta_unoffical_docs/blob/main/VOXTA_DEVELOPMENT_GUIDE.md#6-websocket-protocol-reference) (repo: [vega-holdings/voxta_unoffical_docs](https://github.com/vega-holdings/voxta_unoffical_docs)). This project was made possible by their detailed documentation of the Voxta WebSocket protocol.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
