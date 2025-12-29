# Getting Started

## Installation

You can install the Voxta Python Client directly from PyPI:

```bash
pip install voxta-client
```

## Basic Usage

The following example shows how to connect to a local Voxta server and send a simple message.

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

    # 2. Negotiate connection
    print("Negotiating connection...")
    token, cookies = client.negotiate()
    
    # 3. Connect (runs the message loop in the background)
    connection_task = asyncio.create_task(client.connect(token, cookies))
    
    # Wait for the client to be ready (connected and session pinned)
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

## Advanced Configuration

For more complex scenarios, such as updating context or handling specific SignalR events, please refer to the [API Reference](api/client.md).

