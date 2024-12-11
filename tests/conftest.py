"""Test configuration and fixtures"""
import pytest
import io
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_terminal():
    """Mock terminal with captured output"""
    string_io = io.StringIO()
    with patch('sys.stdout', string_io):
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
