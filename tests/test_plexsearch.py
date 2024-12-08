"""Unit tests for plexsearch core functionality"""
import os
import pytest
import doctest
from unittest.mock import patch
from plexsearch.core import perform_search
from plexsearch import core

def test_docstrings():
    """Test docstrings examples"""
    results = doctest.testmod(core)
    assert results.failed == 0

def test_perform_search_success(mock_response):
    """Test successful API search"""
    with patch('requests.post') as mock_post:
        mock_post.return_value = mock_response
        result = list(perform_search("test query", api_key="test_key", stream=False))
        assert result[0] == "Test response"
        mock_post.assert_called_once()

def test_build_api_payload():
    """Test API payload builder helper"""
    payload = core._build_api_payload(
        query="test query",
        model="test-model",
        stream=True
    )
    # Verify the basic structure and content
    assert payload["model"] == "test-model"
    assert payload["stream"] is True
    assert len(payload["messages"]) == 2
    assert payload["messages"][0]["role"] == "system"
    assert "technical assistant" in payload["messages"][0]["content"]
    assert payload["messages"][1] == {"role": "user", "content": "test query"}

@patch.dict(os.environ, {'OR_APP_NAME': 'Aider'})
def test_no_stream_in_aider():
    """Test that streaming is disabled when running in Aider"""
    with patch('sys.argv', ['plexsearch', 'test query']):
        with patch('plexsearch.core.perform_search') as mock_search:
            mock_search.return_value = iter(['test response'])
            with patch('builtins.print'):  # Suppress actual printing
                core.main()
                # Verify perform_search was called with stream=False
                mock_search.assert_called_once()
                assert mock_search.call_args[1]['stream'] is False

def test_perform_search_error(mock_error_response):
    """Test error handling in API search"""
    with patch('requests.post') as mock_post:
        # Test authentication error
        mock_error_response.status_code = 401
        mock_post.return_value = mock_error_response
        with pytest.raises(Exception) as exc_info:
            list(perform_search("test query", api_key="test_key", stream=False))
        assert "Authentication failed" in str(exc_info.value)
        
        # Test rate limit error
        mock_error_response.status_code = 429
        mock_post.return_value = mock_error_response
        with pytest.raises(Exception) as exc_info:
            list(perform_search("test query", api_key="test_key", stream=False))
        assert "Rate limit exceeded" in str(exc_info.value)
