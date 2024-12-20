import os
import pytest
from unittest.mock import patch, MagicMock
import subprocess
from pathlib import Path

def run_cli_command(args):
    """Helper to run the CLI command"""
    cmd = ["poetry", "run", "plexsearch"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
    return result

@patch("plexsearch.config.Config")
@pytest.mark.integration
def test_cli_basic_search(mock_config):
    """Test basic search using CLI"""
    if "PERPLEXITY_API_KEY" not in os.environ:
        pytest.skip("PERPLEXITY_API_KEY environment variable not set")
    mock_args = MagicMock()
    mock_args.model = "llama-3.1-sonar-large-128k-online"
    mock_config.return_value.args = mock_args
    
    result = run_cli_command(["What is Python?"])
    assert result.returncode == 0
    assert len(result.stdout) > 0

@pytest.mark.integration
@patch("plexsearch.config.Config")
def test_cli_with_model(mock_config):
    """Test CLI search with specific model"""
    if "PERPLEXITY_API_KEY" not in os.environ:
        pytest.skip("PERPLEXITY_API_KEY environment variable not set")
    mock_args = MagicMock()
    mock_args.model = "llama-3.1-sonar-small-128k-online"
    mock_config.return_value.args = mock_args
        
    result = run_cli_command([
        "--model", "llama-3.1-sonar-small-128k-online",
        "What is Python?"
    ])
    assert result.returncode == 0
    assert len(result.stdout) > 0

@pytest.mark.integration
def test_cli_error_handling():
    """Test CLI error handling with invalid API key"""
    # Temporarily override API key
    env = os.environ.copy()
    env["PERPLEXITY_API_KEY"] = "invalid_key"
    
    cmd = ["poetry", "run", "plexsearch", "test query"]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert result.returncode != 0
