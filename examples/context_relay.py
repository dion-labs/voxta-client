import asyncio
import os

from voxta_client import VoxtaClient

"""
Context Relay Example
---------------------
Demonstrates how to relay external events (e.g., subtitles, game state) 
as "silent" context to the AI.

The AI will "know" about these updates but won't respond until 
the user explicitly talks to it.
"""

# logging.basicConfig(level=logging.INFO)


async def main():
    client = VoxtaClient(os.getenv("VOXTA_URL", "http://localhost:5384"))
    relayed = False

    @client.on("ready")
    async def on_ready(session_id):
        nonlocal relayed
        if relayed:
            return
        relayed = True

        print(f"Connected! (Session: {session_id})")

        # Simulate relaying a few background updates
        updates = [
            "User started watching 'The Matrix'.",
            "Subtitles: 'I know kung fu.'",
            "Subtitles: 'Show me.'",
        ]

        for update in updates:
            print(f"Relaying background context: {update}")
            # We send these as 'silent' messages:
            # - do_reply=False: AI won't generate a response
            # - do_user_inference=False: Don't check for actions in this message
            # - do_character_inference=False: Don't check for actions in response
            await client.send_message(
                text=f"[MEDIA CONTEXT]: {update}",
                do_reply=False,
                do_user_inference=False,
                do_character_inference=False,
            )
            await asyncio.sleep(1)  # Simulate time passing

        print("\nContext relay complete. The AI now 'knows' what you're watching.")
        print("Try asking it in the Voxta UI: 'What did Neo just say?'")

    # Connect to Voxta
    token, cookies = client.negotiate()
    if token:
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
