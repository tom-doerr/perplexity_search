"""Unit tests for plexsearch core functionality"""
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
    assert payload == {
        "model": "test-model",
        "messages": [{"role": "user", "content": "test query"}],
        "stream": True
    }

def test_perform_search_error(mock_error_response):
    """Test error handling in API search"""
    with patch('requests.post') as mock_post:
        mock_post.return_value = mock_error_response
        with pytest.raises(Exception):
            list(perform_search("test query", api_key="test_key", stream=False))
