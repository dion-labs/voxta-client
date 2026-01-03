# Models

All communication between the client and Voxta server is handled through strongly-typed models. These are implemented as Python dataclasses, making it easy to inspect, validate, and manipulate the data.

## Base Architecture

Every message inherits from a base class that handles SignalR serialization.

::: voxta_client.models.VoxtaModel
::: voxta_client.models.ServerMessage
::: voxta_client.models.ClientMessage

---

## Server Messages (Incoming)

These messages are sent from the Voxta server to your client. You will typically receive these in your event handlers.

### Core Interaction
The most common messages you'll encounter during a chat session.

::: voxta_client.models.ServerWelcomeMessage
::: voxta_client.models.ServerChatMessage
::: voxta_client.models.ServerActionMessage

### Session Flow
Updates about the state of the chat (starting, loading, paused, etc.).

::: voxta_client.models.ServerChatFlowMessage
::: voxta_client.models.ServerChatStartingMessage
::: voxta_client.models.ServerChatLoadingMessage
::: voxta_client.models.ServerChatClosedMessage

---

## Client Messages (Outgoing)

These models are used when sending requests to the server. Note that the `VoxtaClient` provides helper methods for most of these, so you rarely need to instantiate them directly.

### Chat Control

::: voxta_client.models.ClientStartChatMessage
::: voxta_client.models.ClientResumeChatMessage
::: voxta_client.models.ClientSendMessage

### State & Inference

::: voxta_client.models.ClientTriggerActionMessage
::: voxta_client.models.ClientUpdateContextMessage
::: voxta_client.models.ClientInterruptMessage

---

!!! info "Advanced Models"
    The library contains many more specialized models for audio streaming, resource deployment, and inspector debugging. For the full list of available models, refer to the [source code](https://github.com/dion-labs/voxta-client/blob/main/voxta_client/models.py).
