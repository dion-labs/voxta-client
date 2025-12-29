import asyncio
import json
import logging
from typing import Any, Callable, Optional

import requests
import websockets

from voxta_client.exceptions import VoxtaConnectionError


class VoxtaTransport:
    """
    Handles the low-level SignalR transport over WebSockets.
    """

    def __init__(self, url: str, logger: Optional[logging.Logger] = None):
        self.url = url
        self.logger = logger or logging.getLogger("VoxtaTransport")
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self._on_message_callback: Optional[Callable[[dict[str, Any]], Any]] = None
        self._on_close_callback: Optional[Callable[[], Any]] = None

    def set_callbacks(
        self,
        on_message: Callable[[dict[str, Any]], Any],
        on_close: Optional[Callable[[], Any]] = None,
    ):
        self._on_message_callback = on_message
        self._on_close_callback = on_close

    def negotiate(self) -> tuple[Optional[str], Optional[dict[str, str]]]:
        try:
            response = requests.post(f"{self.url}/hub/negotiate?negotiateVersion=1", timeout=10)
            if response.status_code != 200:
                self.logger.error(f"Failed to negotiate: {response.text}")
                return None, None

            data = response.json()
            cookies = dict(response.cookies.items())
            return data.get("connectionToken"), cookies
        except Exception as e:
            self.logger.error(f"Negotiation error: {e}")
            return None, None

    async def connect(self, connection_token: str, cookies: Optional[dict[str, str]] = None):
        ws_url = self.url.replace("http", "ws").replace("https", "wss") + "/hub"
        extra_headers = {}
        if cookies:
            cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            extra_headers["Cookie"] = cookie_header

        import urllib.parse

        encoded_token = urllib.parse.quote(connection_token)
        full_ws_url = f"{ws_url}?id={encoded_token}"

        try:
            self.websocket = await websockets.connect(full_ws_url, additional_headers=extra_headers)
            self.running = True
            self.logger.info("WebSocket connected")

            # SignalR Handshake
            await self.send({"protocol": "json", "version": 1})
            # Wait for handshake response (type 0 empty response in some SignalR versions)
            await self.websocket.recv()

            asyncio.create_task(self._read_loop())
        except Exception as e:
            self.running = False
            raise VoxtaConnectionError(f"Failed to connect to {full_ws_url}: {e}") from e

    async def send(self, payload: dict[str, Any]):
        if not self.websocket:
            self.logger.warning("Attempted to send message but WebSocket is not connected")
            return

        msg = json.dumps(payload) + "\x1e"
        try:
            await self.websocket.send(msg)
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            self.running = False

    async def _read_loop(self):
        try:
            while self.running and self.websocket:
                try:
                    message = await self.websocket.recv()
                    raw_messages = message.split("\x1e")
                    for raw_msg in raw_messages:
                        if not raw_msg.strip():
                            continue
                        try:
                            parsed = json.loads(raw_msg)
                            if self._on_message_callback:
                                if asyncio.iscoroutinefunction(self._on_message_callback):
                                    await self._on_message_callback(parsed)
                                else:
                                    self._on_message_callback(parsed)
                        except json.JSONDecodeError as e:
                            self.logger.error(f"Failed to decode SignalR message: {e}")
                except websockets.ConnectionClosed as e:
                    self.logger.info(f"WebSocket closed: {e.code} ({e.reason})")
                    break
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Error in transport read loop: {e}")
                    break
        finally:
            self.running = False
            if self._on_close_callback:
                if asyncio.iscoroutinefunction(self._on_close_callback):
                    await self._on_close_callback()
                else:
                    self._on_close_callback()

    async def close(self):
        self.running = False
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
