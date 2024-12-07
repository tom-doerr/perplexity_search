"""Core functionality for plexsearch."""
from .client import perform_search
from .cli import main

__all__ = ["perform_search", "main"]
