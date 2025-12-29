# Voxta Client (Python)

A core library for interacting with the [Voxta](https://voxta.ai) server using Python. This client enables real-time communication with Voxta characters using SignalR.

## Features

- Real-time interaction via SignalR/WebSockets.
- Easy-to-use event-based callback system.
- Support for message sending, interruptions, and context updates.
- Lightweight and minimal dependencies.

## Installation

```bash
pip install voxta-client
```

## Quick Start

```python
import asyncio
from voxta_client import VoxtaClient

async def main():
    client = VoxtaClient("http://localhost:5384")
    
    @client.on("welcome")
    async def on_welcome(data):
        print("Connected to Voxta!")
        await client.start_chat("your_character_id")

    @client.on("message")
    async def on_message(payload):
        if payload.get("senderType") == "Character":
            print(f"Character: {payload.get('text')}")

    token, cookies = client.negotiate()
    await client.connect(token, cookies)

if __name__ == "__main__":
    asyncio.run(main())
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
