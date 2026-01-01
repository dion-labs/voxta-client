# Models

These classes define the data structures for SignalR messages exchanged between the client and the Voxta server. All models are implemented as Python dataclasses for easy manipulation and validation.

## Base Classes

The foundation for all message types in the library.

::: voxta_client.models.VoxtaModel
    options:
      show_root_heading: true
      show_source: false

::: voxta_client.models.ServerMessage
    options:
      show_root_heading: true
      show_source: false

::: voxta_client.models.ClientMessage
    options:
      show_root_heading: true
      show_source: false

## Server Messages

Messages received from the Voxta server.

### Core Messages

::: voxta_client.models.ServerWelcomeMessage
::: voxta_client.models.ServerChatMessage
::: voxta_client.models.ServerActionMessage
::: voxta_client.models.ServerChatFlowMessage

### List Loading Messages

::: voxta_client.models.ServerCharactersListLoadedMessage
::: voxta_client.models.ServerScenariosListLoadedMessage
::: voxta_client.models.ServerChatsListLoadedMessage

### Status & Control Messages

::: voxta_client.models.ServerChatStartingMessage
::: voxta_client.models.ServerChatLoadingMessage
::: voxta_client.models.ServerChatClosedMessage
::: voxta_client.models.ServerChatPausedMessage
::: voxta_client.models.ServerChatParticipantsUpdatedMessage

### Audio & Speech Messages

::: voxta_client.models.ServerSpeechRecognitionStartMessage
::: voxta_client.models.ServerSpeechRecognitionPartialMessage
::: voxta_client.models.ServerSpeechRecognitionEndMessage
::: voxta_client.models.ServerRecordingRequestMessage
::: voxta_client.models.ServerRecordingStatusMessage
::: voxta_client.models.ServerAudioFrameMessage

### Error & Troubleshooting Messages

::: voxta_client.models.ServerChatSessionErrorMessage
::: voxta_client.models.ServerAuthenticationRequiredMessage
::: voxta_client.models.ServerMissingResourcesErrorMessage

## Client Messages

Messages sent from the client to the Voxta server.

### Session Control

::: voxta_client.models.ClientStartChatMessage
::: voxta_client.models.ClientResumeChatMessage
::: voxta_client.models.ClientStopChatMessage
::: voxta_client.models.ClientSubscribeToChatMessage

### Interaction

::: voxta_client.models.ClientSendMessage
::: voxta_client.models.ClientTriggerActionMessage
::: voxta_client.models.ClientInterruptMessage
::: voxta_client.models.ClientRetryMessage
::: voxta_client.models.ClientRevertMessage

### Typing & Presence

::: voxta_client.models.ClientTypingStartMessage
::: voxta_client.models.ClientTypingEndMessage

### Data Retrieval

::: voxta_client.models.ClientLoadCharactersListMessage
::: voxta_client.models.ClientLoadScenariosListMessage
::: voxta_client.models.ClientLoadChatsListMessage

### Audio & Speech Playback

::: voxta_client.models.ClientSpeechPlaybackStartMessage
::: voxta_client.models.ClientSpeechPlaybackCompleteMessage
::: voxta_client.models.ClientCharacterSpeechRequestMessage

### Configuration

::: voxta_client.models.ClientUpdateContextMessage
::: voxta_client.models.ClientRegisterAppMessage
::: voxta_client.models.ClientAuthenticateMessage
