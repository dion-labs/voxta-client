# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-12-30

### Added
- **`VoxtaAudioClient`**: A dedicated client for handling raw binary PCM audio streaming (16-bit, 16kHz).
- Support for `WebSocketStream` audio input and output capabilities.
- New `audio_client.py` module for decoupled audio connection management.
- `stop_chat` method to `VoxtaClient`.
- Enhanced `deploy.sh` with clean git status check and automatic documentation versioning.
- Support for minor version releases in `deploy.sh`.

### Changed
- Refactored `VoxtaClient` to be fully vanilla and "audio-unaware" by default, improving modularity.
- `VoxtaClient.connect` and `authenticate` now use default capabilities unless explicitly extended.
- Improved test coverage for `action`, `interruptSpeech`, `appTrigger`, and `replyGenerating` events.

## [0.1.6] - 2025-12-30

### Fixed
- Protocol alignment for `pauseChat` (previously `pause`).
- Updated `ClientPauseMessage` to include required `pause` (bool) and `sessionId` fields.
- Added `ClientStopChatMessage` for completeness.
- Added `stop_chat` method to `VoxtaClient`.
- Improved test coverage for `action`, `interruptSpeech`, `appTrigger`, and `replyGenerating` events.

## [0.1.5] - 2025-12-30

### Added
- Comprehensive `PYTHON_DEVELOPMENT_GUIDE.md` covering architecture, connection flows, and protocol details.
- `client_send` event emitted for all outgoing SignalR messages to improve debugging.
- New dataclass-based message models in `voxta_client.models` for all protocol actions.

### Changed
- **Stateless Refactor**: Removed internal tracking of `assistant_id`, `chat_id`, and `characters` from the client. These are now expected to be managed by the application layer.
- Updated `character_speech_request` to require a `character_id` and support the mandatory `text` field.
- Centralized all outgoing traffic through `_send_raw` for consistent event emission.
- Refined `_handle_sessions_updated` and `_handle_chat_started` to focus only on protocol-level session pinning.
- Updated test suite to align with the stateless architecture.

### Fixed
- Stale character ID issues by removing default ID caching in the client.
- Protocol mismatch in `character_speech_request` where the server expected a `text` property.
- Improved SignalR message delimiting and parsing robustness.

## [0.1.4] - 2025-12-20
- Initial beta release with basic SignalR support.
- Support for chat starting, resuming, and messaging.
- Event-driven callback system.

