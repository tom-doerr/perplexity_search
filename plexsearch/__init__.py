"""
Perplexity Search - A Python tool for performing technical searches using the Perplexity API
"""

from .client import perform_search
from .cli import main
from .exceptions import PlexSearchError, APIError, ConfigError

__version__ = "0.1.4"
__all__ = ["perform_search", "main", "PlexSearchError", "APIError", "ConfigError"]
