import pytest
import doctest
from unittest.mock import patch, MagicMock
from plexsearch.client import perform_search
from plexsearch.exceptions import APIError, ConfigError
from plexsearch import client, formatter, cli

def test_docstrings():
    """Test docstrings examples"""
    for module in [client, formatter, cli]:
        results = doctest.testmod(module)
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

def test_perform_search_api_error():
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        with pytest.raises(APIError):
            list(perform_search("test query", api_key="test_key", stream=False))

def test_perform_search_missing_api_key():
    with pytest.raises(ConfigError):
        list(perform_search("test query", api_key=None))

def test_format_markdown():
    from plexsearch.formatter import format_markdown
    
    input_text = "# Title\n## Section\n### Subsection\n- Point\n`code`"
    result = format_markdown(input_text)
    
    assert "**#" in result
    assert "**##" in result
    assert "**###" in result
    assert "[cyan]•[/cyan]" in result
    assert "[bold magenta]code[/bold magenta]" in result
