import json
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_websocket():
    """A mock websocket that simulates SignalR communication."""
    websocket = AsyncMock()
    websocket.recv = AsyncMock()
    websocket.send = AsyncMock()

    # Track messages sent by the client
    websocket.sent_messages = []

    async def track_send(msg):
        # SignalR messages end with \x1e
        if msg.endswith("\x1e"):
            websocket.sent_messages.append(json.loads(msg[:-1]))
        else:
            websocket.sent_messages.append(msg)

    websocket.send.side_effect = track_send

    return websocket


@pytest.fixture
def mock_requests():
    """A mock for the requests library used in negotiate."""
    with pytest.MonkeyPatch().context() as mp:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "connectionToken": "test_token_123",
            "connectionId": "test_connection_id",
        }
        mock_resp.cookies = {"test_cookie": "value"}

        mock_post = MagicMock(return_value=mock_resp)
        mp.setattr("requests.post", mock_post)
        yield mock_post
