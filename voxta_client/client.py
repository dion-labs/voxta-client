import asyncio
import logging
import uuid
from typing import Any, Callable, Optional

from voxta_client.constants import EventType
from voxta_client.models import (
    ClientAddChatParticipantMessage,
    ClientAuthenticateMessage,
    ClientCharacterSpeechRequestMessage,
    ClientDeleteMessageMessage,
    ClientInspectAudioInputMessage,
    ClientInspectMessage,
    ClientInterruptMessage,
    ClientLoadCharactersListMessage,
    ClientLoadChatsListMessage,
    ClientLoadScenariosListMessage,
    ClientMessage,
    ClientPauseMessage,
    ClientRegisterAppMessage,
    ClientRemoveChatParticipantMessage,
    ClientRequestSuggestionsMessage,
    ClientResumeChatMessage,
    ClientRetryMessage,
    ClientRevertMessage,
    ClientSendMessage,
    ClientSpeechPlaybackCompleteMessage,
    ClientSpeechPlaybackStartMessage,
    ClientStartChatMessage,
    ClientStopChatMessage,
    ClientSubscribeToChatMessage,
    ClientTriggerActionMessage,
    ClientTypingEndMessage,
    ClientTypingStartMessage,
    ClientUpdateContextMessage,
    ClientUpdateMessageMessage,
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
        self.is_speaking = False
        self.is_thinking = False
        self.last_message_id: Optional[str] = None
        self._active_chat_id: Optional[str] = None

    @property
    def running(self) -> bool:
        """
        Check if the client is currently connected and running.
        """
        return self.transport.running

    def on(self, event_name: str, callback: Optional[Callable] = None) -> Any:
        """
        Register a callback for a specific event. Can be used as a decorator.

        Args:
            event_name: The name of the event to listen for (see EventType).
            callback: The callback function to execute. If None, returns a decorator.
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
        """
        Perform the initial SignalR HTTP negotiation.
        """
        return self.transport.negotiate()

    async def connect(self, connection_token: str, cookies: Optional[dict[str, str]] = None):
        """
        Establish the SignalR connection and authenticate.

        Args:
            connection_token: The SignalR connection token obtained from negotiation.
            cookies: Optional cookies to include in the connection request.
        """
        await self.transport.connect(connection_token, cookies)
        await self.authenticate(connection_token)

    async def _send_client_message(self, message: ClientMessage):
        """
        Internal method to wrap and send a Voxta message over SignalR.
        """
        invocation_id = str(uuid.uuid4())
        payload = message.to_signalr_invocation(invocation_id)
        await self._send_raw(payload)

    async def _send_raw(self, payload: dict[str, Any]):
        # Emit an event for outgoing messages so listeners (like the proxy) can track them
        # SignalR messages of type 1 are Invocations
        if payload.get("type") == 1:
            args = payload.get("arguments", [])
            invocation_id = payload.get("invocationId")
            if args:
                # The actual Voxta message is usually the first argument
                data = args[0]
                if isinstance(data, dict) and invocation_id:
                    data["invocationId"] = invocation_id
                await self._emit("client_send", data)

        await self.transport.send(payload)

    async def authenticate(self, _token: str):
        """
        Send the initial authentication message to the server.
        """
        self.logger.info("Authenticating...")
        await self._send_client_message(ClientAuthenticateMessage())

    async def register_app(self, label: str = "Voxta Python Client"):
        """
        Register the application with the Voxta server.

        Args:
            label: A human-readable label for this client.
        """
        self.logger.info(f"Registering app: {label}")
        await self._send_client_message(
            ClientRegisterAppMessage(clientVersion="1.2.1", label=label)
        )

    async def start_chat(self, character_id: str, contexts: Optional[list[dict[str, Any]]] = None):
        """
        Start a new chat session with a specific character.

        Args:
            character_id: The ID of the character to chat with.
            contexts: Optional list of context objects to initialize the chat.
        """
        msg = ClientStartChatMessage(characterId=character_id, contexts=contexts or [])
        self.logger.info(f"Starting chat with character: {character_id}")
        await self._send_client_message(msg)

    async def resume_chat(self, chat_id: str):
        """
        Resume an existing chat session.

        Args:
            chat_id: The ID of the chat to resume.
        """
        msg = ClientResumeChatMessage(chatId=chat_id)
        self.logger.info(f"Resuming chat: {chat_id}")
        await self._send_client_message(msg)

    async def stop_chat(self, chat_id: str):
        """
        Stop an active chat session.

        Args:
            chat_id: The ID of the chat to stop.
        """
        msg = ClientStopChatMessage(chatId=chat_id)
        self.logger.info(f"Stopping chat: {chat_id}")
        await self._send_client_message(msg)

    async def trigger_action(
        self,
        action: str,
        arguments: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ):
        """
        Explicitly triggers an AI action/response.

        Args:
            action: The name of the action to trigger.
            arguments: Optional dictionary of arguments for the action.
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientTriggerActionMessage(
            sessionId=target_session, messageId=str(uuid.uuid4()), value=action, arguments=arguments
        )
        await self._send_client_message(msg)

    async def revert(self, session_id: Optional[str] = None):
        """
        Revert the last message in the session.

        Args:
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientRevertMessage(sessionId=target_session)
        await self._send_client_message(msg)

    async def retry(self, session_id: Optional[str] = None):
        """
        Retry the last AI response generation.

        Args:
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientRetryMessage(sessionId=target_session)
        await self._send_client_message(msg)

    async def typing_start(self, session_id: Optional[str] = None):
        """
        Notify the server that the user has started typing.

        Args:
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientTypingStartMessage(sessionId=target_session)
        await self._send_client_message(msg)

    async def typing_end(self, session_id: Optional[str] = None):
        """
        Notify the server that the user has stopped typing.

        Args:
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientTypingEndMessage(sessionId=target_session)
        await self._send_client_message(msg)

    async def load_characters_list(self):
        """
        Request the list of available characters.
        """
        await self._send_client_message(ClientLoadCharactersListMessage())

    async def load_scenarios_list(self):
        """
        Request the list of available scenarios.
        """
        await self._send_client_message(ClientLoadScenariosListMessage())

    async def load_chats_list(
        self, character_id: Optional[str] = None, scenario_id: Optional[str] = None
    ):
        """
        Request the list of available chats.

        Args:
            character_id: Optional filter by character ID.
            scenario_id: Optional filter by scenario ID.
        """
        msg = ClientLoadChatsListMessage(characterId=character_id, scenarioId=scenario_id)
        await self._send_client_message(msg)

    async def add_chat_participant(self, character_id: str, session_id: Optional[str] = None):
        """
        Add a character as a participant to the current chat session.

        Args:
            character_id: The ID of the character to add.
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientAddChatParticipantMessage(sessionId=target_session, characterId=character_id)
        await self._send_client_message(msg)

    async def remove_chat_participant(self, character_id: str, session_id: Optional[str] = None):
        """
        Remove a character from the current chat session.

        Args:
            character_id: The ID of the character to remove.
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientRemoveChatParticipantMessage(sessionId=target_session, characterId=character_id)
        await self._send_client_message(msg)

    async def request_suggestions(self, session_id: Optional[str] = None):
        """
        Request message suggestions from the AI.

        Args:
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientRequestSuggestionsMessage(sessionId=target_session)
        await self._send_client_message(msg)

    async def inspect_audio_input(self, enabled: bool, session_id: Optional[str] = None):
        """
        Toggle audio input inspection mode.

        Args:
            enabled: Whether to enable or disable inspection.
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientInspectAudioInputMessage(sessionId=target_session, enabled=enabled)
        await self._send_client_message(msg)

    async def update_message(self, message_id: str, text: str, session_id: Optional[str] = None):
        """
        Update the text of a previous message.

        Args:
            message_id: The ID of the message to update.
            text: The new text for the message.
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientUpdateMessageMessage(sessionId=target_session, messageId=message_id, text=text)
        await self._send_client_message(msg)

    async def delete_message(self, message_id: str, session_id: Optional[str] = None):
        """
        Delete a message from the session history.

        Args:
            message_id: The ID of the message to delete.
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientDeleteMessageMessage(sessionId=target_session, messageId=message_id)
        await self._send_client_message(msg)

    async def subscribe_to_chat(self, session_id: str, chat_id: str):
        """
        Subscribe to events for a specific chat session.

        Args:
            session_id: The session ID.
            chat_id: The chat ID.
        """
        msg = ClientSubscribeToChatMessage(sessionId=session_id, chatId=chat_id)
        self.logger.info(f"Subscribing to chat: {chat_id}")
        await self._send_client_message(msg)

    async def inspect(self, session_id: str, enabled: bool = True):
        """
        Toggle session debug state.

        Args:
            session_id: The session ID.
            enabled: Whether to enable or disable inspection.
        """
        msg = ClientInspectMessage(sessionId=session_id, enabled=enabled)
        self.logger.info(f"Sending inspect: session={session_id}, enabled={enabled}")
        await self._send_client_message(msg)

    async def send_message(
        self,
        text: str,
        session_id: Optional[str] = None,
        do_reply: bool = True,
        do_user_inference: bool = True,
        do_character_inference: bool = True,
    ):
        """
        Send a user message to the session.

        Args:
            text: The message text.
            session_id: Optional session ID. Defaults to the active session.
            do_reply: Whether the AI should generate a reply immediately.
            do_user_inference: Whether to perform action inference on the user message.
            do_character_inference: Whether to perform action inference for the character response.
        """
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
        """
        Interrupt the current AI response/speech.

        Args:
            session_id: Optional session ID. Defaults to the active session.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientInterruptMessage(sessionId=target_session)
        await self._send_client_message(msg)

    async def pause(self, session_id: Optional[str] = None, pause: bool = True):
        """
        Pause automatic continuation of the chat.

        Args:
            session_id: Optional session ID. Defaults to the active session.
            pause: Whether to pause or resume.
        """
        target_session = session_id or self.session_id
        if not target_session:
            return
        msg = ClientPauseMessage(sessionId=target_session, pause=pause)
        await self._send_client_message(msg)

    async def character_speech_request(
        self,
        character_id: str,
        session_id: Optional[str] = None,
        text: str = "",
    ):
        """
        Request the character to start/resume speaking.

        Args:
            character_id: The ID of the character.
            session_id: Optional session ID. Defaults to the active session.
            text: Optional specific text to speak.
        """
        target_session = session_id or self.session_id

        if not target_session:
            self.logger.warning("Cannot send characterSpeechRequest: missing session_id")
            return

        msg = ClientCharacterSpeechRequestMessage(
            sessionId=target_session, characterId=character_id, text=text
        )
        self.logger.info(f"Sending characterSpeechRequest for character: {character_id}")
        await self._send_client_message(msg)

    async def speech_playback_start(
        self, session_id: Optional[str] = None, message_id: Optional[str] = None
    ):
        """
        Notify the server that speech playback has started for a message.

        Args:
            session_id: Optional session ID. Defaults to the active session.
            message_id: Optional message ID. Defaults to the last received message.
        """
        target_session = session_id or self.session_id
        target_message = message_id or self.last_message_id

        if not target_session or not target_message:
            self.logger.warning("Cannot send speechPlaybackStart: missing session_id or message_id")
            return

        msg = ClientSpeechPlaybackStartMessage(sessionId=target_session, messageId=target_message)
        self.logger.info(f"Sending speechPlaybackStart for message: {target_message}")
        await self._send_client_message(msg)

    async def speech_playback_complete(
        self, session_id: Optional[str] = None, message_id: Optional[str] = None
    ):
        """
        Notify the server that speech playback has completed for a message.

        Args:
            session_id: Optional session ID. Defaults to the active session.
            message_id: Optional message ID. Defaults to the last received message.
        """
        target_session = session_id or self.session_id
        target_message = message_id or self.last_message_id

        if not target_session or not target_message:
            self.logger.warning(
                "Cannot send speechPlaybackComplete: missing session_id or message_id"
            )
            return

        msg = ClientSpeechPlaybackCompleteMessage(
            sessionId=target_session, messageId=target_message
        )
        self.logger.info(f"Sending speechPlaybackComplete for message: {target_message}")
        await self._send_client_message(msg)

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
        """
        Update the session context, including actions, events, flags, and roles.

        Args:
            session_id: The session ID.
            context_key: A unique key for this context update.
            contexts: Optional list of context objects.
            actions: Optional list of action definitions.
            events: Optional list of event definitions.
            set_flags: Optional list of flags to set.
            enable_roles: Optional dictionary to enable/disable specific roles.
        """
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
            invocation_id = message.get("invocationId")
            error = message.get("error")
            result = message.get("result")
            
            completion_data = {
                "$type": "completion",
                "invocationId": invocation_id,
                "error": error,
                "result": result
            }
            
            if error:
                self.logger.error(f"Invocation {invocation_id} failed: {error}")
                await self._emit(EventType.ERROR, completion_data)
            else:
                self.logger.debug(f"Invocation {invocation_id} completed")
                await self._emit("completion", completion_data)
            return

        if msg_type == 1:  # Invocation
            target = message.get("target")
            invocation_id = message.get("invocationId")
            if target == "ReceiveMessage":
                args = message.get("arguments", [])
                if args:
                    payload = args[0]
                    if isinstance(payload, dict) and invocation_id:
                        payload["invocationId"] = invocation_id
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
        if sessions:
            target = next(
                (s for s in sessions if s.get("chatId") == self._active_chat_id),
                sessions[0],
            )
            chat_id = target.get("chatId")
            self._active_chat_id = chat_id
            self.session_id = target.get("sessionId")

            self.logger.info(f"Pinned to Chat: {chat_id} (Session: {self.session_id})")
            await self.subscribe_to_chat(self.session_id, chat_id)
            await self._emit(EventType.READY, self.session_id)

    async def _handle_chat_started(self, payload: dict[str, Any]):
        self.session_id = payload.get("sessionId")
        chat_id = payload.get("chatId")
        self._active_chat_id = chat_id

        self.logger.info(f"Chat started: {chat_id} (Session: {self.session_id})")
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
