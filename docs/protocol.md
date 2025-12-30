# Protocol Support Matrix

This client implements the Voxta SignalR protocol. Below is the current support status compared to the full server capabilities.

| Category | Feature | Protocol Method | Status |
| :--- | :--- | :--- | :--- |
| **Core** | Authentication | `authenticate` | ✅ Supported |
| | App Registration | `registerApp` | ✅ Supported |
| | Chat Subscription | `subscribeToChat` | ✅ Supported |
| **Messaging** | Start Chat | `startChat` | ✅ Supported |
| | Resume Chat | `resumeChat` | ✅ Supported |
| | Stop Chat | `stopChat` | ✅ Supported |
| | Send Message | `send` | ✅ Supported |
| | Character Speech Req | `characterSpeechRequest` | ✅ Supported |
| **Control** | Interrupt | `interrupt` | ✅ Supported |
| | Pause | `pause` | ✅ Supported |
| | Inspect Session | `inspect` | ✅ Supported |
| **Advanced** | Send Secret | `sendSecret` | ❌ Planned |
| | Send Note | `sendNote` | ❌ Planned |
| | Send Instructions | `sendInstructions` | ❌ Planned |
| | Trigger Reply | `triggerReply` | ❌ Planned |
| | Request User Action | `requestUserAction` | ❌ Planned |
| | Load Chat | `loadChat` | ❌ Planned |
| | Delete Chat | `deleteChat` | ❌ Planned |
| | Update Message | `updateMessage` | ❌ Planned |
| | Delete Message | `deleteMessage` | ❌ Planned |
| **Context** | Update Context | `updateContext` | ✅ Supported |
| | Actions/Events | `updateContext` | ✅ Supported |
| | Role Management | `enableRoles` | ✅ Supported |
| **Media** | Playback Sync | `speechPlaybackStart/Complete` | ✅ Supported |
| | Audio Streaming | `WebSocketStream` (PCM) | ✅ Supported (via `VoxtaAudioClient`) |
| | Vision / Images | `visionCapture` | ❌ Not Planned |

