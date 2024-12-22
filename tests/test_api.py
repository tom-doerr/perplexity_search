import pytest
from unittest.mock import patch, MagicMock
from plexsearch.api import PerplexityAPI, APIError, AuthenticationError
import json
import os

def test_get_headers():
    api = PerplexityAPI(api_key="test_key")
    headers = api._get_headers()
    assert headers == {
        "Authorization": "Bearer test_key",
        "Content-Type": "application/json"
    }

def test_build_payload_no_context():
    api = PerplexityAPI(api_key="test_key")
    payload = api._build_payload(
        query="test query",
        model="test-model",
        stream=True,
        show_citations=False
    )
    assert payload["model"] == "test-model"
    assert payload["stream"] is True
    assert payload["show_citations"] is False
    assert len(payload["messages"]) == 2
    assert payload["messages"][0]["role"] == "system"
    assert "technical assistant" in payload["messages"][0]["content"]
    assert payload["messages"][1]["role"] == "user"
    assert payload["messages"][1]["content"] == "test query"

def test_build_payload_with_context():
    api = PerplexityAPI(api_key="test_key")
    context = [
        {"role": "user", "content": "previous user message"},
        {"role": "assistant", "content": "previous assistant message"}
    ]
    payload = api._build_payload(
        query="new query",
        model="test-model",
        stream=False,
        show_citations=True,
        context=context
    )
    assert len(payload["messages"]) == 4
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"
    assert payload["messages"][1]["content"] == "previous user message"
    assert payload["messages"][2]["role"] == "assistant"
    assert payload["messages"][2]["content"] == "previous assistant message"
    assert payload["messages"][3]["role"] == "user"
    assert payload["messages"][3]["content"] == "new query"

def test_handle_error_authentication_error():
    api = PerplexityAPI(api_key="invalid_key")
    mock_response = MagicMock()
    mock_response.status_code = 401
    with pytest.raises(AuthenticationError) as exc_info:
        api._handle_error(mock_response)
    assert "Authentication failed" in str(exc_info.value)

def test_handle_error_rate_limit_error():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.status_code = 429
    with pytest.raises(APIError) as exc_info:
        api._handle_error(mock_response)
    assert "Rate limit exceeded" in str(exc_info.value)

def test_handle_error_server_error():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.status_code = 500
    with pytest.raises(APIError) as exc_info:
        api._handle_error(mock_response)
    assert "Perplexity API server error" in str(exc_info.value)

def test_handle_error_other_error():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": {"message": "Not Found"}}
    with pytest.raises(APIError) as exc_info:
        api._handle_error(mock_response)
    assert "API request failed with status code 404: Not Found" in str(exc_info.value)

def test_handle_error_non_json_response():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    with pytest.raises(APIError) as exc_info:
        api._handle_error(mock_response)
    assert "API request failed with status code 400" in str(exc_info.value)



def test_perform_search_stream_false():
    api = PerplexityAPI(api_key="test_key")
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "citations": ["http://test.com"]
        }
        mock_post.return_value = mock_response
        response = list(api.perform_search("test", "test-model", stream=False, show_citations=True))
        assert response == ["Test response\n\nReferences:\n[1] http://test.com"]

def test_perform_search_stream_true():
    api = PerplexityAPI(api_key="test_key")
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}',
            b'data: {"choices":[{"delta":{"content":" World"}}], "citations": ["http://test.com"]}'
        ]
        mock_post.return_value = mock_response
        response = list(api.perform_search("test", "test-model", stream=True, show_citations=True))
        assert response == ["Hello", " World", "\n\nReferences:\n[1] http://test.com"]


def test_get_headers():
    api = PerplexityAPI(api_key="test_key")
    headers = api._get_headers()
    assert headers == {
        "Authorization": "Bearer test_key",
        "Content-Type": "application/json"
    }

def test_build_payload_no_context():
    api = PerplexityAPI(api_key="test_key")
    payload = api._build_payload(
        query="test query",
        model="test-model",
        stream=True,
        show_citations=False
    )
    assert payload["model"] == "test-model"
    assert payload["stream"] is True
    assert payload["show_citations"] is False
    assert len(payload["messages"]) == 2
    assert payload["messages"][0]["role"] == "system"
    assert "technical assistant" in payload["messages"][0]["content"]
    assert payload["messages"][1]["role"] == "user"
    assert payload["messages"][1]["content"] == "test query"

def test_build_payload_with_context():
    api = PerplexityAPI(api_key="test_key")
    context = [
        {"role": "user", "content": "previous user message"},
        {"role": "assistant", "content": "previous assistant message"}
    ]
    payload = api._build_payload(
        query="new query",
        model="test-model",
        stream=False,
        show_citations=True,
        context=context
    )
    assert len(payload["messages"]) == 4
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"
    assert payload["messages"][1]["content"] == "previous user message"
    assert payload["messages"][2]["role"] == "assistant"
    assert payload["messages"][2]["content"] == "previous assistant message"
    assert payload["messages"][3]["role"] == "user"
    assert payload["messages"][3]["content"] == "new query"

def test_handle_error_authentication_error():
    api = PerplexityAPI(api_key="invalid_key")
    mock_response = MagicMock()
    mock_response.status_code = 401
    with pytest.raises(AuthenticationError) as exc_info:
        api._handle_error(mock_response)
    assert "Authentication failed" in str(exc_info.value)

def test_handle_error_rate_limit_error():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.status_code = 429
    with pytest.raises(APIError) as exc_info:
        api._handle_error(mock_response)
    assert "Rate limit exceeded" in str(exc_info.value)

def test_handle_error_server_error():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.status_code = 500
    with pytest.raises(APIError) as exc_info:
        api._handle_error(mock_response)
    assert "Perplexity API server error" in str(exc_info.value)

def test_handle_error_other_error():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": {"message": "Not Found"}}
    with pytest.raises(APIError) as exc_info:
        api._handle_error(mock_response)
    assert "API request failed with status code 404: Not Found" in str(exc_info.value)

def test_handle_error_non_json_response():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    with pytest.raises(APIError) as exc_info:
        api._handle_error(mock_response)
    assert "API request failed with status code 400" in str(exc_info.value)

def test_format_citations():
    api = PerplexityAPI(api_key="test_key")
    citations = ["http://test1.com", "http://test2.com"]
    formatted = api._format_citations(citations)
    expected = "\n\nReferences:\n[1] http://test1.com\n[2] http://test2.com"
    assert formatted == expected

def test_handle_stream_response():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = [
        b'data: {"choices":[{"delta":{"content":"Hello"}}]}',
        b'data: {"choices":[{"delta":{"content":" World"}}], "citations": ["http://test.com"]}'
    ]
    generator = api._handle_stream_response(mock_response, show_citations=True)
    output = list(generator)
    assert output == ["Hello", " World", "\n\nReferences:\n[1] http://test.com"]
    assert output[2] == "\n\nReferences:\n[1] http://test.com"

def test_handle_stream_response_empty():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = []
    generator = api._handle_stream_response(mock_response, show_citations=True)
    output = list(generator)
    assert output == []

def test_perform_search_stream_false():
    api = PerplexityAPI(api_key="test_key")
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "citations": ["http://test.com"]
        }
        mock_post.return_value = mock_response
        response = list(api.perform_search("test", "test-model", stream=False, show_citations=True))
        assert response == ["Test response\n\nReferences:\n[1] http://test.com"]

def test_perform_search_stream_true():
    api = PerplexityAPI(api_key="test_key")
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}',
            b'data: {"choices":[{"delta":{"content":" World"}}], "citations": ["http://test.com"]}'
        ]
        mock_post.return_value = mock_response
        response = list(api.perform_search("test", "test-model", stream=True, show_citations=True))
        assert response == ["Hello", " World", "\n\nReferences:\n[1] http://test.com"]
def test_format_citations():
    api = PerplexityAPI(api_key="test_key")
    citations = ["http://test1.com", "http://test2.com"]
    formatted = api._format_citations(citations)
    expected = "\n\nReferences:\n[1] http://test1.com\n[2] http://test2.com"
    assert formatted == expected
def test_handle_stream_response_empty():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = []
    generator = api._handle_stream_response(mock_response, show_citations=True)
    output = list(generator)
    assert output == []
def test_format_citations():
    api = PerplexityAPI(api_key="test_key")
    citations = ["http://test1.com", "http://test2.com"]
    formatted = api._format_citations(citations)
    expected = "\n\nReferences:\n[1] http://test1.com\n[2] http://test2.com"
    assert formatted == expected

def test_missing_api_key():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            api = PerplexityAPI()
        assert "API key required" in str(exc_info.value)

def test_handle_search_with_malformed_context():
    from plexsearch.core import handle_search
    from plexsearch.config import Config
    
    mock_args = MagicMock()
    mock_args.api_key = "test_key"
    mock_args.model = "test-model"
    mock_args.citations = False
    mock_args.no_stream = False
    
    with patch('sys.argv', ['plexsearch']):
        config = Config()
    config.args = mock_args
    
    malformed_context = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant"}  # Missing 'content'
    ]
    
    with patch('plexsearch.api.PerplexityAPI.perform_search') as mock_search:
        mock_search.return_value = iter(["Hello", " World"])
        content = handle_search("test query", config.args, malformed_context)
        assert content == "Hello World"
def test_format_citations():
    api = PerplexityAPI(api_key="test_key")
    citations = ["http://test1.com", "http://test2.com"]
    formatted = api._format_citations(citations)
    expected = "\n\nReferences:\n[1] http://test1.com\n[2] http://test2.com"
    assert formatted == expected
def test_handle_stream_response_empty():
    api = PerplexityAPI(api_key="test_key")
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = []
    generator = api._handle_stream_response(mock_response, show_citations=True)
    output = list(generator)
    assert output == []
def test_missing_api_key():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            api = PerplexityAPI()
        assert "API key required" in str(exc_info.value)
