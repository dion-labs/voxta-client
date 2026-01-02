import asyncio
import os

from voxta_client import VoxtaClient

# --- Optional: Enable logs to see SignalR activity ---
# logging.basicConfig(level=logging.INFO)


async def main():
    voxta_url = os.getenv("VOXTA_URL", "http://localhost:5384")
    client = VoxtaClient(voxta_url)

    # Handle character responses (Streaming)
    @client.on("replyStart")
    def on_start(_):
        print("\nAI is thinking... [", end="", flush=True)

    @client.on("replyChunk")
    def on_chunk(data):
        print(data.get("text", ""), end="", flush=True)

    @client.on("replyEnd")
    def on_end(_):
        print("] (Done)\n")

    # Wait for the client to be ready (connected and session pinned)
    @client.on("ready")
    async def on_ready(session_id):
        print(f"Connected! Session ID: {session_id}")

        # Send a test message
        message_text = "Hello! Tell me a short story."
        print(f"Sending: '{message_text}'")
        await client.send_message(message_text)

    # Connection Flow
    token, cookies = client.negotiate()
    if not token:
        print("Error: Could not negotiate connection. Is Voxta running?")
        return

    await client.connect(token, cookies)
    print("Waiting for Voxta to be ready (Ensure a chat is active in the Voxta UI)...")

    try:
        # Keep alive
        while client.running:
            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
