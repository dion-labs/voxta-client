# VoxtaAudioClient

The `VoxtaAudioClient` is a specialized client designed for high-throughput, low-latency binary audio streaming. While the main `VoxtaClient` handles text and control messages, the `VoxtaAudioClient` establishes a dedicated WebSocket for raw PCM data.

!!! note "Typical Use Case"
    You would use this client if you are building a voice-to-voice application where you need to stream the user's microphone to Voxta (STT) and receive the character's voice as a stream (TTS).

::: voxta_client.audio_client.VoxtaAudioClient
    options:
      show_root_heading: false
      members:
        - __init__
        - connect
        - send_audio
        - on_audio
        - close
        - running

## Audio Format

Currently, the audio client expects and delivers:

- **Format**: Raw PCM
- **Sample Rate**: Depends on server configuration (typically 16kHz or 24kHz)
- **Channels**: Mono
- **Bit Depth**: 16-bit signed integer

## Implementation Example

```python
audio_client = VoxtaAudioClient("http://localhost:5384")

# Handle incoming audio from the AI
@audio_client.on_audio
def handle_tts(pcm_data):
    # Play the data via sounddevice or save to a buffer
    pass

# Start connection (requires token from VoxtaClient.negotiate)
await audio_client.connect(token)

# Send user voice data
await audio_client.send_audio(microphone_bytes)
```




