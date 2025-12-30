import asyncio
import logging
import json
import websockets
from typing import Optional, Callable


import uuid
import asyncio
import logging
import json
import websockets
from typing import Optional, Callable, Any


class VoxtaAudioClient:
    """
    Dedicated client for handling binary PCM audio streaming to/from Voxta.
    """

    def __init__(self, url: str, logger: Optional[logging.Logger] = None):
        self.url = url
        self.logger = logger or logging.getLogger("VoxtaAudioClient")
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self._on_audio_data: Optional[Callable[[bytes], None]] = None

    async def connect(self, connection_token: str, cookies: Optional[dict[str, str]] = None):
        """
        Connect to the audio stream WebSocket and authenticate.
        """
        import urllib.parse
        
        ws_url = self.url.replace("http", "ws").replace("https", "wss")
        encoded_token = urllib.parse.quote(connection_token)
        full_ws_url = f"{ws_url}/hub?id={encoded_token}"

        extra_headers = {}
        if cookies:
            cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            extra_headers["Cookie"] = cookie_header

        self.logger.info(f"Connecting to audio client: {full_ws_url}")
        try:
            self.websocket = await websockets.connect(
                full_ws_url, 
                additional_headers=extra_headers
            )
            
            # 1. SignalR Handshake
            await self.websocket.send(json.dumps({"protocol": "json", "version": 1}) + "\x1e")
            handshake_resp = await self.websocket.recv()
            self.logger.info(f"Audio client handshake complete: {handshake_resp}")

            # 2. Authenticate with audio capabilities
            # This specific connection is for audio streaming
            auth_msg = {
                "type": 1,
                "invocationId": str(uuid.uuid4()),
                "target": "SendMessage",
                "arguments": [{
                    "$type": "authenticate",
                    "client": "Voxta.AudioClient.Python",
                    "clientVersion": "1.2.1",
                    "scope": ["role:app"],
                    "capabilities": {
                        "audioInput": "WebSocketStream",
                        "audioOutput": "WebSocketStream",
                        "acceptedAudioContentTypes": ["audio/pcm"]
                    }
                }]
            }
            await self.websocket.send(json.dumps(auth_msg) + "\x1e")
            self.logger.info("Audio client authentication sent")

            self.running = True
            asyncio.create_task(self._read_loop())
        except Exception as e:
            self.running = False
            self.logger.error(f"Failed to connect to audio client: {e}")
            raise

    def on_audio(self, callback: Callable[[bytes], None]):
        self._on_audio_data = callback

    async def send_audio(self, pcm_data: bytes):
        """
        Send binary PCM data to the server.
        """
        if self.websocket and self.running:
            try:
                await self.websocket.send(pcm_data)
            except Exception as e:
                self.logger.error(f"Failed to send audio data: {e}")
                self.running = False

    async def _read_loop(self):
        try:
            while self.running and self.websocket:
                data = await self.websocket.recv()
                if isinstance(data, bytes):
                    if self._on_audio_data:
                        self._on_audio_data(data)
                else:
                    self.logger.debug(f"Received non-binary data on audio stream: {data}")
        except websockets.ConnectionClosed:
            self.logger.info("Audio stream closed")
        except Exception as e:
            self.logger.error(f"Error in audio stream read loop: {e}")
        finally:
            self.running = False

    async def close(self):
        self.running = False
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

