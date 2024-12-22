import os
import pytest
import subprocess
import logging
from pathlib import Path
from unittest.mock import patch

def run_cli_command(args, env=None):
    """Helper to run the CLI command"""
    cmd = ["poetry", "run", "plexsearch"] + args
    print(f"Running command: {cmd}")
    logging.debug(f"Running command: {cmd}")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    print(f"stdout: {result.stdout}")
    logging.debug(f"stdout: {result.stdout}")
    logging.debug(f"stderr: {result.stderr}")
    return result

@pytest.mark.integration
def test_cli_basic_search(mock_terminal):
    """Test basic search using CLI"""
    with patch('plexsearch.api.PerplexityAPI.perform_search') as mock_handle_search:
        mock_handle_search.return_value = iter(["test response"])
        result = run_cli_command(["What is Python?"], env=os.environ)
        mock_handle_search.assert_called_once()

@pytest.mark.integration
def test_cli_with_model(mock_terminal):
    """Test CLI search with specific model"""
    with patch('plexsearch.api.PerplexityAPI.perform_search') as mock_search:
        mock_search.return_value = iter(["test response"])
        run_cli_command([
            "--model", "llama-3.1-sonar-small-128k-online",
            "What is Python?"
        ], env=os.environ)
        mock_search.assert_called_once()

@pytest.mark.integration
def test_cli_error_handling(mock_terminal):
    """Test CLI error handling with invalid API key"""
    with patch('plexsearch.api.PerplexityAPI.perform_search') as mock_search:
        mock_search.side_effect = Exception("API Error")
        result = run_cli_command(["test query"], env=os.environ)
        assert result.returncode != 0  # Verify non-zero exit code on error
