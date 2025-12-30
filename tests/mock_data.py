"""
Mock data for VoxtaClient tests, extracted from real server logs.
"""

# SignalR handshake response (mocked, as logs usually don't show the initial protocol exchange)
HANDSHAKE_RESPONSE = {"type": 0}  # SignalR type 0 is often used for handshake ack

# welcome event - received after authentication
WELCOME_EVENT = {
    "$type": "welcome",
    "assistant": {
        "id": "06c2046c-86d0-4e73-d5d8-0595022eb74d",
        "name": "Apex",
    },
    "user": {
        "id": "a8e8ce68-72e5-a9fa-871a-7c124ccb1054",
        "name": "User",
    },
}

# chatStarted event
CHAT_STARTED_EVENT = {
    "$type": "chatStarted",
    "sessionId": "916f4059-1e81-983a-cb04-489176bcc680",
    "chatId": "chat_12345",
    "characters": [
        {
            "id": "06c2046c-86d0-4e73-d5d8-0595022eb74d",
            "name": "Apex",
        }
    ],
}

# update event (e.g. user message)
UPDATE_EVENT = {
    "$type": "update",
    "messageId": "37290ad4-0d0f-491b-854c-9200df65be95",
    "senderId": "a8e8ce68-72e5-a9fa-871a-7c124ccb1054",
    "text": "heh we have a long list of priorities, now its 3d avatars turn",
    "tokens": 0,
    "index": 5,
    "conversationIndex": 5,
    "chatTime": 2599170,
    "role": "User",
    "timestamp": "2025-12-29T11:04:42.7828357+00:00",
    "sessionId": "916f4059-1e81-983a-cb04-489176bcc680",
}

# replyGenerating event
REPLY_GENERATING_EVENT = {
    "$type": "replyGenerating",
    "messageId": "5d33a8b2-766f-4b3f-b0f1-7c2b1d8a3111",
    "senderId": "06c2046c-86d0-4e73-d5d8-0595022eb74d",
    "role": "Assistant",
    "isNarration": False,
    "sessionId": "916f4059-1e81-983a-cb04-489176bcc680",
}

# replyStart event
REPLY_START_EVENT = {
    "$type": "replyStart",
    "messageId": "5d33a8b2-766f-4b3f-b0f1-7c2b1d8a3111",
    "senderId": "06c2046c-86d0-4e73-d5d8-0595022eb74d",
    "chatTime": 2614885,
    "sessionId": "916f4059-1e81-983a-cb04-489176bcc680",
}

# replyChunk event
REPLY_CHUNK_EVENT = {
    "$type": "replyChunk",
    "messageId": "5d33a8b2-766f-4b3f-b0f1-7c2b1d8a3111",
    "senderId": "06c2046c-86d0-4e73-d5d8-0595022eb74d",
    "startIndex": 0,
    "endIndex": 14,
    "text": "Oh absolutely.",
    "audioUrl": "",
    "isNarration": False,
    "sessionId": "916f4059-1e81-983a-cb04-489176bcc680",
}

# speechPlaybackStart event
SPEECH_PLAYBACK_START_EVENT = {
    "$type": "speechPlaybackStart",
    "messageId": "5d33a8b2-766f-4b3f-b0f1-7c2b1d8a3111",
    "startIndex": 0,
    "duration": 0,
    "sessionId": "916f4059-1e81-983a-cb04-489176bcc680",
}

# replyEnd event
REPLY_END_EVENT = {
    "$type": "replyEnd",
    "messageId": "5d33a8b2-766f-4b3f-b0f1-7c2b1d8a3111",
    "senderId": "06c2046c-86d0-4e73-d5d8-0595022eb74d",
    "tokens": 25,
    "messageIndex": 6,
    "conversationIndex": 6,
    "sessionId": "916f4059-1e81-983a-cb04-489176bcc680",
}

# action event
ACTION_EVENT = {
    "$type": "action",
    "contextKey": "_scenario",
    "layer": "emotes",
    "value": "play_neutral_emote",
    "role": "Assistant",
    "senderId": "06c2046c-86d0-4e73-d5d8-0595022eb74d",
    "sessionId": "916f4059-1e81-983a-cb04-489176bcc680",
}

# speechPlaybackComplete event
SPEECH_PLAYBACK_COMPLETE_EVENT = {
    "$type": "speechPlaybackComplete",
    "messageId": "5d33a8b2-766f-4b3f-b0f1-7c2b1d8a3111",
    "sessionId": "916f4059-1e81-983a-cb04-489176bcc680",
}

# interruptSpeech event
INTERRUPT_SPEECH_EVENT = {
    "$type": "interruptSpeech",
    "sessionId": "916f4059-1e81-983a-cb04-489176bcc680",
}

# error event
ERROR_EVENT = {"$type": "error", "message": "Chat session already exists"}

# chatsSessionsUpdated event
CHATS_SESSIONS_UPDATED_EVENT = {
    "$type": "chatsSessionsUpdated",
    "sessions": [
        {
            "sessionId": "916f4059-1e81-983a-cb04-489176bcc680",
            "chatId": "00000000-0000-0000-0000-000000000000",
            "user": {"id": "a8e8ce68-72e5-a9fa-871a-7c124ccb1054", "name": "D"},
            "characters": [{"id": "06c2046c-86d0-4e73-d5d8-0595022eb74d", "name": "Apex"}],
        }
    ],
}


# Wrap in SignalR type 1 message structure
def wrap_signalr(payload):
    return {"type": 1, "target": "ReceiveMessage", "arguments": [payload]}
