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
