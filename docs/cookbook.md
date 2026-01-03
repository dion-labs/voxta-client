# Cookbook

Common "recipes" and use-cases for the Voxta Python client. These examples address frequent questions from the community.

## 1. Handling Custom App Triggers

**Question:** *"How do I trigger an action in my Python app from a Voxta scenario?"*

Voxta allows you to send custom "App Triggers" from within a Scenario using Javascript. Your Python client can listen for these triggers and execute local code (like moving a robot, changing lights, or updating a UI).

### Scenario Script (Voxta UI)
In your Voxta Scenario, you can use the following script in an Action:

```javascript
import { chat } from "@voxta";

export const trigger = (e) => {
  // name: "my_custom_event", argument: "some_value"
  chat.appTrigger("my_custom_event", "some_value");
};
```

### Python Implementation
Use the `appTrigger` event to catch these signals:

```python
@client.on("appTrigger")
async def on_app_trigger(payload):
    name = payload.get("name")
    args = payload.get("arguments", [])
    
    if name == "my_custom_event":
        print(f"Executing local action with args: {args}")
        # Your custom logic here
```

---

## 2. Relaying Background Context (Silent Messages)

**Question:** *"How can I give the AI information about what's happening (e.g. game state, subtitles) without it generating a response every time?"*

Sometimes you want the AI to stay updated on what the user is doing without interrupting the flow. You can send "silent" messages that update the AI's context but don't trigger a reply.

### Python Implementation
Use `send_message` with `do_reply=False`:

```python
async def update_game_context(client, update_text):
    await client.send_message(
        text=f"[GAME CONTEXT]: {update_text}",
        do_reply=False,             # Don't generate an AI response
        do_user_inference=False,      # Don't check for user actions
        do_character_inference=False  # Don't check for character actions
    )

# Example usage:
await update_game_context(client, "The player entered the Dark Forest.")
```

The AI will now "know" the player is in the Dark Forest, and if the user later asks "Where am I?", the AI will have that context.

---

## 3. Handling Disconnection Events

**Question:** *"How do I know when the connection drops, and how should I handle it?"*

The `VoxtaClient` provides a `close` event that is triggered whenever the SignalR connection is lost or closed.

### Python Implementation

```python
import asyncio

async def start_client():
    client = VoxtaClient("http://localhost:5384")
    
    @client.on("close")
    async def on_close(_):
        print("Connection lost! Attempting to reconnect in 5 seconds...")
        await asyncio.sleep(5)
        await run_client() # Simple recursive reconnect logic

    # ... negotiation and connection logic ...
```

### Checking Status
You can also check the `client.running` property at any time:

```python
if not client.running:
    print("Client is disconnected.")
```

---

## 4. Streaming Text Responses

**Question:** *"How do I get the AI's response word-by-word as it's being generated?"*

For a more responsive UI, you should use the streaming events instead of waiting for the full message.

### Python Implementation

```python
@client.on("replyStart")
def on_start(_):
    print("AI started typing...")

@client.on("replyChunk")
def on_chunk(data):
    # 'text' contains the partial chunk of text
    print(data.get("text", ""), end="", flush=True)

@client.on("replyEnd")
def on_end(_):
    print("\nAI finished.")
```

