from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class VoxtaModel:
    """Base class for Voxta data models."""

    def to_dict(self) -> Dict[str, Any]:
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        # Map internal names to SignalR/Voxta names
        if "type_name" in data:
            data["$type"] = data.pop("type_name")
        return data


@dataclass
class ServerMessage(VoxtaModel):
    """Base class for all messages from the server."""

    pass


@dataclass
class ServerWelcomeMessage(ServerMessage):
    assistant: Dict[str, Any]
    user: Dict[str, Any]
    type_name: str = "welcome"


@dataclass
class ServerChatMessage(ServerMessage):
    messageId: str
    senderId: str
    text: str
    role: str
    timestamp: str
    sessionId: str
    type_name: str = "message"


@dataclass
class ServerActionMessage(ServerMessage):
    value: str
    role: str
    senderId: str
    sessionId: str
    contextKey: Optional[str] = None
    layer: Optional[str] = None
    arguments: Optional[List[Dict[str, Any]]] = None
    type_name: str = "action"


@dataclass
class ClientMessage(VoxtaModel):
    """Base class for all messages to the server."""

    def to_signalr_invocation(self, invocation_id: str) -> Dict[str, Any]:
        return {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [self.to_dict()],
        }


@dataclass
class ClientSendMessage(ClientMessage):
    sessionId: str
    text: str
    doReply: bool = True
    doUserActionInference: bool = True
    doCharacterActionInference: bool = True
    type_name: str = "send"


@dataclass
class ClientUpdateContextMessage(ClientMessage):
    sessionId: str
    contextKey: str
    contexts: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    events: Optional[List[Dict[str, Any]]] = None
    setFlags: Optional[List[str]] = None
    enableRoles: Optional[Dict[str, bool]] = None
    type_name: str = "updateContext"


@dataclass
class ClientRegisterAppMessage(ClientMessage):
    clientVersion: str
    label: str
    type_name: str = "registerApp"


@dataclass
class ClientAuthenticateMessage(ClientMessage):
    client: str = "Voxta.Client.Web"
    clientVersion: str = "1.2.1"
    scope: List[str] = field(
        default_factory=lambda: ["role:app", "role:admin", "role:inspector", "role:user"]
    )
    capabilities: Dict[str, Any] = field(
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
