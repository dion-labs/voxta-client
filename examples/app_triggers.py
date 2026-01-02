import asyncio
import os

from voxta_client import VoxtaClient

"""
App Triggers Example
--------------------
Demonstrates how to handle custom appTriggers sent from Voxta Scenarios.

To test this, you can create a Scenario Action in Voxta with a script effect:
    import { chat } from "@voxta";
    
    export const trigger = (e) => {
      chat.appTrigger("my_custom_event", "some_value");
    };
"""

# --- Optional: Enable logs to see SignalR activity ---
# logging.basicConfig(level=logging.INFO)


async def main():
    client = VoxtaClient(os.getenv("VOXTA_URL", "http://localhost:5384"))

    @client.on("ready")
    async def on_ready(session_id):
        print(f"Ready! Subscribed to session: {session_id}")
        print("Waiting for triggers from Voxta...")

    @client.on("appTrigger")
    async def on_app_trigger(payload):
        name = payload.get("name")
        args = payload.get("arguments", [])
        print(f"Trigger Received: {name} | Args: {args}")

    # Start connection
    token, cookies = client.negotiate()
    if not token:
        print("Error: Is Voxta running?")
        return

    await client.connect(token, cookies)

    try:
        while client.running:
            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
