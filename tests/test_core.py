import pytest
import pytest
from plexsearch import __version__
from toml import load
import json
from unittest.mock import patch
from plexsearch.api import PerplexityAPI

def test_version_matches_pyproject():
    with open("pyproject.toml", "r") as f:
        pyproject = load(f)
    assert __version__ == pyproject["tool"]["poetry"]["version"]

def test_version_matches_changelog():
    with open("CHANGELOG.md", "r") as f:
        changelog = f.read()
    assert f"## [{__version__}]" in changelog
    
def test_payload_is_correct(mock_terminal):
    """Test that the payload is correctly constructed."""
    string_io, log_io = mock_terminal
    api = PerplexityAPI(api_key="test_key")
    
    query = "test query"
    model = "test_model"
    stream = True
    show_citations = False
    context = [{"role": "assistant", "content": "context message"}]

    with patch("requests.post") as mock_post:
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}

        list(api.perform_search(query, model, stream, show_citations, context))

    log_output = log_io.getvalue()
    
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
