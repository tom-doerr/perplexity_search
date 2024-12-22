import pytest
import pytest
from plexsearch import __version__
from toml import load
import json
from unittest.mock import patch
from plexsearch.api import PerplexityAPI, logging

import signal
import tempfile
import os

def test_version_matches_pyproject():
    with open("pyproject.toml", "r") as f:
        pyproject = load(f)
    assert __version__ == pyproject["tool"]["poetry"]["version"]

def test_setup_signal_handler():
    from plexsearch.core import setup_signal_handler
    with patch('plexsearch.core.console.print') as mock_print:
        setup_signal_handler()
        signal.raise_signal(signal.SIGINT)
        mock_print.assert_called_with("\n[yellow]Search interrupted by user[/yellow]")

def test_write_to_markdown_file():
    from plexsearch.core import _write_to_markdown_file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        _write_to_markdown_file(temp_file.name, messages)
        
        with open(temp_file.name, 'r') as f:
            content = f.read()
        
        assert "**User**: Hello" in content
        assert "**Assistant**: Hi there" in content
        os.unlink(temp_file.name)

def test_write_to_markdown_file_error():
    from plexsearch.core import _write_to_markdown_file
    with patch('builtins.open', side_effect=IOError("Test error")), \
         patch('plexsearch.core.console.print') as mock_print:
        _write_to_markdown_file("/nonexistent/file", [{"role": "user", "content": "test"}])
        mock_print.assert_called_with("[red]Error writing to markdown file: Test error[/red]")

def test_handle_streaming_search_error():
    from plexsearch.core import handle_streaming_search
    with patch('plexsearch.api.PerplexityAPI.perform_search', side_effect=Exception("API Error")), \
         patch('plexsearch.core.console.print') as mock_print:
        args = MagicMock()
        args.api_key = "test_key"
        args.model = "test_model"
        args.citations = False
        result = handle_streaming_search("test query", args)
        assert result == ""
        mock_print.assert_called_with("[red]Error: API Error[/red]")

def test_version_matches_changelog():
    with open("CHANGELOG.md", "r") as f:
        changelog = f.read()
    assert f"## [{__version__}]" in changelog
    
def test_payload_is_correct(mock_terminal):
    """Test that the payload is correctly constructed."""
    api = PerplexityAPI(api_key="test_key")    
    
    query = "test query"
    model = "test_model"    
    stream = True
    show_citations = False
    context = [{"role": "assistant", "content": "context message"}]

    with patch("requests.post") as mock_post, \
         patch('plexsearch.api.logging') as mock_logging:
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}

        list(api.perform_search(query, model, stream, show_citations, context))

    log_output = mock_logging.debug.call_args[0][0]
    
    # Extract the payload from the log output
    payload_str = log_output.split("payload: ", 1)[1].strip()
    payload = json.loads(payload_str)

    assert payload["model"] == model
    assert payload["stream"] == stream
    assert payload["show_citations"] == show_citations
    assert len(payload["messages"]) == 3
    assert payload["messages"][0]["role"] == "system"  # System message first
    assert payload["messages"][1]["role"] == "assistant"  # Context message second 
    assert payload["messages"][1]["content"] == "context message"
    assert payload["messages"][2]["role"] == "user"  # User query last
    assert payload["messages"][2]["content"] == query
