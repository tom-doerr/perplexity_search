"""Unit tests for plexsearch core functionality"""
import os
import pytest
import doctest
from unittest.mock import patch, MagicMock
from plexsearch.core import perform_search, MagicMock
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
    assert len(payload["messages"]) == 1
    assert payload["messages"][0]["role"] == "system"
    assert "technical assistant" in payload["messages"][0]["content"]

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

@patch('plexsearch.config.Config._parse_arguments')
def test_handle_search_alternating_roles_error(mock_parse_args, capsys):
    """Test error handling for alternating roles in handle_search"""
    from plexsearch.core import handle_search
    from plexsearch.config import Config

    # Create a mock config object
    mock_args = MagicMock()
    mock_args.api_key = "test_key"
    mock_args.model = "test-model"
    mock_args.citations = False
    mock_args.no_stream = False
    mock_parse_args.return_value = mock_args
    config = Config()

    # Create a context with non-alternating roles
    context = [
        {"role": "user", "content": "test"},
        {"role": "assistant", "content": "response"},
        {"role": "user", "content": "test2"},
        {"role": "user", "content": "test3"}
    ]

    with patch('plexsearch.api.PerplexityAPI.perform_search') as mock_search, \
         patch('plexsearch.core.console.print') as mock_console_print:
        mock_search.side_effect = Exception("API request failed with status code 400: After the (optional) system message(s), user and assistant roles should be alternating.")
        
        with pytest.raises(Exception) as exc_info:
            handle_search("test query", config.args, context)

        expected_error = "API request failed with status code 400: After the (optional) system message(s), user and assistant roles should be alternating."
        console_output = " ".join([str(call.args[0]) for call in mock_console_print.mock_calls])
        assert expected_error in str(exc_info.value) or expected_error in console_output

def test_handle_search_no_context(capsys):
    """Test successful handle_search call with no context."""
    from plexsearch.core import handle_search
    from plexsearch.config import Config

    # Create a mock config object
    config = Config()
    config.args.api_key = "test_key"
    config.args.model = "test-model"
    config.args.citations = False
    config.args.no_stream = False

    with patch('plexsearch.api.PerplexityAPI.perform_search') as mock_search:
        mock_search.return_value = iter(["test response"])
        result = handle_search("test query", config.args)
        assert result == "test response"
        mock_search.assert_called_once()
        assert mock_search.call_args[1]['context'] is None
        
def test_handle_search_with_context(capsys):
    """Test successful handle_search call with context."""
    from plexsearch.core import handle_search
    from plexsearch.config import Config

    # Create a mock config object
    config = Config()
    config.args.api_key = "test_key"
    config.args.model = "test-model"
    config.args.citations = False
    config.args.no_stream = False

    # Create a context
    context = [
        {"role": "user", "content": "test"},
        {"role": "assistant", "content": "response"}
    ]

    with patch('plexsearch.api.PerplexityAPI.perform_search') as mock_search:
        mock_search.return_value = iter(["test response"])
        result = handle_search("test query", config.args, context)
        assert result == "test response"
        mock_search.assert_called_once()
        assert mock_search.call_args[1]['context'] is not None
        assert len(mock_search.call_args[1]['context']) == 3
        assert mock_search.call_args[1]['context'][0]['role'] == 'system'
        assert mock_search.call_args[1]['context'][1]['role'] == 'user'
        assert mock_search.call_args[1]['context'][1]['content'] == 'test'
        assert mock_search.call_args[1]['context'][2]['role'] == 'assistant'
        assert mock_search.call_args[1]['context'][2]['content'] == 'response'

def test_log_conversation_only_new_messages():
    """Test that log_conversation appends only new messages to the log file."""
    from plexsearch.core import log_conversation
    import tempfile
    import json

    # Create a temporary log file
    with tempfile.NamedTemporaryFile(delete=False) as temp_log:
        log_file = temp_log.name

    # Initial messages to log
    initial_messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]

    # Log the initial messages
    log_conversation(log_file, initial_messages)

    # Read the log file and verify the content
    with open(log_file, "r") as f:
        logged_messages = [json.loads(line) for line in f]

    assert logged_messages == initial_messages

    # New messages to log
    new_messages = [
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"}
    ]

    # Log the new messages
    log_conversation(log_file, new_messages)

    # Read the log file again and verify the content
    with open(log_file, "r") as f:
        logged_messages = [json.loads(line) for line in f]

    # Ensure the log file contains both sets of messages without duplicates
    expected_messages = initial_messages + new_messages
    assert logged_messages == expected_messages

def test_log_conversation_no_file():
    """Test that log_conversation creates a new file if it doesn't exist."""
    from plexsearch.core import log_conversation
    import tempfile
    import json

    # Create a temporary log file
    with tempfile.NamedTemporaryFile(delete=True) as temp_log:
        log_file = temp_log.name

    # Initial messages to log
    initial_messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]

    # Log the initial messages
    log_conversation(log_file, initial_messages)

    # Read the log file and verify the content
    with open(log_file, "r") as f:
        logged_messages = [json.loads(line) for line in f]

    assert logged_messages == initial_messages

def test_log_conversation_empty_messages():
    """Test that log_conversation handles empty messages list."""
    from plexsearch.core import log_conversation
    import tempfile
    import json

    # Create a temporary log file
    with tempfile.NamedTemporaryFile(delete=False) as temp_log:
        log_file = temp_log.name

    # Log empty messages
    log_conversation(log_file, [])

    # Read the log file and verify the content
    with open(log_file, "r") as f:
        logged_messages = [json.loads(line) for line in f]

    assert logged_messages == []

def test_log_conversation_invalid_json(capsys):
    """Test that log_conversation handles invalid json."""
    from plexsearch.core import log_conversation
    import tempfile

    # Create a temporary log file
    with tempfile.NamedTemporaryFile(delete=False) as temp_log:
        log_file = temp_log.name

    # Log invalid json
    with open(log_file, "w") as f:
        f.write("invalid json\n")

    # Log new messages
    log_conversation(log_file, [{"role": "user", "content": "test"}])

    # Read the log file and verify the content
    with open(log_file, "r") as f:
        logged_messages = f.readlines()

    assert len(logged_messages) == 2
    assert logged_messages[0].strip() == "invalid json"
    assert logged_messages[1].strip() == '{"role": "user", "content": "test"}'

def test_log_conversation_file_permission_error(capsys):
    """Test that log_conversation handles file permission errors."""
    from plexsearch.core import log_conversation
    import tempfile
    import os

    # Create a temporary log file
    with tempfile.NamedTemporaryFile(delete=False) as temp_log:
        log_file = temp_log.name

    # Make the file read-only
    os.chmod(log_file, 0o444)

    # Log new messages
    log_conversation(log_file, [{"role": "user", "content": "test"}])

    # Read the log file and verify the content
    with open(log_file, "r") as f:
        logged_messages = [line.strip() for line in f]

    assert len(logged_messages) == 0

    # Reset file permissions
    os.chmod(log_file, 0o644)
