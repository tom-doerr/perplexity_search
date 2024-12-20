"""Unit tests for plexsearch core functionality"""
import os
import pytest
import doctest
from unittest.mock import patch, MagicMock
from plexsearch.core import perform_search
from plexsearch import core
from plexsearch.api import PerplexityAPI

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

def test_perform_search_with_citations_enabled(mock_response):
    """Test search with citations enabled"""
    with patch('requests.post') as mock_post:
        # Mock a streaming response with citations
        mock_response.iter_lines.return_value = [
            b'data: {"choices":[{"delta":{"content":"Test content"}}]}',
            b'data: {"citations":["http://test1.com", "http://test2.com"]}'
        ]
        mock_post.return_value = mock_response
        
        result = list(perform_search("test query", api_key="test_key", stream=True, show_citations=True))
        assert len(result) == 2
        assert result[0] == "Test content"
        assert "References:" in result[1]
        assert "[1] http://test1.com" in result[1]
        assert "[2] http://test2.com" in result[1]

def test_perform_search_with_citations_disabled(mock_response):
    """Test search with citations disabled"""
    with patch('requests.post') as mock_post:
        # Mock a streaming response with citations that should be ignored
        mock_response.iter_lines.return_value = [
            b'data: {"choices":[{"delta":{"content":"Test content"}}]}',
            b'data: {"citations":["http://test1.com", "http://test2.com"]}'
        ]
        mock_post.return_value = mock_response
        
        result = list(perform_search("test query", api_key="test_key", stream=True, show_citations=False))
        assert len(result) == 1
        assert result[0] == "Test content"
        assert not any("References:" in r for r in result)
        assert not any("http://test1.com" in r for r in result)

def test_build_api_payload():
    """Test API payload builder helper"""
    api = PerplexityAPI("test_key")
    payload = api._build_payload(
        query="test query",
        model="test-model",
        stream=True,
        show_citations=False
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
        with patch('plexsearch.api.PerplexityAPI.perform_search') as mock_search:
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

def test_interactive_mode_error_handling(capsys):
    """Test error handling in interactive mode"""
    from plexsearch.core import main

    with patch('sys.argv', ['plexsearch']), \
         patch('builtins.input', side_effect=['invalid query', 'exit']), \
         patch('plexsearch.api.PerplexityAPI.perform_search', side_effect=Exception("Test error")):

        main()

        captured = capsys.readouterr()
        assert "Error: Test error" in captured.out
        assert "Exiting interactive mode." in captured.out

def test_interactive_mode_context_management(capsys):
    """Test context management in interactive mode"""
    from plexsearch.core import main

    with patch('sys.argv', ['plexsearch']), \
         patch('builtins.input', side_effect=['query1', 'query2', 'exit']), \
         patch('plexsearch.api.PerplexityAPI.perform_search') as mock_search:

        mock_search.side_effect = [
            iter(['response1']),
            iter(['response2'])
        ]

        main()

        captured = capsys.readouterr()
        assert "response1" in captured.out
        assert "response2" in captured.out
        assert "Exiting interactive mode." in captured.out

def test_interactive_mode_exit_condition(capsys):
    """Test exit condition in interactive mode"""
    from plexsearch.core import main
    
    with patch('sys.argv', ['plexsearch']), \
         patch('builtins.input', side_effect=['exit']), \
         patch('plexsearch.core.perform_search') as mock_search:
        
        main()
        
        captured = capsys.readouterr()
        assert "Exiting interactive mode." in captured.out
        mock_search.assert_not_called()

@patch("plexsearch.config.Config")
def test_interactive_mode_alternating_roles_error(mock_config, capsys):
    """Test error handling for alternating roles in interactive mode"""
    from plexsearch.core import main
    
    with patch('sys.argv', ['plexsearch']), \
         patch('builtins.input', side_effect=['query1', 'query2', 'exit']), \
         patch('plexsearch.core.perform_search') as mock_search:
        
        # Simulate the API returning a 400 error due to incorrect alternating roles
        mock_search.side_effect = Exception("API request failed with status code 400: After the (optional) system message(s), user and assistant roles should be alternating.")
        
        mock_args = MagicMock()        
        mock_args.model = "llama-3.1-sonar-large-128k-online"
        mock_config.return_value.args = mock_args
        
        main()
         
        captured = capsys.readouterr()
        assert '[red]Error:[/red] API request failed with status code 400: ["At body -> model: Input should be a valid string"]' in captured.err
