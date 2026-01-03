# API Reference

The Voxta Python client is designed to be intuitive and event-driven. The library is divided into high-level clients for general interaction and low-level data structures for message handling.

## Primary Interfaces

If you are building an application, you will primarily interact with these two classes:

| Class | Purpose |
|-------|---------|
| [`VoxtaClient`](api/client.md) | The main entry point. Handles SignalR, chat sessions, and text-based interaction. |
| [`VoxtaAudioClient`](api/audio_client.md) | specialized client for raw PCM audio streaming (STT/TTS). |

## Data & Constants

The library uses strongly-typed models and constants to ensure reliable communication with the Voxta server.

*   **[Models](api/models.md)**: Dataclasses for every message type (e.g., `ClientSendMessage`, `ServerChatMessage`).
*   **[Constants](api/constants.md)**: Enumerations for `EventType` and `ServiceType`.

## Architectural Overview

The client follows an **asynchronous, event-driven** pattern. 

1.  **Negotiate**: Perform HTTP handshake to get a connection token.
2.  **Connect**: Establish the SignalR WebSocket connection.
3.  **Listen**: Subscribe to events like `message`, `appTrigger`, or `replyStart`.
4.  **Act**: Send messages or trigger actions via asynchronous methods.

For a deep dive into the underlying protocol, see the [Protocol Support Matrix](protocol.md).
