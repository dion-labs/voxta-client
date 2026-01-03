# VoxtaClient

The `VoxtaClient` is the primary interface for interacting with the Voxta platform. It manages the SignalR connection lifecycle and provides an event-driven API for chat interactions.

::: voxta_client.client.VoxtaClient
    options:
      show_root_heading: false
      members:
        - __init__
        - on
        - running

## Connection Lifecycle

These methods handle the connection to the Voxta server.

::: voxta_client.client.VoxtaClient
    options:
      show_root_heading: false
      members:
        - negotiate
        - connect
        - close

## Session Management

Manage active chat sessions and character participants.

::: voxta_client.client.VoxtaClient
    options:
      show_root_heading: false
      members:
        - start_chat
        - resume_chat
        - stop_chat
        - subscribe_to_chat
        - add_chat_participant
        - remove_chat_participant

## Interaction

Methods for sending messages and controlling the AI's response flow.

::: voxta_client.client.VoxtaClient
    options:
      show_root_heading: false
      members:
        - send_message
        - update_message
        - delete_message
        - trigger_action
        - interrupt
        - retry
        - revert
        - pause

## UI & Presence

Handle typing indicators and status updates.

::: voxta_client.client.VoxtaClient
    options:
      show_root_heading: false
      members:
        - typing_start
        - typing_end
        - request_suggestions
        - character_speech_request
        - speech_playback_start
        - speech_playback_complete

## Discovery

Fetch available assets from the Voxta server.

::: voxta_client.client.VoxtaClient
    options:
      show_root_heading: false
      members:
        - load_characters_list
        - load_scenarios_list
        - load_chats_list

## Debugging

Tools for inspecting the internal state and SignalR traffic.

::: voxta_client.client.VoxtaClient
    options:
      show_root_heading: false
      members:
        - inspect
        - inspect_audio_input
        - session_id
        - is_speaking
        - is_thinking
        - last_message_id
