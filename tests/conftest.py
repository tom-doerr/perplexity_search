"""Test configuration and fixtures"""
import pytest
from unittest.mock import MagicMock

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
