import asyncio
import os
from voxta_client import VoxtaClient

"""
App Triggers Example
--------------------
This script demonstrates how to:
1. Initialize the VoxtaClient and connect to the server.
2. Listen for 'appTrigger' events sent from Voxta Scenarios.
3. Handle custom logic when a specific trigger is received.

Usage:
    python examples/app_triggers.py
    
To test this, you can create a Scenario Action in Voxta with a script effect:
    import { chat } from "@voxta";
    export const trigger = (e) => {
      chat.appTrigger("my_custom_event", "some_value");
    };
"""


async def main():
    # 1. Initialize the client
    # Replace with your Voxta server URL if different
    voxta_url = os.getenv("VOXTA_URL", "http://localhost:5384")
    client = VoxtaClient(voxta_url)

    # 2. Register for the 'ready' event
    # This event fires when the client has successfully connected, authenticated,
    # and subscribed to the active chat session.
    @client.on("ready")
    async def on_ready(session_id):
        print(f"Connected and ready! Session ID: {session_id}")
        print("Waiting for app triggers from Voxta (Press Ctrl+C to stop)...")

    # 3. Register for the 'appTrigger' event
    @client.on("appTrigger")
    async def on_app_trigger(payload):
        # The payload contains:
        # - name: The string name of the trigger (e.g., "my_custom_event")
        # - arguments: A list of arguments passed to chat.appTrigger()
        # - sessionId: The ID of the session that fired the trigger
        trigger_name = payload.get("name")
        args = payload.get("arguments", [])

        print(f"\n[Trigger Received] Name: {trigger_name}")
        if args:
            print(f"Arguments: {args}")

        # --- PLACE YOUR CUSTOM LOGIC HERE ---
        # Example: if trigger_name == "D_PLAY_ANIMATION":
        #             play_animation(args[0])
        print(f"Action: Your custom logic for '{trigger_name}' goes here.")
        # ------------------------------------

    # 4. Connection Flow
    print(f"Negotiating connection with {voxta_url}...")
    try:
        token, cookies = client.negotiate()
        if not token:
            print("Failed to negotiate. Is the Voxta server running?")
            return
    except Exception as e:
        print(f"Negotiation failed: {e}")
        return

    # Start the background message loop
    connection_task = asyncio.create_task(client.connect(token, cookies))

    print("Connecting to Voxta...")
    try:
        # Keep the script running to listen for events
        # We wait for the connection task to either finish or be cancelled
        await connection_task
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nStopping client...")
    finally:
        # Clean up
        await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

