from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class VoxtaModel:
    """Base class for Voxta data models."""

    def to_dict(self) -> dict[str, Any]:
        # Ensure $type is the first key in the resulting dictionary.
        # This is often required by SignalR/Voxta for polymorphic deserialization.
        res = {}
        if "type_name" in self.__dict__:
            res["$type"] = self.__dict__["type_name"]

        for k, v in self.__dict__.items():
            if k != "type_name" and v is not None:
                res[k] = v
        return res


@dataclass
class ServerMessage(VoxtaModel):
    """Base class for all messages from the server."""

    pass


@dataclass
class ServerWelcomeMessage(ServerMessage):
    """
    Message received from the server upon successful connection.
    Contains information about the assistant and the user.
    """

    assistant: dict[str, Any]
    user: dict[str, Any]
    type_name: str = "welcome"


@dataclass
class ServerChatMessage(ServerMessage):
    """
    Represents a chat message received from the server.

    Attributes:
        messageId: Unique identifier for the message.
        senderId: ID of the character or user who sent the message.
        text: The content of the message.
        role: The role of the sender (e.g., 'Assistant', 'User').
        timestamp: ISO timestamp of when the message was sent.
        sessionId: The active chat session ID.
    """

    messageId: str  # noqa: N815
    senderId: str  # noqa: N815
    text: str
    role: str
    timestamp: str
    sessionId: str  # noqa: N815
    type_name: str = "message"


@dataclass
class ServerActionMessage(ServerMessage):
    """
    Represents an action triggered by the AI (e.g., an emote or a command).

    Attributes:
        value: The name of the action (e.g., 'smile', 'search_web').
        arguments: Optional list of parameters for the action.
        role: The character role performing the action.
        senderId: ID of the character.
        sessionId: The active chat session ID.
    """

    value: str
    role: str
    senderId: str  # noqa: N815
    sessionId: str  # noqa: N815
    contextKey: Optional[str] = None  # noqa: N815
    layer: Optional[str] = None
    arguments: Optional[list[dict[str, Any]]] = None
    type_name: str = "action"


@dataclass
class ServerAuthenticationRequiredMessage(ServerMessage):
    """
    Received if the client needs to authenticate.
    """

    type_name: str = "authenticationRequired"


@dataclass
class ServerChatSessionErrorMessage(ServerMessage):
    """
    Received when an error occurs within a chat session.
    """

    message: str
    code: Optional[str] = None
    serviceName: Optional[str] = None  # noqa: N815
    type_name: str = "chatSessionError"


@dataclass
class ServerCharactersListLoadedMessage(ServerMessage):
    """
    Contains the list of available characters requested by the client.
    """

    characters: list[dict[str, Any]]
    type_name: str = "charactersListLoaded"


@dataclass
class ServerScenariosListLoadedMessage(ServerMessage):
    """
    Contains the list of available scenarios requested by the client.
    """

    scenarios: list[dict[str, Any]]
    type_name: str = "scenariosListLoaded"


@dataclass
class ServerChatsListLoadedMessage(ServerMessage):
    """
    Contains the list of available chats requested by the client.
    """

    chats: list[dict[str, Any]]
    type_name: str = "chatsListLoaded"


@dataclass
class ServerChatStartingMessage(ServerMessage):
    """
    Received when a chat session is starting.
    """

    type_name: str = "chatStarting"


@dataclass
class ServerChatLoadingMessage(ServerMessage):
    """
    Received while a chat session is being loaded.
    """

    type_name: str = "chatLoading"


@dataclass
class ServerChatClosedMessage(ServerMessage):
    """
    Received when a chat session has been closed.
    """

    chatId: str  # noqa: N815
    type_name: str = "chatClosed"


@dataclass
class ServerChatUpdatedMessage(ServerMessage):
    """
    Received when chat session properties are updated.
    """

    chatId: str  # noqa: N815
    # Add other fields as needed
    type_name: str = "chatUpdated"


@dataclass
class ServerChatPausedMessage(ServerMessage):
    """
    Received when a chat session is paused.
    """

    sessionId: str  # noqa: N815
    type_name: str = "chatPaused"


@dataclass
class ServerChatFlowMessage(ServerMessage):
    """
    Indicates a change in the chat flow state (e.g., waiting for user, thinking).
    """

    state: str
    type_name: str = "chatFlow"


@dataclass
class ServerChatParticipantsUpdatedMessage(ServerMessage):
    """
    Received when the list of participants in a chat changes.
    """

    sessionId: str  # noqa: N815
    type_name: str = "chatParticipantsUpdated"


@dataclass
class ServerReplyCancelledMessage(ServerMessage):
    """
    Received when an AI reply generation is cancelled.
    """

    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    type_name: str = "replyCancelled"


@dataclass
class ServerSpeechRecognitionStartMessage(ServerMessage):
    """
    Indicates that speech recognition has started.
    """

    type_name: str = "speechRecognitionStart"


@dataclass
class ServerSpeechRecognitionPartialMessage(ServerMessage):
    """
    Contains a partial speech recognition result.
    """

    text: str
    type_name: str = "speechRecognitionPartial"


@dataclass
class ServerSpeechRecognitionEndMessage(ServerMessage):
    """
    Contains the final speech recognition result.
    """

    text: str
    type_name: str = "speechRecognitionEnd"


@dataclass
class ServerRecordingRequestMessage(ServerMessage):
    """
    A request from the server to enable or disable audio recording.
    """

    enabled: bool
    type_name: str = "recordingRequest"


@dataclass
class ServerRecordingStatusMessage(ServerMessage):
    """
    Indicates the current status of audio recording.
    """

    enabled: bool
    type_name: str = "recordingStatus"


@dataclass
class ServerUpdatedMessage(ServerMessage):
    """
    Generic update message for a chat message or participant.
    """

    text: str
    role: str
    type_name: str = "updated"


@dataclass
class ServerDocumentUpdatedMessage(ServerMessage):
    """
    Received when a document in the chat session is updated.
    """

    documentId: str  # noqa: N815
    type_name: str = "documentUpdated"


@dataclass
class ServerModuleRuntimeInstancesMessage(ServerMessage):
    """
    Contains the list of active module runtime instances.
    """

    instances: list[dict[str, Any]]
    type_name: str = "moduleRuntimeInstances"


@dataclass
class ServerConfigurationMessage(ServerMessage):
    """
    Contains server-wide configuration information.
    """

    configurations: list[dict[str, Any]]
    type_name: str = "configuration"


@dataclass
class ServerChatConfigurationMessage(ServerMessage):
    """
    Contains configuration specific to a chat session.
    """

    # Add fields
    type_name: str = "chatConfiguration"


@dataclass
class ServerSuggestionsMessage(ServerMessage):
    """
    Contains AI-generated suggestions for the user.
    """

    suggestions: list[str]
    type_name: str = "suggestions"


@dataclass
class ServerUserInteractionRequestMessage(ServerMessage):
    """
    A request for specific user interaction (e.g., choosing an option).
    """

    requestId: str  # noqa: N815
    input: dict[str, Any]
    type_name: str = "userInteractionRequest"


@dataclass
class ServerCloseUserInteractionRequestMessage(ServerMessage):
    """
    Closes a previously sent user interaction request.
    """

    requestId: str  # noqa: N815
    type_name: str = "closeUserInteractionRequest"


@dataclass
class ServerVisionCaptureRequestMessage(ServerMessage):
    """
    A request for a vision capture (e.g., a screenshot or camera image).
    """

    source: str
    type_name: str = "visionCaptureRequest"


@dataclass
class ServerWakeWordStatusMessage(ServerMessage):
    """
    Indicates whether wake word detection is enabled.
    """

    enabled: bool
    type_name: str = "wakeWordStatus"


@dataclass
class ServerDownloadProgressMessage(ServerMessage):
    """
    Indicates the progress of a file download.
    """

    progress: float
    type_name: str = "downloadProgress"


@dataclass
class ServerInspectorMessage(ServerMessage):
    """
    A log message from the session inspector.
    """

    log: str
    type_name: str = "inspector"


@dataclass
class ServerInspectorEnabledMessage(ServerMessage):
    """
    Indicates whether the session inspector is enabled.
    """

    enabled: bool
    type_name: str = "inspectorEnabled"


@dataclass
class ServerInspectorActionExecutedMessage(ServerMessage):
    """
    Log of an action executed within the inspector.
    """

    action: str
    type_name: str = "inspectorActionExecuted"


@dataclass
class ServerInspectorScriptExecutedMessage(ServerMessage):
    """
    Log of a script executed within the inspector.
    """

    script: str
    type_name: str = "inspectorScriptExecuted"


@dataclass
class ServerInspectorScenarioEventExecutedMessage(ServerMessage):
    """
    Log of a scenario event executed within the inspector.
    """

    event: str
    type_name: str = "inspectorScenarioEventExecuted"


@dataclass
class ServerListResourcesResultMessage(ServerMessage):
    """
    The result of a request to list available resources.
    """

    resources: list[dict[str, Any]]
    type_name: str = "listResourcesResult"


@dataclass
class ServerDeployResourceResultMessage(ServerMessage):
    """
    The result of a request to deploy a resource.
    """

    success: bool
    error: Optional[str] = None
    type_name: str = "deployResourceResult"


@dataclass
class ServerMissingResourcesErrorMessage(ServerMessage):
    """
    Indicates that resources required for a chat session are missing.
    """

    resources: list[dict[str, Any]]
    type_name: str = "missingResourcesError"


@dataclass
class ServerAudioFrameMessage(ServerMessage):
    """
    A single frame of audio data received from the server.
    """

    data: str  # Base64 encoded?
    type_name: str = "audioFrame"


@dataclass
class ClientMessage(VoxtaModel):
    """Base class for all messages sent from the client to the server."""

    def to_signalr_invocation(self, invocation_id: str) -> dict[str, Any]:
        """
        Wraps the message in a SignalR invocation payload.
        """
        return {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [self.to_dict()],
        }


@dataclass
class ClientTriggerActionMessage(ClientMessage):
    """
    Trigger an AI action manually.
    """

    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    value: str
    arguments: Optional[dict[str, Any]] = None
    type_name: str = "triggerAction"


@dataclass
class ClientStopChatMessage(ClientMessage):
    """
    Stop an active chat session.
    """

    chatId: str  # noqa: N815
    type_name: str = "stopChat"


@dataclass
class ClientRevertMessage(ClientMessage):
    """
    Revert the last message in a session.
    """

    sessionId: str  # noqa: N815
    type_name: str = "revert"


@dataclass
class ClientRetryMessage(ClientMessage):
    """
    Retry the last generation in a session.
    """

    sessionId: str  # noqa: N815
    type_name: str = "retry"


@dataclass
class ClientTypingStartMessage(ClientMessage):
    """
    Notify the server that the user started typing.
    """

    sessionId: str  # noqa: N815
    type_name: str = "typingStart"


@dataclass
class ClientTypingEndMessage(ClientMessage):
    """
    Notify the server that the user stopped typing.
    """

    sessionId: str  # noqa: N815
    sent: bool = True
    type_name: str = "typingEnd"


@dataclass
class ClientLoadCharactersListMessage(ClientMessage):
    """
    Request the list of available characters.
    """

    type_name: str = "loadCharactersList"


@dataclass
class ClientLoadScenariosListMessage(ClientMessage):
    """
    Request the list of available scenarios.
    """

    type_name: str = "loadScenariosList"


@dataclass
class ClientLoadChatsListMessage(ClientMessage):
    """
    Request the list of available chats.
    """

    characterId: Optional[str] = None  # noqa: N815
    scenarioId: Optional[str] = None  # noqa: N815
    type_name: str = "loadChatsList"


@dataclass
class ClientAddChatParticipantMessage(ClientMessage):
    """
    Add a participant to the current chat session.
    """

    sessionId: str  # noqa: N815
    characterId: str  # noqa: N815
    type_name: str = "addChatParticipant"


@dataclass
class ClientRemoveChatParticipantMessage(ClientMessage):
    """
    Remove a participant from the current chat session.
    """

    sessionId: str  # noqa: N815
    characterId: str  # noqa: N815
    type_name: str = "removeChatParticipant"


@dataclass
class ClientRequestSuggestionsMessage(ClientMessage):
    """
    Request AI suggestions for the user.
    """

    sessionId: str  # noqa: N815
    type_name: str = "requestSuggestions"


@dataclass
class ClientInspectAudioInputMessage(ClientMessage):
    """
    Toggle audio input inspection mode.
    """

    sessionId: str  # noqa: N815
    enabled: bool
    type_name: str = "inspectAudioInput"


@dataclass
class ClientUpdateMessageMessage(ClientMessage):
    """
    Update the text of a previous message.
    """

    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    text: str
    type_name: str = "update"


@dataclass
class ClientDeleteMessageMessage(ClientMessage):
    """
    Delete a message from the session.
    """

    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    type_name: str = "deleteMessage"


@dataclass
class ClientSendMessage(ClientMessage):
    """
    Send a message from the user to the session.
    """

    sessionId: str  # noqa: N815
    text: str
    doReply: bool = True  # noqa: N815
    doUserActionInference: bool = True  # noqa: N815
    doCharacterActionInference: bool = True  # noqa: N815
    type_name: str = "send"


@dataclass
class ClientUpdateContextMessage(ClientMessage):
    """
    Update the session context.
    """

    sessionId: str  # noqa: N815
    contextKey: str  # noqa: N815
    contexts: Optional[list[dict[str, Any]]] = None
    actions: Optional[list[dict[str, Any]]] = None
    events: Optional[list[dict[str, Any]]] = None
    setFlags: Optional[list[str]] = None  # noqa: N815
    enableRoles: Optional[dict[str, bool]] = None  # noqa: N815
    type_name: str = "updateContext"


@dataclass
class ClientInspectMessage(ClientMessage):
    """
    Message to toggle session debug state.
    WARNING: Effect unknown, no visible UI change or logged output confirmed.
    """

    sessionId: str  # noqa: N815
    enabled: bool = True
    type_name: str = "inspect"


@dataclass
class ClientSubscribeToChatMessage(ClientMessage):
    """
    Subscribe to events for a specific chat.
    """

    sessionId: str  # noqa: N815
    chatId: str  # noqa: N815
    type_name: str = "subscribeToChat"


@dataclass
class ClientResumeChatMessage(ClientMessage):
    """
    Resume a specific chat.
    """

    chatId: str  # noqa: N815
    type_name: str = "resumeChat"


@dataclass
class ClientStartChatMessage(ClientMessage):
    """
    Start a new chat with a character.
    """

    characterId: str  # noqa: N815
    contexts: list[dict[str, Any]] = field(default_factory=list)
    type_name: str = "startChat"


@dataclass
class ClientPauseMessage(ClientMessage):
    """
    Message to pause automatic continuation.
    WARNING: Effect unknown, AI often still responds to messages.
    """

    sessionId: str  # noqa: N815
    pause: bool = True
    type_name: str = "pauseChat"


@dataclass
class ClientInterruptMessage(ClientMessage):
    """
    Interrupt the AI response.
    """

    sessionId: str  # noqa: N815
    type_name: str = "interrupt"


@dataclass
class ClientSpeechPlaybackStartMessage(ClientMessage):
    """
    Notify that speech playback has started.
    """

    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    startIndex: int = 0  # noqa: N815
    endIndex: int = 0  # noqa: N815
    duration: float = 0
    type_name: str = "speechPlaybackStart"


@dataclass
class ClientSpeechPlaybackCompleteMessage(ClientMessage):
    """
    Notify that speech playback has completed.
    """

    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    type_name: str = "speechPlaybackComplete"


@dataclass
class ClientCharacterSpeechRequestMessage(ClientMessage):
    """
    Request the character to start speaking.
    """

    sessionId: str  # noqa: N815
    characterId: str  # noqa: N815
    text: str = ""
    type_name: str = "characterSpeechRequest"


@dataclass
class ClientRegisterAppMessage(ClientMessage):
    """
    Register the client application with the server.
    """

    clientVersion: str  # noqa: N815
    label: str
    type_name: str = "registerApp"


@dataclass
class ClientAuthenticateMessage(ClientMessage):
    """
    Perform initial authentication with server capabilities.
    """

    client: str = "Voxta.Client.Web"
    clientVersion: str = "1.2.1"  # noqa: N815
    scope: list[str] = field(
        default_factory=lambda: ["role:app", "role:admin", "role:inspector", "role:user"]
    )
    capabilities: dict[str, Any] = field(
        default_factory=lambda: {
            "audioInput": "WebSocketStream",
            "audioOutput": "Url",
            "acceptedAudioContentTypes": [
                "audio/x-wav",
                "audio/wav",
                "audio/mpeg",
                "audio/webm",
                "audio/pcm",
                "audio/ogg",
            ],
            "visionCapture": "PostImage",
            "visionSources": ["Screen", "Eyes", "Attachment"],
        }
    )
    type_name: str = "authenticate"
