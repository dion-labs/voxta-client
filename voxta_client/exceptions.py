class VoxtaError(Exception):
    """Base exception for all Voxta client errors."""

    pass


class VoxtaConnectionError(VoxtaError):
    """Raised when the connection to the Voxta server fails."""

    pass


class VoxtaAuthError(VoxtaError):
    """Raised when authentication with the Voxta server fails."""

    pass


class VoxtaProtocolError(VoxtaError):
    """Raised when a SignalR or Voxta protocol violation occurs."""

    pass
