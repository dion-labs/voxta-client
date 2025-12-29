import logging
import requests
import websockets
import asyncio
import json
import uuid
from typing import Callable, Coroutine

class VoxtaClient:
    def __init__(self, url: str):
        self.logger = logging.getLogger("VoxtaClient")
        self.url = url
        self.websocket = None
        self.running = False
        self.callbacks = {} # type: ignore
        self.session_id = None
        self.chat_id = None
        self.assistant_id = None
        self.is_speaking = False
        self.is_thinking = False
        self.last_message_id = None
        self._active_chat_id = None

    def on(self, event_name: str, callback: Callable):
        """Register a callback for a specific event (e.g., 'welcome', 'chatStarted')"""
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []
        self.callbacks[event_name].append(callback)

    def negotiate(self):
        try:
            response = requests.post(f"{self.url}/hub/negotiate?negotiateVersion=1")
            if response.status_code != 200:
                self.logger.error(f"Failed to negotiate: {response.text}")
                return None, None
            
            data = response.json()
            # self.logger.info(f"Negotiated: {data}")
            return data.get("connectionToken"), response.cookies
        except Exception as e:
            self.logger.error(f"Negotiation error: {e}")
            return None, None

    async def connect(self, connection_token: str, cookies=None):
        self.logger.info(f"Connecting to websocket with token: {connection_token}")
        ws_url = self.url.replace("http", "ws") + "/hub"
        
        extra_headers = {}
        if cookies:
            cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            extra_headers["Cookie"] = cookie_header

        import urllib.parse
        encoded_token = urllib.parse.quote(connection_token)
        full_ws_url = f"{ws_url}?id={encoded_token}"
        self.logger.info(f"Connecting to: {full_ws_url}")
        async with websockets.connect(full_ws_url, additional_headers=extra_headers) as websocket:
            self.logger.info("Connected to websocket")
            self.websocket = websocket
            self.running = True
            
            await self._handshake()
            await self.authenticate(connection_token)
            await self._read_loop()

    async def _handshake(self):
        await self._send_json({"protocol": "json", "version": 1})

    async def authenticate(self, connection_token: str):
        self.logger.info("Authenticating...")
        invocation_id = str(uuid.uuid4())
        
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "authenticate",
                "client": "Voxta.Client.Web",
                "clientVersion": "1.2.1",
                "scope": ["role:app", "role:admin", "role:inspector", "role:user"],
                "capabilities": {
                    "audioInput": "WebSocketStream",
                    "audioOutput": "Url",
                    "acceptedAudioContentTypes": [
                        "audio/x-wav", "audio/wav", "audio/mpeg", "audio/webm", "audio/pcm", "audio/ogg"
                    ],
                    "visionCapture": "PostImage",
                    "visionSources": ["Screen", "Eyes", "Attachment"]
                }
            }]
        }
        await self._send_json(payload)

    async def start_chat(self, character_id: str, contexts: list = None):
        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "startChat",
                "characterId": character_id,
                "contexts": contexts or []
            }]
        }
        self.logger.info(f"Starting chat with character: {character_id}")
        await self._send_json(payload)

    async def resume_chat(self, chat_id: str):
        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "resumeChat",
                "chatId": chat_id
            }]
        }
        self.logger.info(f"Resuming chat: {chat_id}")
        await self._send_json(payload)

    async def register_app(self, label: str = "Voxta Proxy"):
        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "registerApp",
                "clientVersion": "1.2.1",
                "label": label
            }]
        }
        self.logger.info(f"Registering app: {label}")
        await self._send_json(payload)

    async def subscribe_to_chat(self, session_id: str, chat_id: str):
        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "subscribeToChat",
                "sessionId": session_id,
                "chatId": chat_id
            }]
        }
        self.logger.info(f"Subscribing to chat: {chat_id}")
        await self._send_json(payload)

    async def inspect(self, session_id: str, enabled: bool = True):
        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "inspect",
                "sessionId": session_id,
                "enabled": enabled
            }]
        }
        self.logger.info(f"Sending inspect: session={session_id}, enabled={enabled}")
        await self._send_json(payload)

    async def send_message(self, text: str, session_id: str = None, 
                           do_reply: bool = True,
                           do_user_inference: bool = True, 
                           do_character_inference: bool = True):
        target_session = session_id or self.session_id
        if not target_session:
            self.logger.error(f"No session ID available to send message: {text[:50]}...")
            return

        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "send", 
                "sessionId": target_session,
                "text": text,
                "doReply": do_reply,
                "doUserActionInference": do_user_inference,
                "doCharacterActionInference": do_character_inference
            }]
        }

        self.logger.info(f"Sending message to session {target_session}: {text[:50]}...")
        await self._send_json(payload)

    async def interrupt(self, session_id: str = None):
        target_session = session_id or self.session_id
        if not target_session:
            self.logger.error("No session ID available to interrupt")
            return

        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "interrupt",
                "sessionId": target_session
            }]
        }
        self.logger.info(f"Interrupting session: {target_session}")
        await self._send_json(payload)

    async def pause(self, session_id: str = None):
        target_session = session_id or self.session_id
        if not target_session:
            self.logger.error("No session ID available to pause")
            return

        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "pause",
                "sessionId": target_session
            }]
        }
        self.logger.info(f"Pausing session: {target_session}")
        await self._send_json(payload)

    async def speech_playback_start(self, session_id: str = None, message_id: str = None):
        """
        Sends speechPlaybackStart to the server. 
        Sometimes used to signal client-side playback takeover or to force-stop current streams.
        """
        target_session = session_id or self.session_id
        target_message = message_id or self.last_message_id
        
        if not target_session or not target_message:
            self.logger.warning("Cannot send speechPlaybackStart: missing session_id or message_id")
            return

        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "speechPlaybackStart",
                "sessionId": target_session,
                "messageId": target_message,
                "startIndex": 0,
                "endIndex": 0,
                "duration": 0
            }]
        }
        self.logger.info(f"Sending speechPlaybackStart for message: {target_message}")
        await self._send_json(payload)

    async def speech_playback_complete(self, session_id: str = None, message_id: str = None):
        """
        Sends speechPlaybackComplete to the server.
        """
        target_session = session_id or self.session_id
        target_message = message_id or self.last_message_id
        
        if not target_session or not target_message:
            self.logger.warning("Cannot send speechPlaybackComplete: missing session_id or message_id")
            return

        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "speechPlaybackComplete",
                "sessionId": target_session,
                "messageId": target_message
            }]
        }
        self.logger.info(f"Sending speechPlaybackComplete for message: {target_message}")
        await self._send_json(payload)

    async def character_speech_request(self, session_id: str = None, character_id: str = None):
        """
        Sends characterSpeechRequest to the server to ask the character to start/resume speaking.
        """
        target_session = session_id or self.session_id
        target_character = character_id or self.assistant_id
        
        if not target_session or not target_character:
            self.logger.warning("Cannot send characterSpeechRequest: missing session_id or character_id")
            return

        invocation_id = str(uuid.uuid4())
        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [{
                "$type": "characterSpeechRequest",
                "sessionId": target_session,
                "characterId": target_character
            }]
        }
        self.logger.info(f"Sending characterSpeechRequest for character: {target_character}")
        await self._send_json(payload)

    async def _read_loop(self):
        while self.running:
            try:
                message = await self.websocket.recv()
                
                # SignalR splitting
                raw_messages = message.split('\x1e')
                for raw_msg in raw_messages:
                    if not raw_msg.strip():
                        continue
                    
                    try:
                        parsed_message = json.loads(raw_msg)
                        await self._handle_server_message(parsed_message)
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to decode message chunk: {raw_msg} | Error: {e}")

            except Exception as e:
                self.logger.error(f"Error in read loop: {e}")
                self.running = False
                break

    async def _handle_server_message(self, message: dict):
        msg_type = message.get("type")
        target = message.get("target")
        
        # Log ALL raw messages at INFO level for debugging
        if msg_type != 6:
            self.logger.info(f"SIGNALR IN: (type {msg_type}, target {target}): {json.dumps(message)}")

        if msg_type == 1:
            arguments = message.get("arguments", [])
            if arguments:
                payload = arguments[0]
                msg_inner_type = payload.get("$type")
                
                # Track last message ID for interruptions/playback sync
                msg_id = payload.get("messageId") or payload.get("id")
                if msg_id and msg_inner_type in ["message", "update", "replyStart", "speechPlaybackStart"]:
                    self.last_message_id = msg_id

                if msg_inner_type:
                    # Selective INFO logging for important state-changing events
                    important_events = {
                        "welcome", "chatsSessionsUpdated", "chatStarted", "error", 
                        "message", "replyGenerating", "replyStart", "replyEnd", 
                        "speechPlaybackStart", "speechPlaybackComplete", "interruptSpeech"
                    }
                    
                    if msg_inner_type in important_events:
                        self.logger.info(f"Voxta Event: {msg_inner_type}")
                    else:
                        self.logger.debug(f"Voxta Event: {msg_inner_type}")
                    
                    if msg_inner_type in ["message", "update"]:
                        sender = payload.get("senderType") or payload.get("role")
                        text = payload.get("text", "")[:100]
                        self.logger.info(f"  Message from {sender}: {text}...")
                    
                    # Emit generic event
                    await self._emit(msg_inner_type, payload)
                else:
                    # If no $type, log target at DEBUG
                    self.logger.debug(f"Voxta Event (no type, target={target}): {json.dumps(payload)}")
                    await self._emit(target, payload)
                
                # Internal logic
                if msg_inner_type == "welcome":
                    assistant = payload.get("assistant", {})
                    self.assistant_id = assistant.get("id")
                    self.logger.info(f"Connected as {assistant.get('name')} ({self.assistant_id})")
                    # Register app
                    await self.register_app()
                    # We don't start a chat automatically anymore; 
                    # we wait for chatsSessionsUpdated to see if one already exists.
                    # Or we start one only if requested or if no sessions exist after a delay.

                elif msg_inner_type == "chatsSessionsUpdated":
                    # This event lists all active chats and their associated session IDs.
                    # We use it to find our chat if we don't have one, but we 
                    # should NEVER switch our sessionId to one belonging to another client (like the Web UI).
                    sessions = payload.get("sessions", [])
                    self.logger.debug(f"Active sessions updated: {len(sessions)}")
                    
                    if sessions:
                        # If we don't have a chat_id yet, pick one to follow
                        if not self.chat_id:
                            # Prefer the one we were previously on if it still exists
                            target = next((s for s in sessions if s.get("chatId") == self._active_chat_id), sessions[0])
                            
                            self.chat_id = target.get("chatId")
                            self._active_chat_id = self.chat_id
                            # Only set session_id from here if we don't have one from chatStarted
                            if not self.session_id:
                                self.session_id = target.get("sessionId")
                            
                            self.logger.info(f"Pinned to Chat: {self.chat_id} (Using Session: {self.session_id})")
                            await self.subscribe_to_chat(self.session_id, self.chat_id)
                            await self._emit("ready", self.session_id)
                        else:
                            # We already have a chat. Just log for debug if it disappeared
                            found_current = any(s.get("chatId") == self.chat_id for s in sessions)
                            if not found_current:
                                self.logger.warning(f"Current chat {self.chat_id} no longer in active list!")
                
                elif msg_inner_type == "chatStarted":
                    new_session_id = payload.get("sessionId")
                    new_chat_id = payload.get("chatId")
                    self.logger.info(f"Chat started, Session ID: {new_session_id}, Chat ID: {new_chat_id}")
                    
                    if new_chat_id and new_chat_id != self._active_chat_id:
                        self.session_id = new_session_id
                        self.chat_id = new_chat_id
                        self._active_chat_id = new_chat_id
                        # await self.subscribe_to(new_chat_id)
                        # await self.inspect(self.session_id)
                        await self._emit("ready", self.session_id)

                elif msg_inner_type == "error":
                    err_msg = payload.get("message", "")
                    if "Chat session already exists" in err_msg:
                        self.logger.info("Ignoring 'Chat session already exists' error (this is normal during proxy resumption).")
                    else:
                        self.logger.error(f"Voxta Error: {err_msg}")

                elif msg_inner_type == "replyGenerating" or msg_inner_type == "replyStart":
                    self.is_thinking = True
                elif msg_inner_type == "replyEnd":
                    self.is_thinking = False
                
                elif msg_inner_type == "speechPlaybackStart":
                    self.is_speaking = True
                elif msg_inner_type == "speechPlaybackComplete":
                    self.is_speaking = False
                
                elif msg_inner_type == "interruptSpeech":
                    self.is_speaking = False
                    self.is_thinking = False
        elif msg_type == 6: # Ping
            pass
        else:
            self.logger.debug(f"SignalR Message Type {msg_type}: {message}")

    async def _emit(self, event_name, data):
        if event_name in self.callbacks:
            for cb in self.callbacks[event_name]:
                if asyncio.iscoroutinefunction(cb):
                    await cb(data)
                else:
                    cb(data)

    async def update_context(self, session_id: str, context_key: str, 
                           contexts: list = None, actions: list = None, events: list = None,
                           set_flags: list = None, enable_roles: list = None):
        """
        Sends an updateContext message to Voxta.
        """
        if not session_id:
            self.logger.error("No session ID provided for context update")
            return

        invocation_id = str(uuid.uuid4())
        
        args = {
            "$type": "updateContext",
            "sessionId": session_id,
            "contextKey": context_key
        }
        
        if contexts: args["contexts"] = contexts
        if actions: args["actions"] = actions
        if events: args["events"] = events
        if set_flags: args["setFlags"] = set_flags
        if enable_roles: args["enableRoles"] = enable_roles

        payload = {
            "type": 1,
            "invocationId": invocation_id,
            "target": "SendMessage",
            "arguments": [args]
        }

        self.logger.info(f"Sending context update: {context_key}")
        await self._send_json(payload)

    async def _send_json(self, data: dict):
        msg = json.dumps(data) + "\x1e"
        self.logger.info(f"SIGNALR OUT: {json.dumps(data)}")
        if self.websocket:
            await self.websocket.send(msg)
