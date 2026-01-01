# API Reference

The Voxta Python client library is structured into several modules, providing both high-level chat interactions and low-level audio streaming capabilities.

## Core Clients

### [VoxtaClient](api/client.md)

The primary entry point for the library. It handles the SignalR connection, chat session management, and high-level message sending/receiving.

**Key Features:**
- Connection management (`negotiate`, `connect`, `close`)
- Event-based architecture (`on`)
- Chat session control (`start_chat`, `resume_chat`, `stop_chat`)
- Message interaction (`send_message`, `update_message`, `delete_message`)
- AI control (`trigger_action`, `interrupt`, `retry`, `revert`)
- Context management (`update_context`)

### [VoxtaAudioClient](api/audio_client.md)

A specialized client for streaming raw binary PCM audio data. Use this for low-latency voice interactions.

**Key Features:**
- Binary audio streaming (`send_audio`, `on_audio`)
- Dedicated WebSocket connection for audio throughput

## Data Structures

### [Models](api/models.md)

All messages exchanged with the Voxta server are represented as typed dataclasses. 

- **Outgoing Messages:** `ClientSendMessage`, `ClientStartChatMessage`, `ClientUpdateContextMessage`, etc.
- **Incoming Messages:** `ServerChatMessage`, `ServerActionMessage`, `ServerWelcomeMessage`, etc.

### [Constants](api/constants.md)

Enums and string constants for event types and service types.

- `EventType`: All possible event names emitted by `VoxtaClient`.
- `ServiceType`: Various service types within the Voxta ecosystem (TTS, STT, etc.).
