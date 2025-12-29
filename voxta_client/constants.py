from enum import Enum


class ServiceType(str, Enum):
    TEXT_GEN = "TextGen"
    ACTION_INFERENCE = "ActionInference"
    SUMMARIZATION = "Summarization"
    TTS = "TextToSpeech"
    STT = "SpeechToText"
    AUDIO_INPUT = "AudioInput"
    AUDIO_OUTPUT = "AudioOutput"
    AUDIO_PIPELINE = "AudioPipeline"
    WAKE_WORD = "WakeWord"
    VISION_CAPTURE = "VisionCapture"
    COMPUTER_VISION = "ComputerVision"
    CHAT_AUGMENTATIONS = "ChatAugmentations"
    MEMORY = "Memory"
    IMAGE_GEN = "ImageGen"
    NONE = "None"


class EventType:
    # Server Messages (SignalR Invocation Target: ReceiveMessage)
    WELCOME = "welcome"
    CHAT_STARTED = "chatStarted"
    CHATS_SESSIONS_UPDATED = "chatsSessionsUpdated"
    MESSAGE = "message"
    UPDATE = "update"
    REPLY_GENERATING = "replyGenerating"
    REPLY_START = "replyStart"
    REPLY_CHUNK = "replyChunk"
    REPLY_END = "replyEnd"
    SPEECH_PLAYBACK_START = "speechPlaybackStart"
    SPEECH_PLAYBACK_COMPLETE = "speechPlaybackComplete"
    INTERRUPT_SPEECH = "interruptSpeech"
    ERROR = "error"
    ACTION = "action"
    CONTEXT_UPDATED = "contextUpdated"
    MEMORY_UPDATED = "memoryUpdated"
    APP_TRIGGER = "appTrigger"

    # Internal / Meta Events
    READY = "ready"
