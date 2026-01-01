# VoxtaClient API

The `VoxtaClient` is the primary high-level interface for interacting with the Voxta platform. It handles the SignalR connection, manages chat sessions, and provides a simple event-driven API for handling AI responses and actions.

## Main Client

::: voxta_client.client.VoxtaClient
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - on
        - negotiate
        - connect
        - close
        - start_chat
        - resume_chat
        - stop_chat
        - send_message
        - trigger_action
        - interrupt
        - pause
        - retry
        - revert
        - typing_start
        - typing_end
        - load_characters_list
        - load_scenarios_list
        - load_chats_list
        - add_chat_participant
        - remove_chat_participant
        - request_suggestions
        - update_context
        - update_message
        - delete_message
        - character_speech_request
        - speech_playback_start
        - speech_playback_complete
        - inspect
        - inspect_audio_input
        - running
        - session_id
        - is_speaking
        - is_thinking
        - last_message_id
