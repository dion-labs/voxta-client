# Constants

This module contains common string constants and enums used across the Voxta ecosystem. Using these constants is recommended to avoid typos in event listeners.

## EventType

The `EventType` class contains string constants for all events emitted by the `VoxtaClient`. 

!!! tip "Usage"
    ```python
    from voxta_client.constants import EventType
    
    @client.on(EventType.MESSAGE)
    def handle_msg(payload):
        ...
    ```

::: voxta_client.constants.EventType
    options:
      show_root_heading: false

---

## ServiceType

The `ServiceType` enum defines the different types of services available in the Voxta platform (e.g., STT, TTS, LLM). These are used during capability negotiation.

::: voxta_client.constants.ServiceType
    options:
      show_root_heading: false
