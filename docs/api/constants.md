# Constants

This module contains common string constants and enums used across the Voxta ecosystem to identify event types and service capabilities.

## EventType

The `EventType` class contains string constants for all events emitted by the `VoxtaClient`. You can use these constants when registering event listeners with `client.on()`.

::: voxta_client.constants.EventType
    options:
      show_root_heading: true
      show_source: false

## ServiceType

The `ServiceType` enum defines the different types of services available in the Voxta platform, used during capability negotiation and service discovery.

::: voxta_client.constants.ServiceType
    options:
      show_root_heading: true
      show_source: false
