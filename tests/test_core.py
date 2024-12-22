import pytest
import pytest
from plexsearch import __version__
from toml import load
import json
from unittest.mock import patch, MagicMock
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
        mock_print.assert_called_with("\n[yellow]Search interrupted by user. Press Ctrl-D to exit[/yellow]")

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
        with pytest.raises(Exception, match="API Error"):
            handle_streaming_search("test query", args)
        mock_print.assert_called_with("[red]Error: API Error[/red]")

def test_version_matches_changelog():
    with open("CHANGELOG.md", "r") as f:
        changelog = f.read()
    assert f"## [{__version__}]" in changelog
    
import pytest
from unittest.mock import patch, MagicMock
from plexsearch.core import handle_no_stream_search, handle_streaming_search, log_conversation, _write_to_markdown_file, _format_message_to_markdown, handle_search
from plexsearch.api import PerplexityAPI
import tempfile
import json
import os
import subprocess

def test_handle_no_stream_search(capsys):
    with patch('plexsearch.core.clear_new_area'), \
         patch('plexsearch.core.PerplexityAPI.perform_search', return_value=["Test response"]):
        args = MagicMock()
        args.api_key = "test_key"
        args.model = "test_model"
        args.citations = False
        content = handle_no_stream_search("test query", args)
        assert content == "Test response"

def test_handle_streaming_search():
    with patch('plexsearch.core.PerplexityAPI.perform_search', return_value=["Hello", " World"]):
        args = MagicMock()
        args.api_key = "test_key"
        args.model = "test_model"
        args.citations = False
        content = handle_streaming_search("test query", args)
        assert content == "Hello World"

def test_log_conversation_append():
    with tempfile.NamedTemporaryFile(delete=False) as temp_log:
        log_file = temp_log.name
    
    messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]
    log_conversation(log_file, messages)
    
    with open(log_file, "r") as f:
        logged = [json.loads(line) for line in f]
    assert logged == messages
    os.unlink(log_file)

def test_log_conversation_file_write_error():
    with patch('plexsearch.core.open', side_effect=PermissionError("No permission")), \
         patch('plexsearch.core.console.print') as mock_print:
        log_conversation("dummy_log_file", [{"role": "user", "content": "Test"}])
        mock_print.assert_called_with("[red]Error writing to log file: No permission[/red]")

def test_format_message_to_markdown():
    message = {"role": "user", "content": "Hello"}
    markdown = _format_message_to_markdown(message)
    assert markdown == "**User**: Hello\n\n"

def test_write_to_markdown_file(tmp_path):
    messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}]
    markdown_file = tmp_path / "conversation.md"
    _write_to_markdown_file(str(markdown_file), messages)
    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()
    expected = "**User**: Hello\n\n**Assistant**: Hi!\n\n"
    assert content == expected

def test_write_to_markdown_file_write_error():
    with patch('plexsearch.core.open', side_effect=IOError("Write error")), \
         patch('plexsearch.core.console.print') as mock_print:
        _write_to_markdown_file("dummy_markdown.md", [{"role": "user", "content": "Test"}])
        mock_print.assert_called_with("[red]Error writing to markdown file: Write error[/red]")


def test_handle_no_stream_search_api_exception(capsys):
    with patch('plexsearch.core.clear_new_area'), \
         patch('plexsearch.core.PerplexityAPI.perform_search', side_effect=Exception("API error")), \
         patch('plexsearch.core.console.print') as mock_print:
        args = MagicMock()
        args.api_key = "test_key"
        args.model = "test_model"
        args.citations = False
        content = handle_no_stream_search("test query", args)
        assert content == ""
        mock_print.assert_called_with("[red]Error: API error[/red]")

def test_handle_streaming_search_api_exception():
    with patch('plexsearch.core.PerplexityAPI.perform_search', side_effect=Exception("API streaming error")), \
         patch('plexsearch.core.console.print') as mock_print:
        args = MagicMock()
        args.api_key = "test_key"
        args.model = "test_model"
        args.citations = False
        with pytest.raises(Exception, match="API streaming error"), \
             patch('plexsearch.core.console.print') as mock_print:
            handle_streaming_search("test query", args)
        mock_print.assert_called_with("[red]Error: API streaming error[/red]")


def test_handle_search_no_context():
    from plexsearch.core import handle_search    
    with patch('plexsearch.api.PerplexityAPI.perform_search', return_value=["Test response"]):
        args = MagicMock()
        args.no_stream = False
        result = handle_search("test query", args)
        assert result == "Test response"
def test_handle_search_with_context():
    from plexsearch.core import handle_search
    from plexsearch.config import Config
    from unittest.mock import patch, MagicMock
    
    with patch('plexsearch.config.Config._parse_arguments') as mock_parse_args, \
         patch('plexsearch.api.PerplexityAPI.perform_search', return_value=["Test response"]):
        mock_args = MagicMock()
        mock_args.api_key = "test_key"
        mock_args.model = "test_model"
        mock_args.citations = False
        mock_args.no_stream = False
        mock_parse_args.return_value = mock_args
        config = Config()
        
        context = [
            {"role": "user", "content": "test"},
            {"role": "assistant", "content": "response"}
        ]
        
        result = handle_search("test query", config.args, context)
        assert result == "Test response"
        # Verify perform_search was called with extended context

def test_setup_signal_handler():
    from plexsearch.core import setup_signal_handler
    import signal
    from unittest.mock import patch

    with patch('plexsearch.core.console.print') as mock_print:
        setup_signal_handler()
        # Simulate SIGINT signal
        signal.raise_signal(signal.SIGINT)
        mock_print.assert_called_with("\n[yellow]Search interrupted by user. Press Ctrl-D to exit[/yellow]")
import pytest
from plexsearch.config import Config
from unittest.mock import patch
import argparse

def test_invalid_model():
    with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        query=None,
        api_key=None,
        model="invalid-model",
        no_stream=False,
        citations=False,
        log_file=None,
        markdown_file=None,
        debug=False
    )):
        with pytest.raises(ValueError) as exc_info:
            config = Config()
            _ = config.model
        assert "Invalid model: invalid-model" in str(exc_info.value)
