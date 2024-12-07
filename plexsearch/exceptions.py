"""Custom exceptions for plexsearch."""

class PlexSearchError(Exception):
    """Base exception for plexsearch errors."""
    pass

class APIError(PlexSearchError):
    """Raised when the API request fails."""
    pass

class ConfigError(PlexSearchError):
    """Raised when there's a configuration error."""
    pass
