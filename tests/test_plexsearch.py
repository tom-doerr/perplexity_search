import pytest
import doctest
from unittest.mock import patch, MagicMock
from plexsearch.core import perform_search
from plexsearch import core

def test_docstrings():
    """Test docstrings examples"""
    results = doctest.testmod(core)
    assert results.failed == 0

def test_perform_search_success():
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Test response"}}
            ]
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = list(perform_search("test query", api_key="test_key", stream=False))
        assert result[0] == "Test response"
        mock_post.assert_called_once()

def test_perform_search_error():
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            list(perform_search("test query", api_key="test_key", stream=False))
            perform_search("test query", api_key="test_key")

def test_perform_search_streaming():
    """Test streaming search functionality"""
    with patch('requests.post') as mock_post:
        # Mock streaming response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'data: {"choices":[{"delta":{"content":"Python"}}]}',
            b'data: {"choices":[{"delta":{"content":" is"}}]}',
            b'data: {"choices":[{"delta":{"content":" awesome"}}]}'
        ]
        mock_post.return_value = mock_response
        
        # Collect streamed output
        result = list(perform_search("test query", api_key="test_key", stream=True))
        assert result == ["Python", " is", " awesome"]
        mock_post.assert_called_once()
