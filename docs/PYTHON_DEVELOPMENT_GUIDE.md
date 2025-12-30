# Python Voxta Development Guide

## Complete Reference for Building Voxta Python Integrations

**Version:** 1.0
**Last Updated:** 2025-12-30
**Client Version:** 0.1.6

This guide provides a comprehensive overview of how to build applications that interact with the Voxta AI platform using the `voxta-client` Python library. It is inspired by the unofficial C# development guide but tailored for Python's async-first approach.

---

## 1. Architecture Overview

In the Voxta ecosystem, the Python client acts as a **Client (App SDK)**. It is responsible for owning the chat session, managing character selection, and handling real-time interaction through a SignalR-based WebSocket connection.

```
┌─────────────────────────────────────────────────────────┐
│                   WebSocket Hub (/hub)                   │
└─────────────────────────────────────────────────────────┘
          │
          ▼
   ┌─────────────┐
   │   CLIENT    │
   │(voxta-client)│
   │             │
   │ Owns chat   │
   │ session     │
   │             │
   └─────────────┘
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Session** | A chat instance with a unique `SessionId` (GUID). |
| **Chat** | Persistent conversation with history, identified by `ChatId`. |
| **Character** | AI persona with personality, voice, and behavior settings. |
| **Context** | Dynamic information injected into AI's knowledge via `updateContext`. |
| **Actions** | Functions the AI can invoke, received as `action` events. |

---

## 2. Getting Started

### Installation

```bash
pip install voxta-client
```

### Basic Connection Flow

Connecting to Voxta requires a three-step process:

1.  **Negotiate**: Get a connection token and cookies from the HTTP endpoint.
2.  **Connect**: Establish the SignalR WebSocket connection.
3.  **Authenticate**: Send the initial `authenticate` message via SignalR.

```python
import asyncio
from voxta_client import VoxtaClient

async def connect_voxta():
    client = VoxtaClient("http://localhost:5384")
    
    # 1. Negotiate
    token, cookies = client.negotiate()
    
    # 2 & 3. Connect and Authenticate
    # This runs the internal read loop
    await client.connect(token, cookies)
    
    # Wait for ready signal
    ready_event = asyncio.Event()
    client.on("ready", lambda sid: ready_event.set())
    await ready_event.wait()
    
    print(f"Connected to session: {client.session_id}")
```

---

## 3. WebSocket Protocol

The client implements the SignalR protocol. All messages are JSON-encoded and delimited by the `\x1e` character.

### Message Structure

All client-to-server messages follow the SignalR Invocation format:

```json
{
    "type": 1,
    "invocationId": "...",
    "target": "SendMessage",
    "arguments": [
        {
            "$type": "...",
            "sessionId": "...",
            ...other fields
        }
    ]
}
```

### Supported Method Names

| Method | Description |
|--------|-------------|
| `authenticate` | Must be sent first to establish identity. |
| `registerApp` | Reports client name/version to server. |
| `subscribeToChat` | Directs the server to send updates for a specific chatId. |
| `startChat` | Creates a new chat session with a character. |
| `resumeChat` | Restores an existing chat by its ID. |
| `stopChat` | Ends the current chat session. |
| `send` | Sends a text message to the AI. |
| `characterSpeechRequest` | Asks the AI to start or resume speaking. |
| `interrupt` | Stops current AI speech playback. |
| `pause` | Stops current AI text generation/thinking. |
| `updateContext` | Injects knowledge, flags, or allowed actions. |
| `updateMessage` | Modifies a previously sent message. |
| `deleteMessage` | Removes a message from history. |
| `triggerReply` | Explicitly requests the AI to respond. |

---

## 4. Audio Streaming (`VoxtaAudioClient`)

For applications requiring real-time voice interaction, the library provides a dedicated `VoxtaAudioClient`. This client handles a separate WebSocket connection for raw binary PCM data.

### Key Features
- **Binary PCM**: Supports 16-bit, 16kHz mono audio.
- **Decoupled**: Runs on its own connection to avoid interfering with SignalR control messages.
- **On-Demand**: Can be started and stopped independently of the main chat session.

### Usage Example

```python
from voxta_client import VoxtaAudioClient

async def setup_audio(url, token, cookies):
    audio_client = VoxtaAudioClient(url)
    
    @audio_client.on_audio
    def handle_pcm_data(chunk: bytes):
        # Play chunk using sounddevice or other library
        print(f"Received {len(chunk)} bytes of audio")

    await audio_client.connect(token, cookies)
    print("Audio streaming active")
```

---

## 5. Message Models

The library provides `dataclasses` for all common protocol messages in `voxta_client.models`.

### Sending a Message

```python
from voxta_client.models import ClientSendMessage

msg = ClientSendMessage(
    sessionId=client.session_id,
    text="Hello Apex!",
    doReply=True
)
# Handled automatically by client.send_message(text)
```

---

## 6. Events & Callbacks

The client is entirely event-driven. You should handle events to update your application state.

### Common Events

| Event | Description |
|-------|-------------|
| `welcome` | Received after successful auth. Contains user and default assistant info. |
| `chatStarted` | Received when a character session is initialized. |
| `chatsSessionsUpdated` | Received when chat/session status changes globally. |
| `message` | A complete message from the AI or User. |
| `replyChunk` | A partial text stream from the AI. |
| `replyGenerating` / `replyStart` | Indicates AI has started thinking. |
| `replyEnd` | Indicates AI has finished text generation. |
| `speechPlaybackStart` | Client should start playing audio. |
| `speechPlaybackComplete` | Client has finished playing audio. |
| `error` | Server-side protocol or logic errors. |

### Handling State

```python
@client.on("chatStarted")
async def on_chat(payload):
    # Payload contains sessionId, chatId, and characters list
    print(f"Chat with {payload['characters'][0]['name']} is ready")

@client.on("replyChunk")
async def on_stream(payload):
    print(payload['text'], end="", flush=True)
```

---

## 7. Advanced Usage

### Context Injection

Use `updateContext` to keep the AI aware of your application's state.

```python
await client.update_context(
    session_id=client.session_id,
    context_key="game_state",
    contexts=[{
        "name": "Location",
        "content": "The player is currently in the Dark Forest."
    }],
    set_flags=["is_raining"]
)
```

### Action Handling

When the AI wants to perform an action (like changing an expression or triggering a game event), you will receive an `action` event.

```python
@client.on("action")
async def on_action(payload):
    # payload['value'] is the action name (e.g., "play_happy_emote")
    # payload['arguments'] contains any parameters
    print(f"AI triggered action: {payload['value']}")
```

### Speech Control

To achieve natural interaction, use the playback sync methods:

1. AI sends `replyChunk` with audio URL.
2. AI sends `speechPlaybackStart`.
3. Client plays audio.
4. Client sends `speechPlaybackComplete` to tell AI the "turn" is over.

---

## 8. Known Protocol Gaps / Under Investigation

The following methods and features are currently documented in unofficial protocol guides but have been removed from the primary `voxta-client` due to non-functional status or unrecognized discriminators on the current server version. They are preserved here for research and future investigation.

| Feature | Method | Current Status / Note |
|---------|--------|-----------------------|
| **Secret Messages** | `sendSecret` | Discriminator unrecognized by server. |
| **Private Notes** | `sendNote` | Unrecognized. AI likely expects standard `send` with `/note` prefix. |
| **System Instructions** | `sendInstructions` | Discriminator unrecognized by server. |
| **User Action Request** | `requestUserAction` | Non-functional; server does not process. |
| **Load Chat** | `loadChat` | Discriminator unrecognized by server. |
| **Delete Chat** | `deleteChat` | Server error: `LocalId is empty`. Mapping mismatch. |
| **List Resources** | `listResources` | Missing `resources` property on server side or mismatch in model. |
| **Deploy Resource** | `deployResource` | Untested/Complex payload. |
| **Update Chat** | `updateChat` | Non-functional/Untested. |
| **Update Document** | `updateDocument` | Non-functional/Untested. |
| **Unsubscribe From** | `unsubscribeFrom` | Non-functional/Untested. |
| **Fulfill Interaction** | `fulfillUserInteraction` | Non-functional/Untested. |
| **Run Script** | `runScript` | Non-functional/Untested. |
| **Trigger Script Event** | `triggerScriptEvent` | Non-functional/Untested. |
| **App Trigger Complete** | `appTriggerComplete` | Non-functional/Untested. |

---

*This guide reflects the state of the Voxta Python Client as of Dec 2025. For issues or protocol changes, refer to the [Protocol Support Matrix](protocol.md).*

