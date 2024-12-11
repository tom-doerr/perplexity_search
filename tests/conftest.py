"""Test configuration and fixtures"""
import pytest
import io
from unittest.mock import MagicMock, patch
from rich.console import Console

@pytest.fixture
def mock_terminal():
    """Mock terminal with captured output"""
    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=True)
    with patch('plexsearch.core.console', console):
        yield string_io

@pytest.fixture
def mock_response():
    """Create a mock successful API response"""
    response = MagicMock()
    response.json.return_value = {
        "choices": [
            {"message": {"content": "Test response"}}
        ]
    }
    response.status_code = 200
    return response

@pytest.fixture
def mock_error_response():
    """Create a mock error API response"""
    response = MagicMock()
    response.status_code = 400
    return response
