# Protocol Support Matrix

This client implements the Voxta SignalR protocol. Below is the current support status compared to the full server capabilities.

| Category | Feature | Protocol Method | Status |
| :--- | :--- | :--- | :--- |
| **Core** | Authentication | `authenticate` | ✅ Supported |
| | App Registration | `registerApp` | ✅ Supported |
| | Chat Subscription | `subscribeToChat` | ✅ Supported |
| **Messaging** | Start Chat | `startChat` | ✅ Supported |
| | Resume Chat | `resumeChat` | ✅ Supported |
| | Send Message | `send` | ✅ Supported |
| | Character Speech Req | `characterSpeechRequest` | ✅ Supported |
| **Control** | Interrupt | `interrupt` | ✅ Supported |
| | Pause | `pause` | ✅ Supported |
| | Inspect Session | `inspect` | ✅ Supported |
| **Context** | Update Context | `updateContext` | ✅ Supported |
| | Actions/Events | `updateContext` | ✅ Supported |
| | Role Management | `enableRoles` | ✅ Supported |
| **Media** | Playback Sync | `speechPlaybackStart/Complete` | ✅ Supported |
| | Audio Streaming | `WebSocketStream` (PCM) | ❌ Not Planned |
| | Vision / Images | `visionCapture` | ❌ Not Planned |

