# API Reference

The library is structured into several modules following the Voxta C# SDK conventions.

## VoxtaClient

The main entry point for the library.

### Methods

- `__init__(url: str)`: Initialize the client.
- `on(event_name: str, callback: Optional[Callable])`: Register an event listener.
- `negotiate()`: Perform the initial HTTP negotiation.
- `connect(token: str, cookies: Optional[Dict[str, str]])`: Establish the SignalR connection.
- `close()`: Close the connection.
- `send_message(text: str, ...)`: Send a user message.
- `start_chat(character_id: str, ...)`: Start a new chat.
- `update_context(...)`: Update session context, actions, or flags.

## Models

All message structures are defined as dataclasses in `voxta_client.models`.

### Outgoing Messages

- `ClientSendMessage`
- `ClientAuthenticateMessage`
- `ClientRegisterAppMessage`
- `ClientUpdateContextMessage`

### Incoming Messages

- `ServerWelcomeMessage`
- `ServerChatMessage`
- `ServerActionMessage`

## Constants

- `EventType`: String constants for all Voxta events.
- `ServiceType`: Enum for Voxta service types.

