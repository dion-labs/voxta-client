import logging
import asyncio
from voxta_client import VoxtaClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Reduce noise from websockets
logging.getLogger("websockets").setLevel(logging.WARNING)

async def main():
    logger = logging.getLogger("VoxtaHuman")
    client = VoxtaClient("http://127.0.0.1:5384")

    # Event Handlers
    async def on_ready(session_id):
        logger.info(f"Connected! Session ID: {session_id}")
        print("\n--- You can start typing now ---\n")

    async def on_server_message(data):
        # Print everything that looks like a message for now
        if data.get('$type') == 'replyChunk':
             print(f"AI: {data.get('text')}", end="", flush=True)
        elif data.get('$type') == 'replyEnd':
             print("\n")
        else:
             logger.info(f"Event: {data.get('$type')}")

    # Hooking into the client's internal emit or just relying on existing logging?
    # voxta_client emits based on $type.
    # We can't subscribe to "*" yet.
    # But we can assume some common types: 'replyChunk', 'replyEnd', 'speechStarted', 'speechFinished'
    
    client.on("replyChunk", lambda d: print(d.get('text', ''), end="", flush=True))
    client.on("replyEnd", lambda d: print("\n"))
    client.on("speechStarted", lambda d: print("\n[AI is speaking...]"))

    # Connection
    connection_token, cookies = client.negotiate()
    if not connection_token:
        logger.error("Could not obtain connection token.")
        return

    # Start client in background
    client_task = asyncio.create_task(client.connect(connection_token, cookies))

    # User Input Loop
    try:
        while not client.running:
            await asyncio.sleep(0.1) # Wait for connection start
        
        while client.running:
            # We use a thread functionality for input to not block the event loop
            text = await asyncio.to_thread(input, "You > ")
            if text.lower() in ["exit", "quit"]:
                break
            
            if client.session_id:
                await client.send_message(text)
            else:
                logger.warning("Waiting for session ready...")
                
    except KeyboardInterrupt:
        logger.info("Exiting...")
    finally:
        client.running = False
        await client_task

if __name__ == "__main__":
    asyncio.run(main())