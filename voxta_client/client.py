import asyncio
import logging
import uuid
from typing import Any, Callable, Optional

from voxta_client.constants import EventType
from voxta_client.models import (
    ClientAuthenticateMessage,
    ClientMessage,
    ClientRegisterAppMessage,
    ClientSendMessage,
    ClientUpdateContextMessage,
)
from voxta_client.transport import VoxtaTransport


class VoxtaClient:
    """
    High-level client for interacting with the Voxta conversational AI platform.
    """

    def __init__(self, url: str):
        self.url = url
        self.logger = logging.getLogger("VoxtaClient")
        self.transport = VoxtaTransport(url, logger=self.logger.getChild("Transport"))
        self.transport.set_callbacks(
            on_message=self._handle_server_message, on_close=self._handle_close
        )

        self.callbacks: dict[str, list[Callable]] = {}
        self.session_id: Optional[str] = None
        self.chat_id: Optional[str] = None
        self.assistant_id: Optional[str] = None
        self.is_speaking = False
        self.is_thinking = False
        self.last_message_id: Optional[str] = None
        self._active_chat_id: Optional[str] = None

    @property
    def running(self) -> bool:
        return self.transport.running

    def on(self, event_name: str, callback: Optional[Callable] = None) -> Any:
        """
        Register a callback for a specific event. Can be used as a decorator.
        """
        if callback is not None:
            if event_name not in self.callbacks:
                self.callbacks[event_name] = []
            self.callbacks[event_name].append(callback)
            return callback

        def decorator(inner_callback: Callable):
            if event_name not in self.callbacks:
                self.callbacks[event_name] = []
            self.callbacks[event_name].append(inner_callback)
            return inner_callback

        return decorator

    def negotiate(self):
        return self.transport.negotiate()

    async def connect(self, connection_token: str, cookies: Optional[dict[str, str]] = None):
        await self.transport.connect(connection_token, cookies)
        await self.authenticate(connection_token)

    async def _send_client_message(self, message: ClientMessage):
        invocation_id = str(uuid.uuid4())
        await self.transport.send(message.to_signalr_invocation(invocation_id))

    async def authenticate(self, _token: str):
        self.logger.info("Authenticating...")
        await self._send_client_message(ClientAuthenticateMessage())

    async def register_app(self, label: str = "Voxta Python Client"):
        self.logger.info(f"Registering app: {label}")
        await self._send_client_message(
            ClientRegisterAppMessage(clientVersion="1.2.1", label=label)
        )

    async def start_chat(self, character_id: str, contexts: Optional[list[dict[str, Any]]] = None):
        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [
                {"$type": "startChat", "characterId": character_id, "contexts": contexts or []}
            ],
        }
        self.logger.info(f"Starting chat with character: {character_id}")
        await self.transport.send(payload)

    async def resume_chat(self, chat_id: str):
        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{"$type": "resumeChat", "chatId": chat_id}],
        }
        self.logger.info(f"Resuming chat: {chat_id}")
        await self.transport.send(payload)

    async def subscribe_to_chat(self, session_id: str, chat_id: str):
        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{"$type": "subscribeToChat", "sessionId": session_id, "chatId": chat_id}],
        }
        self.logger.info(f"Subscribing to chat: {chat_id}")
        await self.transport.send(payload)

    async def send_message(
        self,
        text: str,
        session_id: Optional[str] = None,
        do_reply: bool = True,
        do_user_inference: bool = True,
        do_character_inference: bool = True,
    ):
        target_session = session_id or self.session_id
        if not target_session:
            self.logger.error("No session ID available to send message")
            return

        msg = ClientSendMessage(
            sessionId=target_session,
            text=text,
            doReply=do_reply,
            doUserActionInference=do_user_inference,
            doCharacterActionInference=do_character_inference,
        )
        self.logger.info(f"Sending message to session {target_session}: {text[:50]}...")
        await self._send_client_message(msg)

    async def interrupt(self, session_id: Optional[str] = None):
        target_session = session_id or self.session_id
        if not target_session:
            return
        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{"$type": "interrupt", "sessionId": target_session}],
        }
        await self.transport.send(payload)

    async def pause(self, session_id: Optional[str] = None):
        target_session = session_id or self.session_id
        if not target_session:
            return
        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{"$type": "pause", "sessionId": target_session}],
        }
        await self.transport.send(payload)

    async def update_context(
        self,
        session_id: str,
        context_key: str,
        contexts: Optional[list[dict[str, Any]]] = None,
        actions: Optional[list[dict[str, Any]]] = None,
        events: Optional[list[dict[str, Any]]] = None,
        set_flags: Optional[list[str]] = None,
        enable_roles: Optional[dict[str, bool]] = None,
    ):
        msg = ClientUpdateContextMessage(
            sessionId=session_id,
            contextKey=context_key,
            contexts=contexts,
            actions=actions,
            events=events,
            setFlags=set_flags,
            enableRoles=enable_roles,
        )
        await self._send_client_message(msg)

    async def _handle_server_message(self, message: dict[str, Any]):
        msg_type = message.get("type")
        if msg_type == 6:  # Ping
            return
        if msg_type == 7:  # Close
            self.logger.warning("SignalR Close message received")
            self.transport.running = False
            return
        if msg_type == 3:  # Completion
            if message.get("error"):
                self.logger.error(f"Invocation failed: {message.get('error')}")
            return

        if msg_type == 1:  # Invocation
            target = message.get("target")
            if target == "ReceiveMessage":
                args = message.get("arguments", [])
                if args:
                    payload = args[0]
                    await self._process_voxta_event(payload)

    async def _process_voxta_event(self, payload: dict[str, Any]):
        event_type = payload.get("$type")
        if not event_type:
            return

        # Track message IDs
        msg_id = payload.get("messageId") or payload.get("id")
        if msg_id and event_type in [
            EventType.MESSAGE,
            EventType.UPDATE,
            EventType.REPLY_START,
            EventType.SPEECH_PLAYBACK_START,
        ]:
            self.last_message_id = msg_id

        # Logging
        if event_type in [EventType.MESSAGE, EventType.UPDATE]:
            sender = payload.get("senderType") or payload.get("role")
            text = payload.get("text", "")[:100]
            self.logger.info(f"Voxta Event: {event_type} | From {sender}: {text}...")
        else:
            self.logger.info(f"Voxta Event: {event_type}")

        # Internal state management
        if event_type == EventType.WELCOME:
            self.assistant_id = payload.get("assistant", {}).get("id")
            await self.register_app()
        elif event_type == EventType.CHATS_SESSIONS_UPDATED:
            await self._handle_sessions_updated(payload)
        elif event_type == EventType.CHAT_STARTED:
            await self._handle_chat_started(payload)
        elif event_type == EventType.ERROR:
            err_msg = payload.get("message", "")
            if "Chat session already exists" in err_msg:
                self.logger.info(
                    "Ignoring 'Chat session already exists' error "
                    "(this is normal during proxy resumption)."
                )
            else:
                self.logger.error(f"Voxta Error: {err_msg}")
        elif event_type in [EventType.REPLY_GENERATING, EventType.REPLY_START]:
            self.is_thinking = True
        elif event_type == EventType.REPLY_END:
            self.is_thinking = False
        elif event_type == EventType.SPEECH_PLAYBACK_START:
            self.is_speaking = True
        elif event_type in [EventType.SPEECH_PLAYBACK_COMPLETE, EventType.INTERRUPT_SPEECH]:
            self.is_speaking = False
            if event_type == EventType.INTERRUPT_SPEECH:
                self.is_thinking = False

        # Emit event
        await self._emit(event_type, payload)

    async def _handle_sessions_updated(self, payload: dict[str, Any]):
        sessions = payload.get("sessions", [])
        if sessions and not self.chat_id:
            target = next(
                (s for s in sessions if s.get("chatId") == self._active_chat_id),
                sessions[0],
            )
            self.chat_id = target.get("chatId")
            self._active_chat_id = self.chat_id
            if not self.session_id:
                self.session_id = target.get("sessionId")
            self.logger.info(f"Pinned to Chat: {self.chat_id}")
            await self.subscribe_to_chat(self.session_id, self.chat_id)
            await self._emit(EventType.READY, self.session_id)

    async def _handle_chat_started(self, payload: dict[str, Any]):
        new_session_id = payload.get("sessionId")
        new_chat_id = payload.get("chatId")
        if new_chat_id and new_chat_id != self._active_chat_id:
            self.session_id = new_session_id
            self.chat_id = new_chat_id
            self._active_chat_id = new_chat_id
            await self._emit(EventType.READY, self.session_id)

    async def _emit(self, event_name: str, data: Any):
        if event_name in self.callbacks:
            for cb in self.callbacks[event_name]:
                try:
                    if asyncio.iscoroutinefunction(cb):
                        await cb(data)
                    else:
                        cb(data)
                except Exception as e:
                    self.logger.error(f"Error in callback for {event_name}: {e}")

    def _handle_close(self):
        self.logger.info("Connection closed")
        asyncio.create_task(self._emit("close", None))

    async def close(self):
        """
        Close the client connection.
        """
        await self.transport.close()
