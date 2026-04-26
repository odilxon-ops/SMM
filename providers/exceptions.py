class ProviderError(Exception):
    """Base exception for external provider failures."""


class ProviderTimeoutError(ProviderError):
    """Raised when the external provider does not respond in time."""


class ProviderAuthError(ProviderError):
    """Raised when provider credentials are invalid or expired."""


class ProviderUnavailableError(ProviderError):
    """Raised when provider is temporarily unavailable."""


class ProviderResponseError(ProviderError):
    """Raised when provider returns an invalid or unexpected payload."""
