import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
import websockets
from voxta_client.transport import VoxtaTransport
from voxta_client.audio_client import VoxtaAudioClient
from voxta_client.exceptions import VoxtaConnectionError
from voxta_client import VoxtaClient

@pytest.mark.asyncio
async def test_transport_negotiate_errors():
    transport = VoxtaTransport("http://localhost:5384")
    
    # Test 404 response
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 404
        mock_post.return_value.text = "Not Found"
        token, cookies = transport.negotiate()
        assert token is None
        assert cookies is None

    # Test exception
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("Network down")
        token, cookies = transport.negotiate()
        assert token is None
        assert cookies is None

@pytest.mark.asyncio
async def test_transport_connect_error():
    transport = VoxtaTransport("http://localhost:5384")
    with patch("websockets.connect", side_effect=Exception("Connection refused")):
        with pytest.raises(VoxtaConnectionError):
            await transport.connect("token")
    assert transport.running is False

@pytest.mark.asyncio
async def test_transport_send_not_connected():
    transport = VoxtaTransport("http://localhost:5384")
    # Should just log a warning and return
    await transport.send({"test": "data"})
    assert transport.websocket is None

@pytest.mark.asyncio
async def test_transport_send_exception(mock_websocket):
    transport = VoxtaTransport("http://localhost:5384")
    transport.websocket = mock_websocket
    transport.running = True
    
    mock_websocket.send.side_effect = Exception("Send failed")
    await transport.send({"test": "data"})
    assert transport.running is False

@pytest.mark.asyncio
async def test_transport_read_loop_sync_callback(mock_websocket):
    transport = VoxtaTransport("http://localhost:5384")
    transport.websocket = mock_websocket
    transport.running = True
    
    received = []
    def sync_callback(msg):
        received.append(msg)
        transport.running = False # Stop the loop
        
    transport.set_callbacks(on_message=sync_callback)
    
    mock_websocket.recv.return_value = json.dumps({"type": 1}) + "\x1e"
    await transport._read_loop()
    
    assert received == [{"type": 1}]

@pytest.mark.asyncio
async def test_transport_read_loop_json_error(mock_websocket):
    transport = VoxtaTransport("http://localhost:5384")
    transport.websocket = mock_websocket
    transport.running = True
    
    # Invalid JSON followed by something that stops the loop
    mock_websocket.recv.side_effect = ["invalid json\x1e", Exception("Stop")]
    
    await transport._read_loop()
    # Should not crash, just log error

@pytest.mark.asyncio
async def test_transport_close_not_connected():
    transport = VoxtaTransport("http://localhost:5384")
    await transport.close() # Should not crash
    assert transport.websocket is None

@pytest.mark.asyncio
async def test_audio_client_basic_flow(mock_websocket):
    client = VoxtaAudioClient("http://localhost:5384")
    
    with patch("websockets.connect", new_callable=AsyncMock, return_value=mock_websocket):
        mock_websocket.__aenter__.return_value = mock_websocket
        mock_websocket.recv.return_value = json.dumps({"type": 0}) + "\x1e"
        
        # Mock _read_loop to avoid background task hanging
        with patch.object(client, "_read_loop", new_callable=AsyncMock):
            await client.connect("test_token")
            assert client.running is True
            assert client.websocket is not None
            
            # Test sending audio
            await client.send_audio(b"pcmdata")
            mock_websocket.send.assert_called_with(b"pcmdata")
            
            # Test close
            await client.close()
            assert client.running is False
            mock_websocket.close.assert_called()

@pytest.mark.asyncio
async def test_audio_client_connect_failure():
    client = VoxtaAudioClient("http://localhost:5384")
    with patch("websockets.connect", side_effect=Exception("Failed")):
        with pytest.raises(Exception):
            await client.connect("token")
    assert client.running is False

@pytest.mark.asyncio
async def test_audio_client_read_loop(mock_websocket):
    client = VoxtaAudioClient("http://localhost:5384")
    client.websocket = mock_websocket
    client.running = True
    
    received_audio = []
    def on_audio(data):
        received_audio.append(data)
        client.running = False # Stop loop
        
    client.on_audio(on_audio)
    
    # Mock receiving binary data
    mock_websocket.recv.return_value = b"rawpcm"
    await client._read_loop()
    
    assert received_audio == [b"rawpcm"]

@pytest.mark.asyncio
async def test_audio_client_read_loop_text_data(mock_websocket):
    client = VoxtaAudioClient("http://localhost:5384")
    client.websocket = mock_websocket
    client.running = True
    
    # Mock receiving text data followed by something that stops loop
    mock_websocket.recv.side_effect = ["some text", Exception("Stop")]
    await client._read_loop()
    # Should just log debug and continue/stop

@pytest.mark.asyncio
async def test_audio_client_send_error(mock_websocket):
    client = VoxtaAudioClient("http://localhost:5384")
    client.websocket = mock_websocket
    client.running = True
    
    mock_websocket.send.side_effect = Exception("Failed")
    await client.send_audio(b"data")
    assert client.running is False

@pytest.mark.asyncio
async def test_client_on_direct_callback():
    client = VoxtaClient("http://localhost:5384")
    calls = []
    async def my_callback(data):
        calls.append(data)
        
    # Test passing callback directly instead of decorator
    client.on("test", my_callback)
    await client._emit("test", {"hello": "world"})
    assert calls == [{"hello": "world"}]

@pytest.mark.asyncio
async def test_client_all_event_types():
    # Just to touch all the event type handlers in _handle_server_message
    client = VoxtaClient("http://localhost:5384")
    from tests.mock_data import wrap_signalr
    
    # Test various events to trigger different branches in _handle_server_message
    events = [
        {"$type": "replyStart"},
        {"$type": "replyGenerating"},
        {"$type": "speechPlaybackStart"},
        {"$type": "speechPlaybackComplete"},
        {"$type": "interruptSpeech"},
        {"$type": "error", "message": "test"},
    ]
    for e in events:
        await client._handle_server_message(wrap_signalr(e))

@pytest.mark.asyncio
async def test_audio_client_with_cookies(mock_websocket):
    client = VoxtaAudioClient("http://localhost:5384")
    with patch("websockets.connect", new_callable=AsyncMock, return_value=mock_websocket):
        mock_websocket.__aenter__.return_value = mock_websocket
        mock_websocket.recv.return_value = json.dumps({"type": 0}) + "\x1e"
        with patch.object(client, "_read_loop", new_callable=AsyncMock):
            await client.connect("test_token", cookies={"auth": "secret"})
            # Verify cookie header was built
            args, kwargs = websockets.connect.call_args
            assert kwargs["additional_headers"]["Cookie"] == "auth=secret"

@pytest.mark.asyncio
async def test_transport_with_cookies(mock_websocket):
    transport = VoxtaTransport("http://localhost:5384")
    with patch("websockets.connect", new_callable=AsyncMock, return_value=mock_websocket):
        mock_websocket.__aenter__.return_value = mock_websocket
        mock_websocket.recv.return_value = json.dumps({"type": 0}) + "\x1e"
        with patch.object(transport, "_read_loop", new_callable=AsyncMock):
            await transport.connect("test_token", cookies={"auth": "secret"})
            # Verify cookie header was built
            args, kwargs = websockets.connect.call_args
            assert kwargs["additional_headers"]["Cookie"] == "auth=secret"

@pytest.mark.asyncio
async def test_client_missing_session_id():
    client = VoxtaClient("http://localhost:5384")
    client.session_id = None
    
    # These should all return early without calling transport.send
    with patch.object(client.transport, "send", new_callable=AsyncMock) as mock_send:
        await client.trigger_action("act")
        await client.revert()
        await client.retry()
        await client.typing_start()
        await client.typing_end()
        await client.add_chat_participant("char")
        await client.remove_chat_participant("char")
        await client.inspect_audio_input(True)
        await client.update_message("msg", "text")
        await client.delete_message("msg")
        await client.speech_playback_start()
        await client.speech_playback_complete()
        await client.character_speech_request(character_id="char")
        await client.request_suggestions()
        await client.interrupt()
        await client.pause()
        
        mock_send.assert_not_called()

@pytest.mark.asyncio
async def test_client_close():
    client = VoxtaClient("http://localhost:5384")
    with patch.object(client.transport, "close", new_callable=AsyncMock) as mock_close:
        await client.close()
        mock_close.assert_called_once()

@pytest.mark.asyncio
async def test_client_emit_sync():
    client = VoxtaClient("http://localhost:5384")
    calls = []
    def my_sync_cb(data):
        calls.append(data)
    client.on("test", my_sync_cb)
    await client._emit("test", {"foo": "bar"})
    assert calls == [{"foo": "bar"}]

@pytest.mark.asyncio
async def test_transport_read_loop_exception(mock_websocket):
    transport = VoxtaTransport("http://localhost:5384")
    transport.websocket = mock_websocket
    transport.running = True
    # Generic exception in read loop
    mock_websocket.recv.side_effect = Exception("Unknown error")
    await transport._read_loop()
    assert transport.running is False

@pytest.mark.asyncio
async def test_transport_read_loop_closed(mock_websocket):
    transport = VoxtaTransport("http://localhost:5384")
    transport.websocket = mock_websocket
    transport.running = True
    
    # Simple way to mock ConnectionClosed
    from websockets.exceptions import ConnectionClosedOK
    mock_websocket.recv.side_effect = ConnectionClosedOK(None, None)
    
    await transport._read_loop()
    assert transport.running is False

@pytest.mark.asyncio
async def test_audio_client_read_loop_closed(mock_websocket):
    client = VoxtaAudioClient("http://localhost:5384")
    client.websocket = mock_websocket
    client.running = True
    
    from websockets.exceptions import ConnectionClosedOK
    mock_websocket.recv.side_effect = ConnectionClosedOK(None, None)
    
    await client._read_loop()
    assert client.running is False

@pytest.mark.asyncio
async def test_transport_read_loop_sync_close(mock_websocket):
    transport = VoxtaTransport("http://localhost:5384")
    transport.websocket = mock_websocket
    transport.running = False # Already false to finish loop immediately
    
    calls = []
    def on_close():
        calls.append(True)
    transport.set_callbacks(on_message=MagicMock(), on_close=on_close)
    
    await transport._read_loop()
    assert calls == [True]
