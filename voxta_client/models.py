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
    assistant: dict[str, Any]
    user: dict[str, Any]
    type_name: str = "welcome"


@dataclass
class ServerChatMessage(ServerMessage):
    messageId: str  # noqa: N815
    senderId: str  # noqa: N815
    text: str
    role: str
    timestamp: str
    sessionId: str  # noqa: N815
    type_name: str = "message"


@dataclass
class ServerActionMessage(ServerMessage):
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
    type_name: str = "authenticationRequired"


@dataclass
class ServerChatSessionErrorMessage(ServerMessage):
    message: str
    code: Optional[str] = None
    serviceName: Optional[str] = None  # noqa: N815
    type_name: str = "chatSessionError"


@dataclass
class ServerCharactersListLoadedMessage(ServerMessage):
    characters: list[dict[str, Any]]
    type_name: str = "charactersListLoaded"


@dataclass
class ServerScenariosListLoadedMessage(ServerMessage):
    scenarios: list[dict[str, Any]]
    type_name: str = "scenariosListLoaded"


@dataclass
class ServerChatsListLoadedMessage(ServerMessage):
    chats: list[dict[str, Any]]
    type_name: str = "chatsListLoaded"


@dataclass
class ServerChatStartingMessage(ServerMessage):
    type_name: str = "chatStarting"


@dataclass
class ServerChatLoadingMessage(ServerMessage):
    type_name: str = "chatLoading"


@dataclass
class ServerChatClosedMessage(ServerMessage):
    chatId: str  # noqa: N815
    type_name: str = "chatClosed"


@dataclass
class ServerChatUpdatedMessage(ServerMessage):
    chatId: str  # noqa: N815
    # Add other fields as needed
    type_name: str = "chatUpdated"


@dataclass
class ServerChatPausedMessage(ServerMessage):
    sessionId: str  # noqa: N815
    type_name: str = "chatPaused"


@dataclass
class ServerChatFlowMessage(ServerMessage):
    state: str
    type_name: str = "chatFlow"


@dataclass
class ServerChatParticipantsUpdatedMessage(ServerMessage):
    sessionId: str  # noqa: N815
    type_name: str = "chatParticipantsUpdated"


@dataclass
class ServerReplyCancelledMessage(ServerMessage):
    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    type_name: str = "replyCancelled"


@dataclass
class ServerSpeechRecognitionStartMessage(ServerMessage):
    type_name: str = "speechRecognitionStart"


@dataclass
class ServerSpeechRecognitionPartialMessage(ServerMessage):
    text: str
    type_name: str = "speechRecognitionPartial"


@dataclass
class ServerSpeechRecognitionEndMessage(ServerMessage):
    text: str
    type_name: str = "speechRecognitionEnd"


@dataclass
class ServerRecordingRequestMessage(ServerMessage):
    enabled: bool
    type_name: str = "recordingRequest"


@dataclass
class ServerRecordingStatusMessage(ServerMessage):
    enabled: bool
    type_name: str = "recordingStatus"


@dataclass
class ServerUpdatedMessage(ServerMessage):
    text: str
    role: str
    type_name: str = "updated"


@dataclass
class ServerDocumentUpdatedMessage(ServerMessage):
    documentId: str  # noqa: N815
    type_name: str = "documentUpdated"


@dataclass
class ServerModuleRuntimeInstancesMessage(ServerMessage):
    instances: list[dict[str, Any]]
    type_name: str = "moduleRuntimeInstances"


@dataclass
class ServerConfigurationMessage(ServerMessage):
    configurations: list[dict[str, Any]]
    type_name: str = "configuration"


@dataclass
class ServerChatConfigurationMessage(ServerMessage):
    # Add fields
    type_name: str = "chatConfiguration"


@dataclass
class ServerSuggestionsMessage(ServerMessage):
    suggestions: list[str]
    type_name: str = "suggestions"


@dataclass
class ServerUserInteractionRequestMessage(ServerMessage):
    requestId: str  # noqa: N815
    input: dict[str, Any]
    type_name: str = "userInteractionRequest"


@dataclass
class ServerCloseUserInteractionRequestMessage(ServerMessage):
    requestId: str  # noqa: N815
    type_name: str = "closeUserInteractionRequest"


@dataclass
class ServerVisionCaptureRequestMessage(ServerMessage):
    source: str
    type_name: str = "visionCaptureRequest"


@dataclass
class ServerWakeWordStatusMessage(ServerMessage):
    enabled: bool
    type_name: str = "wakeWordStatus"


@dataclass
class ServerDownloadProgressMessage(ServerMessage):
    progress: float
    type_name: str = "downloadProgress"


@dataclass
class ServerInspectorMessage(ServerMessage):
    log: str
    type_name: str = "inspector"


@dataclass
class ServerInspectorEnabledMessage(ServerMessage):
    enabled: bool
    type_name: str = "inspectorEnabled"


@dataclass
class ServerInspectorActionExecutedMessage(ServerMessage):
    action: str
    type_name: str = "inspectorActionExecuted"


@dataclass
class ServerInspectorScriptExecutedMessage(ServerMessage):
    script: str
    type_name: str = "inspectorScriptExecuted"


@dataclass
class ServerInspectorScenarioEventExecutedMessage(ServerMessage):
    event: str
    type_name: str = "inspectorScenarioEventExecuted"


@dataclass
class ServerListResourcesResultMessage(ServerMessage):
    resources: list[dict[str, Any]]
    type_name: str = "listResourcesResult"


@dataclass
class ServerDeployResourceResultMessage(ServerMessage):
    success: bool
    error: Optional[str] = None
    type_name: str = "deployResourceResult"


@dataclass
class ServerMissingResourcesErrorMessage(ServerMessage):
    resources: list[dict[str, Any]]
    type_name: str = "missingResourcesError"


@dataclass
class ServerAudioFrameMessage(ServerMessage):
    data: str # Base64 encoded?
    type_name: str = "audioFrame"


@dataclass
class ClientMessage(VoxtaModel):
    """Base class for all messages to the server."""

    def to_signalr_invocation(self, invocation_id: str) -> dict[str, Any]:
        return {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [self.to_dict()],
        }


@dataclass
class ClientTriggerActionMessage(ClientMessage):
    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    value: str
    arguments: Optional[dict[str, Any]] = None
    type_name: str = "triggerAction"


@dataclass
class ClientStopChatMessage(ClientMessage):
    chatId: str  # noqa: N815
    type_name: str = "stopChat"


@dataclass
class ClientRevertMessage(ClientMessage):
    sessionId: str  # noqa: N815
    type_name: str = "revert"


@dataclass
class ClientRetryMessage(ClientMessage):
    sessionId: str  # noqa: N815
    type_name: str = "retry"


@dataclass
class ClientTypingStartMessage(ClientMessage):
    sessionId: str  # noqa: N815
    type_name: str = "typingStart"


@dataclass
class ClientTypingEndMessage(ClientMessage):
    sessionId: str  # noqa: N815
    sent: bool = True
    type_name: str = "typingEnd"


@dataclass
class ClientLoadCharactersListMessage(ClientMessage):
    type_name: str = "loadCharactersList"


@dataclass
class ClientLoadScenariosListMessage(ClientMessage):
    type_name: str = "loadScenariosList"


@dataclass
class ClientLoadChatsListMessage(ClientMessage):
    characterId: Optional[str] = None  # noqa: N815
    scenarioId: Optional[str] = None  # noqa: N815
    type_name: str = "loadChatsList"


@dataclass
class ClientAddChatParticipantMessage(ClientMessage):
    sessionId: str  # noqa: N815
    characterId: str  # noqa: N815
    type_name: str = "addChatParticipant"


@dataclass
class ClientRemoveChatParticipantMessage(ClientMessage):
    sessionId: str  # noqa: N815
    characterId: str  # noqa: N815
    type_name: str = "removeChatParticipant"


@dataclass
class ClientRequestSuggestionsMessage(ClientMessage):
    sessionId: str  # noqa: N815
    type_name: str = "requestSuggestions"


@dataclass
class ClientInspectAudioInputMessage(ClientMessage):
    sessionId: str  # noqa: N815
    enabled: bool
    type_name: str = "inspectAudioInput"


@dataclass
class ClientUpdateMessageMessage(ClientMessage):
    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    text: str
    type_name: str = "update"


@dataclass
class ClientDeleteMessageMessage(ClientMessage):
    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    type_name: str = "deleteMessage"


@dataclass
class ClientSendMessage(ClientMessage):
    sessionId: str  # noqa: N815
    text: str
    doReply: bool = True  # noqa: N815
    doUserActionInference: bool = True  # noqa: N815
    doCharacterActionInference: bool = True  # noqa: N815
    type_name: str = "send"


@dataclass
class ClientUpdateContextMessage(ClientMessage):
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
    sessionId: str  # noqa: N815
    chatId: str  # noqa: N815
    type_name: str = "subscribeToChat"


@dataclass
class ClientResumeChatMessage(ClientMessage):
    chatId: str  # noqa: N815
    type_name: str = "resumeChat"


@dataclass
class ClientStartChatMessage(ClientMessage):
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
class ClientStopChatMessage(ClientMessage):
    chatId: str  # noqa: N815
    type_name: str = "stopChat"


@dataclass
class ClientInterruptMessage(ClientMessage):
    sessionId: str  # noqa: N815
    type_name: str = "interrupt"


@dataclass
class ClientSpeechPlaybackStartMessage(ClientMessage):
    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    startIndex: int = 0  # noqa: N815
    endIndex: int = 0  # noqa: N815
    duration: float = 0
    type_name: str = "speechPlaybackStart"


@dataclass
class ClientSpeechPlaybackCompleteMessage(ClientMessage):
    sessionId: str  # noqa: N815
    messageId: str  # noqa: N815
    type_name: str = "speechPlaybackComplete"


@dataclass
class ClientCharacterSpeechRequestMessage(ClientMessage):
    sessionId: str  # noqa: N815
    characterId: str  # noqa: N815
    text: str = ""
    type_name: str = "characterSpeechRequest"


@dataclass
class ClientRegisterAppMessage(ClientMessage):
    clientVersion: str  # noqa: N815
    label: str
    type_name: str = "registerApp"


@dataclass
class ClientAuthenticateMessage(ClientMessage):
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
