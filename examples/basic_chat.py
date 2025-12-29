import asyncio
import os

from voxta_client import VoxtaClient

"""
Basic Chat Example
------------------
This script demonstrates how to:
1. Initialize the VoxtaClient.
2. Handle incoming messages from a character.
3. Negotiate and establish a SignalR connection.
4. Send a text message to the server.

Usage:
    python examples/basic_chat.py
"""


async def main():
    # 1. Initialize the client
    # Replace with your Voxta server URL if different
    voxta_url = os.getenv("VOXTA_URL", "http://localhost:5384")
    client = VoxtaClient(voxta_url)

    # Set up event listeners
    @client.on("message")
    async def on_message(payload):
        if payload.get("senderType") == "Character":
            print(f"\nCharacter: {payload.get('text')}")

    @client.on("error")
    async def on_error(payload):
        print(f"Error from Voxta: {payload.get('message')}")

    # 2. Negotiate authentication
    print(f"Negotiating connection with {voxta_url}...")
    try:
        token, cookies = client.negotiate()
        if not token:
            print("Failed to negotiate connection. Is the Voxta server running?")
            return
    except Exception as e:
        print(f"Negotiation failed: {e}")
        return

    # 3. Connect (runs the message loop in the background)
    connection_task = asyncio.create_task(client.connect(token, cookies))

    # Wait for the client to be ready (connected and session pinned)
    ready_event = asyncio.Event()
    client.on("ready", lambda _: ready_event.set())

    print("Connecting to Voxta...")
    try:
        # Wait up to 10 seconds for connection
        await asyncio.wait_for(ready_event.wait(), timeout=10.0)
    except asyncio.TimeoutError:
        print("Timed out waiting for connection.")
        await client.close()
        await connection_task
        return

    print(f"Connected! Session ID: {client.session_id}")

    # 4. Send a message
    message_text = "Hello! Tell me a short story."
    print(f"Sending message: '{message_text}'")
    await client.send_message(message_text)

    # Keep the script running to receive the response
    print("Waiting for response (Press Ctrl+C to stop)...")
    try:
        # Wait for a few seconds to see the response
        await asyncio.sleep(15)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up
        print("\nClosing connection...")
        await client.close()
        await connection_task


if __name__ == "__main__":
    asyncio.run(main())
