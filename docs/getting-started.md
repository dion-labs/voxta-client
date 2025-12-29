# Getting Started

## Installation

```bash
pip install voxta-client
```

## Quick Start

The following example demonstrates how to initialize the client, connect to a local Voxta server, and send a message.

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

## Event Callbacks

The `VoxtaClient` uses an event-driven system. You can register callbacks using the `.on()` decorator or method.

```python
@client.on("chatStarted")
async def on_chat_started(payload):
    print(f"Chat started: {payload['chatId']}")

# Or directly
client.on("error", lambda p: print(f"Error: {p['message']}"))
```
